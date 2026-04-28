#!/usr/bin/env python3
"""
checkpoint.py — Session pulse + stale-session detection.

A session writes a small JSON file (the *pulse*) at startup and updates it
periodically. A graceful end marks the pulse `complete`. If a pulse is older
than the staleness threshold and was never marked complete, the session is
treated as abandoned — almost always because of a rate-limit kill, an OOM, or
the user closing the terminal mid-edit.

Pulse path:        <repo>/.claude/state/session-pulse.json
Stale archive:     <repo>/.claude/state/stale-sessions/<timestamp>.json

The pulse captures, on every beat, the list of git-uncommitted files. That is
the single most useful piece of data when recovering from an abandoned
session — it tells the next session exactly which files held in-flight work.

Design notes:
  - Single-file atomic state. Each beat overwrites the pulse in full; we never
    have a half-written pulse on disk.
  - No daemon. The session itself calls `beat` from the session-checkpoint
    skill protocol. `scan` runs at session start to surface abandoned work.
  - Repo-scoped. Each repo has its own pulse. Cross-repo scans iterate roots.
  - No metaphors. `complete` not "flatline", `stale` not "ghost".

CLI:
  checkpoint.py beat --session ID --action TEXT [--context TEXT] [--files A B]
  checkpoint.py complete [--session ID]
  checkpoint.py status [--json]
  checkpoint.py scan [--stale-minutes N] [--json]
  checkpoint.py recover [--json]
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PULSE_FILENAME = "session-pulse.json"
STATE_DIR = Path(".claude/state")
STALE_DIR_NAME = "stale-sessions"
DEFAULT_STALE_MINUTES = 30

# Files we never list as "at risk" — they're either generated, ignored,
# or part of the checkpointing system itself.
SKIP_PREFIXES = (
    ".claude/state/",
    "__pycache__/",
    "node_modules/",
    ".next/",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
)
SKIP_SUFFIXES = (".pyc", ".pyo", ".log")


# ─────────────────────────────────────────────
# Path helpers
# ─────────────────────────────────────────────

def repo_root(start: Path = None) -> Path:
    """Walk up from `start` (or cwd) until we find a .git directory."""
    p = (start or Path.cwd()).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return candidate
    return p  # fall back to cwd if not a git repo


def pulse_path(root: Path = None) -> Path:
    return (root or repo_root()) / STATE_DIR / PULSE_FILENAME


def stale_dir(root: Path = None) -> Path:
    return (root or repo_root()) / STATE_DIR / STALE_DIR_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ─────────────────────────────────────────────
# Pulse read/write
# ─────────────────────────────────────────────

def read_pulse(root: Path = None) -> dict | None:
    path = pulse_path(root)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def write_pulse(pulse: dict, root: Path = None) -> Path:
    path = pulse_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(pulse, indent=2))
    tmp.replace(path)  # atomic on POSIX
    return path


def beat(
    session_id: str,
    action: str,
    context: str = "",
    files_in_play: list[str] | None = None,
    root: Path = None,
) -> dict:
    """Record a heartbeat. Increments beat_count when the session continues."""
    root = root or repo_root()
    now = _now()
    existing = read_pulse(root)

    if existing and existing.get("session_id") == session_id and existing.get("status") != "complete":
        started_at = existing.get("started_at", now)
        beat_count = int(existing.get("beat_count", 0)) + 1
    else:
        started_at = now
        beat_count = 1

    pulse = {
        "session_id": session_id,
        "started_at": started_at,
        "last_beat": now,
        "beat_count": beat_count,
        "status": "active",
        "last_action": action,
        "context": context,
        "files_in_play": files_in_play or [],
        "at_risk": at_risk_files(root),
    }
    write_pulse(pulse, root)
    return pulse


def complete(session_id: str | None = None, root: Path = None) -> dict | None:
    """Mark the current pulse complete. A no-op if no pulse exists."""
    root = root or repo_root()
    pulse = read_pulse(root)
    if pulse is None:
        return None
    if session_id and pulse.get("session_id") != session_id:
        return None
    pulse["status"] = "complete"
    pulse["completed_at"] = _now()
    write_pulse(pulse, root)
    return pulse


# ─────────────────────────────────────────────
# Staleness detection
# ─────────────────────────────────────────────

def minutes_since(iso_ts: str) -> float | None:
    try:
        # Accept both naive ISO and tz-aware ISO.
        ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() / 60
    except (ValueError, TypeError, AttributeError):
        return None


def is_stale(pulse: dict, stale_minutes: int = DEFAULT_STALE_MINUTES) -> bool:
    if not pulse:
        return False
    if pulse.get("status") == "complete":
        return False
    elapsed = minutes_since(pulse.get("last_beat", ""))
    return elapsed is None or elapsed > stale_minutes


# ─────────────────────────────────────────────
# Git introspection — files at risk
# ─────────────────────────────────────────────

def _git(root: Path, *args: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    return [line for line in proc.stdout.splitlines() if line]


def _is_skippable(path: str) -> bool:
    if path.startswith(".") and not path.startswith(".claude/"):
        # dotfiles in repo root are usually noise (.DS_Store, .env.local)
        return True
    return path.startswith(SKIP_PREFIXES) or path.endswith(SKIP_SUFFIXES)


def at_risk_files(root: Path = None, limit: int = 25) -> list[str]:
    """Files that would be lost if the session crashed right now.

    Union of: untracked (new files) + unstaged-modified + staged-but-uncommitted.
    Filtered against SKIP_PREFIXES/SKIP_SUFFIXES and capped at `limit`.
    """
    root = root or repo_root()
    untracked = _git(root, "ls-files", "--others", "--exclude-standard")
    modified = _git(root, "diff", "--name-only")
    staged = _git(root, "diff", "--name-only", "--cached")

    seen: set[str] = set()
    ordered: list[str] = []
    for f in [*untracked, *modified, *staged]:
        if f in seen or _is_skippable(f):
            continue
        seen.add(f)
        ordered.append(f)
        if len(ordered) >= limit:
            break
    return ordered


# ─────────────────────────────────────────────
# Scan + archive
# ─────────────────────────────────────────────

def scan(root: Path = None, stale_minutes: int = DEFAULT_STALE_MINUTES) -> dict | None:
    """Detect a stale pulse and archive it. Returns the report or None."""
    root = root or repo_root()
    pulse = read_pulse(root)
    if not pulse or not is_stale(pulse, stale_minutes):
        return None

    elapsed = minutes_since(pulse.get("last_beat", ""))
    handoff_path = root / "HANDOFF.md"
    handoff_present = handoff_path.exists()

    report = {
        "detected_at": _now(),
        "minutes_silent": round(elapsed, 1) if elapsed is not None else None,
        "stale_threshold_minutes": stale_minutes,
        "handoff_present": handoff_present,
        "handoff_path": str(handoff_path) if handoff_present else None,
        "pulse": pulse,
    }
    report["recovery_summary"] = format_recovery(report)

    archive = stale_dir(root)
    archive.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sid = (pulse.get("session_id") or "unknown").replace("/", "_")[:60]
    out = archive / f"{stamp}-{sid}.json"
    out.write_text(json.dumps(report, indent=2))
    report["archive_path"] = str(out)
    return report


def format_recovery(report: dict) -> str:
    pulse = report.get("pulse", {})
    files = pulse.get("at_risk") or pulse.get("files_in_play") or []
    handoff_note = (
        f"HANDOFF.md present at {report['handoff_path']} — start there."
        if report.get("handoff_present")
        else "No HANDOFF.md was written. The session likely died before handoff."
    )
    lines = [
        f"Stale session: {pulse.get('session_id', '?')}",
        f"Silent for {report.get('minutes_silent')} minutes "
        f"(threshold {report.get('stale_threshold_minutes')}m).",
        f"Started:     {pulse.get('started_at', '?')}",
        f"Last beat:   {pulse.get('last_beat', '?')}",
        f"Beats:       {pulse.get('beat_count', 0)}",
        f"Last action: {pulse.get('last_action', '?')}",
    ]
    if pulse.get("context"):
        lines.append(f"Context:     {pulse['context']}")
    if files:
        lines.append("Files at risk (uncommitted when session died):")
        lines.extend(f"  - {f}" for f in files)
    lines.append(handoff_note)
    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def _print(obj, as_json: bool):
    if as_json:
        print(json.dumps(obj, indent=2, default=str))
    elif isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="checkpoint", description=__doc__.splitlines()[1])
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("beat", help="Record a heartbeat.")
    b.add_argument("--session", required=True)
    b.add_argument("--action", required=True)
    b.add_argument("--context", default="")
    b.add_argument("--files", nargs="*", default=None)
    b.add_argument("--json", action="store_true")

    c = sub.add_parser("complete", help="Mark the current pulse complete.")
    c.add_argument("--session", default=None)
    c.add_argument("--json", action="store_true")

    s = sub.add_parser("status", help="Show current pulse and at-risk files.")
    s.add_argument("--json", action="store_true")

    sc = sub.add_parser("scan", help="Detect and archive a stale session.")
    sc.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    sc.add_argument("--json", action="store_true")

    r = sub.add_parser("recover", help="Print recovery summary for the latest stale or active session.")
    r.add_argument("--json", action="store_true")

    sub.add_parser("new-id", help="Generate a fresh session id.")

    args = ap.parse_args(argv)
    root = repo_root()

    if args.cmd == "beat":
        pulse = beat(args.session, args.action, args.context, args.files, root)
        _print(pulse, args.json)
        return 0

    if args.cmd == "complete":
        pulse = complete(args.session, root)
        if pulse is None:
            _print({"ok": False, "reason": "no matching pulse"}, args.json)
            return 1
        _print(pulse, args.json)
        return 0

    if args.cmd == "status":
        pulse = read_pulse(root)
        report = {
            "pulse": pulse,
            "stale": is_stale(pulse) if pulse else False,
            "at_risk": at_risk_files(root),
        }
        _print(report, args.json)
        return 0

    if args.cmd == "scan":
        report = scan(root, args.stale_minutes)
        if report is None:
            _print({"ok": True, "stale": False}, args.json)
            return 0
        _print(report["recovery_summary"] if not args.json else report, args.json)
        return 0

    if args.cmd == "recover":
        pulse = read_pulse(root)
        if pulse is None:
            _print({"ok": False, "reason": "no pulse"}, args.json)
            return 1
        if pulse.get("status") == "complete":
            _print({"ok": True, "status": "complete", "pulse": pulse}, args.json)
            return 0
        elapsed = minutes_since(pulse.get("last_beat", ""))
        report = {
            "detected_at": _now(),
            "minutes_silent": round(elapsed, 1) if elapsed is not None else None,
            "stale_threshold_minutes": DEFAULT_STALE_MINUTES,
            "handoff_present": (root / "HANDOFF.md").exists(),
            "handoff_path": str(root / "HANDOFF.md") if (root / "HANDOFF.md").exists() else None,
            "pulse": pulse,
        }
        _print(format_recovery(report) if not args.json else report, args.json)
        return 0

    if args.cmd == "new-id":
        print(f"sess-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
