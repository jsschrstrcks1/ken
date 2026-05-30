# LoRA Training — Infrastructure Blocker

**Status:** 2026-05-30 10:13 EDT — Data prepared, training blocked

## What's Ready ✅

- **Ken-Expanded corpus:** 19,651 samples (18,668 train / 983 eval)
  - 40% Ken personal voice (7,861 samples)
  - 60% archive theological breadth (11,791 samples)
  - Location: `~/lora-data/ken/train.jsonl` + `eval.jsonl`
  - Validation: 18,668 JSONL records confirmed valid

- **Complete LoRA trainer:** `tools/lora-train-mlx.py`
  - Supports local OR remote (cluster) training
  - Sanity check mode (r=8, 100 steps)
  - Full training mode (r=16, 2 epochs)
  - Logging + validation built-in

- **Spurgeon LoRA prep:** Ready to follow Ken after Ken completes

## What's Blocked ❌

### Training Infrastructure Not Accessible

**mlx-lm (local):**
- Not installed locally
- Cannot import: `ModuleNotFoundError: No module named 'mlx_lm'`
- Would need: `pip install mlx_lm`

**Remote nodes (m4max, m3pro):**
- m4max (100.120.40.114): Network reachable, SSH port 22 connection refused
- m3pro (kens-macbook-pro.local): SSH port 22 connection refused
- **Solution needed:** Enable SSH on one or both nodes, OR provide alternative

**Ollama local:**
- Is running (http://localhost:11434 reachable)
- Has qwen3:8b available
- **BUT:** Does not support LoRA fine-tuning via API (only inference)

## Three Paths Forward

### Path 1: Enable SSH on m4max (Recommended)
```bash
# On m4max, enable SSH:
sudo systemsetup -setremotelogin on
# Or: System Settings → General → Sharing → Remote Login

# Then from here:
python3 tools/lora-train-mlx.py train --author ken \
  --data ~/lora-data/ken/train.jsonl \
  --eval ~/lora-data/ken/eval.jsonl \
  --node m4max
```
- **Time to train:** ~4 hrs wall-clock (Ken sanity + full + Spurgeon)
- **Status:** Waiting for Ken's action

### Path 2: Install mlx-lm Locally
```bash
pip install mlx-lm
python3 tools/lora-train-mlx.py train --author ken \
  --data ~/lora-data/ken/train.jsonl \
  --eval ~/lora-data/ken/eval.jsonl
```
- **Time to install:** ~10 min
- **Time to train:** ~8 hrs wall-clock (local machine slows down during)
- **Status:** Ready to execute if Ken approves local training

### Path 3: Cloud-Based Training
- HuggingFace training endpoint?
- Replicate API?
- Other cloud LLM service?
- **Status:** Pending Ken's preference

## What I Can Do Right Now

- ✅ Continue corpus work (Spurgeon, MacArthur, etc.)
- ✅ Build validation gates (drift detection, cite-or-flag)
- ✅ Prepare sermon-archive metadata (index, organize)
- ✅ SEBTS podcast transcription (once MP4→audio extraction resolved)
- ❌ Actually train LoRA (blocked on infrastructure)

## Decision Needed from Ken

**Choose one:**
1. Enable SSH on m4max and I'll train immediately
2. Approve `pip install mlx-lm` for local training
3. Suggest alternative cloud training service
4. Defer training until infrastructure is available

**Data is ready. Trainer is built. Awaiting go signal on infrastructure.**

---

_Soli Deo Gloria._
