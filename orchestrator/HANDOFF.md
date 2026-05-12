# HANDOFF — P1#9 continuous-learning-v2 auto-extraction loop

**Status:** 7 slices shipped. Auto-extraction loop is structurally complete in `single-operator-local` profile. Slice 2.5 dogfood gate is the next decision point — NOT another implementation slice.

**Last commit:** ken `3808147` (Slice 7.5: consensus auto-promotion).

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

**Test count:** 251 (227 in `test_memory_ops.py` + 24 in `test_meta_ci.py`). All pass. `~/.memory/` byte-diff empty across every shipped slice.

---

## What Still Needs Doing — prioritized

### **Now (Slice 2.5 dogfood gate, NOT a code slice)**

Use the system on real sessions for ~2 weeks. Track:
- How often `extract_candidates_from_session` gets invoked (target: >0; ideally several times per week)
- Candidates surfaced per session (target: 0-10; too many = noise, too few = bug)
- Candidates promoted via `promote_to_instinct` or `auto_promote_eligible`
- Promoted instincts demoted later (target: <20% — high demote rate = false positives)

**Decision gate:** if invocations are zero, the friction profile is wrong; soften before shipping more. If active and stable, schedule Slices 3A/B/C/6.

### **Deferred until dogfood signal**

| Slice | Effort | Risk | Reason deferred |
|---|---|---|---|
| 3A — observation log | ~1.5 sessions | Higher (new disk surface) | Awaits dogfood; bigger attack-surface jump |
| 3B — extraction from log | ~1 session | Medium | Needs 3A |
| 3C — log integrity (HMAC) | ~1 session | Medium | Activates `_assert_evidence_integrity` stub |
| 6 — hooks (PreToolUse/PostToolUse) | ~2 sessions + rollout | Highest | Needs 3A/B/C stable |
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

## Files Created/Modified (across all 7 slices)

- `orchestrator/memory_ops.py` — 10 invariants, 5 mutation defenses, 4 new public functions, 5 profile-aware flag readers
- `orchestrator/tests/test_memory_ops.py` — 227 tests (was 46 before P1#9)
- `orchestrator/tests/test_meta_ci.py` — 24 meta-tests (NEW file from Slice 0.5)
- `orchestrator/CONTINUOUS_LEARNING_PLAN.md` — 935-line v5 plan
- `orchestrator/CONTINUOUS_LEARNING_REVIEWS.md` — 384-line LLM review ledger
- `orchestrator/CONTINUOUS_LEARNING_DOCTRINE.md` — 150-line plain-language principles
- `WORKING-CONTEXT.md` — updated with each slice's outcome
- `open-claw-stuff/schemas/records/continuous-learning-v2.json` — provenance record + regression baseline

---

## How to Resume

If returning **before dogfood window expires** (~2 weeks from 2026-05-12):
1. Read this file
2. Check cognitive memory: `python3 orchestrator/memory_ops.py recall "dogfood gate"`
3. Look at usage metrics: any memories with `is_auto_promoted` or `is_instinct` set?
4. If yes → schedule a Slice 3A/B/C planning session
5. If no → consider why; soften friction before extending

If returning **after dogfood window** with positive usage data:
- Run `/orchestra` round 4 review on plan v5 with the dogfood metrics as new context
- Schedule Slice 3A; budget ~1.5 sessions

If returning **after dogfood window with zero usage**:
- The plan got the friction model wrong
- Re-read v5 §0 friction-tax section before extending
- Consider whether the entire auto-extraction loop is right for this household

---

## Reminder

Dogfood gate reminder encoded in cognitive memory under domain `ken` with type `decision`. To recall:
```
python3 /home/user/ken/orchestrator/memory_ops.py recall "dogfood gate"
```
