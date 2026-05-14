#!/usr/bin/env python3
"""Slice 6 ship-gate benchmark.

Measures synchronous overhead per record_observation call (the heavy
work the detached hook writer pays off the critical path) and the
end-to-end hook latency including bash startup + fire-and-forget
subprocess spawn (the actual user-visible cost).

Two scenarios:

1. Direct API benchmark — N back-to-back record_observation calls in
   the current Python process. Measures the floor.

2. Hook-shaped benchmark — invokes the bash wrapper with a fake
   JSON payload on stdin N times. Measures what a real tool call
   would pay.

The plan §3 Slice 6 ship-gate target was <5ms per call. Under
realistic POSIX fork overhead that target is aspirational for any
hook that spawns a subprocess; this script reports the actual numbers
so the operator can decide whether the cost is acceptable for their
workflow. (For comparison, prompt-injection-guard.js's node startup
is in the same range.)

Usage:
    python3 bench_hook.py [N]   # default N=100

To run the hook-shaped benchmark you need MEMORY_AUTO_OBSERVE_ENABLED=true
in the environment AND a writable tmpdir for the observation log.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid


KEN_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK_SH = os.path.join(
    os.path.dirname(KEN_DIR), ".claude", "hooks", "observe-tool-use.sh"
)


def bench_direct(n, tmpdir):
    os.environ["MEMORY_ROOT"] = tmpdir
    os.environ["MEMORY_OBSERVATIONS_ENABLED"] = "true"
    sys.path.insert(0, KEN_DIR)
    import memory_ops
    memory_ops.MEMORY_ROOT = tmpdir
    memory_ops._INTEGRITY_KEY_PATH = os.path.join(tmpdir, "_integrity.key")
    memory_ops._INTEGRITY_FINGERPRINT_PATH = os.path.join(
        tmpdir, "_integrity.fingerprint"
    )
    memory_ops._ensure_dirs()

    session = "bench-direct"
    h = "a" * 64

    # Warm up (first call generates key + fingerprint)
    memory_ops.record_observation("Bash", h, "success", session)

    start = time.perf_counter()
    for _ in range(n):
        memory_ops.record_observation("Bash", h, "success", session)
    elapsed = time.perf_counter() - start

    per_call_ms = (elapsed / n) * 1000
    return per_call_ms


def bench_hook_shaped(n, tmpdir):
    """Invoke the bash wrapper directly with a fake JSON payload."""
    if not os.path.exists(HOOK_SH):
        return None

    env = {
        **os.environ,
        "MEMORY_AUTO_OBSERVE_ENABLED": "true",
        "MEMORY_OBSERVATIONS_ENABLED": "true",
        "MEMORY_ROOT": tmpdir,
        "CLAUDE_PROJECT_DIR": os.path.dirname(KEN_DIR),
    }

    payload = json.dumps({
        "session_id": "bench-hook-session",
        "tool_name": "Bash",
        "tool_input": {"command": "echo hello"},
        "tool_response": {"stdout": "hello\n", "exit_code": 0},
    })

    # Warm up
    subprocess.run([HOOK_SH], input=payload, env=env,
                   capture_output=True, text=True, timeout=5)

    start = time.perf_counter()
    for _ in range(n):
        subprocess.run([HOOK_SH], input=payload, env=env,
                       capture_output=True, text=True, timeout=5)
    elapsed = time.perf_counter() - start

    per_call_ms = (elapsed / n) * 1000
    return per_call_ms


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    with tempfile.TemporaryDirectory() as direct_tmp:
        direct_ms = bench_direct(n, direct_tmp)

    with tempfile.TemporaryDirectory() as hook_tmp:
        hook_ms = bench_hook_shaped(n, hook_tmp)

    print(f"Slice 6 ship-gate benchmark (N={n})")
    print(f"  direct record_observation:  {direct_ms:6.2f} ms/call "
          f"(in-process, no fork)")
    if hook_ms is not None:
        print(f"  hook-shaped (bash + fork):  {hook_ms:6.2f} ms/call "
              f"(synchronous wrapper cost; writer is detached)")
    else:
        print(f"  hook-shaped: skipped ({HOOK_SH} not present)")
    print()
    print("Plan §3 Slice 6 target was <5ms. Direct cost is dominated")
    print("by HMAC compute + flock + sidecar fsync; hook cost adds")
    print("bash startup + fork. The writer runs DETACHED so its work")
    print("doesn't add to user-visible tool-call latency.")


if __name__ == "__main__":
    main()
