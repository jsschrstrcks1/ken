#!/usr/bin/env python3
"""Tests for orchestrator/checkpoint.py.

Run: python3 orchestrator/tests/test_checkpoint.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import checkpoint  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=repo, check=True, capture_output=True,
    )


def _new_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "seed.txt").write_text("seed\n")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-qm", "init")
    return repo


class CheckpointTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = _new_repo(Path(self.tmp.name))
        self._old_cwd = os.getcwd()
        os.chdir(self.repo)

    def tearDown(self):
        os.chdir(self._old_cwd)
        self.tmp.cleanup()

    def test_repo_root_finds_git_dir(self):
        sub = self.repo / "a" / "b"
        sub.mkdir(parents=True)
        self.assertEqual(checkpoint.repo_root(sub), self.repo)

    def test_at_risk_files_lists_untracked_modified_staged(self):
        (self.repo / "new.txt").write_text("x")            # untracked
        (self.repo / "seed.txt").write_text("seed\nedit")  # modified
        (self.repo / "staged.txt").write_text("s")
        _git(self.repo, "add", "staged.txt")               # staged
        risk = set(checkpoint.at_risk_files(self.repo))
        self.assertEqual(risk, {"new.txt", "seed.txt", "staged.txt"})

    def test_at_risk_skips_pulse_state_dir(self):
        # The pulse itself must never appear in at_risk.
        checkpoint.beat("s1", "noise", root=self.repo)
        risk = checkpoint.at_risk_files(self.repo)
        self.assertNotIn(".claude/state/session-pulse.json", risk)

    def test_beat_increments_count_and_preserves_started_at(self):
        p1 = checkpoint.beat("sX", "first", root=self.repo)
        p2 = checkpoint.beat("sX", "second", root=self.repo)
        self.assertEqual(p1["beat_count"], 1)
        self.assertEqual(p2["beat_count"], 2)
        self.assertEqual(p1["started_at"], p2["started_at"])
        self.assertEqual(p2["status"], "active")

    def test_new_session_resets(self):
        checkpoint.beat("s1", "first", root=self.repo)
        p2 = checkpoint.beat("s2", "fresh", root=self.repo)
        self.assertEqual(p2["beat_count"], 1)

    def test_complete_marks_status_and_inhibits_stale(self):
        checkpoint.beat("sC", "work", root=self.repo)
        done = checkpoint.complete("sC", root=self.repo)
        self.assertEqual(done["status"], "complete")
        self.assertIn("completed_at", done)
        # Even with threshold 0 (everything is "old"), complete pulses
        # must not be flagged stale.
        self.assertFalse(checkpoint.is_stale(done, stale_minutes=0))
        self.assertIsNone(checkpoint.scan(self.repo, stale_minutes=0))

    def test_complete_returns_none_when_no_pulse(self):
        self.assertIsNone(checkpoint.complete("anything", root=self.repo))

    def test_complete_session_id_mismatch_is_no_op(self):
        checkpoint.beat("real", "work", root=self.repo)
        self.assertIsNone(checkpoint.complete("imposter", root=self.repo))
        self.assertEqual(checkpoint.read_pulse(self.repo)["status"], "active")

    def test_scan_archives_stale_pulse_and_returns_report(self):
        (self.repo / "wip.py").write_text("pass\n")
        checkpoint.beat("sStale", "midway", context="ctx", root=self.repo)
        report = checkpoint.scan(self.repo, stale_minutes=0)
        self.assertIsNotNone(report)
        self.assertTrue(report["pulse"]["session_id"] == "sStale")
        self.assertIn("wip.py", report["pulse"]["at_risk"])
        self.assertFalse(report["handoff_present"])
        archive = Path(report["archive_path"])
        self.assertTrue(archive.exists())
        self.assertEqual(json.loads(archive.read_text())["pulse"]["session_id"], "sStale")

    def test_scan_notes_handoff_when_present(self):
        (self.repo / "HANDOFF.md").write_text("# wip")
        checkpoint.beat("sH", "midway", root=self.repo)
        report = checkpoint.scan(self.repo, stale_minutes=0)
        self.assertTrue(report["handoff_present"])
        self.assertIn("HANDOFF.md", report["recovery_summary"])

    def test_scan_returns_none_when_fresh(self):
        checkpoint.beat("sFresh", "now", root=self.repo)
        self.assertIsNone(checkpoint.scan(self.repo, stale_minutes=30))

    def test_minutes_since_handles_aware_and_naive(self):
        aware = datetime.now(timezone.utc).isoformat()
        naive = datetime.now().isoformat()
        for ts in (aware, naive):
            elapsed = checkpoint.minutes_since(ts)
            self.assertIsNotNone(elapsed)
            self.assertLess(abs(elapsed), 1)

    def test_minutes_since_returns_none_on_garbage(self):
        self.assertIsNone(checkpoint.minutes_since(""))
        self.assertIsNone(checkpoint.minutes_since("not-a-date"))

    def test_is_stale_handles_missing_pulse(self):
        self.assertFalse(checkpoint.is_stale(None))
        self.assertFalse(checkpoint.is_stale({}))

    def test_is_stale_threshold_boundary(self):
        old = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
        pulse = {"session_id": "x", "last_beat": old, "status": "active"}
        self.assertTrue(checkpoint.is_stale(pulse, stale_minutes=30))
        self.assertFalse(checkpoint.is_stale(pulse, stale_minutes=60))

    def test_atomic_write_no_tmp_left_behind(self):
        checkpoint.beat("sA", "x", root=self.repo)
        leftovers = list((self.repo / ".claude/state").glob("*.tmp"))
        self.assertEqual(leftovers, [])


class CLITests(unittest.TestCase):
    """Exercise the CLI surface end-to-end via subprocess."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = _new_repo(Path(self.tmp.name))
        self.script = ROOT / "checkpoint.py"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=self.repo, capture_output=True, text=True,
        )

    def test_full_lifecycle(self):
        sid = self._run("new-id").stdout.strip()
        self.assertTrue(sid.startswith("sess-"))

        beat = self._run("beat", "--session", sid, "--action", "edit", "--json")
        self.assertEqual(beat.returncode, 0)
        self.assertEqual(json.loads(beat.stdout)["beat_count"], 1)

        scan = self._run("scan", "--json")
        self.assertEqual(json.loads(scan.stdout), {"ok": True, "stale": False})

        forced = self._run("scan", "--stale-minutes", "0", "--json")
        self.assertIn("recovery_summary", json.loads(forced.stdout))

        done = self._run("complete", "--session", sid, "--json")
        self.assertEqual(json.loads(done.stdout)["status"], "complete")

        after = self._run("scan", "--stale-minutes", "0", "--json")
        self.assertEqual(json.loads(after.stdout), {"ok": True, "stale": False})


if __name__ == "__main__":
    unittest.main(verbosity=2)
