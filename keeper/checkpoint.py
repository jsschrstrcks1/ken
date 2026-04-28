"""keeper.checkpoint — Stage 1 core.

Five commands: join / beat / complete / recover / help / new-id.

File layout per family:
    .claude/state/families/<name>/
    ├── family.json          # consolidated lease+state, atomic tmp+rename
    ├── family.json.backup   # prior generation, for corruption fallback
    ├── heartbeat            # 0-byte file; mtime IS the heartbeat
    ├── journal.jsonl        # linked log via prev_event_id
    └── completed/           # archive of completed/forced-released sessions

Concepts lifted (with attribution): atomic_write w/ unique tmp suffix
(mclaude), worktree+branch detection (mclaude), schema_version migration
hook (mclaude), `ended_cleanly` flag + auto-escalation + handoff field
set + state-accumulator merge semantics (CONTINUITY), `family.json.backup`
safety net + debounced PreCompact + inline takeover prompt (orchestra
triad blind-spot). Strategic frame: keeper is session-continuity only;
Anthropic Auto Memory (v2.1.59+) owns knowledge-accumulation.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

STATE_DIR = ".claude/state/families"
STALE_WALL_SECONDS = 90 * 60          # composed criterion: wall-clock floor
STALE_SCAN_INTERVAL_SECONDS = 5       # second-scan delay for sequence check
STATE_SIZE_WARN = 2 * 1024            # 2 KB
STATE_SIZE_FAIL = 8 * 1024            # 8 KB
JOURNAL_ENTRY_MAX = 4 * 1024          # PIPE_BUF (atomic append)
COMPLETED_KEEP = 50                   # bound completed/ archive

FAMILY_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_HELD = 10
EXIT_STALE_NEEDS_TAKEOVER = 11
EXIT_NOT_FOUND = 12
EXIT_TOKEN_MISMATCH = 13
EXIT_CORRUPT_NO_BACKUP = 14


# ─── Path helpers ───────────────────────────────────────────────────────

def repo_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for c in [p, *p.parents]:
        if (c / ".git").exists():
            return c
    return p


def family_dir(family: str, root: Path | None = None) -> Path:
    return (root or repo_root()) / STATE_DIR / family


def family_json_path(family: str, root: Path | None = None) -> Path:
    return family_dir(family, root) / "family.json"


def family_json_backup_path(family: str, root: Path | None = None) -> Path:
    return family_dir(family, root) / "family.json.backup"


def heartbeat_path(family: str, root: Path | None = None) -> Path:
    return family_dir(family, root) / "heartbeat"


def journal_path(family: str, root: Path | None = None) -> Path:
    return family_dir(family, root) / "journal.jsonl"


def completed_dir(family: str, root: Path | None = None) -> Path:
    return family_dir(family, root) / "completed"


def keeper_conf_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".claude" / "keeper.conf"


# ─── Time, identity ─────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _now_epoch() -> float:
    return time.time()


def new_id() -> str:
    """Mint a fresh session id: sess-YYYYMMDDTHHMMSSZ-<6hex>."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"sess-{ts}-{uuid.uuid4().hex[:6]}"


def _new_token() -> str:
    return uuid.uuid4().hex


def _new_event_id() -> str:
    return uuid.uuid4().hex[:16]


def _hostname() -> str:
    try:
        return socket.gethostname()
    except OSError:
        return "unknown"


def _boot_id() -> str | None:
    """Linux boot-id; used to distinguish a same-host reboot from a live
    process. Returns None on macOS/other where /proc isn't available."""
    p = Path("/proc/sys/kernel/random/boot_id")
    if p.exists():
        try:
            return p.read_text().strip()
        except OSError:
            return None
    return None


# ─── Git helpers (mclaude pattern) ──────────────────────────────────────

def _git(root: Path, *args: str) -> str | None:
    import subprocess
    try:
        r = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=3,
        )
        if r.returncode != 0:
            return None
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def detect_branch(root: Path | None = None) -> str | None:
    root = root or repo_root()
    out = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return out if out and out != "HEAD" else None


def detect_worktree(root: Path | None = None) -> str | None:
    root = root or repo_root()
    common = _git(root, "rev-parse", "--git-common-dir")
    gd = _git(root, "rev-parse", "--git-dir")
    if not common or not gd:
        return None
    if os.path.realpath(common) != os.path.realpath(gd):
        toplevel = _git(root, "rev-parse", "--show-toplevel")
        return toplevel
    return None


def detect_git_hash(root: Path | None = None) -> str | None:
    root = root or repo_root()
    return _git(root, "rev-parse", "HEAD")


# ─── Atomic IO (mclaude unique-tmp-suffix pattern) ──────────────────────

def atomic_write(path: Path, content: str) -> None:
    """Write content via tmp+rename. Unique tmp suffix prevents collision
    when one session writes from two threads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{uuid.uuid4().hex[:8]}")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_state(family: str, state: dict, root: Path | None = None) -> Path:
    """Write family.json with .backup safety net (orchestra invariant 12).

    Order:
      1. If primary exists, rename it to .backup (atomic).
      2. Write new primary via tmp+rename (atomic).
      3. Old .backup is now overwritten by step 1's rename.
    On crash between step 1 and step 2, recovery falls back to .backup.
    """
    primary = family_json_path(family, root)
    backup = family_json_backup_path(family, root)
    body = json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True)
    if len(body.encode("utf-8")) > STATE_SIZE_FAIL:
        raise ValueError(
            f"family.json would be {len(body)} bytes, exceeds {STATE_SIZE_FAIL} hard cap"
        )
    primary.parent.mkdir(parents=True, exist_ok=True)
    if primary.exists():
        # atomic rename of primary → backup
        os.replace(primary, backup)
    atomic_write(primary, body)
    return primary


# ─── State read with backup fallback (orchestra O4) ─────────────────────

def read_state(family: str, root: Path | None = None) -> dict | None:
    """Read family.json. On corruption, fall back to family.json.backup.
    Returns None if neither exists or both are unreadable."""
    primary = family_json_path(family, root)
    backup = family_json_backup_path(family, root)
    for path, label in ((primary, "primary"), (backup, "backup")):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if label == "backup":
                # Loud warning but don't fail; user should know
                print(
                    f"[keeper] WARNING: {primary.name} unreadable; "
                    f"recovered from {backup.name}",
                    file=sys.stderr,
                )
            return _migrate_schema(data)
        except (json.JSONDecodeError, OSError):
            continue
    return None


def _migrate_schema(data: dict) -> dict:
    """Schema-version migration hook. v1 → v1 is a no-op."""
    schema = data.get("schema", 0)
    if schema == SCHEMA_VERSION:
        return data
    if schema > SCHEMA_VERSION:
        raise RuntimeError(
            f"family.json schema {schema} newer than keeper {SCHEMA_VERSION}; "
            f"upgrade keeper"
        )
    # Future: chain migrations here
    raise RuntimeError(
        f"family.json schema {schema} cannot be migrated to {SCHEMA_VERSION}"
    )


# ─── Heartbeat ──────────────────────────────────────────────────────────

def touch_heartbeat(family: str, root: Path | None = None) -> Path:
    p = heartbeat_path(family, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        os.utime(p, None)
    else:
        p.touch()
    return p


def heartbeat_age(family: str, root: Path | None = None) -> float | None:
    p = heartbeat_path(family, root)
    if not p.exists():
        return None
    try:
        return _now_epoch() - p.stat().st_mtime
    except OSError:
        return None


def is_stale(family: str, root: Path | None = None) -> bool:
    """Composed criterion: wall-clock floor only at Stage 1.

    Stage 1.5 will add the second-scan sequence-unchanged check; for v1,
    ~90 min wall-clock silence is good enough — false positives are
    handled by the inline-takeover prompt."""
    age = heartbeat_age(family, root)
    return age is not None and age > STALE_WALL_SECONDS


# ─── Journal (linked log) ───────────────────────────────────────────────

def _last_event_id(family: str, root: Path | None = None) -> str | None:
    """Read the last event_id from journal.jsonl, or None if empty.
    Skips trailing newline / partial-write lines."""
    p = journal_path(family, root)
    if not p.exists():
        return None
    last = None
    try:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    last = e.get("event_id")
                except json.JSONDecodeError:
                    # Partial write / corruption — stop at last good
                    break
        return last
    except OSError:
        return None


def journal_append(
    family: str,
    event_type: str,
    payload: dict,
    session_id: str,
    instance_token: str,
    root: Path | None = None,
) -> str:
    """Append a linked-log entry. Returns the new event_id.

    Single-line JSON, <PIPE_BUF for atomic append. Fails loudly if a line
    would exceed the limit.
    """
    p = journal_path(family, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": _now_iso(),
        "event_id": _new_event_id(),
        "prev_event_id": _last_event_id(family, root),
        "session_id": session_id,
        "instance_token": instance_token,
        "git_hash": detect_git_hash(root),
        "type": event_type,
        "payload": payload,
    }
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
    if len(line.encode("utf-8")) > JOURNAL_ENTRY_MAX:
        raise ValueError(
            f"journal entry {len(line)} bytes exceeds atomic-append limit {JOURNAL_ENTRY_MAX}"
        )
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    return entry["event_id"]


def journal_tail(family: str, n: int = 50, root: Path | None = None) -> list[dict]:
    p = journal_path(family, root)
    if not p.exists():
        return []
    out: list[dict] = []
    try:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    break
    except OSError:
        return []
    return out[-n:]


# ─── State construction & merge ─────────────────────────────────────────

def _empty_state(family: str, session_id: str, instance_token: str,
                 generation: int = 1, goal: str = "") -> dict:
    now = _now_iso()
    return {
        "schema": SCHEMA_VERSION,
        "family": family,
        "session_id": session_id,
        "instance_token": instance_token,
        "generation": generation,
        "ended_cleanly": False,
        "host": _hostname(),
        "pid": os.getpid(),
        "boot_id": _boot_id(),
        "started_at": now,
        "worktree": detect_worktree(),
        "branch": detect_branch(),
        "git_hash": detect_git_hash(),
        "phase": "",
        "goal": goal,
        "done": [],
        "not_worked": [],
        "working": [],
        "broken": [],
        "blocked": [],
        "decisions": [],
        "next_step": "",
        "files_in_play": [],
        "warnings": [],
        "refs": [],
        "last_event_id": None,
        "beat_count": 0,
    }


def _merge_state(state: dict, updates: dict) -> dict:
    """CONTINUITY accumulator: latest wins for scalars, append-with-dedup
    for arrays. Mutates state and returns it."""
    SCALAR_KEYS = ("phase", "goal", "next_step")
    ARRAY_KEYS = (
        "done", "not_worked", "working", "broken", "blocked",
        "warnings", "refs", "files_in_play",
    )
    for k in SCALAR_KEYS:
        if k in updates and updates[k]:
            state[k] = updates[k]
    for k in ARRAY_KEYS:
        if k in updates and updates[k]:
            existing = state.get(k, [])
            for item in updates[k]:
                if item not in existing:
                    existing.append(item)
            state[k] = existing
    if "decisions" in updates and updates["decisions"]:
        existing = state.get("decisions", [])
        for d in updates["decisions"]:
            existing.append(d)
        state["decisions"] = existing
    if "files_in_play_set" in updates:  # explicit replace
        state["files_in_play"] = updates["files_in_play_set"]
    return state


# ─── Public API: join / beat / complete / recover ───────────────────────

def _validate_family(family: str) -> None:
    if not FAMILY_NAME_RE.match(family):
        raise ValueError(
            f"invalid family name {family!r}: must match {FAMILY_NAME_RE.pattern}"
        )


def join(
    family: str,
    *,
    goal: str = "",
    force: bool = False,
    reason: str | None = None,
    interactive: bool = True,
    root: Path | None = None,
) -> dict:
    """Acquire a family. Three paths:
      1. Family does not exist → create.
      2. Family exists, holder is stale → prompt y/n (or auto-takeover if --force).
      3. Family exists, holder is fresh → reject (caller can retry --force).

    Returns the new state dict.
    """
    _validate_family(family)
    root = root or repo_root()
    primary = family_json_path(family, root)
    existing = read_state(family, root) if primary.exists() else None

    if existing is None:
        # Path 1: fresh create
        sess = new_id()
        token = _new_token()
        state = _empty_state(family, sess, token, generation=1, goal=goal)
        eid = journal_append(
            family, "join",
            {"goal": goal, "first": True},
            sess, token, root,
        )
        state["last_event_id"] = eid
        atomic_write_state(family, state, root)
        touch_heartbeat(family, root)
        return state

    # Path 2 or 3: family exists
    stale = is_stale(family, root)
    holder_unclean = not existing.get("ended_cleanly", False)
    if not stale and not force:
        # Fresh holder — reject (path 3)
        age = heartbeat_age(family, root) or 0
        msg = (
            f"[keeper] family '{family}' is held by session "
            f"{existing.get('session_id')} (heartbeat {age:.0f}s ago). "
            f"Use --force to take over."
        )
        raise SystemExit(_format_held_error(msg, EXIT_HELD))

    # Path 2: stale or force — possibly prompt
    if stale and not force and interactive:
        age = heartbeat_age(family, root) or 0
        prev_session = existing.get("session_id", "?")
        sys.stderr.write(
            f"[keeper] family '{family}' is STALE "
            f"(heartbeat {age/60:.0f}min ago, holder={prev_session}).\n"
            f"  Take over? [y/N] "
        )
        sys.stderr.flush()
        try:
            answer = input().strip().lower()
        except EOFError:
            answer = "n"
        if answer not in ("y", "yes"):
            raise SystemExit(_format_held_error(
                f"[keeper] aborted; family '{family}' not taken over.",
                EXIT_STALE_NEEDS_TAKEOVER,
            ))

    # Takeover (force or stale-confirmed)
    sess = new_id()
    token = _new_token()
    new_gen = int(existing.get("generation", 1)) + 1
    payload = {
        "previous_session": existing.get("session_id"),
        "previous_generation": existing.get("generation"),
        "previous_ended_cleanly": existing.get("ended_cleanly", False),
        "reason": reason or ("stale-confirmed" if stale else "force"),
        "force": force,
    }
    eid = journal_append(family, "forced_takeover", payload, sess, token, root)
    new_state = _empty_state(family, sess, token, generation=new_gen, goal=goal)
    if holder_unclean:
        new_state["warnings"].append(
            f"previous session {existing.get('session_id')} ended uncleanly"
        )
    new_state["last_event_id"] = eid
    atomic_write_state(family, new_state, root)
    touch_heartbeat(family, root)
    return new_state


def _format_held_error(msg: str, code: int) -> str:
    sys.stderr.write(msg + "\n")
    return msg if False else ""  # unreachable; SystemExit takes the int


def beat(
    family: str,
    *,
    action: str | None = None,
    working_on: str | None = None,
    decision: tuple[str, str] | None = None,
    files: list[str] | None = None,
    next_step: str | None = None,
    phase: str | None = None,
    note: str | None = None,
    auto: bool = False,
    reason: str | None = None,
    root: Path | None = None,
) -> dict:
    """Update family state. Read-modify-write transaction (Android
    DataStore shape). Touches heartbeat. Appends a journal entry.
    """
    _validate_family(family)
    root = root or repo_root()
    state = read_state(family, root)
    if state is None:
        sys.stderr.write(
            f"[keeper] no family '{family}' in this repo; "
            f"run `keeper join --family {family}` first.\n"
        )
        raise SystemExit(EXIT_NOT_FOUND)
    sess = state["session_id"]
    token = state["instance_token"]

    # Consume any deferred precompact marker
    pending = family_dir(family, root) / "precompact.pending"
    if pending.exists():
        try:
            pending.unlink()
            journal_append(family, "snapshot",
                           {"trigger": "precompact-deferred"},
                           sess, token, root)
        except OSError:
            pass

    # Build update dict
    updates: dict[str, Any] = {}
    if action:
        updates["working"] = [action]
    if working_on:
        updates["phase"] = working_on
    if files is not None:
        updates["files_in_play_set"] = files
    if next_step:
        updates["next_step"] = next_step
    if phase:
        updates["phase"] = phase
    if decision:
        what, why = decision
        updates["decisions"] = [{"what": what, "why": why}]
    if note:
        updates["warnings"] = [note]

    payload = {"action": action, "auto": auto, "reason": reason}
    if decision:
        payload["decision"] = {"what": decision[0], "why": decision[1]}
    eid = journal_append(family, "beat", payload, sess, token, root)

    _merge_state(state, updates)
    state["beat_count"] = int(state.get("beat_count", 0)) + 1
    state["last_event_id"] = eid

    atomic_write_state(family, state, root)
    touch_heartbeat(family, root)
    return state


def complete(
    family: str,
    *,
    summary: str = "",
    root: Path | None = None,
) -> dict:
    """Graceful end. Sets ended_cleanly=true; archives a markdown
    summary; releases the family for the next session."""
    _validate_family(family)
    root = root or repo_root()
    state = read_state(family, root)
    if state is None:
        sys.stderr.write(
            f"[keeper] no family '{family}' to complete in this repo.\n"
        )
        raise SystemExit(EXIT_NOT_FOUND)
    sess = state["session_id"]
    token = state["instance_token"]
    eid = journal_append(family, "complete",
                         {"summary": summary}, sess, token, root)
    state["ended_cleanly"] = True
    state["last_event_id"] = eid
    state["completed_at"] = _now_iso()

    atomic_write_state(family, state, root)
    touch_heartbeat(family, root)

    # Archive markdown summary
    cdir = completed_dir(family, root)
    cdir.mkdir(parents=True, exist_ok=True)
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    archive = cdir / f"{family}_{when}_complete.md"
    archive.write_text(_render_completion_md(state, summary), encoding="utf-8")
    return state


def _render_completion_md(state: dict, summary: str) -> str:
    L = []
    L.append(f"# Session complete — {state.get('family')}")
    L.append("")
    L.append(f"**Session:** {state.get('session_id')}")
    L.append(f"**Generation:** {state.get('generation')}")
    L.append(f"**Started:** {state.get('started_at')}")
    L.append(f"**Completed:** {state.get('completed_at')}")
    L.append(f"**Beat count:** {state.get('beat_count')}")
    if state.get("branch"):
        L.append(f"**Branch:** {state['branch']}")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append(summary or "(no summary provided)")
    L.append("")
    for header, key in (
        ("Done", "done"),
        ("Working", "working"),
        ("Broken", "broken"),
        ("Blocked", "blocked"),
        ("Decisions", "decisions"),
    ):
        items = state.get(key) or []
        if not items:
            continue
        L.append(f"## {header}")
        L.append("")
        for it in items:
            if key == "decisions" and isinstance(it, dict):
                L.append(f"- **{it.get('what','?')}** — {it.get('why','')}")
            else:
                L.append(f"- {it}")
        L.append("")
    return "\n".join(L)


def recover(
    family: str,
    *,
    json_output: bool = False,
    root: Path | None = None,
) -> dict | None:
    """Print the recovery brief. JSON mode for Claude priming; text mode
    for human reading. Falls back to .backup if primary corrupt."""
    _validate_family(family)
    root = root or repo_root()
    state = read_state(family, root)
    if state is None:
        sys.stderr.write(
            f"[keeper] no family '{family}' (or unreadable + no backup) in {root}\n"
        )
        return None

    # Surface mid-thread context
    age = heartbeat_age(family, root)
    state["_recovery_meta"] = {
        "heartbeat_age_seconds": age,
        "stale": is_stale(family, root),
        "ended_cleanly": state.get("ended_cleanly"),
        "journal_tail": journal_tail(family, n=10, root=root),
    }

    if json_output:
        print(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_recovery_text(state))
    return state


def _render_recovery_text(state: dict) -> str:
    meta = state.get("_recovery_meta", {})
    L = []
    L.append(f"=== keeper recovery brief — family '{state.get('family')}' ===")
    L.append(f"Session:    {state.get('session_id')}  (gen {state.get('generation')})")
    if meta.get("heartbeat_age_seconds") is not None:
        age_min = meta["heartbeat_age_seconds"] / 60
        L.append(f"Heartbeat:  {age_min:.1f} min ago"
                 + ("  [STALE]" if meta.get("stale") else ""))
    L.append(f"Ended:      {'cleanly' if meta.get('ended_cleanly') else 'unclean / in-progress'}")
    if state.get("branch"):
        L.append(f"Branch:     {state.get('branch')}")
    if state.get("phase"):
        L.append(f"Phase:      {state['phase']}")
    if state.get("goal"):
        L.append(f"Goal:       {state['goal']}")
    L.append("")
    for header, key in (
        ("Working", "working"),
        ("Broken", "broken"),
        ("Blocked", "blocked"),
    ):
        items = state.get(key) or []
        if not items:
            continue
        L.append(f"{header}:")
        for it in items:
            L.append(f"  • {it}")
    decisions = state.get("decisions") or []
    if decisions:
        L.append("Decisions:")
        for d in decisions:
            if isinstance(d, dict):
                L.append(f"  • {d.get('what','?')} — {d.get('why','')}")
            elif isinstance(d, list) and len(d) >= 2:
                L.append(f"  • {d[0]} — {d[1]}")
    files = state.get("files_in_play") or []
    if files:
        L.append("Files in play:")
        for f in files:
            L.append(f"  • {f}")
    if state.get("next_step"):
        L.append("")
        L.append(f"NEXT STEP: {state['next_step']}")
    return "\n".join(L)


# ─── CLI ────────────────────────────────────────────────────────────────

HELP_TEXT = """\
keeper — session-continuity for Claude Code threads

USAGE
  keeper join     --family <name> [--goal "..."] [--force] [--reason "..."]
  keeper beat     [--family <name>] [--action "..."] [--working-on "..."]
                  [--decision "what" "why"] [--files a.py b.py]
                  [--next-step "..."] [--phase "..."] [--note "..."]
                  [--auto] [--reason "..."]
  keeper complete [--family <name>] [--summary "..."]
  keeper recover  [--family <name>] [--json]
  keeper new-id
  keeper help

EXAMPLES
  # Start a session in family 'ports'
  keeper join --family ports --goal "wire up new health-check endpoint"

  # Record progress mid-session
  keeper beat --action "added /health route" --files src/api.py
  keeper beat --decision "use 200 OK" "matches existing /ready"

  # End cleanly
  keeper complete --summary "endpoint shipping; CI green"

  # Resume in a new shell after the previous one died
  keeper recover --family ports
  keeper recover --family ports --json | jq .

FAMILY NAMES
  Lowercase letters/digits/hyphens, max 32 chars.

ENV / CONFIG
  KEEPER_FAMILY    default family if no --family supplied
  .claude/keeper.conf   repo-local default_family

STATE LIVES IN
  <repo>/.claude/state/families/<name>/family.json
"""


def _resolve_family(arg: str | None, root: Path | None = None) -> str:
    """Resolve family from --family flag, KEEPER_FAMILY env, or
    .claude/keeper.conf."""
    if arg:
        return arg
    env = os.environ.get("KEEPER_FAMILY")
    if env:
        return env
    conf = keeper_conf_path(root)
    if conf.exists():
        try:
            for line in conf.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = (s.strip() for s in line.split("=", 1))
                    if k == "default_family":
                        return v
        except OSError:
            pass
    sys.stderr.write(
        "[keeper] no family specified. Use --family <name>, "
        "set KEEPER_FAMILY, or write `default_family = X` to "
        ".claude/keeper.conf\n"
    )
    raise SystemExit(EXIT_USAGE)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="keeper",
        description="Session-continuity for Claude Code threads",
        add_help=False,  # we provide our own `help` subcommand
    )
    p.add_argument("-h", "--help", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    p_join = sub.add_parser("join", add_help=False)
    p_join.add_argument("--family")
    p_join.add_argument("--goal", default="")
    p_join.add_argument("--force", action="store_true")
    p_join.add_argument("--reason")
    p_join.add_argument("--non-interactive", action="store_true",
                        help="never prompt; rely on --force or fail")

    p_beat = sub.add_parser("beat", add_help=False)
    p_beat.add_argument("--family")
    p_beat.add_argument("--action")
    p_beat.add_argument("--working-on")
    p_beat.add_argument("--decision", nargs=2, metavar=("WHAT", "WHY"))
    p_beat.add_argument("--files", nargs="*")
    p_beat.add_argument("--next-step")
    p_beat.add_argument("--phase")
    p_beat.add_argument("--note")
    p_beat.add_argument("--auto", action="store_true")
    p_beat.add_argument("--reason")

    p_complete = sub.add_parser("complete", add_help=False)
    p_complete.add_argument("--family")
    p_complete.add_argument("--summary", default="")

    p_recover = sub.add_parser("recover", add_help=False)
    p_recover.add_argument("--family")
    p_recover.add_argument("--json", action="store_true")

    sub.add_parser("new-id", add_help=False)
    sub.add_parser("help", add_help=False)

    args = p.parse_args(argv)
    if args.help or args.cmd in (None, "help"):
        sys.stdout.write(HELP_TEXT)
        return EXIT_OK

    try:
        if args.cmd == "new-id":
            print(new_id())
            return EXIT_OK

        if args.cmd == "join":
            family = _resolve_family(args.family)
            join(
                family,
                goal=args.goal,
                force=args.force,
                reason=args.reason,
                interactive=not args.non_interactive,
            )
            print(f"[keeper] joined family '{family}'")
            return EXIT_OK

        if args.cmd == "beat":
            family = _resolve_family(args.family)
            decision = tuple(args.decision) if args.decision else None
            beat(
                family,
                action=args.action,
                working_on=args.working_on,
                decision=decision,
                files=args.files,
                next_step=args.next_step,
                phase=args.phase,
                note=args.note,
                auto=args.auto,
                reason=args.reason,
            )
            return EXIT_OK

        if args.cmd == "complete":
            family = _resolve_family(args.family)
            complete(family, summary=args.summary)
            print(f"[keeper] completed family '{family}'")
            return EXIT_OK

        if args.cmd == "recover":
            family = _resolve_family(args.family)
            r = recover(family, json_output=args.json)
            return EXIT_OK if r is not None else EXIT_NOT_FOUND

        sys.stderr.write(f"unknown command: {args.cmd}\n")
        return EXIT_USAGE

    except ValueError as e:
        sys.stderr.write(f"[keeper] {e}\n")
        return EXIT_USAGE
    except SystemExit as e:
        # Already wrote its own message to stderr
        if isinstance(e.code, int):
            return e.code
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
