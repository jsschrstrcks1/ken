# LoRA Training — Final Status & Next Steps

**Date:** 2026-05-30 10:18 EDT  
**Status:** Ken-Expanded data ready. Training infrastructure identified but needs model setup.

---

## ✅ What's Complete

### Ken-Expanded Corpus (19,651 samples)
- **40% Ken personal voice** (7,861 samples from Romans repo)
- **60% archive theological breadth** (11,791 samples from 18 preachers: TGC, Mohler, Begg, MacArthur, Ascol, Akin, Mbewe, Noblit, Sproul, +9)
- **Files ready:**
  - `~/lora-data/ken/train.jsonl` (18,668 samples)
  - `~/lora-data/ken/eval.jsonl` (983 samples)
  - `~/lora-data/ken/prep-report.json` (audit trail)

### Training Infrastructure
- ✅ **mlx-lm 0.31.3** installed locally
- ✅ **LoRA trainer scripts** built (`tools/lora-train-mlx.py`, `tools/lora-train-mlx-v031.py`)
- ✅ **Validation gates** designed (drift detection, cite-or-flag, cross-era stability)
- ✅ **Queue planning** done (Ken → Spurgeon/TGC → Mohler → Begg → MacArthur → rest)

---

## ❌ What's Blocked

### Missing Model for Training

**Problem:**
- mlx-lm needs a base model (Llama-3.1-8B requested, but doesn't exist locally or on HF with auth)
- Local Ollama has `qwen3:8b` (inference-only, not in MLX format)
- HF API errors when trying to download (401 Unauthorized)

**Solutions needed (Ken chooses one):**

1. **Point to local MLX model on m4max**
   - Ken said "you have a model installed on that machine"
   - If model path is `/path/to/model` on m4max, use that
   - **What I need:** Path to the model directory

2. **Provide HuggingFace access token**
   - If needed for private/gated models
   - Set `HF_TOKEN` env var
   - Re-run training

3. **Use Ollama's qwen3:8b**
   - Train via Ollama API instead of mlx-lm
   - Different process (would need to script around Ollama's fine-tuning limitations)
   - Simpler but slower

4. **Download & convert a model**
   - `python -m mlx_lm convert Qwen/Qwen2.5-7B` (open, no auth needed)
   - Takes ~30 min
   - Then train with converted model

---

## ⏱️ Timeline (Once Model is Available)

| Step | Time | What |
|------|------|------|
| Ken sanity LoRA | 30 min | r=8, 100 iters, 10k tokens |
| Ken full LoRA | 3-4 hrs | r=16, 2 epochs, full corpus |
| Ken validation | 1 hr | Drift detection, cite-or-flag, era-stability |
| **Ken total** | **~5.5 hrs** | Ready to deploy |
| Spurgeon/TGC prep | 10 min | Convert corpus to JSONL |
| Spurgeon/TGC LoRA | 3-4 hrs | Full training |
| **Spurgeon/TGC total** | **~3.5 hrs** | Ready to deploy |

**If model ready now:** Ken LoRA done by ~15:30 EDT, Spurgeon/TGC by ~19:00 EDT

---

## Next Step: Your Input

**I need one of these:**

A. **Model path on m4max:**  
   "The model is at `/path/to/qwen3-mlx` or similar"  
   → I'll reconfigure trainer and start immediately

B. **HF token:**  
   "Here's `hf_xxxxxx`"  
   → I'll set it and retry download

C. **Use Ollama:**  
   "Train via Ollama instead of mlx-lm"  
   → I'll build an Ollama-based trainer

D. **Download & convert:**  
   "Go ahead and download Qwen2.5-7B, convert it, train"  
   → Will take ~1 hr setup, then training starts

---

## What's Committed

- ✅ Ken-Expanded corpus (19.6k samples, balanced)
- ✅ Complete LoRA training pipeline (mlx-lm compatible)
- ✅ Validation framework (drift, cite-or-flag, era-stability)
- ✅ Queue plan (Ken → Spurgeon/TGC → Mohler → Begg → MacArthur → rest)
- ✅ Documentation (all blockers, solutions, timeline)

---

_**Everything is ready. Just need model path or access token. Ken, your move.**_

_Soli Deo Gloria._
