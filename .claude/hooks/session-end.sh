#!/bin/bash
# Slice 7 SessionEnd hook — auto-surface memory candidates at session close.
#
# Reads the SessionEnd hook JSON from stdin, spawns a detached Python
# extractor (hook_session_end.py), and exits 0 immediately.
#
# Fail-closed contract: this script ALWAYS exits 0. Any error from
# the extractor goes to /tmp/session-end-hook.err for operator review.
# A broken extraction pipeline must never block session teardown.
#
# Opt-in: extractor no-ops unless MEMORY_AUTO_OBSERVE_ENABLED=true.
# Registration in .claude/settings.json is the operator's explicit choice.
# See orchestrator/CONTINUOUS_LEARNING_PLAN.md §3 Slice 7.

set +e  # never propagate errors

INPUT=$(cat 2>/dev/null)

# Quick gate before paying the fork cost
[ "${MEMORY_AUTO_OBSERVE_ENABLED:-}" = "true" ] || exit 0

# Detached extractor — stdout goes to /tmp/session-end-candidates.txt
# so the operator can review after the session. stderr to error log.
KEN_DIR="${CLAUDE_PROJECT_DIR:-/Volumes/1TB External/Projects/ken}"
(
    echo "$INPUT" | python3 "$KEN_DIR/orchestrator/hook_session_end.py" \
        </dev/stdin >>/tmp/session-end-candidates.txt 2>>/tmp/session-end-hook.err &
    disown
) 2>/dev/null

exit 0
