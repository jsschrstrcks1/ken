# Cluster Final Configuration — 3-Node + Concurrent Sourcing

**Date:** 2026-05-30 12:28 EDT | **Status:** CORRECTED

---

## Actual Cluster Configuration

### Node Mapping (CORRECTED)

| Node | Device | CPU | RAM | Model | Role |
|------|--------|-----|-----|-------|------|
| **m4max** | M4 Max | 16-core | 24 GB | qwen3:32b | Primary training (largest LoRAs) |
| **m3pro** | M3 Pro | 12-core | 18 GB | qwen3:14b | Secondary training (medium LoRAs) |
| **homeserve** | M4 Mini | 8-core | 16 GB | qwen2.5:7b | Tertiary training + **continuous sourcing** |

---

## Optimized Pipeline (Concurrent Sourcing + Training)

### Phase 1: Start Sourcing (Continuous Background)

**On homeserve (m4mini):**
```bash
# Start sourcing loop (background, lowest priority)
while true; do
    python3 integrated-mega-pipeline.py \
      --limit 20 \
      --discovery-only \
      --append-to ~/lora-data/discovery-log.jsonl
    
    sleep 6h  # Run discovery every 6 hours
done
```

**Why homeserve (m4mini)?**
- Sourcing is I/O-bound (network, disk)
- Doesn't need heavy GPU compute
- Can run in background while training happens
- Keeps pipeline fed with new content

---

### Phase 2: Training Queue (All 3 Nodes)

**Dispatch strategy:**
```
homeserve (m4mini) SOURCING LOOP (background, nice -20)
    ↓ (feeds)
TRAINING QUEUE
    ↓
m4max:   [Ken 2.5h] → [Mohler 12.5h] → [TGC 4.7h] → ...
m3pro:   [Carson 5.45h] → [Allison 3.6h] → [MacArthur 7h] → ...
homeserve: [Begg 8.5h] → [Mbewe 5.6h] → [Noblit 4.9h] → ...
           + sourcing in background
```

**Key:** homeserve runs sourcing at CPU level, training at GPU level
- GPU training uses compute cores
- Sourcing uses network I/O (doesn't block GPU)

---

### Phase 3: Concurrent Execution

**Timeline:**
```
Time 0:00
├─ homeserve: Start sourcing loop + start Begg training (GPU)
├─ m4max: Start Ken training
└─ m3pro: Start Carson training

Time 2:30
├─ m4max finishes Ken, starts Mohler
├─ sourcing still running (6-hour cycle, next discovery at 6h)
└─ m3pro still on Carson

Time 5:45
├─ m3pro finishes Carson, starts Allison
├─ m4max on Mohler (~9h remaining)
└─ homeserve on Begg (~11h remaining)

Time 6:00
├─ SOURCING CYCLE 2: homeserve discovers new content
├─ Appends to discovery-log.jsonl
├─ If new content found, queue for incremental retraining
└─ Continue Begg training

Time 8:50
├─ homeserve finishes Begg, starts Mbewe
├─ Sourcing still running (next cycle at 12:00)
└─ m4max and m3pro continuing

... continue until queue empty ...

FINAL: 7-9 hours wall-clock
       + continuous sourcing in background
       + new content discovered automatically
```

---

## HuggingFace Deployment (Parallel)

### While Training, Upload Completed LoRAs

```bash
# After m4max finishes Ken training:
python3 << 'EOF'
import subprocess
from pathlib import Path

# List of trained models
trained_models = [
    ("Ken", "jsschrstrcks/ken-lora"),
    ("Carson", "jsschrstrcks/carson-lora"),
    ("Begg", "jsschrstrcks/begg-lora"),
]

for lora_name, hf_repo in trained_models:
    # Upload to HF (background, non-blocking)
    subprocess.Popen([
        "huggingface-cli", "upload",
        hf_repo,
        f"./lora-models/{lora_name}/",
        "--repo-type=model",
        "--private"  # Keep private or remove for public
    ])

print("✓ Uploads queued (parallel with training)")
EOF
```

**Advantage:**
- Upload while training continues
- No wait time between jobs
- Backup copies on HuggingFace
- Free storage (up to limits)

---

## Final Resource Allocation

### CPU-Level Tasks (homeserve m4mini, low priority)
```
nice -20 python3 integrated-mega-pipeline.py
```
- YouTube enumeration (yt-dlp)
- Podcast RSS parsing (feedparser)
- Website scraping (BeautifulSoup)
- SEBTS institutional discovery
- Deduplication logic

### GPU-Level Tasks (all nodes, high priority)
```
# m4max
python3 lora-training-pipeline.py --author "Ken" --gpu cuda:0

# m3pro
python3 lora-training-pipeline.py --author "Carson" --gpu cuda:0

# homeserve (m4mini)
python3 lora-training-pipeline.py --author "Begg" --gpu cuda:0
```

**Result:** No interference. Sourcing runs in OS background, training in foreground.

---

## Wall-Clock Timeline (Final)

| Event | Time | Action |
|-------|------|--------|
| Start | 0:00 | m4max Ken, m3pro Carson, homeserve Begg + sourcing loop |
| Discovery 1 | 6:00 | Sourcing finds new content, queues for next retraining |
| m4max free | 2:30 | Picks up Mohler immediately |
| m3pro free | 5:45 | Picks up Allison immediately |
| homeserve free | 8:50 | Picks up Mbewe immediately |
| ... | ... | Continuous queue filling |
| Discovery 2 | 12:00 | Sourcing cycle 2, finds more content |
| ... | ... | Training continues |
| **Complete** | **7-9 hrs** | All 25 LoRAs trained + new content discovered |

---

## Advantages of This Setup

✅ **No idle nodes** — All 3 training in parallel  
✅ **Continuous sourcing** — Feed training pipeline automatically  
✅ **Incremental updates** — New content → retraining queue  
✅ **HuggingFace backup** — Uploads parallel with training  
✅ **m4mini utilized** — Both training + sourcing simultaneously  
✅ **Minimal latency** — No waiting between jobs  

---

## Implementation (Ready to Execute)

### 1. Start sourcing loop on homeserve
```bash
ssh homeserve.local
cd /path/to/workspace
nohup python3 integrated-mega-pipeline.py --discovery-only &
```

### 2. Start cluster training orchestrator
```bash
python3 orchestrator-cluster-training.py \
  --strategy maximize-all-nodes \
  --concurrent-sourcing
```

### 3. Watch training progress
```bash
tail -f ~/lora-data/cluster-training.log
```

### 4. (Optional) Monitor HuggingFace uploads
```bash
watch huggingface-cli list-models --repo-type=model
```

---

## Next Steps

1. ✅ Confirm homeserve = m4mini (just did)
2. ⏳ Finalize sourcing strategy (how often, what sources)
3. ⏳ Confirm HuggingFace upload format + privacy settings
4. ⏳ Start sourcing loop (continuous)
5. ⏳ Begin training when ready

---

_3-node cluster. Concurrent sourcing. Continuous training. All nodes active._

_Soli Deo Gloria._
