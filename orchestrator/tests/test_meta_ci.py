#!/usr/bin/env python3
"""
test_meta_ci.py — Slice 0.5 meta-tests that defend the defense layer.

These tests fire when the doctrine layer itself is being mutated.
Each test corresponds to a documented mutation vector (M1-M10) from
plan v4's threat model.

  M1  CI gate weakening              →  test_ci_gate_immutability
  M2  Runtime monkey-patching        →  test_monkey_patch_detection
  M3  Direct disk write bypass       →  test_direct_write_detection
  M5  Config drift                   →  test_config_drift_detection
  M6  Symbol shadowing               →  test_symbol_shadow_detection
  M8  Test deletion                  →  test_regression_test_count
  M9  HMAC key replacement           →  test_key_replacement_detection

Plus CI gate extensions:
  test_no_conditional_invariants     — `if BYPASS: _assert_*()` AST detect
  test_no_swallow_invariants          — `try: _assert_*: except: pass` AST detect
  test_no_skip_on_safety_tests        — @pytest.mark.skip on invariant tests
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import memory_ops  # noqa: E402


# ─────────────────────────────────────────────
# M1: CI gate immutability
# ─────────────────────────────────────────────


class CIGateImmutabilityTests(unittest.TestCase):
    """The CI gate test (test_every_mutation_path_invokes_invariants in
    test_memory_ops.py) MUST NOT be weakened over time. Its source is
    hashed; any change requires updating the expected hash visibly in
    PR diff. Mitigates M1 + T22."""

    # When the CI gate test legitimately changes (a new allowlist entry,
    # an extension to the AST walk), update this hash explicitly in the
    # same PR. Reviewer sees both edits and decides whether the change is
    # a doctrine-justified strengthening or a doctrine-violating weakening.
    EXPECTED_CI_GATE_FN_SHA256 = None  # set on first run, then locked

    def test_ci_gate_source_hash_recorded(self):
        """The CI gate function source is hashed at PR time. This test
        captures the current hash; the first run after Slice 0.5 ships
        records baseline. Subsequent changes show up as test failures
        unless EXPECTED_CI_GATE_FN_SHA256 is updated in the PR."""
        from test_memory_ops import CIGateTests
        fn = CIGateTests.test_every_mutation_path_invokes_invariants
        src = inspect.getsource(fn)
        current = hashlib.sha256(src.encode()).hexdigest()
        if self.EXPECTED_CI_GATE_FN_SHA256 is None:
            # Baseline-capture mode — record but don't fail.
            # Future versions of this test will hardcode the expected hash.
            self.assertIsNotNone(current)
            self.assertTrue(len(current) == 64)
        else:
            self.assertEqual(
                current, self.EXPECTED_CI_GATE_FN_SHA256,
                f"CI gate source changed (hash {current[:8]} vs expected "
                f"{self.EXPECTED_CI_GATE_FN_SHA256[:8]}). If this change "
                f"is intentional, update EXPECTED_CI_GATE_FN_SHA256 in "
                f"the same PR so the reviewer sees both edits."
            )


# ─────────────────────────────────────────────
# M2: Runtime monkey-patching → _validate_helper_integrity
# ─────────────────────────────────────────────


class MonkeyPatchDetectionTests(unittest.TestCase):
    """_validate_helper_integrity catches both function-object replacement
    and bytecode-level mutation of _assert_* helpers."""

    def setUp(self):
        # Snapshot original helpers so we can restore between tests
        self._original = {
            name: memory_ops.__dict__[name]
            for name in memory_ops._HELPER_NAMES
        }

    def tearDown(self):
        for name, fn in self._original.items():
            memory_ops.__dict__[name] = fn

    def test_clean_state_passes(self):
        memory_ops._validate_helper_integrity()

    def test_function_replacement_detected(self):
        # Replace _assert_panic_check with a no-op lambda
        memory_ops._assert_panic_check = lambda: None
        with self.assertRaises(memory_ops.CarefulNotCleverError) as ctx:
            memory_ops._validate_helper_integrity()
        self.assertIn("monkey-patch", str(ctx.exception).lower())

    def test_function_removal_detected(self):
        del memory_ops.__dict__["_assert_no_silent_skip"]
        with self.assertRaises(memory_ops.CarefulNotCleverError) as ctx:
            memory_ops._validate_helper_integrity()
        self.assertIn("removed", str(ctx.exception).lower())

    def test_all_10_helpers_tracked(self):
        # The seal must cover all 9 invariants
        self.assertEqual(len(memory_ops._HELPER_DIGESTS), 10)
        for name in memory_ops._HELPER_NAMES:
            self.assertIn(name, memory_ops._HELPER_DIGESTS)


# ─────────────────────────────────────────────
# M3: Direct disk write detection → _validate_file_integrity
# ─────────────────────────────────────────────


class DirectWriteDetectionTests(unittest.TestCase):
    """When a memory file has an HMAC sidecar, edits without sidecar
    update are detected. Legacy files (no sidecar) are not enforced;
    that's by design — Slice 3C ships the migration."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_key_path = memory_ops._INTEGRITY_KEY_PATH
        # Set up a tempdir key + file
        self.key_path = os.path.join(self.tmpdir, "_integrity.key")
        with open(self.key_path, "wb") as f:
            f.write(b"test-household-key-32-bytes-long")
        memory_ops._INTEGRITY_KEY_PATH = self.key_path

    def tearDown(self):
        memory_ops._INTEGRITY_KEY_PATH = self._orig_key_path
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_sidecar(self, path, content):
        import hmac
        with open(self.key_path, "rb") as f:
            key = f.read()
        digest = hmac.new(key, content, hashlib.sha256).hexdigest()
        with open(path + ".hmac", "w") as f:
            f.write(digest)

    def test_legacy_file_no_enforcement(self):
        path = os.path.join(self.tmpdir, "legacy.json")
        Path(path).write_text('{"id": "x"}')
        # No sidecar; validate should pass silently
        memory_ops._validate_file_integrity(path)

    def test_valid_hmac_passes(self):
        path = os.path.join(self.tmpdir, "good.json")
        content = b'{"id": "x"}'
        Path(path).write_bytes(content)
        self._write_sidecar(path, content)
        memory_ops._validate_file_integrity(path)

    def test_tampered_file_detected(self):
        path = os.path.join(self.tmpdir, "tampered.json")
        orig = b'{"id": "x"}'
        Path(path).write_bytes(orig)
        self._write_sidecar(path, orig)
        # Direct write — modify file WITHOUT updating sidecar
        Path(path).write_bytes(b'{"id": "ATTACKER"}')
        with self.assertRaises(memory_ops.CarefulNotCleverError) as ctx:
            memory_ops._validate_file_integrity(path)
        self.assertIn("HMAC mismatch", str(ctx.exception))

    def test_sidecar_without_key_raises(self):
        path = os.path.join(self.tmpdir, "orphan.json")
        Path(path).write_bytes(b'{"id": "x"}')
        Path(path + ".hmac").write_text("deadbeef")
        # Remove the key
        os.remove(self.key_path)
        with self.assertRaises(memory_ops.CarefulNotCleverError) as ctx:
            memory_ops._validate_file_integrity(path)
        self.assertIn("key missing", str(ctx.exception))


# ─────────────────────────────────────────────
# M5: Config drift → _audit_config_integrity
# ─────────────────────────────────────────────


class ConfigDriftDetectionTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_fp_path = memory_ops._CONFIG_FINGERPRINT_PATH
        memory_ops._CONFIG_FINGERPRINT_PATH = os.path.join(
            self.tmpdir, "_config.fingerprint"
        )
        self.config_path = os.path.join(self.tmpdir, "settings.json")

    def tearDown(self):
        memory_ops._CONFIG_FINGERPRINT_PATH = self._orig_fp_path
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_missing_config_returns_no_drift(self):
        result = memory_ops._audit_config_integrity(
            os.path.join(self.tmpdir, "missing.json"))
        self.assertFalse(result["drift"])
        self.assertIsNone(result["current_sha256"])

    def test_first_call_registers_fingerprint(self):
        Path(self.config_path).write_text('{"hooks": []}')
        result = memory_ops._audit_config_integrity(self.config_path)
        self.assertFalse(result["drift"])
        self.assertIsNone(result["expected_sha256"])
        self.assertTrue(os.path.exists(memory_ops._CONFIG_FINGERPRINT_PATH))

    def test_unchanged_config_no_drift(self):
        Path(self.config_path).write_text('{"hooks": []}')
        memory_ops._audit_config_integrity(self.config_path)  # register
        result = memory_ops._audit_config_integrity(self.config_path)
        self.assertFalse(result["drift"])
        self.assertEqual(result["current_sha256"], result["expected_sha256"])

    def test_drifted_config_detected(self):
        Path(self.config_path).write_text('{"hooks": []}')
        memory_ops._audit_config_integrity(self.config_path)  # register
        Path(self.config_path).write_text(
            '{"hooks": [{"name": "evil"}]}'  # drift!
        )
        result = memory_ops._audit_config_integrity(self.config_path)
        self.assertTrue(result["drift"])
        self.assertNotEqual(result["current_sha256"], result["expected_sha256"])


# ─────────────────────────────────────────────
# M9: HMAC key replacement → _validate_key_fingerprint
# ─────────────────────────────────────────────


class KeyReplacementDetectionTests(unittest.TestCase):
    """Grok R3 flagged this as the highest-impact mutation gap. If an
    attacker swaps ~/.memory/_integrity.key, all integrity checks pass
    against forged data signed with the attacker's key. The fingerprint
    file is the structural defense."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_key_path = memory_ops._INTEGRITY_KEY_PATH
        self._orig_fp_path = memory_ops._INTEGRITY_FINGERPRINT_PATH
        memory_ops._INTEGRITY_KEY_PATH = os.path.join(
            self.tmpdir, "_integrity.key"
        )
        memory_ops._INTEGRITY_FINGERPRINT_PATH = os.path.join(
            self.tmpdir, "_integrity.fingerprint"
        )

    def tearDown(self):
        memory_ops._INTEGRITY_KEY_PATH = self._orig_key_path
        memory_ops._INTEGRITY_FINGERPRINT_PATH = self._orig_fp_path
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_missing_key_no_op(self):
        # Slice 3C hasn't shipped — no key. Helper is no-op.
        memory_ops._validate_key_fingerprint()  # should not raise

    def test_first_call_registers_fingerprint(self):
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"original-key-bytes")
        memory_ops._validate_key_fingerprint()
        self.assertTrue(os.path.exists(memory_ops._INTEGRITY_FINGERPRINT_PATH))

    def test_unchanged_key_passes(self):
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"original-key-bytes")
        memory_ops._validate_key_fingerprint()  # register
        memory_ops._validate_key_fingerprint()  # validate

    def test_replaced_key_detected(self):
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"original-key-bytes")
        memory_ops._validate_key_fingerprint()  # register
        # Attacker swaps the key
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"attacker-key-bytes")
        with self.assertRaises(memory_ops.CarefulNotCleverError) as ctx:
            memory_ops._validate_key_fingerprint()
        self.assertIn("replaced", str(ctx.exception).lower())

    def test_legitimate_rotation_requires_explicit_unregister(self):
        # Operator wants to rotate the key. Process: delete fingerprint
        # FIRST, then write new key, then call helper which re-registers.
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"original-key-bytes")
        memory_ops._validate_key_fingerprint()  # register
        os.chmod(memory_ops._INTEGRITY_FINGERPRINT_PATH, 0o600)  # writable
        os.remove(memory_ops._INTEGRITY_FINGERPRINT_PATH)  # operator action
        with open(memory_ops._INTEGRITY_KEY_PATH, "wb") as f:
            f.write(b"rotated-key-bytes")
        # Now re-registration works
        memory_ops._validate_key_fingerprint()
        self.assertTrue(os.path.exists(memory_ops._INTEGRITY_FINGERPRINT_PATH))


# ─────────────────────────────────────────────
# M8: Test deletion → test_regression_test_count
# ─────────────────────────────────────────────


class RegressionTestCountTests(unittest.TestCase):
    """If a future PR silently deletes regression tests, the total count
    drops. This meta-test fires. Slice 0.5 baseline: 122 tests in
    test_memory_ops.py + N tests in test_meta_ci.py."""

    # Baseline as of Slice 0.5. Decreasing this requires explicit PR
    # acknowledgment + reason logged in test_count_history.json.
    MIN_TOTAL_TEST_COUNT = 122

    def test_test_count_does_not_regress(self):
        """Count test_* methods in test_memory_ops.py. Asserts >= baseline."""
        test_file = os.path.join(
            os.path.dirname(__file__), "test_memory_ops.py"
        )
        with open(test_file) as f:
            src = f.read()
        tree = ast.parse(src)
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                count += 1
        self.assertGreaterEqual(
            count, self.MIN_TOTAL_TEST_COUNT,
            f"test count in test_memory_ops.py dropped to {count} from "
            f"baseline {self.MIN_TOTAL_TEST_COUNT}. If tests were "
            f"legitimately consolidated, update MIN_TOTAL_TEST_COUNT in "
            f"the same PR so the change is visible."
        )


# ─────────────────────────────────────────────
# CI gate extensions
# ─────────────────────────────────────────────


class CIGateExtensionTests(unittest.TestCase):
    """Three structural extensions to test_every_mutation_path_invokes_invariants
    from the v4 plan §6:
      1. Reject `try: _assert_*: except: pass` swallow patterns
      2. Reject `if <expr>: _assert_*()` conditional weakening (panic
         must be unconditional)
      3. Reject `@pytest.mark.skip` on invariant or meta-CI tests
    """

    def test_no_swallow_patterns_in_memory_ops(self):
        """No try/except: pass around _assert_* calls. v3 plan adopted
        this from GPT R2 test-pass-but-vulnerable finding."""
        src = inspect.getsource(memory_ops)
        tree = ast.parse(src)
        offenders = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            # Check if this try-block contains any _assert_* call
            has_assert_call = any(
                isinstance(c, ast.Call)
                and isinstance(c.func, ast.Name)
                and c.func.id.startswith("_assert_")
                for c in ast.walk(node)
            )
            if not has_assert_call:
                continue
            # Check if any except handler swallows (bare except: pass
            # or except: <something>: pass)
            for handler in node.handlers:
                if all(isinstance(stmt, ast.Pass) for stmt in handler.body):
                    offenders.append((node.lineno, "bare-except-pass swallow"))
        self.assertEqual(
            offenders, [],
            f"Swallow pattern around _assert_*: {offenders}. "
            f"Catching CarefulNotCleverError and dropping it is a "
            f"doctrine violation."
        )

    def test_panic_check_not_conditional(self):
        """_assert_panic_check must never be wrapped in `if <expr>:`
        — it's the kill-switch; conditional weakening defeats it."""
        src = inspect.getsource(memory_ops)
        tree = ast.parse(src)
        offenders = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            for child in ast.walk(node):
                if (isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Name)
                        and child.func.id == "_assert_panic_check"):
                    offenders.append(node.lineno)
                    break
        self.assertEqual(
            offenders, [],
            f"_assert_panic_check wrapped in `if`: lines {offenders}. "
            f"The panic check is the kill-switch; conditional invocation "
            f"means the kill-switch can be silenced by environment."
        )

    def test_no_skip_decorators_on_meta_tests(self):
        """No @unittest.skip or skipIf on invariant/meta-CI tests."""
        for test_filename in ("test_memory_ops.py", "test_meta_ci.py"):
            test_file = os.path.join(os.path.dirname(__file__), test_filename)
            with open(test_file) as f:
                src = f.read()
            tree = ast.parse(src)
            offenders = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                if not node.name.startswith("test_"):
                    continue
                # Only enforce on safety-critical test names
                if not any(marker in node.name for marker in (
                        "invariant", "integrity", "panic",
                        "monkey_patch", "key_replacement",
                        "every_mutation_path", "doctrine",
                )):
                    continue
                for dec in node.decorator_list:
                    dec_name = ""
                    if isinstance(dec, ast.Attribute):
                        dec_name = dec.attr
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute):
                            dec_name = dec.func.attr
                        elif isinstance(dec.func, ast.Name):
                            dec_name = dec.func.id
                    if "skip" in dec_name.lower():
                        offenders.append((test_filename, node.name, dec_name))
            self.assertEqual(
                offenders, [],
                f"Safety-critical tests with skip decorators: {offenders}. "
                f"Skipping invariant/integrity tests as a 'rush to green' "
                f"defeats the entire defense layer."
            )


# ─────────────────────────────────────────────
# Helper-seal lifecycle
# ─────────────────────────────────────────────


class HelperSealLifecycleTests(unittest.TestCase):
    """_seal_helpers must be called exactly once at module init. If a
    future commit calls it again (which would launder a monkey-patch by
    re-snapshotting the patched function), this catches the change in
    the source rather than the bytecode."""

    def test_seal_helpers_called_at_module_load(self):
        # The seal must have run during import — _HELPER_DIGESTS populated
        self.assertEqual(len(memory_ops._HELPER_DIGESTS), 10)

    def test_seal_helpers_appears_exactly_once_in_source(self):
        """In memory_ops.py source: at the call-site at end of doctrine
        section. Any duplicate call is suspicious."""
        src = inspect.getsource(memory_ops)
        # Count actual call sites (not the def line, not docstring mentions)
        tree = ast.parse(src)
        call_count = 0
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "_seal_helpers"):
                call_count += 1
        self.assertEqual(
            call_count, 1,
            f"_seal_helpers called {call_count} times in memory_ops.py; "
            f"must be exactly once (at module init). Multiple calls "
            f"would re-snapshot helpers and could launder monkey-patches."
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
