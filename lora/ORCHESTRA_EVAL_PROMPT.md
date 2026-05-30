# LoRA Strategy Orchestration Eval

## Context
Ken is building an Integrity LoRA (Low-Rank Adaptation) based on:
1. **Current v1** — 1,613 training examples from 732 memories + Careful Not Clever principles
2. **Claude's 5-bundle expansion** — Behavioral Backbone, Voice Corpora, Negative Examples, Reasoning Traces, Structural Signals
3. **Goal** — Encode epistemic discipline, scope control, constraint persistence, contradiction detection, memory weighting, refusal calibration, reasoning transparency, adversarial robustness, style stability, and failure-mode awareness

## The Question

**Should the LoRA be built:**
- **A) All-in-one** — combine all 5 bundles into v2 now ($400-600, 4-6h, one unified adapter)?
- **B) Phased** — v1 now ($2, 30-60m), validate, then v1.1 + bundles 1-5 incrementally ($15-20 per phase)?
- **C) Per-domain adapters** — separate LoRAs for sermon, cruise, sheep, recipes, family (more complex, but preserves register)?
- **D) Hybrid** — v1 base layer + per-domain voice adapters + reasoning trace overlay?

## Sub-questions for Deliberation

1. **Training data priority**: Which bundles matter most if you could only pick 3?
   - Bundle 01 (Behavioral Backbone — doctrine, rules, invariants)
   - Bundle 04 (Reasoning Traces — multi-LLM debates, keeper journals, superseded chains)
   - Bundle 05 (Structural Signals — graph edges, recall counts, confidence, importance weighting)
   - vs. Bundle 02 (Voice — sermon, cruise, recipe registers) and Bundle 03 (Negatives — anti-patterns)?

2. **Register smearing risk**: ChatGPT warned that sermon voice ≠ cruise voice ≠ sheep voice. Claude's data confirms: "Three grandmothers ≠ one grandmother." Do you:
   - Accept smearing risk (faster, cheaper)?
   - Build per-domain adapters (slower, costlier, but cleaner)?
   - Use register tags in training and test post-training (middle ground)?

3. **Validation gates**: What threshold justifies moving to the next phase?
   - v1 → v1.1: Pass ≥85% of 9 test scenarios?
   - v1.1 → v2: Pass ≥90% + show token efficiency gain?

4. **Failure mode coverage**: Which of the 10 failure modes is most critical?
   - Epistemic discipline (distinguish verified/inference/unverified)
   - Scope control (answer only what was asked)
   - Constraint persistence (maintain rules through long outputs)
   - Contradiction detection (self-consistency)
   - Memory weighting (persistent rules vs temp context)
   - Refusal calibration (partial answer > blank refusal)
   - Reasoning transparency (justify claims)
   - Adversarial robustness (resist leading questions)
   - Style stability (maintain tone under load)
   - Failure mode awareness (interrupt itself when guessing)

5. **Orchestrator integration**: Should the LoRA:
   - Be a *mandatory baseline* for all `/orchestra` calls?
   - Be an *optional enhancement* you can enable for careful work?
   - Be a *post-processing layer* (deliberate, then LoRA-filter the output)?

## Data Points for Deliberation

- **Bundle 01 (Behavioral Backbone)**: 11 CLAUDE.md files, 60 SKILL.md files, 9 invariants from memory_ops.py. Teaches *how* you decide.
- **Bundle 02 (Voice Corpora)**: ~50 sermon manuscripts, port pages, 3 grandmother recipe headnotes, family history prose, 500+ commit messages. Teaches what you *sound like*.
- **Bundle 03 (Negatives)**: voice-audit rules, ai-summary-rewriter before/after pairs, 65 superseded memory chains, adversarial reports. Teaches what to *avoid*.
- **Bundle 04 (Reasoning Traces)**: 3 rounds of multi-LLM debate (CONTINUOUS_LEARNING_REVIEWS.md ~30KB), keeper journals, orchestrator state files, code review responses. Teaches *how you think*.
- **Bundle 05 (Structural Signals)**: 726 memories with fields (protected, recall_count, confidence, related_to, supersedes). Weighted sampling script included. Teaches *importance hierarchy*.

## Trade-offs

| Approach | Cost | Time | Register Smearing | ROI Clarity | Complexity |
|----------|------|------|-------------------|------------|-----------|
| A (All-in-one v2) | $400-600 | 4-6h | HIGH | UNCLEAR | HIGH |
| B (Phased) | $2 + $15/phase | 30m + 2-3h | MEDIUM | CLEAR | MEDIUM |
| C (Per-domain) | $20-40 each | 2-3h each | NONE | SLOW | VERY HIGH |
| D (Hybrid) | $20 + $50/adapter | 2h + 1h each | LOW | MEDIUM | HIGH |

## Critical Constraints

- **Doctrine can't be fully enforced in weights** — invariants live as code; LoRA augments judgment, doesn't replace runtime gating
- **Skill-rule conflicts exist across repos** — register variation is intentional; don't collapse it
- **Memory duplication — dedup by content hash before training (avoid semantic repetition)**
- **Operator redirects are rare** — keep 1 negative per 3-5 positives; don't oversample anti-patterns
- **Sermon volume is finite** — synthetic augmentation risks pulling LoRA toward base-model voice
- **Reasoning traces are enormous** — chunk by decision unit, not by file
- **Graph edges (112 linked memories) are valuable for training memory-association patterns**

## The Synthesis Question

**Given all this data, the team should recommend:**

1. **Go/No-Go** — Is a LoRA the right tool, or would prompt caching + memory ranking be cheaper?
2. **Path** — Which approach (A/B/C/D) wins and why?
3. **Priority** — Which 3 bundles are load-bearing?
4. **Validation** — What measurement makes "success" clear?
5. **Next Step** — What's the *first* 30-minute action?

---

Deliberate openly. Disagree on data, not on authority. The operator paid for honest debate, not consensus.
