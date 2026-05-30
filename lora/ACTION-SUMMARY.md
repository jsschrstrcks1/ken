# INTEGRITY LoRA — ACTION SUMMARY

**What the Orchestra Said:** PHASED APPROACH (Deploy v1 now, expand modular later) ✅

**Confidence:** 0.90 (HIGH) — unanimous across GPT + Perplexity

---

## 3 Critical Findings

1. **Cost Volatility:** v2 is $400-600 (hourly billing), not $2-4. Need ROI proof before scaling.
2. **Register Smearing:** Can't mix 11 repo voices in one LoRA without breaking persona. Use separate stylistic adapter in Phase 2.
3. **Epistemic First:** Layer 1 (verified/inference/unverified labels) must be proven before Layers 2-3.

---

## What to Do Right Now

### ✅ Phase 0 (IMMEDIATE) — Submit v1
```bash
cd /Volumes/1TB External/openclaw/workspace-main
python3 tools/lora-submit.py --model gpt-4o
```

- **Cost:** $0.80-$2.00
- **Time:** 30-60 min
- **What:** Submit current 1,613-example training set (8 principles + 732 memories)

### ✅ After v1 Completes — Validate
Run 9 test scenarios from `lora/lora-validation.py`
- Target pass rate: >95%
- Document any failures

### 🟡 Phase 1 (If v1 validates) — Stabilized v1.1
Integrate Behavioral Backbone (9 invariants, 60 SKILL.md, policies)
+ Core Layer 2 (scope control, constraint persistence, contradiction detection)

- Estimated cost: $10-$25
- Timeline: 2-3 hours
- **Gate:** Only proceed if v1 shows clear utility

### 🔴 Phase 2 (If v1.1 validates) — Voice Corpora as Separate Adapter
Build *secondary* LoRA for voice (sermons, logbooks, recipes) to avoid smearing

- Estimated cost: $300-$600
- Timeline: 4-6 hours
- **Gate:** Only proceed if v1.1 shows >10% improvement

---

## Why Phased Wins

| Metric | v1 Only | v1 + v1.1 | Full v2 |
|--------|---------|-----------|---------|
| Cost | $2 | $15 | $600 |
| Time | 1h | 3h | 7h |
| Risk | Low | Medium | High |
| Validated? | Yes (v1) | Maybe | No |
| Register smearing? | No | Unlikely | High (unless separate adapter) |

---

## Files Ready to Deploy

Everything is built and ready:

```
lora/
├── training-data/
│   └── training-data.jsonl (3.2 MB, 1,613 examples)
├── lora-validation.py
├── lora-submit.py
├── lora-orchestrator-integration.py
├── README.md
├── HANDOFF.md
├── BUILD_SUMMARY.md
├── ORCHESTRA-SYNTHESIS.md (THIS DECISION)
└── ACTION-SUMMARY.md (YOU ARE HERE)
```

---

## One Critical Reminder

**The LoRA is a bias layer, not a guarantee.**

Doctrine + invariants live as **code** (CarefulNotCleverError in memory_ops.py), not weights.

The LoRA will make Claude *prefer* Careful Not Clever reasoning, but the orchestrator's **runtime layer** (IntegrityGate, IntegrityCheckpointer) is what actually *enforces* it.

Keep both: LoRA (learned bias) + Orchestrator runtime (enforced rules).

---

## Go/No-Go

**Status:** ✅ **GO** — Submit v1 whenever you're ready

```bash
python3 tools/lora-submit.py --model gpt-4o
```

Watch for completion, then run validation tests.

Report back with results and we'll decide Phase 1.

---

**Orchestra completed:** 2026-05-23 18:05 UTC | Cost: $0.0837 | Duration: ~15 min
