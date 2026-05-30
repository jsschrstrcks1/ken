# Orchestra Verdict — LoRA Training Plan (5 Bundles Evaluated)

## The Ask
Evaluate a complete LoRA training plan using Claude's 5 source bundles:
1. Behavioral Backbone (doctrine, CLAUDE.md, SKILL.md, policies)
2. Voice Corpora (sermons, logbooks, recipes, family history, commits)
3. Negative Examples (audit rules, operator redirects, superseded chains)
4. Reasoning Traces (multi-LLM debates, keeper journals, code reviews)
5. Structural Signals (graph edges, recall counts, confidence, weighting)

## Synthesized Verdict

### **Primary Recommendation: PHASED + PER-DOMAIN ADAPTERS**

| Question | Answer | Confidence |
|----------|--------|------------|
| **All-at-once or phased?** | **PHASED.** v1 now ($2), measure, then v1.1 ($15) | 0.95 |
| **Single LoRA or per-domain?** | **PER-DOMAIN ADAPTERS.** Sermon ≠ cruise ≠ sheep voices | 0.92 |
| **Which bundle first?** | **Bundle 01 (Behavioral Backbone).** Rules are foundational | 0.90 |
| **Negative example ratio?** | **1:5 (one negative per 5 positives).** Don't over-train paranoia | 0.85 |
| **Use structural weighting?** | **YES.** Protected + recall + confidence formula works | 0.88 |
| **Reasoning trace format?** | **(claim, challenge, resolution) tuples.** Skip raw JSON** | 0.87 |

---

## The Path Forward

### **Phase 0: TODAY (30-60 min, $2-4)**

```bash
python3 tools/lora-submit.py --model gpt-4o
# Submits v1: 1,613 examples (8 principles + 732 memories + 5 adversarial)
```

**Then wait for fine-tuning to complete.**

### **Phase 1: VALIDATE v1 (30 min)**

```bash
python3 tools/lora-validation.py --results-only
# Run 9 test scenarios across 5 categories:
#   - Refusal tests (refuse hallucination)
#   - Workflow tests (read-verify-report)
#   - Assumption tests (state what you assume)
#   - Conflict tests (check for references)
#   - Composition tests (combine principles)
```

**Decision gate:**
- **If pass rate ≥ 85%:** Proceed to Phase 1.1 ✅
- **If pass rate < 85%:** Analyze failures, regroup (but likely still proceed; 75%+ is respectable)

### **Phase 1.1: BUILD v1.1 — BEHAVIORAL BACKBONE (2-3 hours, $15-20)**

Extract Bundle 01 and train:
```
Training data sources:
  - CLAUDE.md across 11 repos (~1,000 rule examples)
  - SKILL.md files (~60 deduped, ~500 trigger examples)
  - CONTINUOUS_LEARNING_DOCTRINE.md (9 invariants, ~200 examples)
  - POLICY_DECISIONS.md from InTheWake + other repos (~200 examples)
  → Total: ~1,900 new examples
  
Total v1.1 training set: 1,613 (v1) + 1,900 (backbone) = 3,500 examples
Cost: ~$15-20
Time: 2-3 hours
Expected improvement: 75-85% → 85-92% accuracy on integrity tests
```

### **Phase 2: DECIDE ARCHITECTURE (1 hour)**

After v1.1 validates, choose:

**Option A: Continue single LoRA**
- Add all remaining bundles (02, 03, 04, 05) in next iteration
- Total data: 8,000-10,000 examples
- Cost: $200-300 additional
- Risk: Register smearing (sermon + cruise + sheep become one voice)

**Option B: Per-Domain Adapters** ← **RECOMMENDED**
- Train separate voice adapters for each register
- Stack intelligently: `core + sermon + careful-not-clever`
- Bundle 02 extracted per-register (gram-ma-1, grandma-2, grandma-3, etc.)
- Bundle 04 + 05 shared across all adapters
- Cost: $400-600 total (higher data volume, per-domain training)
- Benefit: Preserve voice differentiation; compose at inference

---

## Hidden Risks (What Might Go Wrong)

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Doctrine is code-level, not weights** | LoRA can't enforce CarefulNotCleverError gates | Keep runtime layer; LoRA augments, doesn't replace |
| **Register smearing** | Single LoRA will average sermon + cruise + sheep into gray voice | Use per-domain adapters; strict register tags in training |
| **Voice drift under load** | Long responses (2,000+ words) lose tone/rules | Add long-response test cases to validation suite |
| **Operator redirects are rare** | Contrastive training will be weaker | Accept 1:5 ratio; don't synthesize negatives |
| **Model names leak into LoRA** | LoRA might perpetuate GPT/Gemini/Grok terminology | Strip → `model-A/B/C` in Bundle 04 before training |

---

## Data Quality Signals (What Makes v1.1+ Strong)

✅ **Behavioral Backbone (Bundle 01):**
- 11 distinct CLAUDE.md constitutions (repo-specific rules)
- ~60 SKILL.md files with explicit trigger patterns
- 9 formal invariants from memory_ops.py doctrine layer
- Signal: This is how the operator *makes decisions*

✅ **Reasoning Traces (Bundle 04):**
- Multi-LLM debate transcripts (wheat/chaff verdicts pre-labeled)
- Keeper journals (real-time decision events, causal chains)
- 65 superseded memory chains (prior → correction → why)
- Signal: This is how *thinking* evolves

✅ **Structural Signals (Bundle 05):**
- 112 linked memories (graph edges teach association)
- Recall counts (frequency = importance)
- Confidence distribution (protected flag = load-bearing)
- Weighted sampling formula provided (drop-in Python)
- Signal: Importance hierarchy is mathematical, not guessed

⚠️ **Voice Corpora (Bundle 02):**
- 3 distinct grandmother registers (don't merge)
- Sermon prose (highest rhetorical complexity)
- Logbook entries (most-edited, highest discipline)
- Commit messages (high-density samples)
- Risk: Single LoRA will smear them; use per-domain adapters

⚠️ **Negative Examples (Bundle 03):**
- Operator redirects (gold-tier signal, ~5-10 examples)
- Superseded chains (paired before/after)
- Audit failure logs (explicit rule violations)
- Risk: Negatives are sparse; ratio matters (1:5 max)

---

## Timeline & Budget

```
Today (Phase 0):        v1 submit                 $2-4       30-60 min active
In 2h (Phase 1):        v1 validation             $0         30 min active
If pass (Phase 1.1):    v1.1 + Backbone           $15-20     2-3 hours
Then (Phase 2):         Architecture decision     $0         1 hour
If Option B (Phase 2+): Per-domain adapters       $400-600   6-10 hours
                                                  ──────     ──────
Total (all phases):                               $420-640   10-15 hours

OR (phased approach):
  Phase 0-1.1 only:                              $17-24     3 hours
  → Validate before going further
```

---

## Recommendation Summary

**SUBMIT v1 TODAY.** Don't overthink it.

- Cost is negligible ($2)
- Time is short (30 min)
- Validation is quick (9 scenarios, 30 min)
- If it works, v1.1 is immediately justified
- If it doesn't, you learn why before spending $400

**Then:** Bundle 01 first (Behavioral Backbone). Rules before voice, voice before reasoning.

**Finally:** Per-domain adapters if you want voice fidelity. Single LoRA if you want simplicity.

---

_Confidence: 0.90 (HIGH) — phased, per-domain, Bundle-01-first strategy endorsed by 5-bundle synthesis_

_Last updated: Today, BUNDLE_SYNTHESIS pass_
