# HANDOFF — P1#9 continuous-learning-v2 auto-extraction loop

**Status:** 9 slices shipped (0, 0.5, 1, 2, 2.5, 3A, 4, 5, 7.5). Slice 3A — observation log infrastructure — lands the foundation for hook-driven auto-capture (Slice 6) and observation-extraction (Slice 3B). Next is Slice 3B or 3C (per plan §7 sequencing).

**Last commit:** ken `(pending)` — Slice 3A: observation log infrastructure (record_observation + clear_observations + flock + 10MB/10K-line FIFO rotation).

---

## What Was Done

| # | Slice | Commit | Adds |
|---|---|---|---|
| 1 | 0 — doctrine + invariants | `1928f01` | 9 `_assert_*` invariants, `CarefulNotCleverError`, `_learning_profile()`, CI gate, `CONTINUOUS_LEARNING_DOCTRINE.md` |
| 2 | 0.5 — mutation defense | `1312c6f` | 5 helpers (`_validate_helper_integrity`, `_seal_helpers`, `_validate_file_integrity`, `_validate_key_fingerprint`, `_audit_config_integrity`) + 6 meta-tests in `test_meta_ci.py` |
| 3 | 1 — kill-switch | `62b529d` | `_assert_panic_check` wired as first line of Slice 1.1 fns + AST ordering rule + panic-flip probe |
| 4 | 2 — pull session extraction | `4d60bea` | `extract_candidates_from_session()` reads `orchestrator/state/<id>.json`; snapshot pattern; path-traversal defense |
| 5 | 4 — confidence promotion | `925214d` | `consolidate()` bump (+0.05) for `recall_count≥5 AND last_recalled<14d`; new `actions["confidence_promoted"]` |
| 6 | 5 — usage history | `58e1c2b` | `usage_history: [{at, session_id}]` FIFO cap=20 in `recall()`; privacy invariant (no query content) |
| 7 | 7.5 — consensus auto-promotion | `3808147` | `auto_promote_eligible()` + 10th invariant `_assert_promotion_eligibility` (5 cryptographic criteria) |
| 8 | 2.5 — formalized transcript mining | `d07b6c0` | `mine_transcripts()`, `ingest_relayed_memories()`, `_dedup_against_corpus()` (relay-pattern stable surface) |
| 9 | 3A — observation log | `(pending)` | `record_observation()`, `clear_observations()`, `_compute_args_hash()`, flock + FIFO rotation; gitignore for `_observations/` |

**Test count:** 346 (289 in `test_memory_ops.py` + 24 in `test_meta_ci.py` + 33 in other test files). All pass. CI gate (`test_every_mutation_path_invokes_invariants`) + panic-ordering test green.

---

## What Still Needs Doing — prioritized

### **Now (Slice 2.5 dogfood gate, NOT a code slice)**

Use the system on real sessions for ~2 weeks. Track:
- How often `extract_candidates_from_session` gets invoked (target: >0; ideally several times per week)
- Candidates surfaced per session (target: 0-10; too many = noise, too few = bug)
- Candidates promoted via `promote_to_instinct` or `auto_promote_eligible`
- Promoted instincts demoted later (target: <20% — high demote rate = false positives)

**Decision gate:** if invocations are zero, the friction profile is wrong; soften before shipping more. If active and stable, schedule Slices 3A/B/C/6.

### **Next**

| Slice | Effort | Risk | Reason |
|---|---|---|---|
| 3B — extraction from log | ~1 session | Medium | Reads Slice 3A's log; surfaces candidates |
| 3C — log integrity (HMAC) | ~1 session | Medium | Activates `_assert_evidence_integrity` stub; key lives outside any tracked repo |
| 6 — hooks (PreToolUse/PostToolUse) | ~2 sessions + rollout | Highest | Needs 3A/B/C stable + `MEMORY_SESSION_ID` subprocess-inheritance fix |
| 7 — session-end auto-extract | ~1 session | Low | Minor wiring; can ship anytime |

### **Maybe never (documented limits per `CONTINUOUS_LEARNING_PLAN.md` §0)**

- T11 side-channel timing on `consolidate` (out-of-scope; co-located trusted operator)
- T19 OS privilege escalation (non-applicable in single-op-local)
- T21 operator coercion (non-applicable in single-op-local)
- HSM/TPM for HMAC keys (household-grade is `_validate_key_fingerprint`)
- eBPF / syscall tracing supplement to AST checks

---

## Key Decisions (do not revisit without explicit reason)

1. **No auto-promotion to instinct in multi-operator-shared profile.** Locked. `auto_promote_eligible` returns disabled stub regardless of flag.
2. **Single-id contract preserved everywhere.** `auto_promote_eligible` iterates per-id internally; no batch API.
3. **No always-on Python daemon.** Hooks are harness-driven (Slice 6 future); extraction is synchronous from explicit trigger.
4. **HMAC-SHA256, not raw SHA256** for log integrity (Perplexity R2 length-extension finding).
5. **5min/5min temporal window** for `_assert_temporal_consistency` (Grok R3 NTP-drift finding).
6. **`_assert_panic_check` is first executable statement** of every public learning function (AST-enforced).
7. **Profile is configuration, not security.** Flipping `MEMORY_LEARNING_PROFILE` restores or relaxes defenses without code change.

---

## Files Created/Modified (across all 9 slices)

- `orchestrator/memory_ops.py` — 10 invariants, 5 mutation defenses, 6 new public functions (Slices 1-3A), `_compute_args_hash`, observation log infrastructure
- `orchestrator/tests/test_memory_ops.py` — 289 tests (was 46 before P1#9)
- `orchestrator/tests/test_meta_ci.py` — 24 meta-tests (NEW file from Slice 0.5)
- `orchestrator/CONTINUOUS_LEARNING_PLAN.md` — v6.1 plan (Slice 3A added to change log)
- `orchestrator/CONTINUOUS_LEARNING_REVIEWS.md` — 384-line LLM review ledger
- `orchestrator/CONTINUOUS_LEARNING_DOCTRINE.md` — 150-line plain-language principles
- `open-claw-stuff/.gitignore` — `_observations/`, `_checksums/`, `_integrity.*` added
- `open-claw-stuff/.memory/README.md` — privacy posture (private repo)
- `open-claw-stuff/schemas/records/continuous-learning-v2.json` — provenance record + regression baseline

---

## How to Resume

Slice 3A is in. The two natural next steps:

**Option A — Slice 3B (extraction from observation log).** Reads `<MEMORY_ROOT>/_observations/<session_id>.jsonl`, clusters by tool name + result_class, returns candidate dicts in the same shape as Slice 2's `extract_candidates_from_session`. Each candidate must carry observation ids in its `evidence` so `_assert_evidence_present` passes. Pre-Slice 3C, `_assert_evidence_integrity` is still the no-op stub.

**Option B — Slice 3C (HMAC sidecar activation).** Adds `<MEMORY_ROOT>/_checksums/<session_id>.txt` running SHA256, called on every `record_observation` write. `_assert_evidence_integrity` becomes real. The HMAC key (`_integrity.key`) MUST live outside any tracked repo (not in `open-claw-stuff/.memory/`).

**Open prerequisite for Slice 6 hooks:** `MEMORY_SESSION_ID` subprocess-inheritance bug — env var set in one `python3 -c` does not propagate. Fix candidates: harness-level export, session-state file, or template insertion.

Run before either: `python3 -m pytest tests/ -q` should print `346 passed`.

---

## Reminder

Dogfood gate reminder encoded in cognitive memory under domain `ken` with type `decision`. To recall:
```
python3 /home/user/ken/orchestrator/memory_ops.py recall "dogfood gate"
```

## MEMORY_ROOT relocated (2026-05-13)

The persistence hole was identified: `~/.memory/` (→ `/root/.memory/` in web containers) is destroyed when each Claude Code web container ends. Solution: `memory_ops._resolve_memory_root()` now prefers `<parent>/open-claw-stuff/.memory/` — git-tracked, syncs via clone/pull/push across CLI and web environments.

Priority order:
1. `MEMORY_ROOT` env var (operator override)
2. `<parent>/open-claw-stuff/.memory/` (sibling repo; persistent canonical default)
3. `~/.memory/` legacy fallback (CLI/desktop only; ephemeral in web)

**Privacy posture (corrected 2026-05-13):** `open-claw-stuff` is a PRIVATE GitHub repo. Encoded memories committed there are private — as safe as a private GitHub repo gets. The Unlicense is the content license posture (operator-as-publication-gate), not the visibility posture. Secrets/credentials still belong in `.env` regardless of repo visibility. See `open-claw-stuff/.memory/README.md`.
