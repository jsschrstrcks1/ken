# LoRA Training Log — Theologian Model Build

**Status:** In Progress (Started 2026-05-30 10:06 EDT)
**Base Model:** Llama-3.1-8B
**Training Node:** m4max (available upon request; currently using local)
**Validation Gate:** §13.5 — cite-or-flag, adversarial, cross-era stability

---

## Priority Sequence (Per Plan + SEBTS Extension)

1. **Ken** ← Currently running (Step 1 DONE, Step 2 blocked on m4max SSH)
2. **SEBTS-Exegesis** ← NEW (Step 1 in progress: 30 podcast files transcribing via Whisper API)
3. Spurgeon (awaiting corpus)
4. MacArthur · Piper · Edwards · Calvin · Owen · Sproul

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

## Training Run: SEBTS-Exegesis LoRA

**Start:** 2026-05-30 10:08 EDT  
**Architecture:** Corrector LoRA (exegesis strengthening, not voice)
**Training Material:** Southeastern Baptist Theological Seminary chapel + lecture recordings

### Step 1 — Podcast Transcription ⏸️ BLOCKED

- **Source:** `/Volumes/1TB External/Projects/Apple Podcasts/` (30 files, 3 GB total)
- **Format issue:** Files are MP4 video containers; Whisper API expects audio-only or handles mixed better with ffmpeg preprocessing
- **Blocker:** Need to extract audio streams from MP4s before transcription
- **Alternative:** Use local m3pro Whisper + ffmpeg pipeline (more reliable for video sources)
- **Status:** Awaiting decision — extract locally (needs ffmpeg) vs. cloud pipeline (needs video→audio conversion)
- **Queue file:** `~/lora-data/sebts-exegesis/transcription-queue.json` (4 failures logged)

### Step 2 — Transcript Cleaning & Segmentation ⏸️ BLOCKED (Waiting on Step 1)

- **Input:** 30 .txt transcripts from Whisper (pending)
- **Process:** Strip filler words, segment by exegetical pericope, deduplicate
- **Output:** `train.jsonl` / `eval.jsonl` (95/5 split)
- **Expected samples:** 500-1,000 (depending on lecture length)

### Step 3 — LoRA Training ⏸️ BLOCKED (Waiting on Steps 1–2)

- **Config:** r=16, α=32, batch=4, lr=2e-5, epochs=2 (same as Ken)
- **Objective:** Exegesis-aware correction (detect weak hermeneutics, flag eisegesis)
- **Expected runtime:** ~2 hrs on m4max
- **Status:** Queued after Ken LoRA completes

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

**Action items:**
1. **Ken LoRA (CRITICAL):** Data ready (Step 1 ✅). Need m4max SSH access or cloud training endpoint to proceed with Steps 2–3.
2. **SEBTS Transcription:** Blocked on MP4 audio extraction. Options:
   - ✓ Extract audio locally with ffmpeg, then transcribe
   - ✓ Use m3pro Whisper (hardened pipeline per MEMORY.md)
   - ✓ Defer to after Ken training (lower priority)
3. **Next priority:** Get Ken LoRA training running (m4max or alternative) — this is the foundational validator.

**Timeline estimate:**
- If m4max available: Ken (3 hrs) → SEBTS (2 hrs) → done by ~16:00 EDT today
- If m4max unavailable: Ken blocked; SEBTS requires audio extraction preprocessing

---

_Soli Deo Gloria._
