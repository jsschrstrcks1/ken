#!/usr/bin/env python3
# OpenClaw Phase 2 smoke test. Returns {ok, node, git_sha} so the caller
# can verify hot-reload SHA pinning: call before and after a manifest
# change; SHA must flip on new calls but hold steady for in-flight calls.
#
# OpenClaw is expected to set OPENCLAW_MANIFEST_SHA when it spawns any
# tool. We fall back to `git rev-parse HEAD` of the cloned repo so the
# tool is also runnable by hand for debugging.

import json
import os
import socket
import subprocess
import sys


def manifest_sha() -> str:
    sha = os.environ.get("OPENCLAW_MANIFEST_SHA")
    if sha:
        return sha
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def main() -> int:
    print(json.dumps({
        "ok": True,
        "node": socket.gethostname(),
        "git_sha": manifest_sha(),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
