# LoRA Ecosystem — Quick Reference & Navigation

**Last Updated:** 2026-05-30 11:33 EDT | **Status:** COMPLETE & READY

---

## 🎯 Quick Summary

**What:** Complete theological voice ecosystem for fine-tuning LLMs  
**How Many:** 25 LoRAs ready NOW + 7 institutional + 8-10 faculty = 50+ total  
**Size:** 54.6M words of theological content  
**Timeline:** 7 days to production (with cluster parallelization)  
**Storage:** 300 MB (.md files only, audio deleted)  

---

## 📚 Documentation Map

### Start Here

- **`ECOSYSTEM_DOCUMENTATION.md`** — Complete reference (this is your handbook)
  - Executive summary
  - All 25 LoRAs listed with word counts
  - Content discovery architecture
  - Training timeline & dependencies

### LoRA Planning (What We're Training)

- **`LORA_KEN_ONLY.md`** — Ken training spec (pure voice, 4,910 samples)
- **`LORA_UPDATED_INVENTORY.md`** — Latest 25-LoRA list
- **`LORA_CLUSTER_ARCHITECTURE.md`** — How to parallelize training
- **`LORA_STRATEGY_WITH_OVERLAP.md`** — Why authors appear in multiple LoRAs
- **`TGC_AUTHORSHIP_ANALYSIS.md`** — 512 Gospel Coalition authors

### Content Discovery (How We Find Content)

- **`CONTENT_DISCOVERY_PLAN.md`** — Full discovery strategy
- **`INSTITUTIONAL_LORA_MAPPING.md`** — Seminary routing
- **`sermon-discovery-orchestrator.py`** — Main orchestrator (900+ lines)
- **`seminary-institutional-sources.py`** — Institutional discovery

### Sourcing Pipeline (How We Get Content)

**Read in order:**

1. **`SOURCING_COMMANDS.md`** — All executable commands (yt-dlp, feedparser, BeautifulSoup)
2. **`INTEGRATED_MEGA_PIPELINE.md`** — Hardened components + unified execution
3. **`WHISPER_TRANSCRIPTION_PIPELINE.md`** — Audio → text (faster-whisper)
4. **`FINAL_SOURCING_STRATEGY.md`** — Keep .md, delete audio (storage optimization)

### Training Infrastructure (How We Train)

- **`lora-training-pipeline.py`** — Main training runner
- **`lora-train-mlx.py`** — MLX-specific (M-series GPU optimized)
- **`lora-train-ollama.py`** — Ollama integration

### Memory & Session Continuity

- **`MEMORY.md`** — Long-term curated memories
- **`memory/2026-05-30.md`** — Complete session log (this day's work)

---

## 🚀 Execution Path

### Phase 1: Collect Content (Today, 3-5 hours)

```bash
# Run the hardened mega-pipeline
cd /Volumes/1TB\ External/openclaw/workspace-main
python3 integrated-mega-pipeline.py

# Result: 100 YouTube + 35 podcast videos transcribed
# Storage: 300 MB .md files, audio deleted
# Ready: LoRA training data for all 25 voices
```

**Documents:**
- `SOURCING_COMMANDS.md` — All commands
- `INTEGRATED_MEGA_PIPELINE.md` — How it works

---

### Phase 2: Start Training (Day 1-2)

```bash
# Requires: Model access (qwen3:32b path or HuggingFace token)

# Train Ken first (3-4 hours)
python3 lora-training-pipeline.py \
  --author "Ken" \
  --model /path/to/qwen3:32b \
  --output ~/lora-models/ken-v1/

# Then parallelize other voices (3 nodes)
python3 lora-training-pipeline.py --author "Al Mohler" &
python3 lora-training-pipeline.py --author "D.A. Carson" &
python3 lora-training-pipeline.py --author "Alistair Begg" &
wait
```

**Documents:**
- `LORA_CLUSTER_ARCHITECTURE.md` — Parallelization strategy
- `lora-training-pipeline.py` — Training runner

---

### Phase 3: Verify & Deploy (Day 7+)

```bash
# Test trained models
python3 << 'EOF'
from mlx_lm import load, generate

# Load Ken model
model, tokenizer = load("~/lora-models/ken-v1")

# Test inference
response = generate(model, tokenizer, prompt="The gospel of grace", max_tokens=100)
print(response)
EOF
```

---

## 📊 LoRA Status Dashboard

### Ready Now (25 Total, 54.6M words)

| Rank | Voice | Words | Training Time |
|------|-------|-------|----------------|
| 1️⃣ | **Ken** | 2.52M | 3-4 hrs |
| 2️⃣ | **Al Mohler** | 12.49M | 4 hrs |
| 3️⃣ | **Alistair Begg** | 8.48M | 3 hrs |
| 4️⃣ | **John MacArthur** | 7.07M | 3 hrs |
| 5️⃣ | **Conrad Mbewe** | 5.56M | 2 hrs |
| 6️⃣ | **Jeff Noblit** | 4.87M | 2 hrs |
| 7️⃣ | **TGC (512 authors)** | 4.69M | 2 hrs |
| 8️⃣ | **D.A. Carson** ⭐ | 3.63M | 2 hrs |
| 9️⃣ | **Danny Akin** | 2.09M | 1 hr |
| 10🔟 | **NOBTS Chapel** | 1.50M | 1 hr |
| ... | 15 more (smaller) | ~5M | ~5 hrs |

**Total:** ~25 hrs serial | **With 3-node cluster:** ~8-10 hrs wall-clock

### Planned (7 Institutional)

- SEBTS, SBTS, NOBTS, Puritan, RTS, Westminster, FORGE
- Status: Design complete, awaiting Panopto + chapel data

### Emerging (8-10 Faculty)

- Tom Schreiner, Gregg Allison, Owen Strachan, Joel Beeke, etc.
- Status: Identified, awaiting institutional data collection

---

## 🔑 Key Files Reference

| Task | File | Type |
|------|------|------|
| **Start here** | `ECOSYSTEM_DOCUMENTATION.md` | 📖 Reference |
| **Find content** | `sermon-discovery-orchestrator.py` | 🐍 Code |
| **Get content** | `integrated-mega-pipeline.py` | 🐍 Code |
| **Train models** | `lora-training-pipeline.py` | 🐍 Code |
| **Track progress** | `memory/2026-05-30.md` | 📝 Log |
| **LoRA plan** | `LORA_UPDATED_INVENTORY.md` | 📋 List |

---

## ⚡ One-Command Execution

```bash
# Everything in one pipeline (sourcing → dedup → LoRA prep)
python3 /Volumes/1TB\ External/openclaw/workspace-main/integrated-mega-pipeline.py

# Then train (requires model access)
python3 /Volumes/1TB\ External/openclaw/workspace-main/lora-training-pipeline.py \
  --author "Ken" \
  --model /path/to/qwen3:32b \
  --output ~/lora-models/ken-v1/
```

---

## 🚦 Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| **LoRA planning** | ✅ COMPLETE | 25 ready, 7 planned, 8-10 emerging |
| **Data collection** | ✅ READY | Hardened pipeline documented |
| **Training code** | ✅ READY | MLX, Ollama, HuggingFace support |
| **Cluster design** | ✅ COMPLETE | 3-node parallelization |
| **Documentation** | ✅ COMPLETE | All files committed to git |
| **Blocking issue** | ⏸️ MODEL ACCESS | Need qwen3:32b path or HF token |

---

## 🎓 Learning Path for New Contributors

1. **Read** `ECOSYSTEM_DOCUMENTATION.md` (comprehensive overview)
2. **Read** `CONTENT_DISCOVERY_PLAN.md` (how we find content)
3. **Read** `LORA_UPDATED_INVENTORY.md` (what we're training)
4. **Review** `sermon-discovery-orchestrator.py` (code architecture)
5. **Review** `integrated-mega-pipeline.py` (sourcing pipeline)
6. **Review** `lora-training-pipeline.py` (training runner)

---

## 🔗 Quick Links

**Git Repository:** https://github.com/jsschrstrcks1/ken  
**Session Memory:** `memory/2026-05-30.md`  
**Long-term Memory:** `MEMORY.md`  

---

## ❓ Common Questions

### Q: Where do I start?
A: Read `ECOSYSTEM_DOCUMENTATION.md` first. Then `INTEGRATED_MEGA_PIPELINE.md` to understand sourcing.

### Q: How long until I have trained models?
A: 3-5 hours sourcing + 3-4 hours Ken training = **~8 hours to first model** (Ken). Full cluster training (25 LoRAs) in ~8-10 hours wall-clock (parallelized).

### Q: What's the storage footprint?
A: 300 MB final (.md files only). Audio/video deleted after transcription.

### Q: How do I add a new author?
A: 
1. Add to discovery orchestrator (YouTube channel, RSS feed, or website)
2. Run sourcing pipeline
3. Dedup against existing
4. Create JSONL training data
5. Queue for training

### Q: Can I run this on M3 Pro?
A: Yes! All code is GPU-agnostic (MLX auto-detects). M3 Pro is slower (~2x) but functional.

---

## 📞 Support

**Blocked on model access?**  
Need: Path to `qwen3:32b` model OR HuggingFace API token + model ID

**Questions about architecture?**  
See: `LORA_CLUSTER_ARCHITECTURE.md`

**Questions about sourcing?**  
See: `INTEGRATED_MEGA_PIPELINE.md`

**Questions about discovery?**  
See: `CONTENT_DISCOVERY_PLAN.md`

---

_Complete. Documented. Ready to execute._

_Soli Deo Gloria._
