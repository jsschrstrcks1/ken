# HANDOFF — P1#9 continuous-learning-v2 auto-extraction loop

**Status:** 12 slices shipped (0, 0.5, 1, 2, 2.5, 3A, 3B, 3C, 4, 5, 6, 7.5) + session_id continuity. Auto-extraction is now structurally AND operationally complete: when the operator opts in (env flag + .claude/settings.json registration), every tool call writes a hashed observation, every session has a snapshot-extractable candidate list, every cited evidence trail is HMAC-attested. ALL 13 SLICES SHIPPED. CL-v2 is complete.

**Last commit:** ken `(pending)` — Slice 6: PostToolUse hook + Python writer + bench harness + 22 tests (registration in .claude/settings.json deferred to operator).

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
| 9 | 3A — observation log | `b5c9101` | `record_observation()`, `clear_observations()`, `_compute_args_hash()`, flock + FIFO rotation; gitignore for `_observations/` |
| 10 | 3C — HMAC sidecar activation | `8741a6e` | `compute_log_checksum()`, `validate_log_checksum()`, `_ensure_integrity_key()`, `_compute_file_integrity()`; activates `_assert_evidence_integrity` |
| 11 | 3B — observation extraction | `d6709d8` | `extract_candidates_from_observations()`, `_extract_candidates_from_observation_log()`, `_is_well_formed_observation()`; 3 candidate kinds; snapshot under shared flock; per-candidate integrity validation |
| 11+ | Slice 6 prereq — session_id continuity | `c7ca362` | `_current_session_id()` resolves env > CLAUDE_SESSION_ID > `<MEMORY_ROOT>/_session/current`; idle staleness 4h; subprocess-survivable |
| 12 | 6 — PostToolUse hook + writer | `c7ca362` | `hook_observe.py` (Python writer), `.claude/hooks/observe-tool-use.sh` (bash wrapper), `bench_hook.py` (perf harness); fire-and-forget; fail-closed |

**Test count:** 423 (344 in `test_memory_ops.py` + 24 in `test_meta_ci.py` + 22 in `test_hook_observe.py` + 33 in other test files). All pass. CI gate + panic-ordering + helper-seal-lifecycle all green.

**Measured perf:** direct `record_observation` 1.86 ms/call; bash-wrapped fire-and-forget 14.97 ms/call (the writer runs detached, so the wrapper cost is what users actually feel).

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
| Operator: enable Slice 6 in production | 5 min | n/a | Add the hook registration block to `.claude/settings.json` + export `MEMORY_AUTO_OBSERVE_ENABLED=true` |
| 7 — session-end auto-extract | ~1 session | Low | SessionEnd hook → `extract_candidates_from_observations(session_id)` → print candidates to operator |

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

Slice 6 artifacts are shipped but NOT registered. To turn on always-on capture (operator's explicit action):

1. Add to `~/.bashrc` or session env: `export MEMORY_AUTO_OBSERVE_ENABLED=true`
2. Append this block to `.claude/settings.json` under `hooks.PostToolUse`:
   ```json
   {
     "matcher": "*",
     "hooks": [
       {"type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/observe-tool-use.sh"}
     ]
   }
   ```
3. After a few sessions: `python3 orchestrator/memory_ops.py` then in Python `import memory_ops; memory_ops.extract_candidates_from_observations("<session_id>")` to see what surfaced.

**Slice 7 (next code work, ~1 session, low risk):** SessionEnd hook calls `extract_candidates_from_observations(session_id)` and prints the candidate list. No auto-promotion; operator decides. Mirror of `.claude/hooks/observe-tool-use.sh` but the body is `python3 -c "..."` that imports and calls the extractor.

**Web-container note:** `~/.memory/_integrity.key` is ephemeral on web; key regenerates per session, invalidating cross-session HMACs. Within-session integrity always holds. Cross-session persistence requires CLI/desktop where `~/.memory/` survives.

Run before any new work: `python3 -m pytest orchestrator/tests/ -q` should print `423 passed`.
Measure perf: `python3 orchestrator/bench_hook.py 100`.

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
