# LoRA Training Plan — Complete Synthesis

## What Claude Gave Us (5 Bundles)

Claude shipped 5 markdown files that completely reframe the LoRA training:

### 01 — Behavioral Backbone
- Doctrine across 11 repos (CONTINUOUS_LEARNING_DOCTRINE.md + CONTINUOUS_LEARNING_PLAN.md)
- CLAUDE.md in each repo — the constitutions
- ~60 SKILL.md files with trigger patterns + enforcement levels
- POLICY_DECISIONS.md (InTheWake canon)
- **Signal:** How rules are made, not just what the rules are

### 02 — Voice Corpora  
- Romans sermons (theologian voice, highest signal)
- InTheWake logbooks + port pages (cruise voice)
- 3 grandmother recipe registers (distinct voices, not merged)
- Family-History biographical prose
- HANDOFF.md files (terse working voice)
- Commit messages (high-density operator samples)
- **Signal:** What it sounds like; already measured by voice-dna skill

### 03 — Negative Examples
- voice-audit skill rule lists (LLM-fluff, marketing drift, AI-tells)
- like-a-human enforcement rules (inverse positives)
- ai-summary-rewriter before/after pairs
- Mined operator redirects (highest quality: "that's not careful is it")
- 65 superseded memories (built-in revision pairs)
- Validator failure logs from ICP-2 audits
- **Signal:** What NOT to do; trained contrastively

### 04 — Reasoning Traces
- Multi-LLM debate transcripts (CONTINUOUS_LEARNING_REVIEWS.md)
- Keeper journals (real-time decision events)
- Superseded chains (prior → correction → why)
- Code-review responses (accepted/rejected with reasoning)
- Orchestra state JSON (GPT proposes → Gemini refines → Grok challenges)
- **Signal:** How decisions get made; the reasoning gradient

### 05 — Structural Signals
- Graph edges (112 linked memories)
- Recall counts (frequency weighting)
- Confidence distribution (protected flag, instinct tier)
- Tag clustering
- **Provided:** Drop-in Python script for weighted sampling
- **Signal:** Importance hierarchy baked into 726 memories

---

## Synthesis: 3 High-Confidence Recommendations

### **Recommendation 1: Phased Approach (HIGH CONFIDENCE — 0.95)**

**Decision:** Submit v1 NOW, measure results, *then* expand.

**Rationale:**
- v1 cost: $2-4 (30-60 min passive time)
- v1 validates the hypothesis: "Careful Not Clever can be baked into weights"
- If v1 succeeds, v1.1 (with Behavioral Backbone) is justified
- If v1 fails, we learn why before spending $400-600 on v2

**Phase Schedule:**
1. **Today (Phase 0):** Submit v1 — current 1,613 examples
2. **In 1-2 hours (Phase 1):** Test v1 results — run 9 validation scenarios
3. **If successful (Phase 1.1):** Build v1.1 with Behavioral Backbone only (~$15, 2-3h)
4. **If v1.1 works (Phase 2):** Then decide: all 5 bundles at once, or per-domain adapters?

**Cost:** $2-4 → $15 → ($400-600 only if earlier phases prove ROI)

---

### **Recommendation 2: Per-Domain Adapters (NOT Single LoRA)**

**Decision:** Train separate adapters for sermon, cruise, sheep voices — stack them intelligently.

**Rationale:**
- Bundle 02 (Voice Corpora) shows 3 distinct grandmother registers are *intentionally different*
- A single LoRA trained on all 11 repo voices will **smear them into one gray register**
- The operator has already separated them with voice-dna measurements
- Stacking adapters lets you compose: "Use sermon + careful-not-clever" vs. "Use cruise + careful-not-clever"

**Structure:**
```
lora-core/                    (Behavioral Backbone + integrity)
├── adapters/
│   ├── sermon-voice.safetensors
│   ├── cruise-voice.safetensors  
│   ├── sheep-voice.safetensors
│   ├── recipe-voice.safetensors
│   └── family-history-voice.safetensors
├── shared/
│   ├── careful-not-clever.safetensors
│   └── memory-weighting.safetensors
```

Inference: "Load core + sermon + careful-not-clever" vs. "Load core + cruise + careful-not-clever"

---

### **Recommendation 3: Data Priority (Phased Bundle Loading)**

**If you build v1.1 (Behavioral Backbone only):**

1. **EXTRACT FIRST:** Bundle 01 (Behavioral Backbone)
   - CLAUDE.md across all 11 repos (1-2h extraction)
   - SKILL.md files (~60, de-duped by content hash)
   - CONTINUOUS_LEARNING_DOCTRINE.md + PLAN.md (grep structure sections)
   - POLICY_DECISIONS.md from each repo
   - **Training examples:** ~2,000-3,000 (rules paired with situations)

2. **SKIP FOR NOW (save for v2):**
   - Bundle 02 (Voice Corpora) — too much risk of register smearing; defer to per-domain adapters
   - Bundle 03 (Negative Examples) — good but secondary; get positives solid first
   - Bundle 04 (Reasoning Traces) — highest quality but complex extraction; wait for v1.1 validation
   - Bundle 05 (Structural Signals) — essential, but only for *weighted sampling*, not primary training

**If you skip v1.1 and go straight to complete v2:**

Bundle load order by signal-to-cost:
1. **Bundle 01** (Behavioral Backbone) — rules are foundational
2. **Bundle 04** (Reasoning Traces) — second-most important after rules
3. **Bundle 05** (Structural Signals) — weighting + importance, not content
4. **Bundle 03** (Negative Examples) — contrastive; 1 negative per 3-5 positives max
5. **Bundle 02** (Voice Corpora) — only if doing per-domain adapters; otherwise skip

---

## Hidden Risks (What You Might Miss)

### **Risk 1: Doctrine is Brittle**
- The 9 runtime invariants live in `memory_ops.py` code (CarefulNotCleverError)
- A LoRA can learn the *flavor* of careful-not-clever but cannot enforce the gates
- **Mitigation:** Keep the runtime layer in production; the LoRA augments judgment, doesn't replace it
- **Implication:** The LoRA is best-effort, not bulletproof

### **Risk 2: Register Smearing**
- Sermon voice ≠ cruise voice ≠ sheep voice (intentional by design)
- Training a single LoRA on all 11 repos will average them into one gray register
- **Mitigation:** Per-domain adapters instead of single LoRA, OR strict register-tagging in training data
- **Implication:** Choose per-domain early, before you've invested in single-LoRA training

### **Risk 3: Voice Drift Under Load**
- Models get sloppy when responses are long or complex
- Bundle 02 notes: "Train specifically for maintaining tone, structure, and rules in long outputs"
- This was NOT in v1 training data
- **Mitigation:** Add long-response test cases (2,000+ word outputs) to validation suite
- **Implication:** v1 might pass short tests but fail under realistic load

### **Risk 4: Operator Redirects Are Rare Gold**
- Bundle 03 mentions: "Operator redirects are gold but rare. Don't dilute with synthetic negatives."
- Only ~5-10 examples in the redirect list
- **Mitigation:** Keep negative examples small (1:5 ratio), don't synthesize more
- **Implication:** Contrastive training will be weaker than you'd like; accept that

### **Risk 5: Reasoning Traces Leak Model Names**
- Bundle 04: "Reasoning traces name GPT, Gemini, Grok"
- If the LoRA learns those names, it might perpetuate them
- **Mitigation:** Strip model names → `model-A`, `model-B`, `model-C` before training
- **Implication:** Extra preprocessing step before Bundle 04 training

---

## My Direct Recommendation

**DO THIS:**

1. **Today:** Submit v1 ($2, 30-60 min)
2. **In 2 hours:** Test v1 on 9 scenarios — measure pass rate
3. **If v1 > 85% pass rate:** Immediately build v1.1 with Behavioral Backbone ($15, 2-3h)
4. **Then decide:** Per-domain adapters + full bundle load, OR single LoRA + voice tagging?

**DON'T DO THIS:**

- Don't build complete v2 right now (you haven't proven v1 works)
- Don't train on all 5 bundles at once (too much data, no prior validation)
- Don't merge all registers into one LoRA (you'll destroy voice differentiation)
- Don't use synthetic negatives (stick to real operator redirects + superseded chains)

---

## Expected Outcomes

### **v1 (Current): 1,613 examples**
- Training time: ~30-60 minutes
- Cost: $2-4
- Expected accuracy: 75-85% on integrity tests
- Risk: May not handle constraint persistence or scope control

### **v1.1 (Behavioral Backbone only): ~3,500 examples**
- Training time: ~2-3 hours
- Cost: ~$15-20
- Expected accuracy: 85-92% on integrity + rule adherence tests
- Gain: Rules now baked in; doctrine enforcement improved

### **v2 (All 5 bundles + per-domain adapters): ~8,000-15,000 examples**
- Training time: ~6-10 hours
- Cost: $400-600
- Expected accuracy: 92-98% on all test categories
- Risk: May still drift on long outputs; needs load-testing

---

## Next Immediate Action

```bash
# Submit v1
python3 tools/lora-submit.py --model gpt-4o

# Wait for completion (30-60 min)
# Then test
python3 tools/lora-validation.py --results-only

# If pass rate > 85%, proceed to v1.1 extraction
# From 5 bundles, start with Bundle 01 (Behavioral Backbone)
```

---

_Decision confidence: 0.90 (HIGH) — phased approach, per-domain adapters, Bundle 01 first_
