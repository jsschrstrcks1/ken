#!/usr/bin/env python3
"""
checkpoint.py — Thin shim that forwards the v1 API to keeper.

This file used to be a 365-LOC standalone session-checkpoint module. As of
the v1→v2 migration it has been replaced by a backward-compatible shim
that routes all v1 calls into `keeper` (family="default") under the hood.

Why the shim exists:
  - The session-checkpoint skill (.claude/skills/session-checkpoint/) calls
    this file's CLI directly (beat / scan / complete / status / new-id).
  - The session-pulse-scan hook (.claude/hooks/session-pulse-scan.sh)
    calls `python checkpoint.py scan` and parses the JSON output.
  - The orchestrator/tests/test_checkpoint.py suite imports this module's
    Python API.
  - Path C from the migration RFC: keep all those callers working
    unchanged while routing the actual work to keeper, which has the
    modern lease / journal / heartbeat / family semantics.

What this shim quietly fixes (v1 footguns the original orchestra round flagged):
  1. **stale_minutes default:** 30 → 90. Lunch breaks, code reviews, and
     long doc reads no longer trigger false ghosts. Tests passing a
     specific `stale_minutes=` value still work as before.
  2. **session-id-reuse warning:** when `beat()` is called with a different
     session_id than the current state holds, v1 silently reset beat_count
     to 1 (continuity lost). The shim still resets (preserves v1 contract)
     but emits a stderr warning so the caller notices.

Migration: on first read in a repo with a legacy session-pulse.json, the
shim transparently writes a fresh families/default/family.json from it
and archives the old file as session-pulse.json.migrated. Idempotent.

For new code, prefer keeper directly: `python -m keeper join --family X`
gives you per-family scope, lease/instance-token enforcement, atomic
.backup safety, and the cognitive review layer.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Wire keeper onto sys.path. orchestrator/ and keeper/ are siblings under ken/.
_HERE = Path(__file__).resolve().parent
_KEN_ROOT = _HERE.parent
if str(_KEN_ROOT) not in sys.path:
    sys.path.insert(0, str(_KEN_ROOT))

from keeper.checkpoint import (
    atomic_write_state,
    family_dir,
    family_json_path,
    heartbeat_age,
    new_id as _keeper_new_id,
    read_state,
    repo_root,
)
from keeper.checkpoint import beat as _keeper_beat
from keeper.checkpoint import complete as _keeper_complete
from keeper.checkpoint import join as _keeper_join

# v1 constants the test suite + skill + hook expect
DEFAULT_STALE_MINUTES = 90       # was 30; longer window per orchestra critique
LEGACY_PULSE_FILENAME = "session-pulse.json"
LEGACY_STALE_DIR_NAME = "session-pulse-stale"
DEFAULT_FAMILY = "default"


# ─── v1 path helpers (some tests reference these) ───────────────────────

def pulse_path(root: Path | None = None) -> Path:
    """Where the v1 pulse used to live. Post-migration this file is
    archived as `session-pulse.json.migrated` next to its original spot."""
    return (root or repo_root()) / ".claude" / "state" / LEGACY_PULSE_FILENAME


def stale_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".claude" / "state" / LEGACY_STALE_DIR_NAME


def _now() -> str:
    """ISO-8601 UTC, second precision. Same as v1."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ─── git helpers (v1; at_risk_files isn't in keeper) ───────────────────

def _git(root: Path, *args: str) -> list[str]:
    """Run a git command; return stdout lines. Empty list on error."""
    try:
        r = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=3, check=False,
        )
        if r.returncode != 0:
            return []
        return [ln for ln in r.stdout.splitlines() if ln.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


SKIP_PREFIXES = (".git/", "__pycache__/", "node_modules/", "dist/", "build/", ".venv/")
SKIP_SUFFIXES = (".pyc", ".pyo", ".log")


def _is_skippable(path: str) -> bool:
    if any(path.startswith(p) for p in SKIP_PREFIXES):
        return True
    if any(path.endswith(s) for s in SKIP_SUFFIXES):
        return True
    return False


def at_risk_files(root: Path | None = None, limit: int = 25) -> list[str]:
    """Files that look at-risk based on `git status --porcelain`. Same logic
    v1 had — keeper's `files_in_play` is user-supplied, not git-derived,
    so this stays in the shim."""
    root = root or repo_root()
    out = _git(root, "status", "--porcelain")
    files: list[str] = []
    for line in out:
        rest = line[3:] if len(line) > 3 else line
        if "->" in rest:
            rest = rest.split("->", 1)[-1].strip()
        rest = rest.strip().strip('"')
        if not rest or _is_skippable(rest):
            continue
        if rest not in files:
            files.append(rest)
        if len(files) >= limit:
            break
    return files


# ─── Time helpers ───────────────────────────────────────────────────────

def minutes_since(iso_ts: str | None) -> float | None:
    """Parse an ISO timestamp and return minutes elapsed, or None on bad input."""
    if not iso_ts:
        return None
    try:
        dt = datetime.fromisoformat(iso_ts)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    return delta.total_seconds() / 60.0


def is_stale(pulse: dict | None, stale_minutes: int = DEFAULT_STALE_MINUTES) -> bool:
    """True iff pulse is non-empty, status active, and last_beat older
    than stale_minutes. v1 semantics preserved."""
    if not pulse:
        return False
    if pulse.get("status") == "complete":
        return False
    age = minutes_since(pulse.get("last_beat"))
    if age is None:
        return False
    return age >= stale_minutes


# ─── Migration ──────────────────────────────────────────────────────────

def _migrate_legacy_pulse_if_needed(root: Path | None = None) -> bool:
    """If a legacy session-pulse.json exists and we don't yet have a
    families/default/family.json, migrate the pulse into the new format.
    Idempotent. Returns True iff a migration actually happened."""
    root = root or repo_root()
    legacy = pulse_path(root)
    new_path = family_json_path(DEFAULT_FAMILY, root)

    if not legacy.exists():
        return False

    if new_path.exists():
        # Already migrated; archive any straggler legacy file.
        archive = legacy.with_name(legacy.name + ".migrated")
        if not archive.exists():
            try:
                legacy.rename(archive)
            except OSError:
                pass
        return False

    try:
        old = json.loads(legacy.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False  # corrupt / unreadable; skip silently

    from keeper.checkpoint import (
        SCHEMA_VERSION,
        _new_token,
        _now_iso,
        _hostname,
        _boot_id,
        detect_branch,
        detect_worktree,
        detect_git_hash,
        touch_heartbeat,
    )

    state = {
        "schema": SCHEMA_VERSION,
        "family": DEFAULT_FAMILY,
        "session_id": old.get("session_id") or _keeper_new_id(),
        "instance_token": _new_token(),
        "generation": 1,
        "ended_cleanly": (old.get("status") == "complete"),
        "host": _hostname(),
        "pid": os.getpid(),
        "boot_id": _boot_id(),
        "started_at": old.get("started_at") or _now_iso(),
        "worktree": detect_worktree(root),
        "branch": detect_branch(root),
        "git_hash": detect_git_hash(root),
        "phase": "",
        "goal": old.get("context") or "",
        "done": [],
        "not_worked": [],
        "working": [old["last_action"]] if old.get("last_action") else [],
        "broken": [],
        "blocked": [],
        "decisions": [],
        "next_step": "",
        "files_in_play": list(old.get("files_in_play") or []),
        "warnings": ["migrated from legacy session-pulse.json"],
        "refs": [],
        "last_event_id": None,
        "beat_count": int(old.get("beat_count", 0)),
        "completed_at": old.get("completed_at"),
    }
    atomic_write_state(DEFAULT_FAMILY, state, root)
    touch_heartbeat(DEFAULT_FAMILY, root)

    archive = legacy.with_name(legacy.name + ".migrated")
    try:
        legacy.rename(archive)
    except OSError:
        pass

    sys.stderr.write(
        f"[checkpoint] migrated legacy pulse → {new_path}\n"
        f"[checkpoint] archived {legacy.name} → {archive.name}\n"
    )
    return True


def migrate_from_v1(root: Path | None = None) -> bool:
    """Public entry point for the auto-migration. Useful for scripting."""
    return _migrate_legacy_pulse_if_needed(root)


# ─── v1 API: read_pulse / write_pulse / beat / complete / scan ─────────

def read_pulse(root: Path | None = None) -> dict | None:
    """Return a v1-shaped pulse dict, derived from keeper family state."""
    _migrate_legacy_pulse_if_needed(root)
    state = read_state(DEFAULT_FAMILY, root)
    if state is None:
        return None

    age_seconds = heartbeat_age(DEFAULT_FAMILY, root)
    if age_seconds is not None:
        last_beat = (datetime.now(timezone.utc)
                     - timedelta(seconds=age_seconds)).isoformat(timespec="seconds")
    else:
        last_beat = state.get("started_at") or _now()

    last_action = ""
    if state.get("working"):
        last_action = state["working"][-1]

    pulse = {
        "session_id": state.get("session_id"),
        "started_at": state.get("started_at"),
        "last_beat": last_beat,
        "beat_count": int(state.get("beat_count", 0)),
        "status": "complete" if state.get("ended_cleanly") else "active",
        "last_action": last_action,
        "context": state.get("goal", ""),
        "files_in_play": list(state.get("files_in_play") or []),
        "at_risk": at_risk_files(root),
    }
    if state.get("ended_cleanly") and state.get("completed_at"):
        pulse["completed_at"] = state["completed_at"]
    return pulse


def write_pulse(pulse: dict, root: Path | None = None) -> Path:
    """Construct keeper state from a v1 pulse dict and persist it.
    Used by some tests; new callers should use beat() directly."""
    _migrate_legacy_pulse_if_needed(root)
    root = root or repo_root()
    sid = pulse.get("session_id") or _keeper_new_id()
    action = pulse.get("last_action") or ""
    context = pulse.get("context") or ""
    files = list(pulse.get("files_in_play") or [])
    beat(sid, action, context=context, files_in_play=files, root=root)
    return family_json_path(DEFAULT_FAMILY, root)


def beat(
    session_id: str,
    action: str,
    context: str = "",
    files_in_play: list[str] | None = None,
    root: Path | None = None,
) -> dict:
    """Record a heartbeat. Routes to keeper.beat under family='default'.

    Detects session-id changes mid-flight: if the current state has a
    different session_id than what's being passed, the prior session is
    overwritten (v1 contract preserved) but a stderr warning is emitted
    (v1 footgun fixed)."""
    _migrate_legacy_pulse_if_needed(root)
    existing = read_state(DEFAULT_FAMILY, root)

    if existing is None:
        # Fresh family; force=True skips prompts entirely.
        _keeper_join(
            DEFAULT_FAMILY, goal=context, force=True,
            interactive=False, root=root,
        )
        # Override the keeper-minted session_id so the v1 contract holds.
        _force_session_id(session_id, root)
    elif existing.get("session_id") != session_id:
        sys.stderr.write(
            f"[checkpoint] WARNING: session_id changed mid-flight "
            f"({existing.get('session_id')} → {session_id}). beat_count "
            f"is reset to 1. If this is a new session, run "
            f"`checkpoint.py scan` first or use `keeper join --force` "
            f"for an audited takeover.\n"
        )
        _keeper_join(
            DEFAULT_FAMILY, goal=context, force=True,
            interactive=False, reason="session-id-reuse (v1 shim)",
            root=root,
        )
        _force_session_id(session_id, root)

    _keeper_beat(
        DEFAULT_FAMILY,
        action=action,
        files=files_in_play,
        note=context if context else None,
        root=root,
    )
    return read_pulse(root)


def _force_session_id(session_id: str, root: Path | None) -> None:
    """Override the keeper-minted session_id with one supplied by the
    caller. Needed for the v1 contract: beat('sX', ...) must persist 'sX'."""
    state = read_state(DEFAULT_FAMILY, root)
    if state is None:
        return
    state["session_id"] = session_id
    atomic_write_state(DEFAULT_FAMILY, state, root)


def complete(
    session_id: str | None = None,
    root: Path | None = None,
) -> dict | None:
    """Mark current session complete. No-op if no session, or if
    session_id is provided and doesn't match the current."""
    _migrate_legacy_pulse_if_needed(root)
    state = read_state(DEFAULT_FAMILY, root)
    if state is None:
        return None
    if session_id and state.get("session_id") != session_id:
        return None
    _keeper_complete(DEFAULT_FAMILY, summary="", force=True, root=root)
    return read_pulse(root)


def scan(
    root: Path | None = None,
    stale_minutes: int = DEFAULT_STALE_MINUTES,
) -> dict | None:
    """If the current pulse is active AND stale, archive it and return a
    recovery report. Otherwise return None. v1 semantics preserved:
      * archives the stale pulse to .claude/state/session-pulse-stale/
      * surfaces handoff_present (HANDOFF.md at repo root)
      * recovery_summary is the human-readable block format_recovery() prints
    """
    root = root or repo_root()
    _migrate_legacy_pulse_if_needed(root)
    pulse = read_pulse(root)
    if not is_stale(pulse, stale_minutes):
        return None

    archive_path = _archive_stale(pulse, root)
    handoff_path = root / "HANDOFF.md"
    handoff_present = handoff_path.exists()
    age = minutes_since(pulse.get("last_beat"))

    short = {
        "session_id": pulse.get("session_id"),
        "started_at": pulse.get("started_at"),
        "minutes_since_last_beat": age,
        "last_action": pulse.get("last_action"),
        "context": pulse.get("context"),
        "files_in_play": pulse.get("files_in_play", []),
        "at_risk": pulse.get("at_risk", []),
    }
    summary = format_recovery(short)
    if handoff_present:
        summary += "\nHANDOFF.md present at repo root."

    return {
        "stale": True,
        "stale_minutes": stale_minutes,
        "minutes_since_last_beat": age,
        "pulse": pulse,
        "handoff_present": handoff_present,
        "archive_path": str(archive_path) if archive_path else None,
        "recovery_summary": summary,
    }


def _archive_stale(pulse: dict, root: Path) -> Path | None:
    """Save a snapshot of the stale pulse to the v1 stale archive dir.
    Format matches v1: {"pulse": <pulse dict>, "archived_at": iso}."""
    if not pulse:
        return None
    sd = stale_dir(root)
    sd.mkdir(parents=True, exist_ok=True)
    sid = pulse.get("session_id") or "unknown"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = sd / f"{sid}_{ts}.json"
    body = {"pulse": pulse, "archived_at": _now()}
    path.write_text(json.dumps(body, indent=2, default=str), encoding="utf-8")
    return path


def format_recovery(report: dict | None) -> str:
    """Human-readable recovery summary. Matches v1 layout closely."""
    if not report:
        return "(no stale session)"
    L = []
    L.append("── Stale session detected ──────────────────────────────────────")
    L.append(f"Session: {report.get('session_id')}")
    L.append(f"Started: {report.get('started_at')}")
    age = report.get("minutes_since_last_beat")
    if age is not None:
        L.append(f"Silent for: {age:.1f} min")
    if report.get("last_action"):
        L.append(f"Last action: {report['last_action']}")
    if report.get("context"):
        L.append(f"Context: {report['context']}")
    files = report.get("files_in_play") or []
    if files:
        L.append(f"Files in play: {', '.join(files)}")
    at_risk = report.get("at_risk") or []
    if at_risk:
        L.append(f"At risk now:   {', '.join(at_risk)}")
    L.append("────────────────────────────────────────────────────────────────")
    return "\n".join(L)


def new_id() -> str:
    """v1 callers expected this to live here; forward to keeper."""
    return _keeper_new_id()


# ─── CLI ────────────────────────────────────────────────────────────────

def _print(obj, as_json: bool):
    if as_json:
        print(json.dumps(obj, indent=2, default=str) if obj is not None else "null")
        return
    if obj is None:
        print("(no active session)")
        return
    print(json.dumps(obj, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="checkpoint",
        description="v1-compatible session checkpoint shim (forwards to keeper)",
    )
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("new-id", help="mint a fresh session id")

    p_beat = sub.add_parser("beat", help="record a heartbeat")
    p_beat.add_argument("--session", required=True)
    p_beat.add_argument("--action", required=True)
    p_beat.add_argument("--context", default="")
    p_beat.add_argument("--files", nargs="*", default=[])
    p_beat.add_argument("--json", action="store_true")

    p_complete = sub.add_parser("complete", help="mark current pulse complete")
    p_complete.add_argument("--session", default=None)
    p_complete.add_argument("--json", action="store_true")

    p_status = sub.add_parser("status", help="show current pulse")
    p_status.add_argument("--json", action="store_true")

    p_scan = sub.add_parser("scan", help="check for stale pulse")
    p_scan.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    p_scan.add_argument("--json", action="store_true")

    p_recover = sub.add_parser("recover", help="show recovery summary")
    p_recover.add_argument("--json", action="store_true")

    sub.add_parser("migrate", help="migrate legacy pulse (idempotent)")

    args = ap.parse_args(argv)

    if args.cmd == "new-id":
        print(new_id())
        return 0

    if args.cmd == "beat":
        pulse = beat(args.session, args.action,
                     context=args.context, files_in_play=args.files)
        if args.json:
            print(json.dumps(pulse, indent=2, default=str))
        return 0

    if args.cmd == "complete":
        result = complete(args.session)
        if result is None:
            sys.stderr.write(
                "[checkpoint] no active session to complete (or session id mismatch)\n"
            )
            return 1
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        return 0

    if args.cmd == "status":
        _print(read_pulse(), as_json=args.json)
        return 0

    if args.cmd == "scan":
        report = scan(stale_minutes=args.stale_minutes)
        if args.json:
            # Hook + tests expect {"ok": true, "stale": false} when fresh.
            if report is None:
                print(json.dumps({"ok": True, "stale": False}))
            else:
                print(json.dumps(report, indent=2, default=str))
        else:
            print(format_recovery(report) if report else "(no stale session)")
        return 0

    if args.cmd == "recover":
        pulse = read_pulse()
        if pulse is None:
            sys.stderr.write("[checkpoint] no pulse to recover\n")
            return 1
        report = {
            "stale": False,
            "session_id": pulse.get("session_id"),
            "started_at": pulse.get("started_at"),
            "last_action": pulse.get("last_action"),
            "context": pulse.get("context"),
            "files_in_play": pulse.get("files_in_play", []),
            "at_risk": pulse.get("at_risk", []),
            "minutes_since_last_beat": minutes_since(pulse.get("last_beat")),
            "beat_count": pulse.get("beat_count"),
        }
        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            print(format_recovery(report))
        return 0

    if args.cmd == "migrate":
        did = migrate_from_v1()
        print("migrated" if did else "no migration needed")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
