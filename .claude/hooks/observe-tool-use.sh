#!/bin/bash
# Slice 6 PostToolUse hook — fire-and-forget observation recorder.
#
# Reads the hook JSON from stdin, spawns a detached Python writer
# (hook_observe.py), and exits 0 immediately. The synchronous overhead
# is bash startup + cat + fork, typically <20ms. The actual
# record_observation work happens off the critical path.
#
# Fail-closed contract: this script ALWAYS exits 0. Any error from
# the writer goes to /tmp/observe-hook.err for operator review.
# A broken observation pipeline must never block a tool call.
#
# Opt-in: writer no-ops unless MEMORY_AUTO_OBSERVE_ENABLED=true is
# set in the operator's shell. Registration in .claude/settings.json
# is also operator's explicit choice — see
# orchestrator/CONTINUOUS_LEARNING_PLAN.md §3 Slice 6.

set +e  # never propagate errors

INPUT=$(cat 2>/dev/null)

# Quick gate before paying the fork cost
[ "${MEMORY_AUTO_OBSERVE_ENABLED:-}" = "true" ] || exit 0

# Detached writer — stdout suppressed, stderr appended to /tmp log
# for post-hoc operator review. `disown` removes the job from the
# shell's table so the parent exit doesn't signal the child.
KEN_DIR="${CLAUDE_PROJECT_DIR:-/home/user/ken}"
(
    echo "$INPUT" | python3 "$KEN_DIR/orchestrator/hook_observe.py" \
        </dev/stdin >/dev/null 2>>/tmp/observe-hook.err &
    disown
) 2>/dev/null

exit 0
