# Continuous-Learning-v2 Auto-Extraction Plan — v4

**Status:** Round-3 multi-LLM review complete (mutation-prevention focus + answers to v3 open questions). This is v4. Total 14 consults across 3 rounds, ~$0.27 spend.
**Owner:** P1#9 continuation. Slices 1, 1.1, 1.2 already shipped.
**Goal:** Make the household memory system learn from operator behavior without sacrificing the safety properties Slices 1–1.2 established.

---

## 0. Change log

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

### Slice 6 — Optional always-on capture (ECC-shaped)

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

## 5. Invariant helpers — 7 in v2 (was 4)

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
    """v3 (NEW): pre-promotion anomaly heuristic. Mitigates T16 (familiarity
    crafting) and T17 (approval fatigue) by adding visible friction at the
    operator decision point. Does NOT raise — returns a structured response
    that promote_to_instinct() must surface to the operator.

    Returns:
      {"requires_confirmation": True, "matched_terms": [...]} if candidate
      matches any autonomous-action keyword.
      {"requires_confirmation": False, "matched_terms": []} otherwise.

    Caller (promote_to_instinct) must check the response and refuse to
    proceed without an explicit confirmation argument when matches exist.
    """
    AUTONOMOUS_KEYWORDS = [
        "auto", "every", "daily", "schedule", "automatically",
        "on its own", "without asking", "in the background",
    ]
    content = candidate.get("content", "").lower()
    matched = [k for k in AUTONOMOUS_KEYWORDS if k in content]
    return {"requires_confirmation": bool(matched), "matched_terms": matched}

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

## 7. Sequencing rationale (v2)

| Order | Slice | Why this position |
|---|---|---|
| 1 | **0** Doctrine + invariants | Scaffold lands first. Includes CI gate. |
| 2 | **0.5** Mutation defense scaffolding (v4) | Hardens the defense layer against its own mutation BEFORE any extraction lands. Mitigates M1-M10. |
| 3 | **1** Kill-switch | Every subsequent slice's first invariant call. Must exist before extraction. |
| 3 | **2** Pull extraction | Lowest-risk extraction; exercises candidate format from real session data. |
| 4 | **3A** Observation log infra | Disk surface. Lands before extraction-from-log so log surface is stable. |
| 5 | **3B** Observation extraction | Reads 3A. Stub `_assert_evidence_integrity` until 3C. |
| 6 | **3C** Log integrity | SHA256 checksums become real. `_assert_evidence_integrity` activates. |
| 7 | **4** Confidence promotion | Consolidate change. Familiar terrain. |
| 8 | **5** Usage history | Backwards-compat field addition. Adds richer signal for slices 2 + 3B. |
| 9 | **6** Hooks | Highest attack surface. After all four extraction slices are stable. |

**Stopping points:** if the household stops after Slice 1, that's the kill-switch alone (no extraction yet) — a useful primitive on its own. After Slice 2: pull-based extraction only. After Slice 3C: full extraction with integrity. After Slice 5: full inferential capability but no always-on capture. Slice 6 is genuinely optional.

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
