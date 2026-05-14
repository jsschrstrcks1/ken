# Continuous-Learning-v2 Auto-Extraction Plan — v6

**Status:** v6 reflects reality after Slices 0/0.5/1/2/4/5/7.5 shipped + real dogfood data accumulated faster than expected. Plan diverged from reality in productive ways during 2026-05-13; this update aligns the doc with what's deployed.
**Owner:** P1#9 continuation. Slices 1, 1.1, 1.2 already shipped.
**Goal:** Make the household memory system learn from operator behavior without sacrificing the safety properties Slices 1–1.2 established.

---

## 0. Change log

### v6.4 → v6.5 (Slice 6 shipped — hook artifacts ready; registration is operator's choice)

Slice 6 — PostToolUse hook + Python writer — landed at ken `(pending commit)`. Capture is fully automatic when the operator opts in.

Architecture: fire-and-forget bash wrapper + detached Python writer. The wrapper's synchronous cost is bash startup + fork (~15ms measured); the writer runs detached so its work (memory_ops import, HMAC sidecar fsync) doesn't add to user-visible tool-call latency. The plan's <5ms target was aspirational for any fork-based hook on consumer hardware; measured numbers are reported instead of claimed.

Files added:
- `orchestrator/hook_observe.py` — Python writer. Validates payload shape, sanitizes tool_name to the `_OBSERVATION_TOOL_PATTERN` charset, hashes tool_input via `_compute_args_hash` (raw args never reach disk), classifies tool_response into `{success, error, timeout, truncated}`, calls `record_observation`. Wrapped in top-level try/except that ALWAYS exits 0 — fail-closed contract.
- `.claude/hooks/observe-tool-use.sh` — bash wrapper. Reads stdin, gates on `MEMORY_AUTO_OBSERVE_ENABLED=true`, spawns the writer detached via `disown`, exits 0 unconditionally.
- `orchestrator/bench_hook.py` — ship-gate benchmark. Reports two numbers: direct `record_observation` cost (1.86 ms/call measured on this hardware) and end-to-end hook wrapper cost (14.97 ms/call). Operator decides whether the cost is acceptable.

NOT modified: `.claude/settings.json`. Hook registration is the operator's explicit choice per the plan's ship-gate item "Explicit user approval to enable always-on capture in their household." When the operator decides to enable, the registration block is:

```json
"PostToolUse": [
  {
    "matcher": "*",
    "hooks": [
      {"type": "command",
       "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/observe-tool-use.sh"}
    ]
  }
]
```

…plus `export MEMORY_AUTO_OBSERVE_ENABLED=true` in their shell profile. With both, every tool call writes an observation; Slice 3B's `extract_candidates_from_observations(session_id)` surfaces candidates from the accumulated log; Slice 3C's HMAC sidecars attest each cited evidence trail.

Tests added: 22 (12 WriterUnitTests + 7 WriterFailClosedTests + 3 BashWrapperTests). The fail-closed tests use real `subprocess.run` to exercise the contract end-to-end — garbage stdin, top-level array, missing session_id, panic flag set, disabled flag, only-special-chars tool_name all exit 0. Full suite: 423 passing.

Threat surface: highest in the plan (every tool call writes to disk). Defenses already in place via Slices 3A + 3C:
- T3 disk exhaustion → 10MB / 10K-line FIFO cap with INFO-captured rotation
- T4 sensitive-data leakage → `_compute_args_hash` runs in the writer before any disk write; tool name sanitized to a-z0-9_.- charset only
- T6 cross-session race → flock under every write
- T10 log-compaction attack → 10% eviction not full truncate
- T8 plan-injection → Slice 3B's strict 4-key shape check rejects extra keys at extraction time
- T2 fabricated evidence → Slice 3C HMAC sidecar; every record_observation atomically updates the sidecar

Web-container caveat retained: integrity key is ephemeral on Claude Code web, so cross-session HMAC validation fails by design (visible signal, not silent acceptance).

### v6.3 → v6.4 (cross-subprocess session_id continuity)

Fixes the dogfood bug filed in v6 §0: `MEMORY_SESSION_ID` set inside one `python3 -c` invocation didn't inherit into the next, so every recall logged `session_id: "unknown"` in `usage_history`. Prerequisite for Slice 6 hooks — without a stable session_id across subprocess boundaries, observation logs can't be coherently keyed.

`_current_session_id()` rewritten to resolve in priority order:
1. `MEMORY_SESSION_ID` env var — explicit operator override (validated via `_validate_session_id`; malformed values fall through)
2. `CLAUDE_SESSION_ID` env var — future-proofs against a harness that ever exports the transcript UUID
3. `<MEMORY_ROOT>/_session/current` — auto-managed plain-text file with the generated session_id; mtime touched on every read so an active session stays alive; idle beyond `_SESSION_STALE_SECONDS` (4h) triggers regeneration

Generated ids: `sess-YYYYMMDDTHHMMSSZ-<hex6>` — sortable, no path separators, passes `_validate_session_id`.

Robustness:
- Read-only MEMORY_ROOT → returns generated id without persisting (better than crashing the caller)
- Malformed file content (e.g. path-traversal-shaped) → regenerates
- Empty file → regenerates
- Concurrent first-time writers race-converge after one round-trip (single small file, not worth flock)

`open-claw-stuff/.gitignore`: `.memory/_session/` added (auto-managed runtime state).

11 new tests covering env precedence, persistence across subprocess (real `subprocess.check_output`), staleness, active-keep-alive, malformed regeneration, and path-traversal rejection. Full suite: 401 passing.

This unblocks Slice 6 (PreToolUse / PostToolUse hooks) by guaranteeing every `record_observation` call within a session keys to the same log file regardless of how many `python3 -c` invocations the harness spawns.

### v6.2 → v6.3 (Slice 3B shipped — extraction loop is now end-to-end)

Slice 3B — observation-log → candidate extraction — landed at ken `(pending commit)`. Closes the 3A→3B→3C loop. The extraction surface is identical in shape to Slice 2's `extract_candidates_from_session` but reads the structured observation log instead of orchestrator blackboard state, and every candidate's evidence is cryptographically attested by Slice 3C's HMAC sidecars.

Adds:
- Public `extract_candidates_from_observations(session_id, dry_run=True)` — snapshot-pattern read under shared flock; deterministic clustering; per-candidate invariant validation including the now-real `_assert_evidence_integrity`.
- Pure `_extract_candidates_from_observation_log(observations, session_id)` — testable in isolation; no I/O.
- `_is_well_formed_observation(obs)` — strict 4-key shape check (T8 plan-injection mitigation). Lines with extra keys, missing keys, wrong types, invalid tool name, malformed args_hash, or unknown result_class are treated as malformed and counted (never fed to the extractor).

Three candidate kinds (mirror of Slice 2 with observation-log idioms):
- `pattern` (success): same `(tool, result_class="success")` repeated ≥3 times → automation candidate (`_OBS_SUCCESS_PATTERN_MIN = 3`).
- `pattern` (repeat): same `args_hash` repeated ≥3 times → operator did the same thing repeatedly (`_OBS_REPEAT_PATTERN_MIN = 3`).
- `fact` (failure): same `(tool, args_hash)` with `result_class="error"` repeated ≥2 times → known failure mode (`_OBS_ERROR_PATTERN_MIN = 2`).

Every candidate's `evidence.observations[]` entries carry `{session_id, index, ...}` so `_assert_evidence_integrity` (Slice 3C) validates the cited log file before any candidate surfaces. End-to-end integrity is now structural: bytecode in the helper + AST in the CI gate + HMAC on the log + per-candidate validation at extraction.

Snapshot pattern: log is read once in full under `fcntl.LOCK_SH`, then the extractor runs on the immutable copy. Mitigates T9 TOCTOU — concurrent `record_observation` writes after the read are invisible to this call but visible to the next.

Tests added: 21 (9 ExtractFromObservationsTests + 12 ExtractFromObservationsAdversarialTests). Full suite: 390 passing.

Auto-extraction loop is now structurally complete in the single-operator-local profile. The only piece needed for fully-automated capture is Slice 6 (PreToolUse/PostToolUse hooks that call `record_observation`); the read + integrity + extraction pipeline is in place.

### v6.1 → v6.2 (Slice 3C shipped)

Slice 3C — HMAC sidecar activation — landed at ken `(pending commit)`. Activates the integrity layer that Slices 0.5 + 3A scaffolded.

Adds:
- `_ensure_integrity_key()` — generates 32-byte random key at `~/.memory/_integrity.key` (mode 0o400) on first use AND registers the fingerprint atomically with creation. Atomic pairing fixes the bootstrap window where an attacker could swap the key before fingerprint registration.
- `_compute_file_integrity(path)` — writes `<path>.hmac` sidecar with HMAC-SHA256(key, content). Mirror of the existing `_validate_file_integrity`.
- Public `compute_log_checksum(session_id)` — explicit (re)compute path for migration / repair.
- Public `validate_log_checksum(session_id)` — structured-result validation (returns `{valid, reason}` instead of raising) so callers can choose hard-fail vs log-and-skip.
- `_assert_evidence_integrity(candidate)` — STUB → REAL. Walks `evidence.observations[]` and validates the log for any entry with both `session_id` (str) + `index` (int). Legacy / non-3A shapes (`{}`, bare `session_id`, `line_hmac`) no-op so Slice 2 + 2.5 candidates continue to pass.

Wiring:
- `record_observation` now calls `_validate_key_fingerprint()` + `_compute_file_integrity()` under the same flock as the append, so log + sidecar are always written atomically.
- `clear_observations` removes the sidecar alongside the log.
- Test base `_ObservationBase` isolates `_INTEGRITY_KEY_PATH` + `_INTEGRITY_FINGERPRINT_PATH` to the tempdir (no real `~/.memory/` pollution from test runs).

Key design choice — log-reference disambiguation: `_assert_evidence_integrity` only validates when an observation entry has BOTH `session_id` AND integer `index`. Slice 2's `extract_candidates_from_session` produces evidence with bare `session_id` (referencing the blackboard, not the log) and is correctly skipped. Slice 3B (when it ships) MUST include `index` for log-backed evidence to be cryptographically attested.

Web-container caveat: `~/.memory/` is ephemeral on Claude Code web; the key regenerates per session, invalidating cross-session HMACs. Within-session integrity holds. Persistent integrity across sessions requires a local CLI/desktop deployment where `~/.memory/_integrity.key` survives.

Tests added: 23 (12 LogChecksumTests + 11 LogChecksumAdversarialTests). Full suite: 369 passing. CI gate + panic-ordering + helper-seal-lifecycle all still green.

NOT in this slice: Slice 3B extraction from observation log.

### v6 → v6.1 (Slice 3A shipped)

Slice 3A — observation log infrastructure — landed at ken `(pending commit)`. Adds three new public surfaces plus four helpers:
- `record_observation(tool, args_hash, result_class, session_id)` — append one JSONL line to `<MEMORY_ROOT>/_observations/<session_id>.jsonl`, with panic + rate-limit + temporal-consistency + input-validation invariants. flock held across append + rotation pass.
- `clear_observations(session_id)` — explicit cleanup.
- Internal: `_compute_args_hash`, `_validate_observation_inputs`, `_rotate_observation_log`, `_observation_log_path`, `_observations_dir`, `_observations_enabled`.

Feature flag: `MEMORY_OBSERVATIONS_ENABLED=true` opts in (default off).

Caps:
- `_OBSERVATION_MAX_BYTES = 10 MB`
- `_OBSERVATION_MAX_LINES = 10_000`
- `_OBSERVATION_EVICTION_RATIO = 0.10` (FIFO-evict oldest 10% at cap; not full truncate)
- Eviction surfaces in return dict as `rotation.info`; the `_assert_no_silent_skip` raise is caught and captured (silent skip remains forbidden — captured INFO is the operator-visible breadcrumb).

Tests added: 34 (13 unit + 3 clear + 18 adversarial). Full suite: 346 passing. CI gate (`test_every_mutation_path_invokes_invariants`) + panic-ordering test both still green.

Gitignore updated in `open-claw-stuff`: `.memory/_observations/`, `.memory/_checksums/`, `.memory/_integrity.*` (the observation log is high-volume ephemera; Slice 3C key + sidecars never live in any tracked repo).

NOT in this slice: extraction (Slice 3B), HMAC sidecars (Slice 3C), hook integration (Slice 6).

### v5 → v6 (reality alignment after first day of live use)

This update doesn't change the security model; it records the architecture-level surprises encountered during the first day of real cross-thread dogfood + closes the privacy-posture gap that v4/v5 had wrong.

**Persistence hole found + fixed.** v5 assumed `~/.memory/` was persistent. In Claude Code on the web (the primary deployment for this household), `~/.memory/` resolves to `/root/.memory/` in an ephemeral container that's destroyed on session teardown. Every encode written across an unknown number of prior sessions was lost. Fix shipped ken `13cac8a`: `_resolve_memory_root()` now prefers `<parent>/open-claw-stuff/.memory/` (git-tracked sibling) over `~/.memory/`. Order of precedence: (1) `MEMORY_ROOT` env var, (2) sibling repo, (3) legacy `~/.memory/`. Tests unaffected; all 253 still pass. open-claw-stuff `f527cc4` ships the `.memory/` tree with one initial entry.

**Privacy posture corrected.** v4/v5 (and the initial `.memory/README.md`) framed open-claw-stuff as "public-domain — everything committed is permanently public." Operator clarified 2026-05-13 that the *repo* is PRIVATE on GitHub (jsschrstrcks1/open-claw-stuff). The Unlicense applies to *content* if/when the operator chooses to publish, but the storage is private by default. Earlier wording over-restricted encoders (forced pseudonymization of names, decisions, specifics). Standing rule: encode honestly; operator is the publication gate; secrets still go in `.env` (gitignored), regardless of repo visibility. Recorded in `.memory/README.md` + memory `e25c4814`. Earlier commit messages referencing "public-domain implications" are historical record; not force-pushed/rewritten.

**Cross-thread mining emerged as an operating pattern.** v5 had no slice for transcript mining. In practice it became the dominant mode of corpus growth on day one. Pattern:
1. Sibling thread parses its own `/root/.claude/projects/-home-user/*.jsonl` transcripts (persistent across container teardown — Claude Code's harness manages this dir).
2. Extracts unique high-signal operator-directive content (skip auto-resume preambles + system-reminders + one-word imperatives).
3. Encodes via `memory_ops.encode` if the persistence path is reachable, OR outputs JSON in chat for hand-relay if not.
4. Receiving thread dedups against existing corpus, writes files with relayer's IDs preserved (substring + word-overlap dedup), commits + pushes.

Pattern was used 4+ times today across at least 6 sibling threads. Corpus grew from 1 entry → 216 entries in ~3 hours via this loop. **This pattern is being formalized as Slice 2.5 — see §3 below.**

**Dogfood gate substantially satisfied earlier than expected.** v4 specified ~2 weeks of dogfood + 4 concrete metrics (invocations performed, candidates surfaced, promotions, demotions) before Slices 3A-6 ship. Day 1 of dogfood has produced:
- 216 memories across 5 domains (ken=128, cruising=25, sheep=17, romans=16, shared=16)
- Active recall traffic from at least this thread's verification queries
- 6+ sibling threads using `memory_ops.encode` in their work
- The persistence + privacy + cross-thread issues surfaced and fixed
- A meaningful corpus for the TF-IDF degenerate-at-n=1 case (resolved at n>5)

What's STILL not testable from this signal:
- Auto-promotion eligibility (Slice 7.5 requires `recall_count≥10` + `age≥30d` + `≥5 distinct sessions`; nothing in the corpus is even 1 day old)
- Consolidate cycle effects (confidence promotion, decay) — too early
- Whether the harness will use any of this for real session-start context

**Operator-found bugs encoded into the plan as work items:**
- `MEMORY_SESSION_ID` env var does NOT inherit across Python subprocess invocations. Recall bumps in step-2 verification all logged `session_id: "unknown"` because the env was set inside one `python3 -c` and not exported to subsequent calls. Slice 3A or a prerequisite micro-slice should ship a fix: export `MEMORY_SESSION_ID` from the harness, OR have `_current_session_id()` read from a session-state file the harness writes, OR have the cognitive-memory skill insert it in the bash command template.
- Cross-thread mining prompt's privacy paragraph references "PUBLIC domain repo" — outdated. Updated text lives in `e25c4814` for future relays to consult.

**New slice added: Slice 2.5 — formalized mining.** See §3.

### v4 → v5 (operating profile decision)

Operator confirmed they are the sole human with access to the household. Several v4 defenses were modeled against a multi-actor scenario (separate attacker coercing or impersonating operator; shared filesystem; UI fatigue under bulk-approval pressure). In a single-operator local-only environment these threats are non-applicable.

**v5 introduces two operating profiles via `MEMORY_LEARNING_PROFILE`:**

| Profile | Default? | Use case |
|---|---|---|
| `single-operator-local` | **YES (this household)** | One human + one or more AI agents; local-only storage; no shared filesystem |
| `multi-operator-shared` | available, opt-in | Team / enterprise / shared infrastructure |

The profile is read once at import time (mirrors `_learning_enabled`'s discipline). Future profiles can be added without breaking the API contract.

**Cross-slice invariant changes in `single-operator-local`:**

| Invariant | v4 (locked) | v5 single-operator |
|---|---|---|
| #1 Feature flag default OFF | all 8 sub-flags default off | only `MEMORY_LEARNING_PANIC_DISABLE_ALL` defaults off (panic must be opt-in). All other learning flags default **ON**. |
| #2 No auto-promotion to instinct, ever | locked | Auto-promotion permitted **only** when consensus criteria are cryptographically verifiable via `_assert_promotion_eligibility`. Single-id manual `promote_to_instinct` remains the default API; `auto_promote_eligible()` opt-in API for consensus-passing candidates. |

All other cross-slice invariants (3 through 10) unchanged.

**Threat reclassifications:**

| Threat | v4 status | v5 single-operator status |
|---|---|---|
| T11 Side-channel timing | out-of-scope (co-located trusted operators) | **non-applicable** (no observer exists) |
| T16 Social-engineering via familiarity crafting | mitigated by `_assert_human_attention` (blocking) | **relaxed** — no separate attacker to mimic operator. `_assert_human_attention` logs matched terms as INFO; does not block. |
| T17 Approval fatigue | mitigated by 3-candidate cap + 60s inter-promotion delay | **relaxed** — cap raised to 20, inter-promotion delay removed |
| T19 Local privilege escalation | out-of-scope (household OS trust) | **non-applicable** (single user OS) |
| T21 Operator coercion | out-of-scope | **non-applicable** (operator coercing themselves makes no sense) |

T13 (indirect influence post-promotion) **stays mitigated** — self-deception is still a real cognitive risk; `instinct_invocation_count` + 30-day audit surfacing remains.

T1, T2, T8, T9, T10, T14, T15, T18, T20, T22, T23 — **all unchanged**. The external-data contamination, agent-drift, mutation-prevention, and cryptographic layers are independent of operator count.

**Flag defaults in `single-operator-local`:**

| Flag | v4 default | v5 single-operator default |
|---|---|---|
| `MEMORY_LEARNING_ENABLED` | OFF | **ON** |
| `MEMORY_LEARNING_FROM_SESSIONS` | OFF | **ON** |
| `MEMORY_OBSERVATIONS_ENABLED` | OFF | **ON** |
| `MEMORY_AUTO_OBSERVE_ENABLED` (Slice 6 hooks) | OFF | **ON** (after Slice 3C ships) |
| `MEMORY_CONFIDENCE_PROMOTION_ENABLED` | OFF | **ON** |
| `MEMORY_USAGE_HISTORY_ENABLED` | OFF | **ON** |
| `MEMORY_AUTO_PROMOTE_ELIGIBLE` (NEW v5) | (didn't exist) | **ON** |
| `MEMORY_LEARNING_PANIC_DISABLE_ALL` | OFF | OFF (always opt-in) |

**New slice: 7.5 — Consensus auto-promotion eligibility.** Surfaces candidates that pass cryptographically verifiable consensus criteria as auto-promoted (with `is_auto_promoted: true` audit flag); rolls back via one-call `demote_from_instinct`. Detailed §3.

**New invariant: `_assert_promotion_eligibility`.** Cryptographically validates consensus criteria before any auto-promotion. Detailed §5.

**Friction reductions:**

| v4 friction | v5 single-operator |
|---|---|
| Manual extraction trigger | Session-end auto-extract via harness hook (Slice 7) |
| `_assert_human_attention` requires confirmation on autonomous-action keywords | Logs matched terms as INFO; does not block |
| Cap of 3 candidates per session | Cap at 20 |
| 60s inter-promotion delay | Removed |
| Per-id promotion calls only | `auto_promote_eligible()` opt-in for consensus-passing candidates; per-id still works |
| Manual observation log enabling | Default-on after Slice 3C ships |

**What still gates (non-negotiable in v5):**

- Cryptographic integrity layer (HMAC sidecar, helper integrity, key fingerprint) — defends against agent drift, not operator
- CI gate + meta-tests — defends against future commits weakening defenses
- Kill-switch (`_assert_panic_check` as first line) — defends against runaway bugs
- External-data wrapping (`<external-content>`) — defends against tool-output prompt injection
- Plan-injection mitigation — defends against agent self-modification
- TOCTOU snapshot + flock + WAL — defends against concurrent writes
- Rate limiting (now dynamic per Grok R3) — defends against DoS-style runaway
- Test-suite integrity (`test_regression_test_count`) — defends against accidental safety regression

### v3 → v4 (Round-3 mutation-prevention + open-question pass)

Four parallel reviews (GPT/challenge + Grok/challenge + Perplexity/research + You.com/research) tackled two questions: answer the 10 v3 open questions, and audit 10 specific mutation vectors (M1-M10) the design did not previously enumerate.

**Mutation-prevention coverage in v3 was bad.** 7 of 10 vectors had NO defense (per GPT analysis); Grok corroborated with the same count plus concrete fixes per vector. You.com's literature search returned the most honest signal: **for several of these vectors (M6 decorator escapes, M10 test skipping, M9 HMAC key swap), there is NO published vendor playbook**. We would be authoring novel defenses. Where published patterns exist (M1 reproducible builds + Sigstore, M2 Nitro eBPF tamper-evident logging CCS 2024, M3 Nono Merkle-tree agent audit 2026, M7 GitHub push-protection bypass controls, M2 Palo Alto Prisma AIRS external enforcement), v4 cites them. Where they don't, v4 marks the defense as novel and documented as such.

**Biggest structural change:**
- **New Slice 0.5: Mutation Defense Scaffolding** between Slice 0 (doctrine + invariants) and Slice 1 (kill-switch). Ships before any extraction code lands, so every subsequent slice operates inside a hardened envelope. Slice count: 9 → 10.

**6 new threats added (T18–T23):**
- T18 **Intent laundering** (Perplexity arXiv:2602.16729 2026) — agent reformulates requests in stylistically neutral phrasing, defeating name-based or semantic checks; 87% bypass rate published.
- T19 **Local privilege escalation** (Grok) — household OS compromise gives attacker direct `~/.memory/` access. Out-of-scope but documented; relies on household OS trust.
- T20 **Supply-chain via imports** (Grok) — imported module injects code that monkey-patches `_assert_*` helpers. Mitigated by Slice 0.5 `_validate_helper_integrity`.
- T21 **Operator coercion** (Grok) — social engineering of operator outside the design's reach. Acknowledged out-of-scope; doctrine + literacy.
- T22 **CI gate tampering** (GPT + Grok) — future commit weakens `test_every_mutation_path_invokes_invariants` itself. Slice 0.5 meta-test `test_ci_gate_immutability` hashes the gate's source.
- T23 **HMAC key replacement** (Grok — flagged as highest-impact mutation gap) — attacker swaps `~/.memory/_integrity.key`; integrity check still passes against forged data. Slice 0.5 `_validate_key_fingerprint` registers SHA256 of the key on first use and validates on every subsequent load.

**Highest-impact mutation gaps (convergent):**
- M2 monkey-patching (GPT's pick)
- M9 HMAC key swap (Grok's pick)
- Slice 0.5 addresses both. M2 via `_validate_helper_integrity` and `_seal_helpers`; M9 via `_validate_key_fingerprint`.

**3 new invariants in Slice 0.5 (10 total now, was 8):**
- `_validate_helper_integrity()` — SHA256 each `_assert_*` function's source at module-load time, store in module-level constant; re-validate before each call. Mitigates M2.
- `_validate_file_integrity(domain, memory_id)` — HMAC sidecar pattern; reads `~/.memory/<domain>/<id>.hmac` and validates against current file before any read. Mitigates M3.
- `_validate_key_fingerprint()` — store SHA256 of `~/.memory/_integrity.key` on first use in `~/.memory/_integrity.fingerprint`; validate on subsequent loads. Mitigates M9.

Also `_seal_helpers()` (utility, not assertion): called once at module load to mark `_assert_*` functions as final via a custom mechanism; rebinding raises at next invariant call. Mitigates M6.

**Tuning of existing v3 invariants (per Grok Part A):**
- `_assert_rate_limit`: fixed 60/min was arbitrary. v4 specifies dynamic threshold based on baseline 95th percentile + 20%, with explicit fallback to 60/min during first session (no baseline yet).
- `_assert_temporal_consistency`: v3 had 60s future / 1h past. v4 tightens to 5min/5min (NTP drift covers 5min future; backdating tolerance ≥5min was too generous).
- `_assert_panic_check` positioning: v3 said "first invariant call" but didn't enforce order. v4 adds AST rule requiring it as the FIRST executable statement of every public learning function.

**CI gate enhancements (per Grok Part B):**
- Scan extended to ALL `.py` files in project (not just `memory_ops.py`), looking for mutation patterns against `~/.memory/`. Mitigates M4 ("new file outside the gate's view").
- Detect `if not os.getenv('BYPASS'): _assert_*()` conditional weakening (was T15 partial-detection).
- Track allowlist changes in `ci_allowlist_history.json` sidecar; CI fails if `read_only_allowlist` grows without corresponding history entry. Mitigates M7.
- Detect `@pytest.mark.skip` and `if False:` patterns on safety-critical tests. Mitigates M10.

**New meta-test file `tests/test_meta_ci.py` (Slice 0.5):**
- `test_ci_gate_immutability` — SHA256 of CI gate test source matches hardcoded expected hash. Mitigates M1.
- `test_regression_test_count` — total test count >= 175 (v3 baseline); decreasing requires updated baseline in `test_count_history.json` with PR link. Mitigates M8.
- `test_monkey_patch_detection` — patches a helper at runtime, asserts `_validate_helper_integrity` raises.
- `test_direct_write_detection` — writes to a memory file without updating HMAC sidecar, asserts read fails.
- `test_key_replacement_detection` — swaps key file, asserts fingerprint check fails.
- `test_config_drift_detection` — modifies `.claude/settings.json` without manifest update, asserts startup warning.

**Convergent answers to v3 open questions (§9):**

| Q | GPT answer | Grok answer | v4 disposition |
|---|---|---|---|
| 1 (integrity strong enough?) | Asymmetric signing or separate volume | HSM/TPM ideal; write-once audit fallback | Documented as known limit; Slice 0.5's `_validate_key_fingerprint` is the household-grade defense |
| 2 (rate limit 60/min right?) | Dynamic + token bucket | Dynamic, 95th percentile + 20% | v4: dynamic threshold (Grok's specification) |
| 3 (temporal 60s/1h right?) | Configurable | Tighten to 5min/5min | v4: 5min/5min (Grok) |
| 4 (sequencing dependencies?) | Tradeoff accepted | Tight coupling — consider merging 3A/3B/3C | Kept split for review clarity; PR may bundle if scope small |
| 5 (9 slices scope creep?) | Possible — could merge | Yes — consolidate to 5-6 | v4 adds Slice 0.5 → 10 slices. Documented disagreement; choosing safety over consolidation |
| 6 (CI gate covers actual drift?) | No — extend for try/except | Misses conditional weakening + monkey-patch | v4: AST extensions + runtime tracer + meta-tests |
| 7 (panic-check positioning?) | First line | First line — enforce via AST | v4: AST rule requires panic-check first |
| 8 (threat model gaps?) | Insider threats, physical, supply chain | Privilege escalation, supply-chain imports, coercion | v4: T19, T20, T21 documented; T19/T21 out-of-scope |
| 9 ("1 sprint" measurable?) | Concrete metrics | "≥3 sessions × ≥2 weeks × ≥10 extractions" | v4: Grok's specification |
| 10 (helpers vs skills duplicate?) | Complement, no conflict | Complement, document mapping | v4: mapping table in doctrine doc |

### v2 → v3 (Round-2 red-team)

Four red-team analyses returned five new threats (T13–T17), one new invariant, and four corrections to existing v2 choices. The plan stays at 9 slices; v3 hardens what each slice ships.

**New threats added (T13–T17):**
- T13 **Indirect influence post-promotion** (GPT) — promoted instinct subtly biases future sessions; no audit/decay of instinct-driven actions
- T14 **SHA256 length-extension** (Perplexity 00f.net/2025, didof.dev) — raw SHA256 used as suffix MAC is vulnerable; switching to HMAC-SHA256
- T15 **AST-walk CI bypass via dynamic Python** (Perplexity cybersecify.com) — `getattr()`, late-binding decorators, `eval` defeat static AST checks; need runtime supplement
- T16 **Social-engineering via familiarity crafting** (Grok) — attacker mimics operator's own behavior patterns; single-id promotion provides no scrutiny by itself
- T17 **Approval fatigue** (Perplexity) — repeated single-id approvals ≈ bulk approval in practice

**Crypto correction (v2 → v3):**
- v2 specified raw SHA256 in `_assert_evidence_integrity`. v3 specifies HMAC-SHA256 with per-household key stored in `~/.memory/_integrity.key` (mode 0600, gitignored). Addresses T14.

**Concurrency correction (v2 → v3):**
- v2 specified `flock()` for observation log writes. v3 adds: if `flock` contention occurs ≥3 times per session, fall back to SQLite WAL-mode storage (`~/.memory/_observations.sqlite`) for that session. flock alone documented as insufficient for partial-write corruption (Perplexity).

**Asymmetric-integrity correction (v2 → v3):**
- Gemini caught: Slice 2 reads session state but doesn't call `_assert_evidence_integrity` — only Slice 3B+ does. v3 fix: Slice 2 also computes + validates a checksum on `orchestrator/state/<session_id>.json` before extraction. Same invariant, broader coverage.

**CI-gate correction (v2 → v3):**
- v2 specified pure AST walk. v3 supplements with: (a) AST walk MUST reject `try: _assert_*(): except: pass` patterns, (b) AST walk MUST detect `getattr(self, '_assert_*')` and `Call(Attribute(Name=...))` dynamic-dispatch shapes, (c) supplement with a runtime smoke test that calls each public function with a tracer that confirms `_assert_*` actually fired.

**New invariant `_assert_human_attention` (v3):**
- Pre-promotion anomaly heuristic. Flags candidate content matching autonomous-action keywords (`auto`, `every`, `daily`, `schedule`, `automatically`, `on its own`) and requires confirmation. Mitigates T16 by adding friction at the operator decision point. Returns a structured `{requires_confirmation: True, matched_terms: [...]}` rather than raising — promotion still possible but visibly distinct.

**Differential Memory Review (v3 ship-gate addition to Slice 2 + 3B):**
- Candidate output format now includes a `delta` field: what BEHAVIOR would change if this candidate is promoted. Operator reviews the change, not the ID. Mitigates T17.

**Test enhancement (v3 ship-gate addition to all slices):**
- Every adversarial probe now includes ≥1 "familiarity-crafted content" case — natural-language candidate that mimics legitimate behavior and contains no `<system-reminder>`-style syntax. Mitigates T16-style bypasses of T1-shaped tests.

### v1 → v2 (Round-1 review)

Round-1 review (3 models) surfaced 14 findings, 8 of which converged across ≥2 models. v2 incorporates all of them. Specifically:

**Sequencing change:** v1 was `0→2→4→5→3→6`. v2 is `0→1→2→3A→3B→3C→4→5→6` (9 slices, was 7). The new ordering:
- adds an explicit kill-switch slice (new Slice 1) before any extraction code
- splits old Slice 3 into 3A (log infrastructure) + 3B (extraction logic) — separate attack surfaces
- adds a log-integrity slice (new Slice 3C) with SHA256 checksums before downstream slices depend on logs
- moves observation log (3A/3B/3C) BEFORE confidence promotion (Slice 4) so flaws surface earlier

**New threat T8:** plan-injection (arXiv:2506.17318) — attacks targeting internal task representations rather than prompts. Distinct mitigation: candidate output never re-enters extraction agent's planning context.

**New invariants:** v1 shipped 4 in Slice 0. v2 ships 7:
- `_assert_evidence_integrity` (NEW, from Grok + Perplexity/Proof.com) — SHA256-validates evidence against stored checksums
- `_assert_rate_limit` (NEW, from Grok + Perplexity/Fast.io) — bounds extraction call frequency
- `_assert_temporal_consistency` (NEW, from Grok) — rejects backdated or future-dated timestamps
- existing 4 (no_silent_skip, evidence_present, single_id, safety_guard_compliant)

**New invariant-coverage test (CI gate):** `test_every_mutation_path_invokes_invariants` enumerates public APIs in `memory_ops.py` and fails if any lacks a documented invariant call. Mirrors `ai-regression-testing` Stage 4 discipline. Addresses the doctrine-drift concern that emerged as the single biggest behavioral risk (Grok + Perplexity/MIT/CDT both cited "safety drift" in long-running agent deployments).

**New ship-gate item across all slices:** performance benchmark under adversarial load. Particularly explicit for Slice 6 (it would have been an unsupported "5ms overhead" claim otherwise).

**New deferred-forever entries:** programmatic-disable-without-logging, raw observation data in `_observations/`, cross-session lock escalation.

---

## 1. Context (unchanged from v1)

The skill being lifted is ECC's `continuous-learning-v2` (MIT). Three foundational slices shipped:

| Slice | Surface | Test count |
|---|---|---|
| 1 | `MEMORY_LEARNING_ENABLED` flag (default OFF) + `extract_instinct_candidates()` + `promote_to_instinct()` + `demote_from_instinct()` | 24 new (73 total) |
| 1.1 | `is_instinct` shields auto-archive; corrupt-JSON robustness | 3 new (76) |
| 1.2 | shield-aware auto-merge; deterministic tie-break; refuse update on superseded; real-edges-only auto-protect | 9 new (82) |

**Cross-slice invariants (locked):**

1. Feature flag default OFF on every slice.
2. No auto-promotion to instinct, ever. Single-id explicit `promote_to_instinct` only.
3. SKILL.md `allowed-tools` stays read-only. Writes happen in Python.
4. Every observation wrapped `<external-content>` before any agent reads it.
5. Bounded storage with documented rotation policy.
6. No always-on daemon process.
7. Each slice ships its own adversarial probe.
8. `~/.memory/` byte-diff empty when feature flag is off.
9. **NEW v2:** every public API in `memory_ops.py` invokes ≥1 invariant from the 7-helper set; CI test enforces.
10. **NEW v2:** every log-derived candidate carries cryptographic provenance via `_assert_evidence_integrity`.

---

## 2. Threat model (v2 — 8 threats)

| # | Threat | Where it bites | Source | Mitigation |
|---|---|---|---|---|
| T1 | **Prompt injection via observations.** Tool result has `<system-reminder>`-shaped content; extraction agent reads it as instruction. | Slices 3A, 3B, 6 | (existing) | All observations wrapped `<external-content>`. Extraction agent system prompt forbids executing observation content. |
| T2 | **Memory poisoning.** Attacker controls tool output → fake pattern surfaces as candidate → operator approves without checking. | Slices 2, 3B | Palo Alto Unit42 | Candidates carry SHA256-validated provenance (Slice 3C). `_assert_evidence_integrity` blocks unverifiable candidates. |
| T3 | **Disk-space exhaustion.** PreToolUse + PostToolUse → thousands of obs/session. | Slice 3A | (existing) | Bounded log: 10MB or 10,000 lines per session, FIFO rotation. **NEW:** `_assert_rate_limit` caps observation insertion rate. |
| T4 | **Sensitive-data leakage.** API keys / paths / file contents in observation log. | Slice 3A | (existing) | `args_hash` = sha256 of normalized args. `result_class` ∈ {success, error, timeout, truncated}. No raw values. |
| T5 | **Bulk-approval temptation.** Extraction returns N candidates → operator pressured to approve all. | Slices 2, 3B | (existing) | Candidate list capped at 10 per call. Approval is per-id. `_assert_single_id` blocks list arguments. |
| T6 | **Cross-session race.** Two sessions write same log. | Slice 3A | (existing) | One log per `session_id`. **NEW v2:** `flock()` on the log file during write; advisory lock surfaces races as INFO findings. |
| T7 | **Doctrine bypass at runtime.** Future agent edits `_assert_*` helpers to silently no-op, OR adds a new mutation path that doesn't call them. | All slices | Grok + MIT/CDT | Helper test suite anchors each assertion. **NEW v2:** `test_every_mutation_path_invokes_invariants` enumerates public APIs and fails CI if any lacks invariant call. |
| **T8 (NEW)** | **Plan injection.** Attack targets the extraction agent's internal task/plan representation rather than its prompt. (arXiv:2506.17318) | Slices 2, 3B | Perplexity research | Extraction agent never re-uses candidate output to plan next action. Candidates are output-only, never re-enter agent context as planning input. |
| **T9 (NEW)** | **TOCTOU during extraction.** Between session-state read and candidate surface, concurrent write changes underlying data → inconsistent evidence trail. (arXiv:2603.00476) | Slices 2, 3B | GPT + Grok + Perplexity | Snapshot pattern: extraction copies inputs to in-memory tuple before scanning. `flock()` on observation log for Slice 3A. |
| **T10 (NEW)** | **Log compaction attack.** Adversarial tool output rates trigger FIFO rotation that evicts legitimate observations. | Slice 3A | Grok | Two-tier log: rotation evicts oldest 10% only; high-rate detection raises INFO finding instead of silent drop. |
| **T11 (NEW)** | **Side-channel timing.** `consolidate()` duration reveals which memories are shielded/promoted. | Slice 4 | GPT + Grok | Acknowledged limit — household threat model assumes co-located trusted operators. Documented as out-of-scope for v2 mitigation. Re-evaluate if model widens. |
| **T12 (NEW)** | **Temporal manipulation.** `usage_history` entries backdated or clock-skewed to game scoring. | Slice 5 | Grok | `_assert_temporal_consistency`: rejects entries with `at` > now + 60s or `at` < first observation in chain. |
| **T13 (v3)** | **Indirect influence post-promotion.** Promoted instinct biases future sessions; no audit / decay of instinct-driven actions. | Slices 1, 4, 5 | GPT red-team | `usage_history` (Slice 5) tracks recall counts of promoted instincts. Slice 4 `consolidate` reports `instinct_invocation_count` per pass. If an instinct is recalled >50× in 30 days without explicit `demote_from_instinct`, surface as INFO finding for operator review. |
| **T14 (v3)** | **SHA256 length-extension attack.** Raw SHA256 used as a suffix MAC permits forged appends. | Slice 3C | Perplexity (didof.dev 2025, 00f.net 2025) | Use **HMAC-SHA256** (not raw SHA256) with per-household key in `~/.memory/_integrity.key` (mode 0600). Documented as superseding raw SHA256 in `_assert_evidence_integrity`. |
| **T15 (v3)** | **AST-walk CI bypass.** Dynamic Python (`getattr`, decorators, `eval`) defeats `test_every_mutation_path_invokes_invariants`. | Slice 0 | Perplexity (cybersecify.com 2026) | AST walk extended to detect `getattr(self, '_assert_*')` and `try:.../except:pass` swallow patterns. Plus a runtime smoke test that calls each public function with a tracer that confirms `_assert_*` actually fires. |
| **T16 (v3)** | **Social-engineering via familiarity crafting.** Attacker mimics operator's own behavior patterns; single-id promotion provides zero scrutiny by itself. | Slices 1, 2, 3B | Grok red-team | New `_assert_human_attention` invariant flags candidate content matching autonomous-action keywords; surfaces a confirmation requirement (not a block). Differential-memory-review UI shows the behavioral delta of a promotion. |
| **T17 (v3)** | **Approval fatigue.** Repeated single-id approvals on visually similar candidates ≈ bulk approval in practice. | Slices 1, 2, 3B | Perplexity (atlan.com 2026) | Candidate list capped at 3 per session by default (was 10). Operator must wait ≥60s between promotion calls on candidates from the same extraction batch. Surfaces fatigue as a structured finding, not an obstacle. |
| **T18 (v4)** | **Intent laundering.** Agent reformulates requests in stylistically neutral phrasing to bypass name-based / semantic filters. Published 87% bypass rate. | Slices 2, 3B, 6 | Perplexity (arXiv:2602.16729 2026) | `_assert_human_attention` keyword list expanded with semantic equivalents (e.g., `regularly`, `routinely`, `as a matter of course`). Acknowledged: cannot fully mitigate at the heuristic level; documented as known limit. |
| **T19 (v4)** | **Local privilege escalation.** Household OS compromise gives attacker direct `~/.memory/` access, bypassing all API-level invariants. | All slices | Grok R3 | Out-of-scope for v4 mitigation. Household threat model assumes OS trust. Slice 0.5 `_validate_file_integrity` HMAC sidecar pattern detects post-compromise tampering but does not prevent it. |
| **T20 (v4)** | **Supply-chain via imports.** Third-party module imported into `memory_ops.py`'s namespace monkey-patches `_assert_*` helpers. | All slices | Grok R3 | Slice 0.5 `_validate_helper_integrity` (M2) catches post-import patching. `_seal_helpers` (M6) prevents symbol rebinding. |
| **T21 (v4)** | **Operator coercion.** Social engineering of the household operator outside the design's structural reach. | Slices 1, 2, 3B | Grok R3 | Out-of-scope. Doctrine + operator literacy. `_assert_human_attention` adds friction at the decision point but cannot stop a determined social-engineering attack. |
| **T22 (v4)** | **CI gate tampering.** Future commit weakens `test_every_mutation_path_invokes_invariants` (loosens AST check, adds allowlist entries, comments out assertions). | Slice 0 | GPT + Grok R3 (M1) | Slice 0.5 meta-test `test_ci_gate_immutability` hashes the gate's source code; any change requires updating the hash visibly in PR diff. Plus `ci_allowlist_history.json` sidecar tracks every allowlist addition with PR reference. |
| **T23 (v4)** | **HMAC key replacement.** Attacker swaps `~/.memory/_integrity.key`; integrity check still passes against forged data signed with the attacker's key. **Grok's highest-impact mutation gap.** | Slice 3C | Grok R3 (M9) | Slice 0.5 `_validate_key_fingerprint`: on first use, store SHA256 of the key file at `~/.memory/_integrity.fingerprint`; on every subsequent load, validate before use. Key rotation requires explicit fingerprint update — visible in operator command. Published literature (You.com R3, AWS KMS docs) confirms this is the strongest household-grade defense; HSM/TPM is the enterprise upgrade path. |

---

## 3. The nine slices

### Slice 0 — Doctrine document + invariants

**Goal:** Ship the inviolable doctrine document and 7 runtime invariant helpers BEFORE any auto-extraction code.

**Adds:**
- `orchestrator/CONTINUOUS_LEARNING_DOCTRINE.md` — plain-language statement of seven principles + worked anti-example per principle
- 7 `_assert_*` helpers in `memory_ops.py` (see §5)
- `CarefulNotCleverError` exception class
- `test_every_mutation_path_invokes_invariants` — CI gate (see §6)
- ≥14 tests for the helpers themselves (2 per helper minimum)

**Does NOT add:** any behavior change. Pure scaffold.

**Ship gate:**
- doctrine doc passes `like-a-human` + `voice-audit`
- ≥2 unit tests per invariant
- CI gate test passes against the existing memory_ops.py mutation surface (no false positives, no false negatives)
- existing 82 tests untouched
- new test count = ~100

**Effort:** ~1 session (was 0.5; added invariants + CI gate).

---

### Slice 0.5 — Mutation Defense Scaffolding (NEW in v4)

**Goal:** Harden the defense layer against its OWN mutation before any extraction code lands. Without this slice, every subsequent slice operates on a foundation that can be silently weakened (M1–M10).

**Adds:**
- `tests/test_meta_ci.py` — 6 meta-tests covering M1, M2, M3, M8, M9, M5:
  - `test_ci_gate_immutability` — SHA256 of `test_every_mutation_path_invokes_invariants` source matches hardcoded hash. PR that changes the gate updates the hash visibly in the diff. (M1, T22)
  - `test_regression_test_count` — total test count ≥ 175 (v3 baseline). Decreases require corresponding entry in `tests/test_count_history.json` with PR link. (M8)
  - `test_monkey_patch_detection` — replaces an `_assert_*` helper with a no-op at runtime, asserts `_validate_helper_integrity` raises on next invariant call. (M2)
  - `test_direct_write_detection` — writes to `~/.memory/<domain>/<id>.json` without updating sidecar HMAC, asserts read fails. (M3)
  - `test_key_replacement_detection` — replaces `~/.memory/_integrity.key`, asserts `_validate_key_fingerprint` raises. (M9, T23)
  - `test_config_drift_detection` — modifies `.claude/settings.json` without registering the new checksum, asserts `_audit_config_integrity` raises warning at startup. (M5)
- `memory_ops.py` additions:
  - `_validate_helper_integrity()` — at module load, computes SHA256 of `inspect.getsource()` for each `_assert_*` function; stores in `_HELPER_DIGESTS = {...}` module constant. Before each invariant call, re-validates. Mitigates M2 + T20.
  - `_validate_file_integrity(domain, memory_id)` — reads `~/.memory/<domain>/<id>.hmac` (HMAC-SHA256 of file contents under household key); validates before any read. Mitigates M3. Pattern from Grok R3.
  - `_validate_key_fingerprint()` — on first use, stores SHA256 of `~/.memory/_integrity.key` at `~/.memory/_integrity.fingerprint` (mode 0400, gitignored); validates before every use. Mitigates M9 + T23.
  - `_audit_config_integrity()` — checksums `.claude/settings.json` at startup against `~/.memory/_config.fingerprint`. Logs warning on mismatch; allows operator override with explicit `--accept-config-change` flag. Mitigates M5.
  - `_seal_helpers()` — utility called once at module load. Marks `_assert_*` functions as final via custom mechanism; rebinding raises `CarefulNotCleverError` on next invariant call via `_validate_helper_integrity`. Mitigates M6.
- CI configuration additions (in `.github/workflows/ci.yml` or equivalent):
  - Scan ALL `.py` files (not just `memory_ops.py`) for mutation patterns against `~/.memory/`. Fail if any file outside `memory_ops.py` contains direct path manipulation without invariant calls. Mitigates M4.
  - Reject PRs that add entries to `read_only_allowlist` without corresponding entries in `ci_allowlist_history.json`. Mitigates M7.
  - Reject `@pytest.mark.skip` or `if False:` guards on tests matching `test_*_invariant*` or `test_meta_ci_*` patterns. Mitigates M10.
  - AST extension to reject `if <condition>: _assert_*()` conditional-weakening patterns. (Round 3 Q6 enhancement)
  - AST extension to require `_assert_panic_check` as the FIRST executable statement of every public learning function. (Round 3 Q7 enhancement)

**Does NOT add:** any extraction behavior. Pure defense scaffolding.

**Threat surface:** the meta-defenses themselves can be mutated. Recursive defense is unbounded in theory; v4 stops at "defenses defending their defenses." Beyond that is process (human PR review).

**Published-pattern provenance** (so future reviewers know what's based on what):
| Defense | Published pattern | Source |
|---|---|---|
| `_validate_helper_integrity` | `safe_instantiate` allowlist pattern | Palo Alto Unit42 2026 (Hydra/NeMo RCE defenses) |
| `_validate_file_integrity` HMAC sidecar | Nono Merkle-tree agent audit | nono.sh 2026 |
| Sidecar allowlist history | GitHub push-protection bypass controls | github.blog 2024-10-23 |
| `test_ci_gate_immutability` hash check | Reproducible Builds + Sigstore | reproducible-builds.org, Red Hat 2024 |
| Configuration drift audit | Spacelift configuration-drift guidance | spacelift.io 2026 |
| **`_validate_key_fingerprint`** | **NONE published for HMAC keys** | Novel pattern; You.com R3 confirmed no published vendor playbook |
| **`_seal_helpers` final-rebinding** | **NONE published for AI safety** | Novel pattern; You.com R3 confirmed |
| **AST detection of test-skip on safety tests** | **NONE published** | Novel pattern; You.com R3 confirmed |

**Ship gate:**
- ≥6 meta-tests pass
- ≥4 unit tests per new `_validate_*` / `_seal_*` function
- Adversarial probe ≥12 cases:
  - Edit CI gate test → meta-test fails
  - Delete a regression test → `test_regression_test_count` fails
  - Monkey-patch `_assert_evidence_present` to no-op → next invariant call raises
  - Direct-write to `~/.memory/ken/abc.json` → read fails
  - Swap HMAC key → fingerprint check fails
  - Modify `.claude/settings.json` → startup warning
  - Add `memory_ops_v2.py` with mutation logic → CI scan fails
  - Add `read_only_allowlist` entry without history → CI fails
  - Decorate test with `@pytest.mark.skip` → CI fails
  - Add `if BYPASS: _assert_panic_check()` → AST detection fails
  - Place `_assert_panic_check` as 5th line of a public function → AST order check fails
  - Trigger `_seal_helpers` violation → next call raises
- New test count after slice: ~115 (Slice 0 ~100 + 15 from 0.5)

**Effort:** ~2 sessions (largest non-shipping slice; pure defense work).

**Honest limit:** Slice 0.5 cannot prevent OS-level privilege escalation (T19), supply-chain compromise of Python itself (T20 lower bound), or operator coercion (T21). What it prevents is **silent weakening of the defense layer over time**. The household threat model assumes the OS, Python interpreter, and operator are trustworthy; this slice protects against the doctrine itself drifting under that assumption.

---

### Slice 1 — Kill-switch (NEW in v2)

**Goal:** Single env var that halts all learning operations immediately. Emergency stop before extraction code lands.

**Adds:**
- `MEMORY_LEARNING_PANIC_DISABLE_ALL` env var; takes precedence over every other learning flag
- `_assert_panic_check()` invariant called at entry of every public learning API
- Refuses to acknowledge via memory writes (the panic state is read-only from memory_ops' perspective)
- ≥6 tests: panic off = normal, panic on = halts every API, panic mid-operation (set after extraction starts) still allows in-flight to finish but blocks next call, panic value case-insensitive, panic value typos (yes/1/on) treated as off (safety property mirroring Slice 1's `_learning_enabled`)
- ≥6 adversarial probes: rapid toggle, unset mid-extraction, missing env entirely, conflicting flag combinations

**Why this slice exists at this position:** every subsequent slice's first invariant call must be `_assert_panic_check`. Without it, a future bug could continue learning operations during a declared emergency. Mirrors safety-guard discipline at runtime.

**Effort:** ~0.5 session.

---

### Slice 2 — Pull-based session extraction (no hooks)

**Goal:** Operator manually triggers extraction at session end. Reads from existing orchestrator state files. Lowest-attack-surface extraction slice.

**Adds:**
- `extract_candidates_from_session(session_id, dry_run=True)` in `memory_ops.py`
- Returns `{"enabled": bool, "session_id": ..., "candidates": [...], "evidence": {...}}`
- New flag `MEMORY_LEARNING_FROM_SESSIONS=true`
- **NEW v2:** snapshot pattern — read session state into immutable tuple before scanning (mitigates T9 TOCTOU)

**Invariant calls (order matters):**
1. `_assert_panic_check` (Slice 1)
2. `_assert_rate_limit` (Slice 0) — caps extract calls per minute per session
3. `_assert_evidence_present` on each candidate before surfacing
4. `_assert_no_silent_skip` if any session_id was skipped (read failure, malformed JSON)

**Threat surface:** reads orchestrator state. T2 + T9 relevant.

**Ship gate:**
- ≥10 tests (was 8): flag-off no-op, panic-on no-op, candidates emit from synthetic state, provenance includes session_id + observation_count + supporting_observation_ids, dry_run prevents writes, `_assert_evidence_present` blocks bare-pattern, `_assert_rate_limit` blocks over-frequent calls
- Adversarial probe ≥12 cases (was 10): malformed state, path traversal in session_id, empty state, prompt-injection in tool args, oversized state, **plan-injection in tool args (NEW)**, **TOCTOU mid-extraction (NEW — write to file mid-call)**, **rate-limit burst (NEW)**
- `~/.memory/` byte-diff empty when flag off
- New total: ~115 tests

**Effort:** ~1.5 sessions (was 1; added TOCTOU snapshot + rate-limit + plan-injection probes).

---

### Slice 2.5 — Formalized transcript mining (NEW in v6)

**Goal:** Convert the cross-thread mining pattern (emergent on 2026-05-13, used 4+ times across sibling threads) into stable callable surface. Today it's ad-hoc Python in each session; this slice gives it a stable function + relay protocol + dedup discipline.

**Adds:**
- `memory_ops.mine_transcripts(transcript_glob=None, dry_run=True, source_tag=None)` — pure Python function. Reads `*.jsonl` files from `/root/.claude/projects/-home-user/` (default) or operator-supplied path. Extracts unique user-message text (≥30 chars, ≤500 chars; skip auto-resume preambles + system-reminders). Returns candidate dicts with `{content, timestamp, session_id, source}`. Does NOT auto-encode — read-only by default.
- `memory_ops.ingest_relayed_memories(json_list, dedup=True)` — accepts list of complete memory dicts (with IDs already set per the relay protocol). Dedups against `MEMORY_ROOT` corpus. Writes net-new entries with relayer's IDs preserved (no re-encoding). Returns `(written_ids, skipped_with_reasons)`.
- `memory_ops._dedup_against_corpus(content, domain, tags)` — internal helper. Substring head-match (first 200 chars in either direction) + word-overlap > 65% within same-domain + tag-overlap > 60% as soft signal. Returns `(dup_id, reason)` or `(None, None)`.

**Invariant calls (order matters per Slice 1 AST rule):**
1. `_assert_panic_check`
2. `_assert_rate_limit("mine_transcripts", "default")` — bounds mining frequency
3. Per candidate: `_assert_evidence_present` (transcript-path + line-number constitute the evidence trail)
4. `_assert_no_silent_skip` if any parse failures dropped content
5. For `ingest_relayed_memories`: also `_assert_temporal_consistency` on the `created` field

**Threat surface:** lower than Slice 2 because read-only by default (`dry_run=True`). Ingestion writes are gated by dedup; the path-traversal hardening from Slice 2 applies to the transcript path lookup.

**Ship gate:**
- ≥8 tests: mine returns candidates from synthetic transcript, dedup catches duplicates, ingest preserves relayer IDs, ingest skips on dup, panic halts both
- ≥6 adversarial probes: malformed jsonl line in transcript, oversized content (>10MB single message), prompt-injection-shaped content, path traversal in transcript_glob, ID collision in relay, missing required field in relayed dict
- Documented in plan; cross-thread mining prompt simplified to "run `memory_ops.mine_transcripts(); memory_ops.ingest_relayed_memories(candidates)`"

**Effort:** ~1 session. Folds the current ad-hoc patterns into stable callable surface; doesn't change what the system does, just how reliably it can be invoked.

**Why this slice now (was missing from v5):** the cross-thread mining pattern is what's been growing the corpus. Without formalization, every thread reinvents the dedup + parse logic, with different rigor each time. Formalizing eliminates that drift and makes the operation cheap enough that future threads call it as a standard session-start operation.

---

### Slice 3A — Observation log infrastructure (split from old Slice 3)

**Goal:** OPTIONAL append-only observation log. Operator opts in per session.

**Adds:**
- `~/.memory/_observations/<session_id>.jsonl` (gitignored)
- `record_observation(tool, args_hash, result_class, session_id)` writes one line
- `clear_observations(session_id)` explicit cleanup
- Bounded: 10MB or 10,000 lines per session
- **NEW v2:** two-tier rotation — at cap, evict oldest 10% (not whole-file truncate) AND raise INFO finding via `_assert_no_silent_skip`
- **NEW v2:** `flock()` on the log file during write (mitigates T6 + T9)
- New flag `MEMORY_OBSERVATIONS_ENABLED=true`

**Invariant calls:**
1. `_assert_panic_check`
2. `_assert_rate_limit` — caps observation rate (mitigates T10 log compaction attack)
3. `_assert_temporal_consistency` on each observation timestamp
4. `_assert_no_silent_skip` if rotation evicted anything

**Does NOT add:** extraction. That's Slice 3B. Does NOT add: integrity checksums. That's Slice 3C. Hook integration is Slice 6.

**Threat surface:** new disk surface (T3, T4, T6, T10).

**Ship gate:**
- ≥12 tests: log appends bounded, rotation evicts 10% not full-truncate, args_hash deterministic, no raw values in log, structured rotation report, flock acquired during write, `_assert_rate_limit` blocks burst, `_assert_temporal_consistency` blocks future-dated entries, panic halts writes
- Adversarial probe ≥14 cases: path traversal in session_id, oversized args, prompt-injection in args, single-process concurrent writes (simulated), missing session_id, **compaction-attack burst (NEW — 100k records as fast as possible)**, **flock contention (NEW)**, **clock-skewed timestamps (NEW — backdated + future-dated)**, **panic-during-write (NEW)**
- Manual review: no raw tool arg content in `_observations/`
- New total: ~127 tests

**Effort:** ~1.5 sessions.

---

### Slice 3B — Observation extraction (split from old Slice 3)

**Goal:** Read Slice 3A's log and surface candidates.

**Adds:**
- `extract_candidates_from_observations(session_id)` — reads log, clusters, returns candidates
- Same return shape as Slice 2

**Invariant calls:**
1. `_assert_panic_check`
2. `_assert_rate_limit`
3. `_assert_evidence_present` per candidate
4. `_assert_evidence_integrity` per candidate (after Slice 3C ships — pre-3C, this is a stub that always passes)
5. `_assert_no_silent_skip`

**Threat surface:** T1, T2, T8 (plan injection), T9 (TOCTOU).

**Ship gate:**
- ≥8 tests: candidates extracted, clustering deterministic, evidence carries observation ids, panic halts extraction
- Adversarial probe ≥10 cases: malformed log lines, empty log, log with prompt-injection content, log with plan-injection-shaped content, log written-to during extraction (TOCTOU)
- New total: ~137 tests

**Effort:** ~1 session.

---

### Slice 3C — Log integrity (NEW in v2 from Grok + Perplexity/Proof.com)

**Goal:** SHA256 cryptographic provenance for observation logs. Without this, candidate "evidence" is just claimed; attackers controlling tool output can fabricate consistent-looking provenance.

**Adds:**
- `~/.memory/_checksums/<session_id>.txt` — running SHA256 of the observation log
- `compute_log_checksum(session_id)` — called on every observation write
- `validate_log_checksum(session_id)` — called by `_assert_evidence_integrity`
- `_assert_evidence_integrity` (the Slice 0 stub becomes real here)

**Invariant calls:**
1. `_assert_panic_check`
2. Wraps the Slice 3B path; every candidate's evidence runs through `_assert_evidence_integrity` before surface

**Threat surface:** T2 (fabricated evidence) mitigation. New attack surface: the checksum file itself can be tampered with, but tampering visibly invalidates downstream candidates rather than producing false positives.

**Ship gate:**
- ≥8 tests: checksum updates on each write, matches expected hash, mismatch detected, missing checksum treated as integrity failure (not bypass), `_assert_evidence_integrity` raises on mismatch
- Adversarial probe ≥8 cases: checksum file deleted, checksum file truncated, checksum file replaced with valid-looking-but-wrong hash, log file edited without checksum update, concurrent write race during checksum recompute
- New total: ~145 tests

**Effort:** ~1 session.

---

### Slice 4 — Confidence-promotion rules (NOT instinct-promotion)

**Goal:** Frequently-recalled memories get a confidence bump, not just decay.

**Adds:**
- New rule in `consolidate()`: if `recall_count >= 5` AND most-recent recall within 14 days, bump `confidence` by +0.05 (cap 1.0)
- Counter `actions["confidence_promoted"]`
- New flag `MEMORY_CONFIDENCE_PROMOTION_ENABLED=true`

**Invariant calls:**
1. `_assert_panic_check`
2. `_assert_no_silent_skip` if qualifying memory was missed

**Does NOT add:** auto-promotion to instinct. High-confidence memory still requires explicit `promote_to_instinct`.

**Threat surface:** changes consolidate's automatic behavior. T11 (timing side-channel) acknowledged but out-of-scope.

**Ship gate:**
- ≥8 tests (was 6): bump under criteria, doesn't fire if stale, capped at 1.0, instincts unaffected, boundary at recall_count==5 and 14-day cutoff, panic halts consolidate
- Adversarial probe ≥10 cases: bump + decay same pass, bump on just-decayed, bump on protected, bump on superseded, **rapid-fire recalls within seconds (NEW — confirms bump fires once per consolidate pass not per recall)**, **clock-skewed last_recalled (NEW)**
- New total: ~155 tests

**Effort:** ~1 session.

---

### Slice 5 — Cross-session usage tracking

**Goal:** Per-memory recall history with timestamps. Stronger signal than single `last_recalled`.

**Adds:**
- Field `usage_history: [{"at": iso_ts, "session_id": ...}, ...]` on each memory
- Capped at last 20 entries
- `recall()` appends an entry when it bumps `recall_count`
- Slices 2, 3B use `usage_history` for richer scoring

**Invariant calls:**
1. `_assert_panic_check`
2. `_assert_temporal_consistency` on each new entry — rejects backdated (>1 hour past current `at`s) and future-dated entries
3. `_assert_evidence_present` on each entry (must have `at` AND `session_id`)

**Does NOT add:** what query recalled the memory (privacy — queries can contain sensitive prose).

**Backwards compat:** legacy memories without `usage_history` — field initialized on first bump.

**Ship gate:**
- ≥8 tests (was 6): history appended, cap enforced at 20, legacy memories handled, `_assert_evidence_present` blocks malformed, `_assert_temporal_consistency` blocks backdated, `_assert_temporal_consistency` blocks future-dated
- Adversarial probe ≥8 cases: rapid-fire recalls, corrupted field, missing field, cap overflow, **clock-jumped backward (NEW — mitigation T12)**, **clock-jumped forward (NEW)**, **session_id collision (NEW — same id twice)**
- New total: ~163 tests

**Effort:** ~1 session.

---

### Slice 6 — Always-on capture (ECC-shaped; default-on in single-operator profile)

**Goal:** Wire PreToolUse / PostToolUse hooks into Slice 3A's `record_observation`. Highest-leverage AND highest-attack-surface slice.

**Adds:**
- `.claude/hooks/observe-tool-use.sh` — hook script calling `record_observation()`
- Documentation for manual opt-in
- New flag `MEMORY_AUTO_OBSERVE_ENABLED=true` + explicit registration in `.claude/settings.json`

**Invariant calls:** every observation routes through Slice 3A's invariants. Hook itself does no validation beyond panic-check.

**Prerequisites:** Slices 2, 3A, 3B, 3C, 4, 5 all shipped AND adopted in practice for ≥1 full sprint.

**Threat surface:** every tool call writes to disk. Highest in plan.

**Ship gate:**
- Hook script passes `harness-auditor` Stage 3
- `security-scan` (AgentShield) audit passes
- Hook fails closed (any exception → continue tool call, log to stderr)
- **NEW v2:** performance benchmark explicit — <5ms overhead per tool call measured against a stress harness that emits 1000+ tool calls in 10 seconds. The harness is part of the slice, not asserted from theory.
- ≥12 hook-specific tests covering exception isolation, log overflow, missing python, panic-on-during-tool-call
- Explicit user approval to enable always-on capture in their household
- New total: ~175 tests

**Effort:** ~2 sessions + household-wide rollout review.

---

## 4. The doctrine — 7-skill integrity stack (unchanged from v1)

`careful-not-clever` is the keystone. Complete stack:

| Skill | Failure mode | Where it fires |
|---|---|---|
| `careful-not-clever` | Clever shortcuts during authoring | Every edit to `memory_ops.py` or extraction code |
| `safety-guard` | Destructive autonomous runtime ops | Every mutation entry point |
| `verification-before-completion` | False completion claims | Ship gate of every slice |
| `systematic-debugging` | Shallow fixes | When edge-probe finds gap |
| `security-review` | New attack surface unaudited | Slices 3A, 3C, 6 |
| `simplify` | Clever code surviving review | Final pre-merge review |
| `requesting-code-review` | Insufficient pre-merge adversarial review | Every ship gate |

Plus the process skills at transitions (brainstorming, writing-plans, executing-plans, session-checkpoint, finishing-a-development-branch) and slice-specific tools (security-scan + update-config for Slice 6; like-a-human + voice-audit for Slice 0 doc).

---

### Slice 7 — Session-end auto-extract (v5)

**Goal:** Wire the harness's existing session-end hook to invoke extraction without manual operator trigger. From operator perspective: candidates surface at session boundary. From architecture perspective: no Python daemon — uses an existing harness affordance, not a new always-on process.

**Adds:**
- `.claude/hooks/session-end-extract.sh` — calls `extract_candidates_from_session()` and `extract_candidates_from_observations()` (if Slice 3B shipped)
- Output written to `~/.memory/_candidates/<session_id>.json` for next-session pickup
- `MEMORY_AUTO_EXTRACT_ENABLED=true` flag (default-on in `single-operator-local`)

**Invariant calls (in order):**
1. `_assert_panic_check`
2. `_assert_rate_limit` (session-id key, dynamic threshold)
3. `_assert_evidence_integrity` per candidate
4. `_assert_no_silent_skip` if any extraction call failed

**Threat surface:** harness hook execution. Fails closed.

**Ship gate:**
- ≥6 tests: hook runs at session-end, candidates written to expected path, panic halts hook, rate-limit honored, integrity validated
- Adversarial probe ≥6 cases: hook fails mid-extraction, panic flips during hook, session-id collision, oversized candidate set
- New total: ~150 tests

**Effort:** ~1 session.

---

### Slice 7.5 — Consensus auto-promotion eligibility (v5, NEW)

**Goal:** Surface candidates that pass cryptographically verifiable consensus criteria as auto-promoted, with full audit trail and one-call rollback. Operator review becomes "demote any of these 5?" instead of "promote each of these 5?" — zero-friction discovery for the routine case; manual path preserved for unusual candidates.

**Adds:**
- `auto_promote_eligible(domain=None)` in `memory_ops.py`. Runs `_assert_promotion_eligibility` on each candidate; for passes, calls `promote_to_instinct` with `is_auto_promoted: true` + `auto_promoted_at: <iso>` flags set.
- `recommended_for_promotion` queue surfaced at session start: list of candidates that passed consensus
- One-call rollback: `demote_from_instinct(id)` works exactly as before; `auto_promoted_at` is preserved for audit even after demotion (becomes `auto_promoted_at` + `demoted_at` both set)
- New invariant `_assert_promotion_eligibility(candidate)` — see §5

**Consensus criteria (all cryptographically verifiable via the existing integrity layer):**
- `recall_count >= 10` across `>= 30 days` (validated via `usage_history` chain HMAC)
- No `demoted_at` in history
- `confidence >= 0.9`
- Appears in `usage_history` across `>= 5 distinct sessions`
- `_assert_evidence_integrity` passes for the candidate's evidence trail
- `_assert_helper_integrity` passes (no monkey-patched invariants in this process)

If ANY criterion fails → surfaced for manual review per Slice 2/3B path.
If ALL pass → auto-promoted with audit metadata.

**Invariant calls (in order, per auto-promotion):**
1. `_assert_panic_check`
2. `_assert_rate_limit` (per-domain key)
3. `_assert_promotion_eligibility` (NEW v5)
4. `_assert_helper_integrity` (mutation defense from Slice 0.5)
5. `_assert_evidence_integrity` (Slice 3C)
6. `_assert_safety_guard_compliant("promote", candidate)` (single-id surface preserved)

**Single-id surface preserved:** `auto_promote_eligible` iterates candidates one at a time, calling `promote_to_instinct(candidate_id)` for each. `_assert_single_id` still fires per call. No batch API; the iteration just happens automatically. Structurally identical to manual promotion of N candidates one-at-a-time.

**Threat surface:** auto-promotion is the kill-chain endpoint Round 2 red-team flagged. In multi-operator profile this is forbidden. In single-operator profile, the kill chain requires an attacker to construct candidate content that mimics operator habits AND survives 30 days of usage history with HMAC integrity AND never gets demoted. The single-operator profile assumes no separate attacker, so the chain has no entry point. If the threat model widens (additional users added, network exposure introduced), profile switches to `multi-operator-shared` and auto-promotion reverts to forbidden.

**Ship gate:**
- ≥10 tests: criteria all pass → auto-promoted, any criterion fails → manual queue, `_assert_promotion_eligibility` blocks unverifiable consensus, `is_auto_promoted` flag set, `auto_promoted_at` timestamp set, rollback preserves audit
- Adversarial probe ≥12 cases: forge consensus signal (recall_count manipulation) → blocked by HMAC, candidate with fake usage_history → blocked, candidate from poisoned observation log → blocked, monkey-patched eligibility check → fails via Slice 0.5 helper-integrity, panic during auto-promote loop
- New total: ~165 tests

**Profile behavior:**
- `single-operator-local`: `MEMORY_AUTO_PROMOTE_ELIGIBLE=true` default. Auto-promotion active.
- `multi-operator-shared`: `MEMORY_AUTO_PROMOTE_ELIGIBLE=false` permanently. Calling `auto_promote_eligible()` returns `{"enabled": False, "reason": "multi-operator-shared profile forbids auto-promotion"}`.

**Effort:** ~1.5 sessions.

---

## 5. Invariant helpers — 7 in v2 (was 4); 11 in v4; **12 in v5**

```python
class CarefulNotCleverError(Exception):
    """Doctrine violation. NOT a bug to retry — discipline boundary crossed.
    Surface to operator; do not silently retry or downgrade."""

def _assert_panic_check() -> None:
    """Slice 1 invariant: refuse to proceed if MEMORY_LEARNING_PANIC_DISABLE_ALL
    is set. Takes precedence over every other flag."""
    if os.environ.get("MEMORY_LEARNING_PANIC_DISABLE_ALL", "").lower() == "true":
        raise CarefulNotCleverError(
            "panic disable active — all learning operations halted"
        )

def _assert_no_silent_skip(reason: str, count: int) -> None:
    """Existing: refuse to silently skip > 0 items."""
    if count > 0:
        raise CarefulNotCleverError(
            f"silent skip of {count} items: {reason}. Surface as INFO, not drop."
        )

def _assert_evidence_present(candidate: dict) -> None:
    """Existing: every candidate must carry observations + session_ids."""
    if not candidate.get("evidence", {}).get("observations"):
        raise CarefulNotCleverError(
            f"candidate {candidate.get('id', '?')} has no evidence trail"
        )

def _assert_single_id(arg) -> None:
    """Existing: refuse list arguments where API contract is single-id."""
    if isinstance(arg, (list, tuple, set)):
        raise CarefulNotCleverError(
            f"single-id API received {type(arg).__name__}; bulk forbidden"
        )

def _assert_safety_guard_compliant(operation: str, target: dict) -> None:
    """Existing: destructive operations on shielded targets require force=True."""
    if operation in ("delete", "forget", "demote") and target.get("is_instinct"):
        raise CarefulNotCleverError(
            f"{operation} on instinct requires explicit force=True"
        )

def _assert_evidence_integrity(candidate: dict) -> None:
    """v3: HMAC-SHA256-validate each observation in the candidate's evidence
    against a checksum recorded in ~/.memory/_checksums/<session_id>.txt at
    observation time. Mitigates T2 (fabricated evidence) and T14 (length-
    extension on raw SHA256). The HMAC key is per-household at
    ~/.memory/_integrity.key (mode 0600, gitignored)."""
    import hmac, hashlib
    key = _load_integrity_key()  # bytes; created on first use
    for obs_ref in candidate.get("evidence", {}).get("observations", []):
        expected = hmac.new(key, obs_ref["line"].encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, obs_ref["line_hmac"]):
            raise CarefulNotCleverError(
                f"evidence integrity failure: obs {obs_ref['session_id']} HMAC mismatch"
            )

def _assert_human_attention(candidate: dict) -> dict:
    """v5 (profile-aware): pre-promotion anomaly heuristic.

    Behavior depends on MEMORY_LEARNING_PROFILE:
      - 'multi-operator-shared': blocks promotion if autonomous-action
        keyword matches; caller must pass confirm=True to proceed.
        Mitigates T16 (familiarity crafting) + T17 (approval fatigue).
      - 'single-operator-local' (default): no separate attacker exists.
        Logs matched terms as INFO finding via the structured response;
        promotion proceeds. Useful for self-audit ("I keep promoting
        autonomous-action candidates — is that intentional?") but not
        a blocking gate.

    Returns:
      {"matched_terms": [...], "blocking": bool} — blocking only true
      in multi-operator-shared profile.
    """
    AUTONOMOUS_KEYWORDS = [
        "auto", "every", "daily", "schedule", "automatically",
        "on its own", "without asking", "in the background",
        "regularly", "routinely", "as a matter of course",  # T18 intent-laundering
    ]
    content = candidate.get("content", "").lower()
    matched = [k for k in AUTONOMOUS_KEYWORDS if k in content]
    profile = os.environ.get("MEMORY_LEARNING_PROFILE", "single-operator-local")
    blocking = bool(matched) and profile == "multi-operator-shared"
    return {"matched_terms": matched, "blocking": blocking}

def _assert_promotion_eligibility(candidate: dict) -> None:
    """v5 (NEW): cryptographically validate consensus criteria before
    auto-promotion. Raises CarefulNotCleverError if ANY criterion fails;
    auto_promote_eligible() catches and routes the candidate to manual
    review instead of auto-promoting. Manual promote_to_instinct() does
    NOT call this — manual promotion is the operator's explicit choice
    regardless of consensus.

    All criteria must be cryptographically verifiable:
      - recall_count >= 10 across >= 30 days
      - confidence >= 0.9
      - >= 5 distinct sessions in usage_history (HMAC-validated chain)
      - No demoted_at in history
      - _assert_evidence_integrity passes
      - _assert_helper_integrity passes
    """
    now = time.time()
    if candidate.get("recall_count", 0) < 10:
        raise CarefulNotCleverError(
            f"eligibility: recall_count {candidate.get('recall_count', 0)} < 10"
        )
    created_age_days = (now - _parse_ts(candidate.get("created", _now()))) / 86400
    if created_age_days < 30:
        raise CarefulNotCleverError(
            f"eligibility: age {created_age_days:.1f}d < 30d minimum"
        )
    if candidate.get("confidence", 0) < 0.9:
        raise CarefulNotCleverError(
            f"eligibility: confidence {candidate.get('confidence', 0)} < 0.9"
        )
    history = candidate.get("usage_history", [])
    distinct_sessions = {h["session_id"] for h in history if "session_id" in h}
    if len(distinct_sessions) < 5:
        raise CarefulNotCleverError(
            f"eligibility: {len(distinct_sessions)} distinct sessions < 5"
        )
    if candidate.get("demoted_at"):
        raise CarefulNotCleverError(
            "eligibility: previously demoted — auto-promotion forbidden"
        )
    _assert_evidence_integrity(candidate)
    _validate_helper_integrity()  # from Slice 0.5
    # All checks passed; caller may proceed with auto-promotion.

def _assert_rate_limit(operation: str, key: str) -> None:
    """v4 (tuned): dynamic threshold based on historical 95th percentile + 20%
    (per Grok R3). Falls back to 60/min during the first session before
    baseline exists. Mitigates DoS via repeated extraction and observation
    flooding."""
    now = time.time()
    bucket = _rate_buckets.setdefault((operation, key), [])
    bucket[:] = [t for t in bucket if now - t < 60]
    threshold = _dynamic_threshold(operation, key)  # 95th %ile + 20% or 60
    if len(bucket) >= threshold:
        raise CarefulNotCleverError(
            f"rate limit: {operation} for {key} exceeded {threshold}/min "
            f"(dynamic threshold; baseline {_baseline_for(operation, key)})"
        )
    bucket.append(now)

def _assert_temporal_consistency(ts: str, chain: list = None) -> None:
    """v4 (tuned): reject timestamps more than 5 minutes in the future or
    out-of-order by more than 5 minutes against prior entries in chain.
    Tightened from v3's 60s/1h per Grok R3: NTP drift exceeds 60s on consumer
    hardware (false positives); 1h past was too generous (allowed mid-session
    replay attacks)."""
    now = time.time()
    try:
        ts_epoch = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        raise CarefulNotCleverError(f"temporal consistency: unparseable {ts!r}")
    if ts_epoch > now + 300:  # 5 min future
        raise CarefulNotCleverError(f"temporal consistency: {ts} is future-dated")
    if chain:
        last = max(_parse_ts(e["at"]) for e in chain if "at" in e)
        if ts_epoch < last - 300:  # 5 min past
            raise CarefulNotCleverError(
                f"temporal consistency: {ts} backdated >5min from chain head"
            )
```

**Key property (carries through from v1):** invariants have NO opt-out parameter. A future PR that wraps a single id in `[x]` to bypass `_assert_single_id` would have to disclose the workaround in PR text, which the next reviewer sees.

---

## 6. The CI gate: `test_every_mutation_path_invokes_invariants` (v3 hardened)

**Background:** Round-1 review identified doctrine drift as the single biggest behavioral risk (Grok + Perplexity citing MIT/CDT). The doctrine document + invariant helpers are insufficient on their own — a future agent can add a new mutation path that simply doesn't call any invariant. The skill won't catch this; the doctrine document won't catch this. Only a test can.

**Mechanics:**

```python
def test_every_mutation_path_invokes_invariants():
    """Doctrine drift defense: every public function in memory_ops.py
    that mutates state must contain at least one _assert_* call in
    its body. Pure read functions are exempted by an allowlist.

    Implementation: AST-walks memory_ops.py, identifies all public
    functions (no leading underscore), filters out the explicit
    read-only allowlist, then for each remaining function checks
    that at least one Call node references a name starting with
    '_assert_'.
    """
    import ast
    src = Path("memory_ops.py").read_text()
    tree = ast.parse(src)
    read_only_allowlist = {
        "recall", "extract", "tree", "stats", "neighbors",
        "extract_instinct_candidates",
        # NOTE: every addition to this list is itself a doctrine decision;
        # PR reviewers must approve each addition explicitly.
    }
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            if node.name in read_only_allowlist:
                continue
            calls = [c for c in ast.walk(node)
                     if isinstance(c, ast.Call)
                     and isinstance(c.func, ast.Name)
                     and c.func.id.startswith("_assert_")]
            if not calls:
                missing.append(node.name)
    assert not missing, (
        f"DOCTRINE DRIFT: public mutation functions without invariant calls: "
        f"{missing}. Either call ≥1 _assert_* or add to read_only_allowlist "
        f"(and explain why in PR text)."
    )
```

This test is part of Slice 0's ship gate and stays green across every subsequent slice. The allowlist mechanism makes intentional exemptions visible.

**v3 hardening (T15 mitigation):** the AST walk additionally rejects:

1. **Swallow patterns** — any `try` block that contains an `_assert_*` call AND a bare `except:` or `except CarefulNotCleverError: pass`. These look like compliance but neutralize the assertion.
2. **Dynamic dispatch patterns** — `getattr(<x>, '_assert_<name>')(...)` or `Call(Attribute(Name('self'), '_assert_*'))(...)` shapes. These bypass static AST detection by computing the function name at runtime.
3. **Decorator escapes** — any decorator on a public function whose name is not in an allowlist of known-safe decorators (`functools.wraps`, `staticmethod`, `classmethod`, `dataclass`). New decorators require explicit allowlist addition in PR text.

**Runtime supplement:** Slice 0 also ships a `test_invariants_actually_fire_at_runtime` test. It monkey-patches each `_assert_*` helper to record calls in a global list, then invokes every public function in `memory_ops.py` with synthetic safe inputs. After the call, the test asserts the helper-call list is non-empty for non-allowlisted public functions. Closes the gap where an AST walk says "the call exists" but the runtime path doesn't actually reach it (e.g., guarded by a feature-flag check that the test environment doesn't trigger).

---

## 7. Sequencing rationale (v5)

| Order | Slice | Why this position |
|---|---|---|
| 1 | **0** Doctrine + invariants | Scaffold lands first. Includes CI gate. |
| 2 | **0.5** Mutation defense scaffolding (v4) | Hardens the defense layer against its own mutation BEFORE any extraction lands. Mitigates M1-M10. |
| 3 | **1** Kill-switch | Every subsequent slice's first invariant call. Must exist before extraction. |
| (later) | **7** Session-end auto-extract (v5) | After Slice 3B; default-on in `single-operator-local`. Removes manual extraction trigger. |
| (later) | **7.5** Consensus auto-promotion (v5) | After Slices 5 + 7; default-on in `single-operator-local`; forbidden in `multi-operator-shared`. |
| 3 | **2** Pull extraction | Lowest-risk extraction; exercises candidate format from real session data. |
| 4 | **3A** Observation log infra | Disk surface. Lands before extraction-from-log so log surface is stable. |
| 5 | **3B** Observation extraction | Reads 3A. Stub `_assert_evidence_integrity` until 3C. |
| 6 | **3C** Log integrity | SHA256 checksums become real. `_assert_evidence_integrity` activates. |
| 7 | **4** Confidence promotion | Consolidate change. Familiar terrain. |
| 8 | **5** Usage history | Backwards-compat field addition. Adds richer signal for slices 2 + 3B. |
| 9 | **6** Hooks | Highest attack surface. After all four extraction slices are stable. |

**Stopping points:** if the household stops after Slice 1, that's the kill-switch alone (no extraction yet) — a useful primitive on its own. After Slice 2: pull-based extraction only. After Slice 3C: full extraction with integrity. After Slice 5: full inferential capability but no always-on capture. Slice 6 is genuinely optional.

---

## 7a. Influences from related projects (post-v5 reading)

Concept review of `github.com/lthoangg/OpenAgentd` v0.4.1 (2026-05-11, AGPL-3.0) — a self-hosted multi-agent OS with three-tier memory. Patterns adopted, deferred, or rejected.

### Adopted

- **Raw-parts path-traversal check** (`_validate_session_id`). Their `validate_wiki_path` in `app/services/wiki.py` documents the Python `Path` behaviour that bit us silently: `Path("topics/./test.md")` becomes `("topics", "test.md")` — the dot is silently dropped before `parts` check runs. Their fix: check the **raw string** before any path operation. We adopted this; bare `"."` and embedded `"./"` segments now reject explicitly. Before the fix: bare `"."` passed our check. Shipped post-v5; tests `test_path_traversal_single_dot` and `test_path_traversal_embedded_dot_segment` anchor it.

### Deferred design alternatives (documented for future slice work)

- **Slice 3A — observation log shape.** OpenAgentd uses **append-only daily markdown** (`wiki/notes/{date}.md`) instead of structured JSONL. Trade-off: simpler write path, smaller surface, no JSON-injection risk, but extraction becomes string parsing instead of `json.loads`. When Slice 3A is on deck, brainstorm which shape fits the household model better. Their format:
  ```markdown
  ## HH:MM UTC

  observation text

  ## HH:MM UTC

  next observation
  ```
  vs our planned JSONL one-line-per-observation. Both bounded; both rotation-friendly. Decision deferred.

- **Slice 7 — empty-session auto-skip + mark-processed.** OpenAgentd's dream agent does: "Sessions with no messages are auto-skipped (marked processed, no batch slot consumed)." Pattern is "the no-op is recorded, so the queue doesn't re-process it" — different from "skip silently" which would cause re-entry. Slice 7's session-end auto-extract should adopt this: when `extract_candidates_from_session` finds an empty session, record the session_id as processed in a sidecar log (`~/.memory/_processed_sessions`) without consuming a rate-limit slot. Prevents the next harness invocation from re-trying the same empty session.

### Rejected (intentional doctrine departures)

- **Cron-driven dream agent** (their `app/services/dream_scheduler.py`). Violates our cross-slice invariant #6 (no always-on daemon, no background process). Their model uses APScheduler cron expressions. We deliberately chose synchronous-on-demand. Their dream agent runs detached with a fresh agent instance per item — closer to a job system than a daemon, but still requires the scheduler process to be running. Our Slice 7 design uses harness session-end hook (harness-driven, not process-driven).

- **Plugin loader via `importlib.util.spec_from_file_location` + `exec_module`** (their `app/agent/plugins/loader.py`). Standard Python plugin pattern with synthetic module naming for isolation. Their threat model accepts the plugins directory as operator-controlled. We have no plugin surface and adding one would expand attack surface for negative return.

- **`USER.md` auto-injected into every prompt** (their `WikiInjectionHook`). They inject stable user facts into the system prompt on every LLM call. Powerful but expands the prompt-injection attack surface — every memory-derived string ends up in the agent's context. Our pull-based recall is read-on-demand by the agent or operator; memories don't auto-inject. **Reconsidering this is a future slice decision, not a v5 change** — would need new threat-model entries for prompt-injection-via-memory.

- **Last-match-wins glob permission rules** (their `app/agent/permission.py`, mirrors opencode). More granular than our invariant model but less structural. Our `_assert_*` family is "function-level boundary"; theirs is "per-call wildcard rule." Both work; ours composes better with the CI gate.

- **BM25 over our TF-IDF.** They use BM25 (likely `rank_bm25`); we use TF-IDF inline. Both work for household-scale corpora. Switching cost > benefit at this scale.

### Three-tier model — observation worth recording

Their tier framing maps onto ours like this:

| OpenAgentd tier | Our equivalent |
|---|---|
| Raw (`session_messages` in SQLite) | `orchestrator/state/*.json` |
| Episodic (`wiki/notes/{date}.md` append-only daily) | (no equivalent yet — Slice 3A would add this) |
| Wiki (`wiki/topics/`, `USER.md`, `INDEX.md`) | `~/.memory/{domain}/*.json` |

The middle tier (episodic) is what Slice 3A would introduce. OpenAgentd's daily-markdown shape is a viable simpler alternative to the JSONL structured-observation log we currently plan.

---

## 8. Explicitly NOT in plan (deferred indefinitely, expanded)

(Carried from v1, plus new entries from round-1 review:)

- Auto-promotion to instinct at any threshold
- Cross-project / cross-repo namespace
- Background daemon process
- Network egress from any slice
- Confidence-decay tied to instinct status
- `extract_candidates_to_disk()` or any auto-write candidate API
- **NEW v2:** Programmatic disable without logging — every panic / disable / re-enable must surface as INFO finding
- **NEW v2:** Raw observation data in `_observations/` — only hashes and classifications
- **NEW v2:** Cross-session lock escalation — flock is advisory only; no kernel-level mandatory locks
- **NEW v2:** Side-channel timing mitigation — household threat model assumes co-located trusted operators; documented as out-of-scope. Re-evaluate if threat model widens.

---

## 9. Open questions for round-2 review

Round-2 multi-LLM review should challenge:

1. Is `_assert_evidence_integrity` strong enough? It validates checksums but the checksum file itself is on the same disk. Should checksums live on a separate volume / signed by a key?
2. Is `_assert_rate_limit` (`max_per_minute=60`) the right bound? Will it false-positive on legitimate burst-recall sessions?
3. Is `_assert_temporal_consistency` (60s future, 1h past from chain) too tight? Too loose?
4. Does the new sequencing 0→1→2→3A→3B→3C→4→5→6 introduce dependencies that make individual slices harder to ship?
5. Is 9 slices a sign of scope creep, or appropriate decomposition?
6. Does the CI gate test cover the actual drift modes, or just the easy one (no invariant call at all)? What about a slice that calls invariants weakly (wraps in try/except and swallows)?
7. Should `_assert_panic_check` be the FIRST line of every learning function, or is positioning checked anywhere?
8. What attacks does v2's threat model still miss?
9. Is "1 full sprint of adoption" before Slice 6 measurable? What concrete signal indicates adoption?
10. Does the 7-helper invariant set duplicate or conflict with the existing `careful-not-clever` / `safety-guard` skill discipline? Should one supersede the other?
