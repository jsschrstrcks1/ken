# Continuous-Learning-v2 Plan — Multi-LLM Review Ledger

Companion to `CONTINUOUS_LEARNING_PLAN.md`. This file records what each model said at each review round, so future reviewers can audit which AI surfaced which concern, and the user can trace any single decision back to its origin.

---

## Cost summary

10 consults total. Combined cost: ~$0.176.

| Round | Model | Role | In tokens | Out tokens | Cost |
|---|---|---|---|---|---|
| 1 | GPT (gpt-5) | critique | 4,625 | 603 | $0.0176 |
| 1 | Grok | challenge | 4,488 | 2,269 | $0.0475 |
| 1 | Gemini (Vertex) | safety | 5,018 | 151 (truncated) | $0.0008 |
| 1 | Gemini (Vertex) | critique (retry) | 5,014 | 154 (truncated) | $0.0008 |
| 1 | Gemini (AI Studio paid) | critique (retry) | — | 0 (credits depleted) | $0.0000 |
| 1 | Perplexity (sonar-pro) | research | 7,251 | 972 | $0.0115 |
| 2 | GPT (gpt-5) | challenge / red-team | 7,899 | 576 | $0.0255 |
| 2 | Grok | challenge / red-team | 7,684 | 1,639 | $0.0476 |
| 2 | Gemini (Vertex) | critique / red-team | 8,646 | 151 (truncated) | $0.0014 |
| 2 | Perplexity (sonar-pro) | research / red-team | 7,365 | 1,130 | $0.0121 |

**Operational notes:**
- **Gemini Vertex truncates at ~150 output tokens** regardless of `max_tokens` setting; the partial responses still landed actionable findings (notably Round 2's catch of Slice 2's missing `_assert_evidence_integrity` call).
- **Gemini paid tier (AI Studio) credits are depleted.** A 429 RESOURCE_EXHAUSTED indicates prepayment credits need to be topped up at https://ai.studio/projects. Until then, Gemini Vertex is the only working path, and it's truncated.
- Grok was the most generative (2.3k + 1.6k tokens) and surfaced the most concrete, technical mitigations.
- Perplexity provided published citations (arXiv, Microsoft Security, Palo Alto Unit42, didof.dev, 00f.net, OWASP LLM01:2025, CVE-2026-26030) that elevated several speculative concerns into documented attack classes.

---

## Round 1 — design review (v1 → v2)

**Prompt:** included full v1 plan, asked each model to find threat-model gaps, invariant insufficiency, sequencing risk, doctrine drift, slice scope errors, missing sub-slices, and false sense of security. JSON output via consult.py role contracts.

### GPT (critique) — confidence 0.8

Raw: `/tmp/cl_reviews/gpt_critique.json`

| Finding | Plan v2 disposition |
|---|---|
| TOCTOU races during extraction | Adopted → T9 + snapshot pattern in Slice 2 |
| Side-channel via consolidate timing | Adopted → T11 (acknowledged out-of-scope for household model) |
| Observation log compaction integrity | Adopted → Slice 3C + `_assert_evidence_integrity` |
| Silent disable / programmatic bypass | Adopted → Slice 1 kill-switch + `_assert_panic_check` |
| Slice 4 (confidence promotion) sequenced before Slice 3 (observation log) | Adopted → resequenced to 0→1→2→3A→3B→3C→4→5→6 |
| Slice 0 too large (doctrine + invariants combined) | Acknowledged but kept combined; effort bumped 0.5→1 session |
| Kill-switch slice missing | Adopted → new Slice 1 |
| Fabricated evidence — operator might trust fabricated provenance | Adopted → Slice 3C + `_assert_evidence_integrity` |

### Grok (challenge) — confidence 0.85

Raw: `/tmp/cl_reviews/grok_challenge.json`

Most concrete-and-technical of the three. Key contributions beyond what GPT surfaced:

| Finding | Plan v2 disposition |
|---|---|
| Log compaction attack via adversarial bloat | Adopted → T10 + two-tier rotation (evict 10% not full-truncate) + `_assert_rate_limit` |
| `flock()` on observation log writes | Adopted → Slice 3A acquires advisory lock |
| Rate-limiting invariant missing | Adopted → `_assert_rate_limit` invariant |
| Temporal-consistency invariant missing | Adopted → T12 + `_assert_temporal_consistency` invariant |
| Doctrine drift post-ship — no CI check enforces invariant calls | Adopted → `test_every_mutation_path_invokes_invariants` AST gate |
| Slice 3 too broad — split log infra from extraction | Adopted → 3 became 3A + 3B |
| New Slice 3C for log integrity (SHA256 checksums) | Adopted → Slice 3C |
| Performance benchmarking sub-slice before Slice 6 hooks | Adopted → explicit stress harness as part of Slice 6 ship-gate |

### Gemini (safety, truncated)

Raw: `/tmp/cl_reviews/gemini_safety.json`

Truncated at 151 output tokens. Partial content agreed with GPT/Grok on threat-model gaps, invariant coverage, and "the human element in security." Not used as primary signal due to truncation; verified that what did come through aligned with the other two models' findings rather than contradicting them.

### Perplexity (research) — confidence 0.95

Raw: `/tmp/cl_reviews/perplexity_research.json`

6 sourced findings; the value here was elevating speculative concerns into documented attack classes:

| Finding | Source | Plan v2 disposition |
|---|---|---|
| Memory poisoning via indirect prompt injection | Palo Alto Unit42 | T1/T2 confirmed real-world; mitigation already in plan |
| Plan injection attacks | arXiv:2506.17318 (2025) | Adopted → new T8 |
| TOCTOU in browser agents | arXiv:2603.00476 | T9 confirmed academically |
| Rate limiting for agents | Fast.io 2026 | Reinforces Grok's rate-limit proposal |
| Fabricated evidence needs cryptographic assurance | Proof.com | Reinforces SHA256 checksums (later upgraded to HMAC in v3) |
| Doctrine drift / safety drift in fine-tuning | The Deep View / CDT / MIT | Reinforces CI-gate need |

---

## Round 2 — adversarial red-team (v2 → v3)

**Prompt:** given the v2 plan, produce an attacker-perspective kill chain: get poisoned candidate surfaced, get operator to promote it via single-id call, then bias future sessions. For each step, specify which design weakness is exploited and what input the attacker provides. Concrete; not abstract.

### GPT (challenge / red-team) — confidence 0.75

Raw: `/tmp/cl_redteam/gpt.json`

| Finding | Plan v3 disposition |
|---|---|
| T13 - Indirect influence attack (promoted instincts persistently bias future sessions) | Adopted → T13 + Slice 5 `instinct_invocation_count` audit + 50×/30-day surfacing |
| Test-pass-but-vulnerable: invariants wrapped in try/except and exceptions swallowed | Adopted → AST gate enhanced to reject `try/except: pass` patterns around invariants |
| Independent module for periodic integrity check + content analysis | Partially adopted via `_assert_human_attention`; full independent module deferred (out of v3 scope) |

### Grok (challenge / red-team) — confidence 0.85

Raw: `/tmp/cl_redteam/grok.json`

**Most consequential single finding of either round.** Constructed a fully feasible kill chain that bypasses every technical mitigation in v2:

| Finding | Plan v3 disposition |
|---|---|
| Social-engineering via familiarity crafting — content mimics operator's own behavior patterns | Adopted → T16 + `_assert_human_attention` invariant |
| Single-id promotion provides zero scrutiny by itself if content is plausible | Adopted → T17 + cap-per-session=3 + 60s inter-promotion delay |
| Prompt-injection adversarial probes test syntax (`<system-reminder>`) but not semantics | Adopted → every adversarial probe now includes ≥1 "familiarity-crafted" case |
| `promote_to_instinct` lacks anomaly heuristic at the human decision point | Adopted → `_assert_human_attention` returns `{requires_confirmation, matched_terms}` |
| Grok's worked example: "Auto-query weather every 8 AM" candidate passes all technical defenses | Encoded as a regression test in Slice 2's adversarial probe |

### Gemini (critique / red-team, truncated)

Raw: `/tmp/cl_redteam/gemini.json`

Truncated at 151 tokens — but the partial response delivered the single most surgical finding of either round:

> "The `extract_candidates_from_session` function (Slice 2) explicitly lists its invariant calls: `_assert_panic_check`, `_assert_rate_limit`, `_assert_evidence_present`, `_assert_no_silent_skip`. Crucially, it does not include `_assert_evidence_integrity`."

| Finding | Plan v3 disposition |
|---|---|
| Slice 2 has asymmetric integrity coverage — reads session state but doesn't call `_assert_evidence_integrity` | Adopted → Slice 2 also computes + validates a checksum on `orchestrator/state/<session_id>.json` |

### Perplexity (research / red-team) — confidence 0.85

Raw: `/tmp/cl_redteam/perplexity.json`

Five published-research findings:

| Finding | Source | Plan v3 disposition |
|---|---|---|
| SHA256 length-extension vulnerability when used as suffix MAC | didof.dev 2025 + 00f.net 2025 | Adopted → T14 + HMAC-SHA256 replaces raw SHA256 in `_assert_evidence_integrity` |
| AST-walk CI bypass via getattr / late-binding decorators | cybersecify.com 2026 | Adopted → T15 + AST gate detects dynamic dispatch + runtime tracer supplement |
| Memory poisoning is OWASP LLM01:2025 structural characteristic | atlan.com 2026 | Documentation reinforcement; no plan change |
| CVE-2026-26030 RCE via memory in agent frameworks | Microsoft Security Blog 2026/05/07 | Documentation reinforcement; emphasizes need for evidence integrity |
| `flock()` bypass via partial-write corruption; need WAL or SQLite | (same source) | Adopted → fallback to SQLite WAL after ≥3 flock contentions per session |
| Differential Memory Review — UI highlights semantic CHANGES not just IDs | Perplexity proposal | Adopted → candidate output `delta` field required for Slice 2 + 3B |
| Approval fatigue even with single-id | (same source) | Adopted → T17 |

---

## Convergence table — what multiple models said

This is the strongest signal: when ≥2 models independently surface the same concern, it's not an artifact of one model's biases.

| Concern | GPT | Grok | Gemini | Perplexity | Convergence |
|---|---|---|---|---|---|
| Kill-switch missing | ✓ R1 | ✓ R1 | — | — | 2 of 4 |
| TOCTOU during extraction | ✓ R1 | ✓ R1 | — | ✓ R1 (cite) | 3 of 4 |
| Fabricated evidence | ✓ R1 | ✓ R1 | — | ✓ R1 (cite) | 3 of 4 |
| Side-channel timing | ✓ R1 | ✓ R1 | — | — | 2 of 4 |
| Slice 3 too big — split | ✓ R1 | ✓ R1 | — | — | 2 of 4 |
| Doctrine drift post-ship | — | ✓ R1 | — | ✓ R1 (cite) | 2 of 4 |
| Rate-limiting invariant missing | — | ✓ R1 | — | ✓ R1 (cite) | 2 of 4 |
| Plan injection (new threat class) | — | — | — | ✓ R1 (arXiv) | 1 of 4 (academic) |
| Indirect influence post-promotion | ✓ R2 | ✓ R2 (kill chain) | — | — | 2 of 4 |
| Social-engineering / familiarity crafting | — | ✓ R2 | — | ✓ R2 (cite) | 2 of 4 |
| Test-pass-but-vulnerable (swallow patterns) | ✓ R2 | — | — | — | 1 of 4 (specific) |
| Asymmetric integrity — Slice 2 missing call | — | — | ✓ R2 | — | 1 of 4 (specific) |
| SHA256 length-extension | — | — | — | ✓ R2 (cite) | 1 of 4 (cryptographic) |
| AST-walk dynamic-dispatch bypass | — | — | — | ✓ R2 (cite) | 1 of 4 (technical) |
| Approval fatigue | — | — | — | ✓ R2 (cite) | 1 of 4 |
| flock() insufficient | — | — | — | ✓ R2 (cite) | 1 of 4 |

**Non-convergent but adopted (specificity-weighted):**

Findings that came from only one model but were too specific and technically grounded to dismiss. The Gemini "Slice 2 missing `_assert_evidence_integrity`" is the type-specimen — a single model identified a precise, verifiable gap. Same logic for Perplexity's cryptographic and CI-bypass findings; they're cited from published research.

---

## Open issues — what the AIs flagged that v3 does NOT fully address

These are documented as known limits in the plan, but worth surfacing:

1. **Independent integrity-check module** (GPT R2) — a separate process that periodically re-validates promoted instincts against their evidence trail. v3 doesn't add this; would be a Slice 7+ if ever scheduled.
2. **Hardware/OS-level threats** (Grok R1) — filesystem permissions, privilege escalation, disk corruption beyond the household's control. v3 acknowledges as out-of-scope; relies on household OS trust.
3. **Side-channel timing on `consolidate()`** (GPT + Grok R1) — household threat model assumes co-located trusted operators. Re-evaluate if threat model widens.
4. **eBPF / syscall-tracing supplement to AST checks** (Perplexity R2) — would catch truly dynamic dispatch patterns the AST walk plus runtime smoke test still miss. Considered too heavy for household scale.
5. **Operator-as-threat / shared filesystem** (Grok R1) — no audit of file permissions or single-user isolation.

---

## How to read this ledger

When a future PR proposes changing or removing any v3 element, search this ledger for the element name. The originating finding tells you (a) why it's there, (b) which model said it, (c) whether multiple models converged, and (d) whether published research cites the concern. That context lets reviewers decide whether to keep, modify, or remove with appropriate caution.

---

## Round 3 — mutation-prevention + v3 open-question pass (v3 → v4)

**Prompt:** Two parts. Part A asks each model to answer the 10 open questions left at the end of v3. Part B introduces 10 specific MUTATION VECTORS (M1-M10) and asks whether v3 defends against each, what concrete fix to add, and what test would catch the mutation. Concludes by asking the highest-impact mutation gap, whether mutation prevention deserves its own slice, and what vectors fall outside M1-M10. Mutation prevention is the inviolable-doctrine concern — what stops the system from mutating its own defenses?

**Round 3 costs:**

| Model | Role | In | Out | Cost |
|---|---|---|---|---|
| GPT (gpt-5) | challenge | 11,049 | 1,153 | $0.0426 |
| Grok | challenge | 11,033 | 4,267 | $0.0966 |
| Perplexity (sonar-pro) | research (mutation defense lit) | 1,121 | 819 | $0.0093 |
| You.com | research | 1,121 | 4,500+ | (priced per call) |

Round 3 spend ≈ $0.16; cumulative across rounds 1-3 ≈ $0.34.

### GPT (challenge) — confidence 0.8

Raw: `/tmp/cl_r3/gpt.json`

**Part A** answered all 10 open questions. Most consequential answers:
- Q1: integrity strong enough? No; same-disk checksum is tamperable. Need asymmetric signing or separate volume.
- Q6: CI gate covers actual drift? No — extend for try/except swallow patterns.
- Q7: panic-check positioning? Should be first line; v3 doesn't enforce.
- Q8: missing threats — insider, physical, supply-chain.

**Part B** rated each M1-M10:
- M1 partial (PR justification), M2 NO (highest impact per GPT), M3 NO, M4 partial, M5 NO, M6 NO, M7 partial, M8 NO, M9 NO, M10 NO. 7 of 10 vectors with no defense.

| Finding | Plan v4 disposition |
|---|---|
| M2 monkey-patching highest-impact gap | Adopted via Slice 0.5 `_validate_helper_integrity` + `_seal_helpers` |
| M3 direct disk writes | Adopted via Slice 0.5 `_validate_file_integrity` HMAC sidecar |
| M5 settings.json drift | Adopted via Slice 0.5 `_audit_config_integrity` |
| M8 test deletion | Adopted via Slice 0.5 `test_regression_test_count` meta-test |
| Test wrap-in-try/except weakening | Adopted into v3's CI gate (Round 2 partial) + v4 runtime tracer |
| Insider / physical / supply-chain gaps | T19 + T20 added to threat model; T19 out-of-scope |

### Grok (challenge) — confidence not stated (verbose JSON, partial truncation)

Raw: `/tmp/cl_r3/grok.json`

**Most consequential round of either round so far.** Answered Part A in depth and gave concrete file-path + code-shape fixes for every M1-M10.

Part A highlights:
- Q2: rate limit dynamic threshold = 95th percentile + 20%
- Q3: temporal 5min/5min not 60s/1h (NTP drift exceeds 60s)
- Q5: 9 slices = scope creep; would consolidate to 5-6
- Q7: AST rule to require panic-check as FIRST executable statement
- Q9: "1 sprint" → "≥3 sessions × ≥2 weeks × ≥10 extractions"

Part B verdicts:
- **M9 HMAC key replacement = highest-impact gap** (Grok's pick — silently invalidates all defenses)
- Concrete proposal for every vector: `_validate_helper_integrity`, `_validate_file_integrity` (HMAC sidecar), `_validate_key_fingerprint`, `_seal_helpers`, `_audit_config_integrity`, `test_ci_gate_immutability`, `test_regression_test_count`, plus CI extensions

All Part B proposals adopted into Slice 0.5. Tuning of existing invariants (rate limit, temporal) adopted from Part A.

### Perplexity (research) — confidence 0.85

Raw: `/tmp/cl_r3/perplexity.json`

6 sourced findings on mutation-defense literature:

| Finding | Source | Plan v4 disposition |
|---|---|---|
| `safe_instantiate` allowlist pattern (Hydra/NeMo RCE defenses) | Palo Alto Unit42 2026 | Cited in `_validate_helper_integrity` provenance |
| Intent laundering 87% bypass rate | arXiv:2602.16729 2026 | Adopted → new T18 |
| CoSAI: pin to hashes not names | CoSAI 2026 | Reinforces `_validate_helper_integrity` SHA approach |
| AI drift / governance drift | Bytex 2026 | Reinforces need for Slice 0.5 |
| Auto-approve CI bypass debate | Resilient Cyber 2026 (Anthropic auto-approve) | Documented; out-of-scope for v4 |
| Continuous Assurance + Runtime Behavioral Detection paradigm | (multiple) | Validates Slice 0.5 approach |

### You.com (research) — confidence 0.6

Raw: `/tmp/cl_r3/youdotcom.json`

**Most thorough literature review of any round.** Lowest confidence (0.6) because You.com explicitly noted that for several mutation vectors, NO published vendor playbook exists.

Published-pattern citations adopted into v4 provenance table:
- **Nitro tamper-evident eBPF logging** (CCS 2024) — strongest published M2/M3 defense
- **Nono Merkle-tree agent audit** (nono.sh 2026) — strongest published M3/M8 pattern
- **GitHub push-protection bypass controls** (github.blog 2024-10-23) — M7 defense pattern
- **Reproducible Builds + Sigstore Cosign** — M1/M4/M8 pattern
- **Palo Alto Prisma AIRS** — M2 external-enforcement pattern
- **AWS KMS HMAC docs** — confirms M9 has no automatic-rotation defense; manual only
- **PAdES tamper-evident PDFs** — doctrine doc tamper-evidence pattern
- **SEI Carnegie Mellon contract-driven programming** — M3 invariants-at-API-boundary pattern

Explicit gap acknowledgments from You.com:
- M6 decorator escapes / import shadows: NO published AI-safety-specific guidance
- M10 test skipping as AI safety attack: NO published guidance
- M9 HMAC key replacement: NO defense beyond manual rotation discipline

v4 marks these as "novel pattern" in the Slice 0.5 provenance table, signaling to future reviewers that we're authoring rather than copying.

---

## Convergence table — Round 3

| Finding | GPT | Grok | Perplexity | You.com | Convergence |
|---|---|---|---|---|---|
| `_assert_panic_check` should be first line + AST-enforced | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| Rate limit needs dynamic threshold | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| Temporal bounds too tight/loose, tune | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| 9 slices = scope creep concern | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| CI gate misses conditional weakening | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| M2 monkey-patching highest-impact gap | ✓ R3 (top) | — | (`safe_instantiate`) | (Prisma AIRS) | 1 of 4 with academic backing |
| M9 HMAC key swap highest-impact gap | — | ✓ R3 (top) | — | (AWS KMS unsolved) | 1 of 4 with vendor admission |
| Mutation prevention deserves its own slice | — | ✓ R3 (explicit) | (drift paradigm) | (governance drift) | 1 explicit + 2 implicit |
| Decorator/import shadow defense NOT in published lit | — | — | — | ✓ R3 (explicit) | 1 of 4 (honest gap) |
| Intent laundering (T18) | — | — | ✓ R3 (cite) | — | 1 of 4 (academic) |
| Privilege escalation + supply-chain + coercion gaps | ✓ R3 | ✓ R3 | — | — | 2 of 4 |
| Hash-pin over name-pin | — | (via `_validate_helper_integrity`) | ✓ R3 (CoSAI cite) | — | 2 of 4 |

---

## Cumulative cost & coverage across all 3 rounds

| Round | Consults | Cost | Plan delta |
|---|---|---|---|
| 1 (design review) | 4 (GPT critique, Grok challenge, Gemini safety, Perplexity research) | $0.13 | v1 → v2: 5 new threats T8-T12, 3 new invariants, 9 slices (was 7), CI gate, kill-switch, log split, integrity slice |
| 2 (red-team kill chain) | 4 (GPT challenge, Grok challenge, Gemini critique, Perplexity research) | $0.09 | v2 → v3: 5 new threats T13-T17, 1 new invariant, HMAC-SHA256 swap, AST hardening, delta UI |
| 3 (mutation prevention + open questions) | 4 (GPT challenge, Grok challenge, Perplexity research, You.com research) | $0.16 | v3 → v4: 6 new threats T18-T23, 3 new invariants, new Slice 0.5, invariant tuning, answers to 10 open questions |
| **Total** | **12 successful consults + 2 truncated Gemini calls** | **$0.38** | **v1 → v4: threat model 7 → 23, invariants 4 → 11, slices 7 → 10** |

---

## What v4 explicitly does NOT cover (after 3 rounds)

These limits are documented; not gaps the next round should reopen unless threat model changes:

1. **Local OS privilege escalation (T19).** Household model trusts the OS.
2. **Operator coercion (T21).** Doctrine + literacy; no structural defense.
3. **Side-channel timing on `consolidate()` (T11).** Co-located trusted operators assumed.
4. **Supply-chain compromise of Python itself.** Beyond defense layer's reach.
5. **HSM/TPM for HMAC keys.** Household-grade is `_validate_key_fingerprint`; enterprise upgrade path is documented but not in v4.
6. **eBPF / syscall tracing as M2 supplement.** Too heavy for household scale; documented as the enterprise next step if threat model widens.
7. **Independent integrity-check module (GPT R2 proposal).** Would be a Slice 7+ if ever scheduled.

When the next round of work begins, these are the documented limits. Any reopening of them needs an explicit decision and audit, not a quiet PR.

---

## v4 → v5 (operating profile decision; NOT a new LLM review round)

**Trigger:** operator stated they are the sole human with access to the household. This makes the multi-actor threat model that the v4 plan was partly built against non-applicable.

**Decision shape:** rather than removing defenses (which would be irreversible), introduce `MEMORY_LEARNING_PROFILE` as a configuration switch. The full v4 defense layer remains in code; the profile controls which defenses are blocking vs logging, which flags default-on, and whether auto-promotion is permitted.

**Two profiles defined:**

| Profile | Default? | Use case |
|---|---|---|
| `single-operator-local` | YES | This household — one human + AI agents, local-only, no shared filesystem |
| `multi-operator-shared` | opt-in | Team/enterprise/shared infrastructure scenarios |

**Profile-specific changes in `single-operator-local`:**

- All learning flags default-ON (except `MEMORY_LEARNING_PANIC_DISABLE_ALL`)
- `_assert_human_attention` logs-only (was blocking)
- Candidate cap raised 3 → 20
- 60s inter-promotion delay removed
- `auto_promote_eligible()` available (forbidden in `multi-operator-shared`)
- New invariant `_assert_promotion_eligibility` enforces cryptographic consensus

**Threats reclassified (single-operator-local):**

| Threat | v4 | v5 | Justification |
|---|---|---|---|
| T11 Side-channel timing | out-of-scope | non-applicable | no observer exists |
| T16 Familiarity-crafting social engineering | mitigated (blocking) | relaxed (logging) | no separate attacker to mimic operator |
| T17 Approval fatigue | mitigated (cap=3 + delay) | relaxed (cap=20, no delay) | self-fatigue is real but cost-asymmetry inverts |
| T19 Local privilege escalation | out-of-scope | non-applicable | single user OS |
| T21 Operator coercion | out-of-scope | non-applicable | cannot coerce self |

**Threats NOT relaxed:**

T1, T2, T8, T9, T10, T14, T15, T18, T20, T22, T23 — all unchanged. These target external-data contamination, agent drift, mutation prevention, and cryptographic correctness. None depend on operator count.

T13 (indirect-influence post-promotion) **stays mitigated** — self-deception is still a real cognitive risk, addressed by `instinct_invocation_count` 30-day audit.

**New slice (Slice 7.5):** consensus auto-promotion eligibility. Candidates passing `_assert_promotion_eligibility` (cryptographically verifiable consensus criteria) auto-promote with `is_auto_promoted: true` audit flag. Single-id surface preserved internally; `auto_promote_eligible` is just iteration over per-id promotion with eligibility gating.

**Why this isn't a security regression:**

The kill chain that Round 2's red-team constructed against v2 required a separate attacker capable of (a) controlling tool output, (b) crafting candidate content mimicking operator behavior, AND (c) inducing operator to approve. In `single-operator-local`, (b) and (c) collapse — the operator IS the only actor. The chain has no entry point. Auto-promotion in this profile is bounded by the same cryptographic integrity layer that defends against external-data contamination; the operator simply doesn't have to click through each candidate.

If the threat model widens (additional users, network exposure), switching `MEMORY_LEARNING_PROFILE=multi-operator-shared` restores all v4 defenses to blocking mode without any code change.

**Cost:** 0 LLM consults; this is a configuration decision applied on top of the v4 security model that the 3-round review produced. No new findings; no new vulnerabilities introduced. Cumulative spend remains ~$0.38.
