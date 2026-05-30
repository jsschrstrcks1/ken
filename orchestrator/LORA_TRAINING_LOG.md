# LoRA Training Log — Theologian Model Build

**Status:** In Progress (Started 2026-05-30 10:06 EDT)
**Base Model:** Llama-3.1-8B
**Training Node:** m4max (awaiting SSH access)
**Validation Gate:** §13.5 — cite-or-flag, adversarial, cross-era stability

---

## Priority Sequence (Updated Per Corpus Discovery)

1. **Ken-Expanded** ← Currently running (Step 1 COMPLETE, Steps 2–3 awaiting m4max)
2. Spurgeon (minimal corpus in archive, may skip)
3. MacArthur · Piper · Edwards · Calvin · Owen · Sproul

---

## Training Run: Ken-Expanded Corrector LoRA

**Start:** 2026-05-30 10:06 EDT  
**Architecture:** 40% Ken personal voice + 60% Reformed/Baptist archive theological breadth  
**Corpus Size:** 19,651 training samples

### Step 1 — Data Preparation ✅ COMPLETE

**Ken corpus (40% - Personal voice calibration):**
- Source: `/Volumes/1TB External/Projects/Romans/` (7,249 files)
- Samples: 7,861 after segmentation
- Role: Encodes Ken's sermon cadence, argument structure, theological priorities

**Archive corpus (60% - Theological breadth):**
- Source: `/Volumes/1TB External/openclaw-main/sermon-archive/_EXTERNAL-PREACHERS/`
- Preachers: 18 major voices (TGC 6,061 sermons, Mohler 3,449, Begg 3,064, MacArthur 769, etc.)
- Files: 20,128 sermon files total
- Samples collected: 43,559 → Used: 11,791 (stratified sample)
- Role: Anchors Ken's voice in broader Reformed/evangelical theology

**Final mixed corpus:**
- Total samples: 19,651 (10.4× original Ken-only corpus)
- Train/eval: 95/5 (18,668 train / 983 eval)
- Output: `~/lora-data/ken/train.jsonl`, `eval.jsonl`, `prep-report.json`

**Why this mix?**
- Ken-only (4M words) risked overfitting to one voice
- Archive-only would lose personal calibration
- 40/60 preserves Ken's distinctive patterns while grounding in tradition

### Step 2 — Sanity LoRA ⏳ READY (Awaiting m4max)

- **Config:** r=8, α=16, batch=2, lr=1e-4, steps=100
- **Data:** First 10k tokens from train.jsonl
- **Expected runtime:** 30 min on m4max
- **Pass criteria:** Loss decreasing, no NaN/Inf, eval perp ≤ 2× train perp
- **Status:** Data ready. Blocked: m4max SSH access (100.120.40.114 port 22 connection refused)

### Step 3 — Full LoRA Training ⏳ READY (After Step 2 Pass)

- **Config:** r=16, α=32, batch=4, lr=2e-5, epochs=2
- **Corpus:** Full 18,668 train samples (19.6k total with eval)
- **Expected runtime:** ~4 hrs on m4max
- **Output:** `~/lora-weights/ken/adapter.safetensors`
- **Status:** Ready to execute after sanity pass.

### Step 4 — Validation Gates (When Each Completes)

| Gate | Type | Status | Notes |
|------|------|--------|-------|
| Holdout sermon test | Ken-specific | Awaiting | 5–10 holdout sermons not in training |
| Drift detection (20 paraphrases, 18/20 flagged) | Ken-specific | Awaiting | Paraphrases from actual sermons |
| Cross-era stability (pre/mid/post-Romans, in-envelope) | Ken-specific | Awaiting | File dates + era markers |
| Cite-or-flag invariant | Universal | TBD | Every correction must have chunk ID |

---

## Current Status (2026-05-30 10:25 EDT)

✅ **Step 1 COMPLETE:** Data prepared and balanced
- **Ken samples:** 7,861 (from 7,249 files)
- **Archive samples:** 11,791 (from 20,128 files across 18 preachers)
- **Mixed corpus:** 19,651 total
- **Train/eval:** 18,668 / 983
- **Output:** `~/lora-data/ken/train.jsonl` + `eval.jsonl` + `prep-report.json`

⏳ **Steps 2–3 BLOCKED:** m4max not SSH-accessible
- Network reachable (ping 100.120.40.114 OK)
- SSH port 22: connection refused
- **Action needed:** Enable SSH on m4max, or provide alternative training endpoint

**Next:** Once m4max is reachable, run Step 2 sanity check (30 min) → Step 3 full training (4 hrs) → Step 4 validation (~1 hr)
- **ETA if m4max available now:** ~5.5 hrs wall-clock to validated Ken-Expanded LoRA

---

## Corpus Discovery (2026-05-30 10:12 EDT)

Found massive sermon archive in `/Volumes/1TB External/openclaw-main/sermon-archive/`:
- **20,127 sermons across 18 preachers**
- **48.2 million words**
- Includes: TGC (6,061), Mohler (3,449), Begg (3,064), MacArthur (769), Ascol (1,757), Akin (1,200), Mbewe (1,160), Noblit (728), Sproul (548), +8 more

This fundamentally changed the training strategy from Ken-only to Ken-Expanded.

---

## SEBTS Podcast Transcription ⏸ DEFERRED

- **Status:** Blocked on MP4 audio extraction (files are video containers)
- **30 files (3 GB) in `/Volumes/1TB External/Projects/Apple Podcasts/`**
- **Option:** Extract audio with ffmpeg, then transcribe, then create `sebts-exegesis` LoRA (Step 3.5)
- **Decision:** Defer until after Ken-Expanded LoRA completes (lower priority)

---

_Soli Deo Gloria._
