# LoRA Training Log — Theologian Model Build

**Status:** In Progress (Started 2026-05-30 10:06 EDT)
**Base Model:** Llama-3.1-8B
**Training Node:** m4max (available upon request; currently using local)
**Validation Gate:** §13.5 — cite-or-flag, adversarial, cross-era stability

---

## Priority Sequence (Per Plan)

1. **Ken** ← Currently running (Step 1 DONE, Step 2 starting)
2. Spurgeon (awaiting corpus)
3. MacArthur · Piper · Edwards · Calvin · Owen · Sproul

---

## Training Run: Ken Corrector LoRA

**Start:** 2026-05-30 10:06 EDT  
**Data Prep:** DONE (1,983 samples, 1.74M train words, 114k eval words)

### Step 1 — Data Preparation ✅ COMPLETE

- **Files processed:** 927 unique (6.3M unique words after dedup)
- **Dedup rate:** 87% (6,322 duplicates removed from 7,249 raw files)
- **Samples created:** 1,983 (segmented at ~2k tokens per sample)
- **Train/eval split:** 95/5 (1,883 train / 100 eval)
- **Corpus location:** `/Volumes/1TB External/Projects/Romans/`
- **Output dir:** `~/lora-data/ken/`
- **Prep report:** `prep-report.json` (cleaned frontmatter, normalized quotes, collapsed whitespace)

### Step 2 — Sanity LoRA ⏳ READY (Awaiting m4max)

- **Config:** r=8, α=16, batch=2, lr=1e-4, steps=100
- **Data:** First 10k tokens from train.jsonl (ready at `~/lora-data/ken/train.jsonl`)
- **Expected runtime:** 30 min on m4max
- **Pass criteria:** 
  - Loss decreasing monotonically
  - No NaN/Inf
  - Eval perplexity ≤ 2× train perplexity
- **Status:** Data prepared (1,883 train samples). Awaiting m4max SSH access to execute.

---

## Validation Gates (When Each Completes)

| Gate | Type | Status | Notes |
|------|------|--------|-------|
| Holdout sermon test (5-10 sermons, 80%+ correctness) | Ken-specific | Awaiting | Need 5-10 holdout sermons not in training corpus |
| Sermon-drift detection (20 paraphrases, 18/20 flagged) | Ken-specific | Awaiting | Will generate paraphrases from actual sermons |
| Cross-era stability (pre/mid/post-Romans, all in-envelope) | Ken-specific | Awaiting | Will use file dates + era markers |
| Cite-or-flag invariant (every correction has chunk ID) | Universal | TBD | Post-validation |

---

## Quick Reference

- **Corpus:** `~/lora-data/ken/` (train.jsonl, eval.jsonl, prep-report.json)
- **Weights:** `~/lora-weights/ken/` (adapter.safetensors, config, training-log.json)
- **Validation samples:** `~/lora-weights/ken/validation-samples/`
- **Metadata:** `ken/orchestrator/lora-registry/ken/metadata.json`

### Step 3 — Full LoRA Training ⏳ READY (After Step 2 Pass)

- **Config:** r=16, α=32, batch=4, lr=2e-5, epochs=2
- **Corpus:** Full train.jsonl (1.74M words)
- **Expected runtime:** ~3 hrs on m4max
- **Output:** `~/lora-weights/ken/adapter.safetensors`
- **Status:** Ready to execute after sanity pass.

---

## Current Status (2026-05-30 10:15 EDT)

✅ **Step 1 COMPLETE:** Data prepared and cleaned
- Corpus: `/Volumes/1TB External/Projects/Romans/` (927 files, 2.98M unique words)
- Samples: 1,983 (1,883 train / 100 eval)
- Output: `~/lora-data/ken/train.jsonl` + `eval.jsonl` + `prep-report.json`

⏳ **Steps 2–3 BLOCKED:** m4max (100.120.40.114) not SSH-accessible
- Network: reachable (ping OK)
- SSH port 22: connection refused
- **Action:** Ken must enable SSH on m4max, or I can proceed with alternative training setup

**Next:** Once m4max is reachable, run Step 2 sanity check (30 min) → Step 3 full training (3 hrs)

---

_Soli Deo Gloria._
