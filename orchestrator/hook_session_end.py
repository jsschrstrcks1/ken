#!/usr/bin/env python3
"""Slice 7 SessionEnd hook extractor.

Invoked DETACHED from ``.claude/hooks/session-end.sh`` with the
Claude Code SessionEnd hook JSON on stdin. Calls
``extract_candidates_from_observations(session_id)`` and writes a
human-readable candidate report to stdout (the wrapper redirects
stdout to /tmp/session-end-candidates.txt).

Fail-closed contract: ANY error here is swallowed and printed to
stderr (the wrapper redirects stderr to /tmp/session-end-hook.err).
The script always exits 0 so session teardown is never blocked.

No auto-promotion: candidates are surfaced for OPERATOR REVIEW only.
Promotion requires explicit ``memory_ops.promote_to_instinct(id)``
call — this script never promotes anything automatically.

Opt-in: writes only when MEMORY_AUTO_OBSERVE_ENABLED=true is set
(same flag as Slice 6 observe hook). Default off.

Output format (to stdout → /tmp/session-end-candidates.txt):

    === Session-End Candidates [session_id] at [timestamp] ===
    N candidates found.

    [1] TOOL_PATTERN — first_seen … last_seen
        Domain hint: <domain>
        Evidence: <n> observations, integrity <ok|warn>
        Content: <truncated>

    === End ===
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone


def _safe_import_memory_ops():
    """Import memory_ops from the orchestrator directory."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "memory_ops", os.path.join(here, "memory_ops.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _resolve_session_id(hook_json):
    """Extract session_id from Claude Code's SessionEnd hook payload.

    Hook shape (approximate, may vary by Claude Code version):
        {"session_id": "...", "reason": "...", ...}

    Falls back to _current_session_id() from memory_ops if not in payload.
    """
    if isinstance(hook_json, dict):
        sid = hook_json.get("session_id") or hook_json.get("sessionId")
        if sid and isinstance(sid, str) and len(sid) > 0:
            return sid
    return None


def _format_candidates(candidates, session_id):
    """Format candidates as human-readable text for the operator."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        f"",
        f"{'='*70}",
        f"Session-End Candidates  [{session_id}]  at {now}",
        f"{'='*70}",
        f"{len(candidates)} candidate(s) found.",
        "",
    ]

    for i, c in enumerate(candidates, 1):
        kind = c.get("kind", "unknown")
        tool = c.get("tool_pattern", c.get("pattern", "?"))
        domain = c.get("domain_hint", "?")
        confidence = c.get("confidence", 0.0)
        content = c.get("content", c.get("summary", ""))
        evidence = c.get("evidence", {})
        obs_count = len(evidence.get("observations", []))
        integrity = evidence.get("integrity", "unknown")

        # Truncate content for readability
        content_preview = (content[:180] + "…") if len(content) > 180 else content

        lines += [
            f"[{i}] {kind.upper()} — {tool}",
            f"    Domain hint:  {domain}",
            f"    Confidence:   {confidence:.2f}",
            f"    Evidence:     {obs_count} observation(s), integrity={integrity}",
            f"    Content:      {content_preview}",
            "",
        ]

    lines += [
        "To promote a candidate to memory:",
        "  cd /Volumes/1TB External/Projects/ken",
        "  python3 orchestrator/memory_ops.py  # then call promote_to_instinct(id)",
        "",
        "Or via mem CLI:",
        "  mem encode <domain> <type> \"<content>\"",
        "",
        f"{'='*70}",
        "",
    ]
    return "\n".join(lines)


def main():
    # Read hook payload from stdin
    try:
        raw = sys.stdin.read().strip()
        hook_json = json.loads(raw) if raw else {}
    except (json.JSONDecodeError, Exception):
        hook_json = {}

    # Opt-in gate (redundant with shell wrapper, but defense-in-depth)
    if os.environ.get("MEMORY_AUTO_OBSERVE_ENABLED") != "true":
        sys.exit(0)

    try:
        memory_ops = _safe_import_memory_ops()
    except Exception as e:
        print(f"[session-end] Failed to import memory_ops: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)

    # Resolve session_id
    session_id = _resolve_session_id(hook_json)
    if not session_id:
        try:
            session_id = memory_ops._current_session_id()
        except Exception:
            session_id = "unknown"

    # Extract candidates
    try:
        result = memory_ops.extract_candidates_from_observations(
            session_id, dry_run=True
        )
    except Exception as e:
        print(f"[session-end] extract_candidates_from_observations failed: {e}",
              file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)

    if not result.get("enabled"):
        # Observations not enabled — nothing to surface
        sys.exit(0)

    candidates = result.get("candidates", [])

    if not candidates:
        reason = result.get("reason", "no candidates found")
        print(
            f"\n[session-end] {session_id}: no candidates ({reason})",
            file=sys.stderr
        )
        sys.exit(0)

    # Write formatted report to stdout (wrapper → /tmp/session-end-candidates.txt)
    report = _format_candidates(candidates, session_id)
    sys.stdout.write(report)
    sys.stdout.flush()

    # Also log a short summary to stderr for /tmp/session-end-hook.err
    print(
        f"[session-end] {session_id}: {len(candidates)} candidate(s) surfaced "
        f"→ /tmp/session-end-candidates.txt",
        file=sys.stderr,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Absolute last resort — must not raise to shell
        print(f"[session-end] FATAL: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    sys.exit(0)
