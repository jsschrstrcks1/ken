#!/usr/bin/env python3
"""Slice 6 PostToolUse hook writer.

Invoked DETACHED from ``.claude/hooks/observe-tool-use.sh`` with the
Claude Code hook JSON on stdin. Imports memory_ops, hashes args,
classifies the tool response, calls record_observation.

Fail-closed contract: ANY error here is swallowed and printed to
stderr (the wrapper redirects stderr to /tmp/observe-hook.err). The
script always exits 0 so the hook chain never blocks the tool call.

Critical-path discipline: because this script is run detached, its
execution time does NOT affect user-visible tool latency. Slow
imports (memory_ops loads ~2.7K lines + does helper sealing) are
paid here, never in the hook's synchronous path. The hook wrapper
is the only thing on the critical path.

Opt-in: writes only when MEMORY_AUTO_OBSERVE_ENABLED=true is set
(see orchestrator/CONTINUOUS_LEARNING_PLAN.md §3 Slice 6). Default
off; explicit registration in .claude/settings.json is the
operator's choice.
"""
import json
import os
import re
import sys

# Tool names are sanitized to this character set to match memory_ops'
# _OBSERVATION_TOOL_PATTERN. Truncated to 64 chars per the same
# invariant. Anything that can't be sanitized to >=1 char is dropped.
_TOOL_SANITIZE_RE = re.compile(r"[^A-Za-z0-9_.-]")


def _sanitize_tool(name):
    if not isinstance(name, str):
        return ""
    sanitized = _TOOL_SANITIZE_RE.sub("_", name)[:64]
    return sanitized.strip("_") or ""


def _classify_response(response):
    """Map Claude Code's tool_response shape into the 4-value
    result_class enum that record_observation accepts.

    Dict response checks structured error/timeout/truncated flags
    (Claude Code's actual schema). String response checks for
    error-leading prefixes as a heuristic. Everything else is
    treated as success — under-reporting failures is safer than
    over-reporting success because operator review of candidates
    is the next layer of defense."""
    if isinstance(response, dict):
        if response.get("error") or response.get("is_error"):
            return "error"
        if response.get("timeout"):
            return "timeout"
        if response.get("truncated"):
            return "truncated"
        return "success"
    if isinstance(response, str):
        head = response[:200].lower()
        if head.startswith("error") or "traceback" in head:
            return "error"
        return "success"
    return "success"


def main():
    if os.environ.get(
            "MEMORY_AUTO_OBSERVE_ENABLED", "").lower() != "true":
        return

    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError(f"hook payload must be a dict, got {type(payload).__name__}")

    tool_name = _sanitize_tool(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input", {})
    tool_response = payload.get("tool_response")
    # Claude Code injects session_id in every hook event; we also
    # accept the env var as a fallback for testing.
    session_id = (payload.get("session_id")
                  or os.environ.get("MEMORY_SESSION_ID"))

    if not tool_name:
        raise ValueError(
            f"hook payload tool_name {payload.get('tool_name')!r} "
            f"sanitized to empty — skipping"
        )
    if not session_id:
        raise ValueError("hook payload missing session_id and "
                         "MEMORY_SESSION_ID is unset")

    # Heavy import deferred until after argument validation; if the
    # payload is malformed we exit before paying the import cost.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import memory_ops

    result_class = _classify_response(tool_response)
    args_hash = memory_ops._compute_args_hash(tool_input)

    memory_ops.record_observation(
        tool_name, args_hash, result_class, session_id
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Fail-closed: do not propagate exit code to the hook chain.
        sys.stderr.write(
            f"hook_observe: {type(e).__name__}: {e}\n"
        )
    sys.exit(0)
