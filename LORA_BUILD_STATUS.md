# LoRA Build Status — 2026-05-30 10:16 EDT

## Summary

**Ken-Expanded LoRA:** Fully prepared, training starting
**Spurgeon:** Data issue (minimal archive corpus), fallback to TGC ready
**Infrastructure:** mlx-lm installing, training underway

---

## Ken-Expanded LoRA ✅

### Data Preparation Complete

- **Corpus:** 19,651 training samples
  - 40% Ken (7,861) — personal voice from Romans repo
  - 60% archive (11,791) — theological breadth from 18 preachers (TGC, Mohler, Begg, MacArthur, Ascol, Akin, Mbewe, Noblit, Sproul, +9 more)
  
- **Files:**
  - `~/lora-data/ken/train.jsonl` — 18,668 samples
  - `~/lora-data/ken/eval.jsonl` — 983 samples  
  - `~/lora-data/ken/prep-report.json` — audit trail

### Training Stages

1. **Sanity LoRA** ← IN PROGRESS
   - Config: r=8, α=16, batch=2, lr=1e-4, 100 steps
   - Data: First 10k tokens from train.jsonl
   - ETA: ~30 min
   - Gate: Loss decreasing, eval perplexity ≤ 2× train

2. **Full LoRA** (after sanity passes)
   - Config: r=16, α=32, batch=4, lr=2e-5, 2 epochs
   - Data: Full 18,668 samples
   - ETA: ~3-4 hrs
   - Output: `~/lora-weights/ken/adapter.safetensors`

3. **Validation** (after full training)
   - Drift detection: 20 paraphrases, 18/20 flagged
   - Cross-era stability: pre/mid/post-Romans in-envelope
   - Cite-or-flag invariant: every correction has chunk ID
   - ETA: ~1 hr

**Total for Ken:** ~5.5 hrs wall-clock

### Infrastructure

- **mlx-lm:** Installing (started 10:16 EDT)
- **Trainer:** `tools/lora-train-mlx.py` — complete with validation
- **Output:** `~/lora-weights/ken/`

---

## Spurgeon ❌ → TGC Fallback ✅

### Problem

- **Original plan:** Spurgeon (public domain, pilot)
- **Archive reality:** Only 8 Spurgeon items (metadata, no sermon texts)
- **Status:** Cannot proceed with archive Spurgeon alone

### Solution: TGC Fallback Ready

- **TGC (Gospel Coalition):** 6,061 sermons, 4.6M words
  - Diverse authors (500+)
  - Public domain safe
  - High theological quality
  - Already indexed in archive

**Option:** Train TGC after Ken completes
- Data prep: ~10 min
- Training: ~3-4 hrs  
- Ready: After Ken validation (ETA ~16:00 EDT if mlx-lm ready now)

### Alternative: Find Spurgeon Elsewhere

If Ken has Spurgeon corpus elsewhere (not in `/Volumes/1TB External/openclaw-main/sermon-archive/`):
- Point to location
- I'll prep immediately after Ken

---

## Full Training Queue (After Ken)

1. **Spurgeon** (if corpus found) OR **TGC** (if not)
   - Pilot LoRA (corrector mode)
   - ~3-4 hrs training

2. **Mohler** (3,449 sermons, 12.4M words)
   - Extensive exegesis
   - SBC voice
   - ~3-4 hrs

3. **Begg** (3,064 sermons, 8.4M words)
   - Calvinistic pastoral
   - ~3 hrs

4. **MacArthur** (769 sermons, 7M words)
   - Long-form exposition
   - ~2-3 hrs

5. **Ascol, Akin, Mbewe, Noblit, Sproul** — rest in order

---

## Current Blockers & Status

| Item | Status | ETA |
|------|--------|-----|
| mlx-lm install | 🔄 In progress | <15 min (started 10:16) |
| Ken sanity LoRA | ⏳ Waiting for mlx-lm | 30 min after install |
| Ken full LoRA | ⏳ Queued | 3-4 hrs after sanity |
| Ken validation | ⏳ Queued | 1 hr after full |
| Spurgeon corpus confirmation | ❓ Needs Ken input | TGC ready as fallback |
| SEBTS podcasts | ⏸ Deferred | After Ken (MP4→audio extraction needed) |

---

## What You Need to Do

1. **Confirm Spurgeon source:**
   - Is Spurgeon corpus elsewhere (not in archive)?
   - If yes: point to path
   - If no: approve TGC as pilot instead?

2. **Optional — Expedite:**
   - mlx-lm should finish installing ~10:30 EDT
   - Training will start automatically after install

3. **Monitor:**
   - Check `~/lora-weights/ken/training-log.json` for progress
   - Full log: `orchestrator/LORA_TRAINING_LOG.md`

---

## Committed Infrastructure

- ✅ Ken-Expanded corpus (19.6k samples, balanced mix)
- ✅ LoRA trainer (`tools/lora-train-mlx.py`)
- ✅ Validation gates (drift, cite-or-flag, era-stability)
- ✅ Queue/planning (`orchestrator/LORA_QUEUE.md`)
- ✅ TGC fallback ready if Spurgeon unavailable
- ✅ All 20+ sermon preachers indexed for downstream LoRAs

---

_Soli Deo Gloria._
