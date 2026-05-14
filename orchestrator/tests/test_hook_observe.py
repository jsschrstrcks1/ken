"""Slice 6 — PostToolUse hook + Python writer tests.

The hook writer (``hook_observe.py``) is invoked detached from a bash
wrapper, with the Claude Code hook JSON on stdin. Tests exercise it
both by direct module import (for unit coverage) and via real
subprocess invocation (for fail-closed contract verification).

≥12 tests per the v6 plan ship-gate.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import hook_observe  # noqa: E402
import memory_ops  # noqa: E402


HOOK_PY = str(ROOT / "hook_observe.py")
HOOK_SH = str(ROOT.parent / ".claude" / "hooks" / "observe-tool-use.sh")


class _HookBase(unittest.TestCase):
    """Shared setup: tempdir MEMORY_ROOT + isolated integrity key/fp."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = {
            "MEMORY_ROOT": memory_ops.MEMORY_ROOT,
            "ARCHIVE_DIR": memory_ops.ARCHIVE_DIR,
            "_INTEGRITY_KEY_PATH": memory_ops._INTEGRITY_KEY_PATH,
            "_INTEGRITY_FP": memory_ops._INTEGRITY_FINGERPRINT_PATH,
        }
        memory_ops.MEMORY_ROOT = self.tmp
        memory_ops.ARCHIVE_DIR = os.path.join(self.tmp, "_archive")
        memory_ops._INTEGRITY_KEY_PATH = os.path.join(
            self.tmp, "_integrity.key")
        memory_ops._INTEGRITY_FINGERPRINT_PATH = os.path.join(
            self.tmp, "_integrity.fingerprint")
        memory_ops._ensure_dirs()
        memory_ops._rate_buckets.clear()

        os.environ["MEMORY_OBSERVATIONS_ENABLED"] = "true"
        os.environ["MEMORY_AUTO_OBSERVE_ENABLED"] = "true"
        # Pop session-id env to force payload-supplied session_id path
        self._popped = {}
        for k in ("MEMORY_SESSION_ID", "CLAUDE_SESSION_ID",
                  "MEMORY_LEARNING_PANIC_DISABLE_ALL"):
            self._popped[k] = os.environ.pop(k, None)

    def tearDown(self):
        memory_ops.MEMORY_ROOT = self._orig["MEMORY_ROOT"]
        memory_ops.ARCHIVE_DIR = self._orig["ARCHIVE_DIR"]
        memory_ops._INTEGRITY_KEY_PATH = self._orig["_INTEGRITY_KEY_PATH"]
        memory_ops._INTEGRITY_FINGERPRINT_PATH = self._orig["_INTEGRITY_FP"]
        memory_ops._rate_buckets.clear()
        os.environ.pop("MEMORY_OBSERVATIONS_ENABLED", None)
        os.environ.pop("MEMORY_AUTO_OBSERVE_ENABLED", None)
        for k, v in self._popped.items():
            if v is not None:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _read_log(self, session):
        path = os.path.join(self.tmp, "_observations", f"{session}.jsonl")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [json.loads(ln) for ln in f if ln.strip()]


class WriterUnitTests(_HookBase):
    """In-process exercise of hook_observe.main() — fast, deterministic."""

    def _run_main_with_payload(self, payload):
        from io import StringIO
        old_stdin = sys.stdin
        sys.stdin = StringIO(json.dumps(payload))
        try:
            hook_observe.main()
        finally:
            sys.stdin = old_stdin

    def test_writes_observation_on_valid_payload(self):
        self._run_main_with_payload({
            "session_id": "sess-hook-1",
            "tool_name": "Bash",
            "tool_input": {"command": "echo ok"},
            "tool_response": {"stdout": "ok\n", "exit_code": 0},
        })
        records = self._read_log("sess-hook-1")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["tool"], "Bash")
        self.assertEqual(records[0]["result_class"], "success")

    def test_disabled_flag_is_no_op(self):
        os.environ["MEMORY_AUTO_OBSERVE_ENABLED"] = "false"
        self._run_main_with_payload({
            "session_id": "sess-disabled",
            "tool_name": "Bash",
            "tool_input": {"command": "echo"},
            "tool_response": "",
        })
        self.assertEqual(self._read_log("sess-disabled"), [])

    def test_classify_response_error_dict(self):
        self.assertEqual(
            hook_observe._classify_response(
                {"error": "boom", "is_error": True}),
            "error",
        )

    def test_classify_response_timeout(self):
        self.assertEqual(
            hook_observe._classify_response({"timeout": True}),
            "timeout",
        )

    def test_classify_response_truncated(self):
        self.assertEqual(
            hook_observe._classify_response({"truncated": True}),
            "truncated",
        )

    def test_classify_response_string_with_error_prefix(self):
        self.assertEqual(
            hook_observe._classify_response("Error: file not found"),
            "error",
        )

    def test_classify_response_string_with_traceback(self):
        self.assertEqual(
            hook_observe._classify_response(
                "Some output\nTraceback (most recent call last):"),
            "error",
        )

    def test_classify_response_string_success_default(self):
        self.assertEqual(
            hook_observe._classify_response("hello world"),
            "success",
        )

    def test_sanitize_tool_strips_special_chars(self):
        self.assertEqual(
            hook_observe._sanitize_tool("Bash; rm -rf /"),
            "Bash__rm_-rf",  # spaces/semicolons → _, dashes kept,
                              # trailing _ stripped, leading kept
        )

    def test_sanitize_tool_truncates_to_64(self):
        long = "a" * 200
        self.assertEqual(len(hook_observe._sanitize_tool(long)), 64)

    def test_sanitize_tool_empty_input(self):
        self.assertEqual(hook_observe._sanitize_tool(""), "")
        self.assertEqual(hook_observe._sanitize_tool(None), "")

    def test_raw_secret_not_on_disk(self):
        secret = "sk-ant-supersecret-12345"
        self._run_main_with_payload({
            "session_id": "sess-secret",
            "tool_name": "Bash",
            "tool_input": {"env": {"API_KEY": secret}},
            "tool_response": {},
        })
        path = os.path.join(self.tmp, "_observations",
                            "sess-secret.jsonl")
        with open(path) as f:
            content = f.read()
        self.assertNotIn(secret, content)
        self.assertNotIn("sk-ant", content)


class WriterFailClosedTests(_HookBase):
    """The contract: ANY error inside the writer must result in exit 0
    and a stderr line — never a non-zero exit that the hook chain
    could surface back to Claude Code as a tool-call block."""

    def _invoke_writer(self, payload, env_overrides=None):
        env = {**os.environ}
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            [sys.executable, HOOK_PY],
            input=payload if isinstance(payload, str)
                   else json.dumps(payload),
            text=True, env=env, capture_output=True, timeout=10,
        )

    def test_garbage_stdin_exits_zero(self):
        result = self._invoke_writer("this is not json at all")
        self.assertEqual(result.returncode, 0,
                         f"stderr={result.stderr!r}")
        self.assertIn("hook_observe:", result.stderr)

    def test_top_level_array_exits_zero(self):
        result = self._invoke_writer(json.dumps([1, 2, 3]))
        self.assertEqual(result.returncode, 0)
        self.assertIn("hook_observe:", result.stderr)

    def test_missing_session_id_exits_zero(self):
        result = self._invoke_writer({
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "tool_response": "",
        })
        self.assertEqual(result.returncode, 0)
        self.assertIn("session_id", result.stderr)

    def test_missing_tool_name_exits_zero(self):
        result = self._invoke_writer({
            "session_id": "sess-x",
            "tool_input": {},
            "tool_response": "",
        })
        self.assertEqual(result.returncode, 0)
        # Empty/missing tool_name → sanitized to empty → raised
        self.assertIn("tool_name", result.stderr)

    def test_tool_name_with_only_special_chars_exits_zero(self):
        # ';!@#' sanitizes to '____' which strips to '' — empty
        result = self._invoke_writer({
            "session_id": "sess-special",
            "tool_name": ";!@#",
            "tool_input": {},
            "tool_response": "",
        })
        self.assertEqual(result.returncode, 0)

    def test_panic_flag_set_exits_zero(self):
        result = self._invoke_writer(
            {
                "session_id": "sess-panic",
                "tool_name": "Bash",
                "tool_input": {"x": 1},
                "tool_response": "ok",
            },
            env_overrides={
                "MEMORY_LEARNING_PANIC_DISABLE_ALL": "true",
                "MEMORY_OBSERVATIONS_ENABLED": "true",
                "MEMORY_AUTO_OBSERVE_ENABLED": "true",
                "MEMORY_ROOT": self.tmp,
            },
        )
        # Panic raises CarefulNotCleverError inside record_observation;
        # writer's try/except catches and exits 0.
        self.assertEqual(result.returncode, 0)
        self.assertIn("hook_observe:", result.stderr)

    def test_disabled_flag_silent_exit_zero(self):
        result = self._invoke_writer(
            {"session_id": "sess-x", "tool_name": "Bash",
             "tool_input": {}, "tool_response": ""},
            env_overrides={"MEMORY_AUTO_OBSERVE_ENABLED": "false"},
        )
        self.assertEqual(result.returncode, 0)
        # No error message on the disabled path
        self.assertEqual(result.stderr, "")


class BashWrapperTests(_HookBase):
    """End-to-end: the bash hook wrapper spawns the writer detached."""

    def _invoke_hook(self, payload):
        env = {
            **os.environ,
            "MEMORY_ROOT": self.tmp,
            "CLAUDE_PROJECT_DIR": str(ROOT.parent),
        }
        return subprocess.run(
            ["bash", HOOK_SH],
            input=json.dumps(payload),
            text=True, env=env, capture_output=True, timeout=5,
        )

    def test_wrapper_always_exits_zero(self):
        result = self._invoke_hook({
            "session_id": "sess-wrapper",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hi"},
            "tool_response": {"stdout": "hi\n"},
        })
        self.assertEqual(result.returncode, 0,
                         f"stderr={result.stderr!r}")

    def test_wrapper_no_op_when_flag_unset(self):
        env = {
            **os.environ,
            "MEMORY_ROOT": self.tmp,
            "CLAUDE_PROJECT_DIR": str(ROOT.parent),
        }
        env.pop("MEMORY_AUTO_OBSERVE_ENABLED", None)
        result = subprocess.run(
            ["bash", HOOK_SH],
            input=json.dumps({
                "session_id": "sess-off",
                "tool_name": "Bash",
                "tool_input": {},
                "tool_response": "",
            }),
            text=True, env=env, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        # Writer should not have been invoked → no log file
        self.assertFalse(os.path.exists(
            os.path.join(self.tmp, "_observations",
                         "sess-off.jsonl")))

    def test_wrapper_with_garbage_stdin_exits_zero(self):
        env = {
            **os.environ,
            "MEMORY_ROOT": self.tmp,
            "CLAUDE_PROJECT_DIR": str(ROOT.parent),
        }
        result = subprocess.run(
            ["bash", HOOK_SH],
            input="not json {{{",
            text=True, env=env, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
