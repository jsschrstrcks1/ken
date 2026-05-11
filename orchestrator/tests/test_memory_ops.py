#!/usr/bin/env python3
"""Tests for orchestrator/memory_ops.py.

Run:    python3 orchestrator/tests/test_memory_ops.py
Or:     python3 -m unittest orchestrator/tests/test_memory_ops.py

These tests run against a tempdir — `~/.memory/` is never touched.
The module-level `MEMORY_ROOT` and `ARCHIVE_DIR` constants are
monkey-patched in setUp and restored in tearDown.

Coverage:
    encode, recall, update, link, protect, archive, promote, forget,
    extract, consolidate (decay + auto-protect + auto-archive +
    auto-merge), neighbors. Plus internal helpers _tokenize,
    _cosine_similarity, _recency_boost, _graph_centrality.

The point of this suite is not 100% coverage — it is "freeze the
current behavior of memory_ops.py" so that any future continuous-
learning-v2 refactor has a tripwire."""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import memory_ops  # noqa: E402


def _backdate(memory_path: Path, days_old: int) -> None:
    """Rewrite `created` timestamp to be N days in the past.

    Used to exercise consolidate's age-gated branches (decay >7d,
    auto-archive >180d) without sleeping or mocking time.
    """
    with open(memory_path) as f:
        mem = json.load(f)
    backdated_epoch = time.time() - days_old * 86400
    mem["created"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(backdated_epoch))
    with open(memory_path, "w") as f:
        json.dump(mem, f, indent=2)


class MemoryOpsTestBase(unittest.TestCase):
    """Shared setUp/tearDown: each test gets a fresh tempdir as MEMORY_ROOT.

    The constants on the module are monkey-patched in setUp so all code
    paths (including those using glob.glob(os.path.join(MEMORY_ROOT,...)))
    use the tempdir. Originals are restored in tearDown.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_root = memory_ops.MEMORY_ROOT
        self._orig_archive = memory_ops.ARCHIVE_DIR
        memory_ops.MEMORY_ROOT = self._tmp.name
        memory_ops.ARCHIVE_DIR = os.path.join(self._tmp.name, "_archive")
        memory_ops._ensure_dirs()

    def tearDown(self) -> None:
        memory_ops.MEMORY_ROOT = self._orig_root
        memory_ops.ARCHIVE_DIR = self._orig_archive
        self._tmp.cleanup()


# ─────────────────────────────────────────────
# encode
# ─────────────────────────────────────────────


class EncodeTests(MemoryOpsTestBase):

    def test_encode_creates_file_with_required_fields(self):
        mem = memory_ops.encode("the sky is blue", domain="ken")
        self.assertIn("id", mem)
        self.assertEqual(mem["domain"], "ken")
        self.assertEqual(mem["content"], "the sky is blue")
        self.assertEqual(mem["version"], 1)
        self.assertEqual(mem["recall_count"], 0)
        self.assertIsNone(mem["last_recalled"])
        self.assertFalse(mem["protected"])
        self.assertFalse(mem["archived"])
        self.assertEqual(mem["confidence"], 0.8)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{mem['id']}.json")
        self.assertTrue(os.path.exists(path))

    def test_encode_unknown_domain_raises(self):
        with self.assertRaises(ValueError):
            memory_ops.encode("nope", domain="not-a-real-domain")

    def test_encode_with_custom_confidence_and_protected(self):
        mem = memory_ops.encode("foundational", domain="shared",
                                confidence=0.95, protected=True)
        self.assertEqual(mem["confidence"], 0.95)
        self.assertTrue(mem["protected"])

    def test_encode_default_lists_are_independent_instances(self):
        # Regression: default mutable args (tags=[], related_to=[]) must
        # not share state across calls.
        m1 = memory_ops.encode("first", domain="ken")
        m1["tags"].append("leaked")
        m2 = memory_ops.encode("second", domain="ken")
        self.assertEqual(m2["tags"], [])

    def test_encode_id_is_short_uuid(self):
        mem = memory_ops.encode("hi", domain="ken")
        self.assertEqual(len(mem["id"]), 8)


# ─────────────────────────────────────────────
# recall
# ─────────────────────────────────────────────


class RecallTests(MemoryOpsTestBase):

    def test_recall_finds_matching_entry(self):
        memory_ops.encode("kubernetes pod scheduling rules", domain="ken")
        results = memory_ops.recall("kubernetes pods")
        self.assertGreater(len(results), 0)
        self.assertIn("kubernetes", results[0]["content"])

    def test_recall_excludes_low_score(self):
        memory_ops.encode("kubernetes pod scheduling rules", domain="ken")
        # An unrelated query should return nothing (or below threshold)
        results = memory_ops.recall("recipes for lasagna pasta", min_score=0.05)
        # If results come back, the top one should not be the kubernetes entry
        for r in results:
            self.assertNotIn("kubernetes", r["content"].lower())

    def test_recall_skips_superseded(self):
        m1 = memory_ops.encode("the answer is forty-two", domain="ken")
        memory_ops.update(m1["id"], "the answer is forty-three", domain="ken")
        results = memory_ops.recall("the answer", domain="ken")
        # Only the new (non-superseded) version should be in results
        ids = {r["id"] for r in results}
        self.assertNotIn(m1["id"], ids)

    def test_recall_increments_recall_count(self):
        m = memory_ops.encode("unique-content-string-xyzzy", domain="ken")
        self.assertEqual(m["recall_count"], 0)
        memory_ops.recall("unique-content-string-xyzzy", domain="ken")
        # Re-read from disk
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        with open(path) as f:
            after = json.load(f)
        self.assertEqual(after["recall_count"], 1)
        self.assertIsNotNone(after["last_recalled"])

    def test_recall_respects_limit(self):
        # Create enough overlapping entries; verify limit caps results
        for i in range(8):
            memory_ops.encode(f"distinct entry {i} about gardening tomatoes",
                              domain="ken")
        results = memory_ops.recall("gardening tomatoes", limit=3)
        self.assertLessEqual(len(results), 3)

    def test_recall_score_field_present(self):
        memory_ops.encode("rare-token snickerdoodle", domain="ken")
        results = memory_ops.recall("snickerdoodle")
        self.assertGreater(len(results), 0)
        self.assertIn("_score", results[0])
        self.assertIsInstance(results[0]["_score"], float)


# ─────────────────────────────────────────────
# update / supersedes chain
# ─────────────────────────────────────────────


class UpdateTests(MemoryOpsTestBase):

    def test_update_creates_new_version(self):
        m1 = memory_ops.encode("the deploy command is `make deploy`",
                               domain="ken", confidence=0.9)
        m2 = memory_ops.update(m1["id"], "the deploy command is `make ship`",
                               domain="ken")
        self.assertIsNotNone(m2)
        self.assertEqual(m2["supersedes"], m1["id"])
        self.assertEqual(m2["version"], 2)

    def test_update_halves_old_confidence(self):
        m1 = memory_ops.encode("foo", domain="ken", confidence=0.8)
        memory_ops.update(m1["id"], "bar", domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m1['id']}.json")
        with open(path) as f:
            old = json.load(f)
        self.assertAlmostEqual(old["confidence"], 0.4, places=3)

    def test_update_sets_superseded_by_pointer(self):
        m1 = memory_ops.encode("v1", domain="ken")
        m2 = memory_ops.update(m1["id"], "v2", domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m1['id']}.json")
        with open(path) as f:
            old = json.load(f)
        self.assertEqual(old["superseded_by"], m2["id"])

    def test_update_returns_none_for_missing_id(self):
        result = memory_ops.update("no-such-id", "irrelevant", domain="ken")
        self.assertIsNone(result)


# ─────────────────────────────────────────────
# link + neighbors
# ─────────────────────────────────────────────


class LinkTests(MemoryOpsTestBase):

    def test_link_creates_bidirectional_edge(self):
        a = memory_ops.encode("a", domain="ken")
        b = memory_ops.encode("b", domain="ken")
        result = memory_ops.link(a["id"], b["id"], domain="ken")
        self.assertTrue(result["linked"])
        # Re-read both from disk; both should reference each other
        for mem_id, other_id in [(a["id"], b["id"]), (b["id"], a["id"])]:
            path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{mem_id}.json")
            with open(path) as f:
                m = json.load(f)
            self.assertIn(other_id, m["related_to"])

    def test_link_idempotent(self):
        a = memory_ops.encode("a", domain="ken")
        b = memory_ops.encode("b", domain="ken")
        memory_ops.link(a["id"], b["id"], domain="ken")
        memory_ops.link(a["id"], b["id"], domain="ken")  # second call
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{a['id']}.json")
        with open(path) as f:
            m = json.load(f)
        # No duplicate edges
        self.assertEqual(m["related_to"].count(b["id"]), 1)

    def test_link_unknown_id_fails(self):
        a = memory_ops.encode("a", domain="ken")
        result = memory_ops.link(a["id"], "no-such-id", domain="ken")
        self.assertFalse(result["linked"])
        self.assertIn("reason", result)


class NeighborsTests(MemoryOpsTestBase):

    def test_neighbors_returns_direct(self):
        a = memory_ops.encode("a", domain="ken")
        b = memory_ops.encode("b", domain="ken")
        c = memory_ops.encode("c", domain="ken")
        memory_ops.link(a["id"], b["id"], domain="ken")
        memory_ops.link(a["id"], c["id"], domain="ken")
        result = memory_ops.neighbors(a["id"], domain="ken", depth=1)
        ids = {m["id"] for m in result["neighbors"]}
        self.assertEqual(ids, {b["id"], c["id"]})


# ─────────────────────────────────────────────
# protect / archive / promote / forget
# ─────────────────────────────────────────────


class ProtectTests(MemoryOpsTestBase):

    def test_protect_sets_flag(self):
        m = memory_ops.encode("foundational", domain="ken")
        self.assertFalse(m["protected"])
        memory_ops.protect(m["id"], domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        with open(path) as f:
            after = json.load(f)
        self.assertTrue(after["protected"])


class ArchivePromoteTests(MemoryOpsTestBase):

    def test_archive_moves_to_archive_dir(self):
        m = memory_ops.encode("temporary insight", domain="ken")
        active_path = os.path.join(memory_ops.MEMORY_ROOT, "ken",
                                   f"{m['id']}.json")
        archive_path = os.path.join(memory_ops.ARCHIVE_DIR,
                                    f"{m['id']}.json")
        memory_ops.archive(m["id"], domain="ken")
        self.assertFalse(os.path.exists(active_path))
        self.assertTrue(os.path.exists(archive_path))

    def test_promote_round_trips(self):
        m = memory_ops.encode("temporary", domain="ken")
        memory_ops.archive(m["id"], domain="ken")
        result = memory_ops.promote(m["id"])
        self.assertTrue(result["promoted"])
        self.assertEqual(result["to"], "ken")
        active_path = os.path.join(memory_ops.MEMORY_ROOT, "ken",
                                   f"{m['id']}.json")
        archive_path = os.path.join(memory_ops.ARCHIVE_DIR,
                                    f"{m['id']}.json")
        self.assertTrue(os.path.exists(active_path))
        self.assertFalse(os.path.exists(archive_path))

    def test_promote_missing_id_returns_failure(self):
        result = memory_ops.promote("no-such-id")
        self.assertFalse(result["promoted"])
        self.assertIn("reason", result)


class ForgetTests(MemoryOpsTestBase):

    def test_forget_removes_file_from_disk(self):
        m = memory_ops.encode("delete me", domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        self.assertTrue(os.path.exists(path))
        memory_ops.forget(m["id"], domain="ken")
        self.assertFalse(os.path.exists(path))


# ─────────────────────────────────────────────
# extract
# ─────────────────────────────────────────────


class ExtractTests(MemoryOpsTestBase):

    def test_extract_filters_by_domain(self):
        memory_ops.encode("ken-only", domain="ken")
        memory_ops.encode("recipes-only", domain="recipes")
        ken_results = memory_ops.extract(domain="ken")
        self.assertEqual(len(ken_results), 1)
        self.assertEqual(ken_results[0]["domain"], "ken")

    def test_extract_filters_by_type(self):
        memory_ops.encode("insight content", domain="ken", memory_type="insight")
        memory_ops.encode("decision content", domain="ken", memory_type="decision")
        decisions = memory_ops.extract(domain="ken", memory_type="decision")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["type"], "decision")

    def test_extract_filters_by_confidence(self):
        memory_ops.encode("high", domain="ken", confidence=0.9)
        memory_ops.encode("low", domain="ken", confidence=0.3)
        high_only = memory_ops.extract(domain="ken", min_confidence=0.5)
        self.assertEqual(len(high_only), 1)
        self.assertEqual(high_only[0]["content"], "high")

    def test_extract_skips_superseded(self):
        m1 = memory_ops.encode("v1", domain="ken")
        memory_ops.update(m1["id"], "v2", domain="ken")
        results = memory_ops.extract(domain="ken")
        ids = {r["id"] for r in results}
        self.assertNotIn(m1["id"], ids)


# ─────────────────────────────────────────────
# consolidate (decay + auto-protect + auto-archive + auto-merge)
# ─────────────────────────────────────────────


class ConsolidateDecayTests(MemoryOpsTestBase):

    def test_consolidate_decays_old_unrecalled_unprotected(self):
        m = memory_ops.encode("aging-fact", domain="ken", confidence=0.5)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        _backdate(Path(path), days_old=30)
        actions = memory_ops.consolidate(domain="ken")
        self.assertGreaterEqual(actions["decayed"], 1)
        with open(path) as f:
            after = json.load(f)
        # Decayed by 0.05 per call
        self.assertAlmostEqual(after["confidence"], 0.45, places=3)

    def test_consolidate_does_not_decay_protected(self):
        m = memory_ops.encode("protected-fact", domain="ken",
                              confidence=0.5, protected=True)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        _backdate(Path(path), days_old=30)
        memory_ops.consolidate(domain="ken")
        with open(path) as f:
            after = json.load(f)
        self.assertEqual(after["confidence"], 0.5)

    def test_consolidate_does_not_decay_recently_created(self):
        m = memory_ops.encode("fresh-fact", domain="ken", confidence=0.5)
        # Not backdated; <7 days
        memory_ops.consolidate(domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        with open(path) as f:
            after = json.load(f)
        self.assertEqual(after["confidence"], 0.5)

    def test_consolidate_does_not_decay_recalled(self):
        m = memory_ops.encode("recalled-fact-snorkel", domain="ken",
                              confidence=0.5)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        # Backdate first
        _backdate(Path(path), days_old=30)
        # Now recall to bump recall_count
        memory_ops.recall("snorkel", domain="ken")
        memory_ops.consolidate(domain="ken")
        with open(path) as f:
            after = json.load(f)
        # recall_count>0 protects from decay; confidence stays 0.5
        self.assertEqual(after["confidence"], 0.5)

    def test_consolidate_removes_decayed_to_zero(self):
        m = memory_ops.encode("very-low-conf", domain="ken", confidence=0.04)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        _backdate(Path(path), days_old=30)
        actions = memory_ops.consolidate(domain="ken")
        self.assertGreaterEqual(actions["removed"], 1)
        self.assertFalse(os.path.exists(path))


class ConsolidateAutoProtectTests(MemoryOpsTestBase):

    def test_consolidate_auto_protects_at_three_edges(self):
        a = memory_ops.encode("hub", domain="ken")
        b = memory_ops.encode("spoke-1", domain="ken")
        c = memory_ops.encode("spoke-2", domain="ken")
        d = memory_ops.encode("spoke-3", domain="ken")
        memory_ops.link(a["id"], b["id"], domain="ken")
        memory_ops.link(a["id"], c["id"], domain="ken")
        memory_ops.link(a["id"], d["id"], domain="ken")
        actions = memory_ops.consolidate(domain="ken")
        self.assertGreaterEqual(actions["auto_protected"], 1)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{a['id']}.json")
        with open(path) as f:
            after = json.load(f)
        self.assertTrue(after["protected"])

    def test_consolidate_does_not_auto_protect_at_two_edges(self):
        a = memory_ops.encode("not-quite-hub", domain="ken")
        b = memory_ops.encode("spoke-1", domain="ken")
        c = memory_ops.encode("spoke-2", domain="ken")
        memory_ops.link(a["id"], b["id"], domain="ken")
        memory_ops.link(a["id"], c["id"], domain="ken")
        memory_ops.consolidate(domain="ken")
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{a['id']}.json")
        with open(path) as f:
            after = json.load(f)
        self.assertFalse(after["protected"])


class ConsolidateAutoArchiveTests(MemoryOpsTestBase):

    def test_consolidate_auto_archives_old_low_conf_unprotected(self):
        m = memory_ops.encode("ancient-and-weak", domain="ken",
                              confidence=0.25)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        archive_path = os.path.join(memory_ops.ARCHIVE_DIR,
                                    f"{m['id']}.json")
        _backdate(Path(path), days_old=200)
        actions = memory_ops.consolidate(domain="ken")
        self.assertGreaterEqual(actions["auto_archived"], 1)
        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists(archive_path))

    def test_consolidate_does_not_archive_protected_even_if_old_low_conf(self):
        m = memory_ops.encode("ancient-but-protected", domain="ken",
                              confidence=0.25, protected=True)
        path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{m['id']}.json")
        _backdate(Path(path), days_old=200)
        memory_ops.consolidate(domain="ken")
        self.assertTrue(os.path.exists(path),
                        "protected memory must not be auto-archived")


class ConsolidateAutoMergeTests(MemoryOpsTestBase):

    def test_consolidate_merges_high_similarity_pair(self):
        # Hits cosine > 0.85 via 12 shared tokens + 1 unique each side.
        # Math for 2-doc corpus: shared idf=1.0, unique idf≈1.405,
        # cosine = 12 / sqrt(12+1.974)^2 ≈ 0.86.
        text_a = ("one two three four five six seven eight nine ten "
                  "eleven twelve apple")
        text_b = ("one two three four five six seven eight nine ten "
                  "eleven twelve banana")
        a = memory_ops.encode(text_a, domain="ken", confidence=0.9)
        b = memory_ops.encode(text_b, domain="ken", confidence=0.5)
        actions = memory_ops.consolidate(domain="ken")
        self.assertGreaterEqual(actions["summarized"], 1)
        # Higher-confidence one survives in active; lower goes to archive
        a_path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{a['id']}.json")
        b_path = os.path.join(memory_ops.MEMORY_ROOT, "ken", f"{b['id']}.json")
        self.assertTrue(os.path.exists(a_path))
        self.assertFalse(os.path.exists(b_path))
        # The lower-conf one is in archive with merged_into
        b_archive = os.path.join(memory_ops.ARCHIVE_DIR, f"{b['id']}.json")
        self.assertTrue(os.path.exists(b_archive))
        with open(b_archive) as f:
            arch = json.load(f)
        self.assertEqual(arch["merged_into"], a["id"])

    def test_consolidate_records_potential_duplicates_between_70_and_85(self):
        # Hits cosine ≈ 0.72: 10 shared tokens + 2 unique each side.
        # Lands in the (0.70, 0.85] band → flagged not merged.
        a = memory_ops.encode(
            "one two three four five six seven eight nine ten apple banana",
            domain="ken")
        b = memory_ops.encode(
            "one two three four five six seven eight nine ten cherry date",
            domain="ken")
        actions = memory_ops.consolidate(domain="ken")
        # Either it merged or it flagged — at least one of the two
        # should have happened given how similar these are.
        flagged_ids = {(p["a"], p["b"]) for p in actions["potential_duplicates"]}
        merged_at_least_one = actions["summarized"] >= 1
        self.assertTrue(
            merged_at_least_one or (a["id"], b["id"]) in flagged_ids
            or (b["id"], a["id"]) in flagged_ids,
            "near-duplicate must be either merged or flagged",
        )


# ─────────────────────────────────────────────
# internal helpers (regression anchors)
# ─────────────────────────────────────────────


class InternalHelperTests(unittest.TestCase):
    """Anchors for the TF-IDF + recency + centrality formulas.

    These tests do NOT need MEMORY_ROOT patching — pure functions.
    If consolidate/recall ever stop matching expectation, these are
    the first place to look for which atomic helper drifted.
    """

    def test_tokenize_strips_stopwords_and_short_tokens(self):
        tokens = memory_ops._tokenize("the quick brown fox a it")
        # Stopwords (the, a, it) removed; "quick"/"brown"/"fox" remain
        self.assertIn("quick", tokens)
        self.assertIn("brown", tokens)
        self.assertIn("fox", tokens)
        self.assertNotIn("the", tokens)
        self.assertNotIn("a", tokens)
        self.assertNotIn("it", tokens)

    def test_cosine_similarity_identical_vecs(self):
        v = {"a": 1.0, "b": 2.0, "c": 3.0}
        self.assertAlmostEqual(memory_ops._cosine_similarity(v, v), 1.0, places=6)

    def test_cosine_similarity_disjoint_vecs(self):
        a = {"x": 1.0}
        b = {"y": 1.0}
        self.assertEqual(memory_ops._cosine_similarity(a, b), 0.0)

    def test_cosine_similarity_empty(self):
        self.assertEqual(memory_ops._cosine_similarity({}, {"a": 1}), 0.0)
        self.assertEqual(memory_ops._cosine_similarity({"a": 1}, {}), 0.0)

    def test_recency_boost_decays_with_age(self):
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        old_epoch = time.time() - 90 * 86400
        old_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(old_epoch))
        boost_now = memory_ops._recency_boost(now_str)
        boost_old = memory_ops._recency_boost(old_str)
        self.assertGreater(boost_now, boost_old)
        # 90-day half-life → 90d-old should be ≈ 0.5
        self.assertAlmostEqual(boost_old, 0.5, places=1)

    def test_graph_centrality_zero_when_no_edges(self):
        mem = {"related_to": []}
        all_mems = [{"related_to": ["x", "y"]}, mem]
        self.assertEqual(memory_ops._graph_centrality(mem, all_mems), 0.0)

    def test_graph_centrality_normalizes_to_max(self):
        hub = {"related_to": ["a", "b", "c", "d"]}
        spoke = {"related_to": ["a"]}
        all_mems = [hub, spoke]
        self.assertEqual(memory_ops._graph_centrality(hub, all_mems), 1.0)
        self.assertEqual(memory_ops._graph_centrality(spoke, all_mems), 0.25)


if __name__ == "__main__":
    unittest.main(verbosity=2)
