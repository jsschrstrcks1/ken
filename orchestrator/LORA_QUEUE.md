# LoRA Training Queue

**Status:** 2026-05-30 10:16 EDT

## Queue

### 1. Ken-Expanded ✅ READY → IN PROGRESS

**Data prepared:** 19,651 samples (40% Ken / 60% archive)
- Train: 18,668 samples
- Eval: 983 samples
- Location: `~/lora-data/ken/train.jsonl` + `eval.jsonl`

**Training:**
- Sanity: r=8, 100 steps (30 min)
- Full: r=16, 2 epochs (3-4 hrs)
- Validation: drift detection, cite-or-flag, cross-era (1 hr)

**ETA:** ~5 hrs total (waiting for mlx-lm install)

---

### 2. Spurgeon ❓ DATA ISSUE → TGC FALLBACK

**Original plan:** Spurgeon (pilot, public domain)

**Issue:** Archive has only 8 Spurgeon items (all metadata, no sermon texts)

**Decision needed:**
- Option A: Find Spurgeon corpus elsewhere (full, not in archive)
- Option B: Skip Spurgeon, use TGC (6,061 sermons, 4.6M words) as pilot instead
- Option C: Use Mohler (3,449 sermons, 12.4M words) — largest after TGC

**Current state:** Queue blocked until Ken confirms

**If proceeding with TGC:**
- Data prep: ~10 min (convert 6,061 TGC sermons to JSONL)
- Training: ~3-4 hrs
- ETA: After Ken + ~4.5 hrs

---

### 3. Ken (Second Iteration - Optional)

After first Ken LoRA validates, could retrain with different hyperparams or corpus mix.

---

### 4. MacArthur

769 sermons available in archive, 7M+ words.

---

### 5–11. Other Preachers

- Mohler (3,449 sermons)
- Begg (3,064 sermons)
- Ascol (1,757 sermons)
- Akin (1,200 sermons)
- Mbewe (1,160 sermons)
- Noblit (728 sermons)
- Sproul (548 sermons)

---

## Blocking Issue

**mlx-lm installation pending** (started 10:16 EDT, still installing)
- Once complete: Can start Ken sanity LoRA immediately
- If fails: Need alternative training method

**Spurgeon corpus location needed** — confirm if using TGC fallback or find original Spurgeon sermons

---

_Soli Deo Gloria._
