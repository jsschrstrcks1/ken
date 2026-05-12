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
