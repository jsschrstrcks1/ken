# Claude's 5-Bundle LoRA Strategy — Quick Reference

## What Claude Shipped

Five markdown files that completely reframe the LoRA training problem from "memorize facts" to "encode behavioral integrity + voice + reasoning patterns."

### The 5 Bundles

| Bundle | Focus | Key Insight | Training Examples |
|--------|-------|------------|-------------------|
| **01 Behavioral Backbone** | How rules are made | CLAUDE.md + SKILL.md across 11 repos show *decision structure*, not just conclusions | ~2,000 rule examples |
| **02 Voice Corpora** | What it sounds like | 3 distinct grandmothers, sermon prose, logbooks — intentionally different registers that one LoRA will smear | Register-tagged samples per source |
| **03 Negative Examples** | What NOT to do | Audit rules + operator redirects + superseded chains = contrastive training data | ~200-300 negative examples |
| **04 Reasoning Traces** | How thinking evolves | Multi-LLM debates, keeper journals, revision chains show productive disagreement and correction | ~500-800 reasoning examples |
| **05 Structural Signals** | Importance hierarchy | Graph edges (112), recall counts, confidence distribution, protected flags — not content, but *weighting* | Python sampling script provided |

---

## Why These Bundles Matter

**v1 (current) is facts:** "Careful not clever is principle X" (encoded as example)

**Bundles 01-05 are structure:** "Here's how rules cascade through 11 repos, here's what makes decisions, here's what the model sounds like doing it, here's what it got wrong and why, here's the weights."

---

## The Recommended Strategy

### **Immediate (Phase 0-1.1): $17-24, 3 hours**

1. **Today:** Submit v1 (1,613 examples)
2. **In 2h:** Validate v1 (9 test scenarios)
3. **If ≥85% pass:** Build v1.1 with Bundle 01 (Behavioral Backbone)

### **Later (Phase 2): Decision Point**

- **Option A:** Single LoRA + all remaining bundles ($200-300 more)
- **Option B:** Per-domain adapters + register-tagged voice ($400-600 more) ← **RECOMMENDED**

### **Why Phased?**

- v1 costs $2; v2 costs $400-600
- If v1 fails, you learned early
- If v1.1 works, you have ROI data for Phase 2
- You're not betting $400 on an unproven hypothesis

---

## Data Extraction Quick Guide

### **Bundle 01 — Behavioral Backbone**
Where to find it:
```
/Volumes/1TB External/Projects/ken/orchestrator/
  CONTINUOUS_LEARNING_DOCTRINE.md    (7 principles, 9 invariants)
  CONTINUOUS_LEARNING_PLAN.md        (grep '^##' for sections)
  CONTINUOUS_LEARNING_REVIEWS.md     (multi-LLM review verdicts)

/Volumes/1TB External/Projects/*/CLAUDE.md  (each repo's constitution)

/Volumes/1TB External/Projects/*/
  .claude/skills/*/SKILL.md  (~60 unique skills)
  admin/POLICY_DECISIONS.md  (if present)
```

How to extract: Pair each rule with a situation where it applies, tag by enforcement level (`block`, `suggest`, `warn`).

**Signal:** 2,000+ high-quality rule examples; highest value for v1.1

---

### **Bundle 02 — Voice Corpora**
Where to find it:
```
/Volumes/1TB External/Projects/Romans/*.txt         (sermons)
/Volumes/1TB External/Projects/InTheWake/          (logbooks + port pages)
/Volumes/1TB External/Projects/Grandmasrecipes/    (grandmother #1 voice)
/Volumes/1TB External/Projects/Grannysrecipes/     (grandmother #2 voice)
/Volumes/1TB External/Projects/MomsRecipes/        (mother voice)
/Volumes/1TB External/Projects/Family-History/     (biographical voice)

# Also: commit messages and HANDOFF.md across all repos
```

How to extract: **Per-register tagging is non-negotiable.** Extract with labels like `register: sermon`, `register: recipe-grandma1`, etc.

**Signal:** 3,000-5,000 voice samples; highest risk of register smearing if merged

**Recommendation:** Use per-domain adapters, not single LoRA. This prevents smearing.

---

### **Bundle 03 — Negative Examples**
Where to find it:
```
/Volumes/1TB External/Projects/ken/.claude/skills/voice-audit/
  (LLM-fluff phrase lists, marketing drift rules)

/tmp/memories_dump.md
  grep 'anti-pattern\|redirect\|careful-not-clever'
  (Operator redirects: "that's not careful is it")
  grep 'SUPERSEDED-BY:'
  (Revision pairs: old version → new version)

/Volumes/1TB External/Projects/InTheWake/admin/
  (ICP-2 audit failures)
```

How to extract: Pair negatives with positives (1:5 ratio max). Don't synthesize; use real redirects.

**Signal:** 200-300 examples; sparse but high-quality

**Recommendation:** Keep negative ratio small. Prevents paranoid, overly-cautious model.

---

### **Bundle 04 — Reasoning Traces**
Where to find it:
```
/Volumes/1TB External/Projects/ken/orchestrator/
  CONTINUOUS_LEARNING_REVIEWS.md     (3 rounds of debate with verdicts)
  state/*.json                       (orchestra outputs)

/home/user/*/.claude/state/
  families/*/journal.jsonl           (keeper journals)

Everywhere: code-review responses from git + PR bodies
```

How to extract: Shape as `(context, proposal, challenge, resolution, action_taken)` tuples. Strip model names → `model-A/B/C`.

**Signal:** 500-800 examples; shows productive disagreement + correction

**Recommendation:** Essential for teaching "how the operator thinks" — include in Phase 1.1+ if time permits

---

### **Bundle 05 — Structural Signals**
Where to find it:
```
/Volumes/1TB External/Projects/.memory/*/*.json  (all 726 memories)
  - Extract: protected, recall_count, confidence, related_to, supersedes
```

How to extract: **Not content, but weighting.** Use provided Python formula:
```python
weight = (0.4 if protected else 0.0)
       + (0.3 * min(recall_count, 10) / 10)
       + (0.2 * confidence)
       + (0.1 if is_instinct else 0.0)
```

**Signal:** Importance hierarchy; tells you what to over-sample in training

**Recommendation:** Use for weighted sampling in all phases; no primary training data here

---

## High-Confidence Recommendations

1. **SUBMIT v1 TODAY** ← Do this now
2. **IF v1.1 passes (Phase 1.1):** Extract Bundle 01 only
3. **IF v1.1 works well:** Use per-domain adapters for Bundles 02-05 (not single LoRA)
4. **NEVER:** Merge grandmother registers or song voice + cruise voice + sermon voice

---

## What's Already Built (v1)

✅ Training data pipeline (`tools/lora-training-pipeline.py`)
✅ Validation suite (`tools/lora-validation.py`)
✅ Submission script (`tools/lora-submit.py`)
✅ Orchestrator integration (`tools/lora-orchestrator-integration.py`)
✅ Complete documentation (README, HANDOFF, BUILD_SUMMARY)

**Everything is ready. The 5 bundles are the *next layer*, not a blocker.**

---

## Next Action

```bash
# Submit v1 (5 seconds to run, $2, 30-60 min to complete)
python3 tools/lora-submit.py --model gpt-4o

# Check back in 1-2 hours, then validate
python3 tools/lora-validation.py --results-only
```

That's it. Everything else is conditional on v1 success.

---

_Generated: Today_
_Confidence: 0.92 (HIGH) — phased approach endorsed across 5-bundle strategy_
