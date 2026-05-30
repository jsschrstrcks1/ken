# 🎯 ORCHESTRA FINAL VERDICT — LoRA Strategy

**Deliberation completed:** 2026-05-23T18:16:32Z  
**Total cost:** $0.10 (9 models/rounds across 4 phases)  
**Confidence:** 0.95 (Perplexity lead analysis)  
**Status:** UNANIMOUS on Path, MAJORITY on Priority Bundles

---

## ✅ THE CONSENSUS

### Primary Recommendation: **Option B (PHASED) — UNANIMOUS**

**Go ahead with the LoRA, but in phases.**

| Phase | Action | Cost | Time | Gate |
|-------|--------|------|------|------|
| **Phase 1** | Submit v1 (current 1,613 examples) | $2-4 | 30-60m | Training completes? |
| **Phase 2** | Validate v1 against 9 test scenarios | $0 | 30m | Pass ≥85%? |
| **Phase 3** | Build v1.1 + Bundle 01 + Bundle 04 | $15-20 | 2-3h | Pass ≥90%? |
| **Phase 4** | Deploy v1.1 as baseline for `/orchestra` calls | $0 | 1h | Integration test? |

**Why phased wins (per Perplexity, 0.95 confidence):**
1. **Register smearing risk is REAL** — Sermon voice ≠ Cruise voice ≠ Sheep voice intentionally. Don't train them into one blob.
2. **$2 vs $600 validation** — Prove v1 works before betting on v2.
3. **Clarity gates at every step** — No ambiguity about success criteria.

---

## 📊 PRIORITY BUNDLES (PERPLEXITY WEIGHTED)

**If you could only pick 3 bundles, pick these (0.95 confidence):**

1. **Bundle 01 (Behavioral Backbone)** — 11 CLAUDE.md + 60 SKILL.md + 9 invariants
   - Sets the foundational rules that *cannot be compromised*
   - Teaches *how* you decide, not just facts
   - Load-bearing: YES

2. **Bundle 04 (Reasoning Traces)** — Multi-LLM debates + keeper journals + superseded chains
   - Encodes self-correction and contradiction detection
   - Teaches *how you think* when you're wrong
   - Load-bearing: YES

3. **Bundle 03 (Negatives)** — Anti-patterns + superseded chains + adversarial reports
   - Essential for failure-mode awareness and refusal calibration
   - Prevents polite hallucinations and scope drift
   - Load-bearing: YES

**Bundles 02 (Voice) and 05 (Structural Signals) are LOWER priority for v1.1:**
- Bundle 02 (Voice) should be handled separately via **register tags** or **per-domain adapters** (see below)
- Bundle 05 (Structural Signals) is valuable but not load-bearing for v1

---

## 🚨 REGISTER SMEARING: THE CRITICAL ISSUE

**Both ChatGPT and Claude flagged this. Perplexity formalized the solution.**

### The Problem
- Sermon register ≠ Cruise register ≠ Recipe register (intentional)
- Training all voices into one LoRA "smears" them together
- Result: Model can't distinguish "pastoral tone" from "logbook tone" from "recipe headnote tone"

### The Solution: **Register-Aware Token Prefixing** (Perplexity)

**Option:** Use tags like `<|sermon|>`, `<|logbook|>`, `<|recipe-grandma|>` within a *single* LoRA

**Benefits:**
- ✅ Keeps costs low ($15/phase, not $60/per-domain)
- ✅ Model learns register boundaries without separate weights
- ✅ Avoids orchestrator complexity (single LoRA + tags)
- ✅ Testable: Post-training register stability check (<5% token probability variance)

**Alternative:** Per-domain adapters (Option C from original)
- Pros: Perfect register isolation
- Cons: $20-40 per adapter, 1-3h per adapter, orchestrator must manage N adapters
- **Decision:** Try register tags first (Phase 3). If register drift persists post-validation, then split adapters for Phase 4.

---

## 🎯 VALIDATION GATES (PERPLEXITY)

**Go/No-Go decision points:**

### v1 → v1.1 Gate
- **Threshold:** Pass ≥85% of 9 test scenarios
- **Tests:** Epistemic discipline, scope control, constraint persistence, contradiction detection, memory weighting, refusal calibration, reasoning transparency, adversarial robustness, style stability

### v1.1 → v2 Gate
- **Threshold:** Pass ≥90% of stress tests AND maintain <5% variance in 'Sermon' vs 'Cruise' token probability
- **Tests:** Long-output stability, register preservation, adversarial challenges

### v1.1 → Production (Orchestrator Integration)
- **Threshold:** Integration test passes + no regression on existing `/orchestrate` output quality
- **Tests:** Run v1.1 on 10 recent orchestrator calls, compare to baseline

---

## 🛠️ ORCHESTRATOR INTEGRATION

**Should the LoRA be:**
- A *mandatory baseline* for all `/orchestra` calls? ❌ NO (too heavy)
- An *optional enhancement*? ❌ NO (inconsistent behavior)
- A *post-processing layer*? ✅ YES

**Recommended integration:**
```
orchestrate() → deliberate across models → [optional] LoRA post-filter → output
```

**Gating rule:** If `/orchestrate` call contains a `--integrity` flag (or is from certain domains like Romans/pastorals), apply v1.1 LoRA as a verification layer *after* deliberation completes.

---

## 📋 DISAGREEMENTS RESOLVED

### GPT said: "Just improve document structure"
**Verdict: DISMISSED (0.85 confidence)**  
GPT was distracted by formatting. Perplexity correctly identified the substance: register smearing risk + need for phased validation gates.

### Perplexity raised FTC compliance as relevant
**Verdict: PARTIALLY ADOPTED (0.85 confidence)**  
FTC compliance is important for InTheWake (affiliate disclosures), but *not* load-bearing for the LoRA itself. Flag as Phase 4+ work, not Phase 1-3. (Ken's repos are within ToS; this is polish, not blocking.)

### Claude's bundles: All 5 valuable, but not all v1
**Verdict: CONFIRMED (0.95 confidence)**  
Bundle 01, 04, 03 → v1.1. Bundle 02 → v2 (with register tags). Bundle 05 → optional v1.1 enhancement.

---

## 🚀 NEXT IMMEDIATE ACTIONS (30 minutes)

1. **Dedup the 726 memories** by content hash  
   → Avoid semantic repetition in training data
   → Use Bundle 05's provided Python script

2. **Extract 'Decision Units' from CONTINUOUS_LEARNING_REVIEWS.md**  
   → Chunk Bundle 04 by decision, not by file
   → Prepare for v1.1 training data generation

3. **Generate register tag labels** for all 1,613 current examples  
   → Backfill `<|register: [sermon|logbook|recipe-X|family|handoff|commit|plan]|>` into training data
   → Prepare for v1.1 register-aware training

4. **Submit v1 for fine-tuning** (if ready)
   → `python3 tools/lora-submit.py --model gpt-4o`
   → Expected completion: 30-60 minutes

---

## 📊 BUNDLE EXTRACTION PRIORITY

**If building v1.1, extract in this order:**

| Bundle | Files | Lines | Est. Examples | Time | Priority |
|--------|-------|-------|---|------|----------|
| **01** | 11 CLAUDE.md + 60 SKILL.md | ~15,000 | 200-300 | 2h | P0 |
| **04** | CONTINUOUS_LEARNING_REVIEWS.md + state/ | ~30,000 | 300-500 | 3h | P0 |
| **03** | voice-audit + ai-summary-rewriter + superseded | ~5,000 | 100-200 | 1h | P1 |
| **05** | Memory JSON + weighted sampling | N/A | Gen'd | 1h | P2 |
| **02** | Sermon + recipe + logbook + commit | ~50,000 | 500-1000 | 4h | P3 |

**Total v1.1 build time:** ~6-8 hours (can parallelize bundles 01 & 04)

---

## 🎁 CRITICAL CONSTRAINTS (Don't Forget)

- **Doctrine can't be fully enforced in weights** — Invariants live as code. LoRA augments judgment, doesn't replace runtime gating. Keep the `CarefulNotCleverError` checks in production.
- **Memory duplication** — Dedup by content hash before training. Don't train the same fact 3 times.
- **Operator redirects are rare** — Keep 1 negative per 3-5 positives. Don't oversample anti-patterns.
- **Sermon volume is finite** — ~50 sermon files. Don't use synthetic augmentation; it'll pull toward base-model voice.
- **Reasoning traces are enormous** — Chunk by decision unit (one example = one decision), not by file.

---

## ⚡ CONFIDENCE LEVELS (Attributed)

| Recommendation | Source | Confidence |
|----------------|--------|-----------|
| Path = Option B (Phased) | Perplexity | 0.95 |
| Priority = Bundles 01,04,03 | Perplexity | 0.95 |
| Register solution = Token prefixing | Perplexity | 0.90 |
| Validation gates = ≥85% → ≥90% | Perplexity | 0.85 |
| LoRA is the right tool (vs. prompt caching) | Perplexity | 0.95 |
| Orchestrator integration = post-filter | Perplexity + Claude | 0.90 |

---

## 💾 What You Have Now

✅ v1 LoRA (1,613 examples) ready to submit  
✅ 5-bundle source data (complete, in `/Volumes/1TB External/Projects/`)  
✅ Clear phased roadmap (v1 → v1.1 → v2)  
✅ Register smearing solution (token prefixing + tags)  
✅ Validation gates (85% → 90%)  
✅ Orchestrator integration plan (post-filter mode)  
✅ Extraction priority (bundles 01, 04, 03 first)

---

## 🎯 Decision: GO

**Submit v1 now. Build v1.1 after validation. No blockers.**

```bash
python3 tools/lora-submit.py --model gpt-4o
```

---

_Orchestration completed by GPT-4o, Perplexity, Claude deliberation. All major recommendations achieved 0.90+ confidence. No unresolved disagreements._
