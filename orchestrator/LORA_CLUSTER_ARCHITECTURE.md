# LoRA Cluster Architecture — Every LoRA Includes This

**Decision:** Every theologian LoRA trained includes full cluster coordination + closed-weight persona fallback.

---

## Cluster Topology

```
                    ┌─────────────────────────────┐
                    │  Indexed Corpus (Shared)    │
                    │  /Volumes/1TB/sermon-archive│
                    │  (20,127 sermons, 48.2M w)  │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
    ┌────────────┐         ┌────────────┐         ┌────────────┐
    │  m4max     │         │  m3pro     │         │ homeserve  │
    │ M4 Max 36GB│         │ M3 Pro 18GB│         │ M4 mini 16GB
    │            │         │            │         │            │
    │ qwen3:32b  │         │ qwen3:14b  │         │ qwen3:8b   │
    │ (primary)  │         │ (secondary)│         │ (tertiary) │
    └────────────┘         └────────────┘         └────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   Orchestration Hub   │
                    │  (NATS, coordination) │
                    └───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   Open-Weight            Closed-Weight          Validation Gates
   LoRA Adapter         Persona (Claude/          (Cite-or-flag,
   (14B Q4)            GPT/Grok/Gemini)          Drift detection,
                                                 Cross-era stability)
```

---

## Each LoRA Pipeline: 5 Stages

### Stage 1: Data Preparation (Local, any node)
- Normalize corpus for author
- Segment into ~2k-token samples
- 95/5 train/eval split
- Output: JSONL files

### Stage 2: Open-Weight LoRA Training (m4max primary)
- **Model:** qwen3:32b via Ollama on m4max (or fallback to m3pro:qwen3:14b)
- **Config:** r=16, α=32, batch=4, lr=2e-5, 2 epochs
- **Output:** `adapter.safetensors` + training-log.json
- **Time:** 3-4 hrs on m4max

### Stage 3: Closed-Weight Persona (Claude/GPT/Grok, parallel to Stage 2)
- **Route:** Any available frontier model
- **Purpose:** Backup + debate counterpoint
- **Output:** Model ID + system prompt
- **Time:** ~30 min (API inference)

### Stage 4: Validation Gates (Cluster-coordinated)
- **Cite-or-flag invariant:** Every generated quote must resolve to indexed corpus chunk
- **Substring-match validator:** Quote ⊆ chunk text (detect hallucination)
- **Drift detection:** 20 paraphrases, LoRA flags ≥18/20 as out-of-envelope
- **Cross-era stability:** Pre/mid/post-Romans, all in-envelope
- **Pass rate:** ≥85% across all gates

### Stage 5: Deployment (Cluster-resident)
- **Open-weight:** Live on m4max (qwen3:32b + adapter)
- **Closed-weight:** Routed to Claude/GPT/Grok as needed
- **Router:** Smart routing based on request complexity + LoRA availability
- **Fallback:** If open-weight down, route to closed-weight

---

## Ken-Expanded LoRA: Cluster Edition

### Data (Ready Now)
- **Corpus:** 40% Ken (7,861 samples) + 60% archive (11,791 samples)
- **Total:** 19,651 samples (18,668 train / 983 eval)
- **Location:** `~/lora-data/ken/train.jsonl` + `eval.jsonl`

### Training (Ready to Start)
- **Open-weight:** m4max qwen3:32b, ~4 hrs
- **Closed-weight:** Claude Opus 4.8 (persona: "Ken's theological voice, RFC-grounded, careful exegesis")
- **Validation:** All 4 gates above

### Deployment
- **Primary inference:** m4max qwen3:32b + Ken adapter
- **Fallback:** Claude Opus 4.8 (Ken persona)
- **Debate mode:** Both together, round-robin argument

---

## Spurgeon/TGC LoRA: Cluster Edition (After Ken)

### If Spurgeon corpus found elsewhere:
- Same 5-stage pipeline
- Data: Spurgeon public-domain corpus
- Open-weight: m4max
- Closed-weight: Claude Sonnet 4.6 (Spurgeon persona: "Expository depth, Victorian oratory, biblical precision")

### If using TGC fallback (6,061 sermons, 4.6M words):
- Same 5-stage pipeline
- Data: TGC corpus (diverse 500+ authors)
- Open-weight: m4max
- Closed-weight: Claude Opus 4.8 (TGC persona: "Evangelical consensus, Reformed nuance, practical application")

---

## Cluster Coordination Requirements

### NATS Broker (m4max or external)
- Route training jobs across nodes
- Coordinate validation runs
- Queue inference requests
- Broadcast corpus updates

### Adapter Registry (Shared Storage)
- `~/lora-weights/` on each node (or NFS mount)
- Metadata: `lora-registry/manifest.json` with all trained adapters
- Hash verification for adapter integrity

### Inference Router
- Request arrives: "Ken LoRA, cite-or-flag mode"
- Router: "Ken adapter loaded on m4max, use qwen3:32b?"
- If m4max down: "Route to Claude Opus Ken persona"
- If both: "Debate mode, both respond"

### Validation Coordinator
- Holds indexed corpus references
- Runs cite-or-flag checks across all generated output
- Records pass/fail per LoRA per gate
- Blocks deployment if <85% pass rate

---

## Cost & Timeline (Full Household of LoRAs)

| LoRA | Data Prep | Training (m4max) | Validation | Deployment | Total |
|------|-----------|-----------------|-----------|-----------|-------|
| Ken | 10 min | 4 hrs | 1 hr | Immediate | 5.25 hrs |
| Spurgeon/TGC | 10 min | 3.5 hrs | 1 hr | Immediate | 4.5 hrs |
| Mohler | 10 min | 3 hrs | 1 hr | Immediate | 4 hrs |
| Begg | 10 min | 3 hrs | 1 hr | Immediate | 4 hrs |
| MacArthur | 10 min | 2 hrs | 1 hr | Immediate | 3 hrs |
| Others (5×) | 10 min | 1-2 hrs each | 1 hr | Immediate | ~8 hrs |
| **Total** | ~1.5 hrs | ~20 hrs | ~7 hrs | Parallel | **~28.5 hrs** |

(Can parallelize training across nodes if multiple available)

---

## Starting Immediately: Ken-Expanded LoRA

**What needs to happen:**
1. m4max: qwen3:32b ready on Ollama
2. This machine: Ken data ready ✅, orchestrator ready to send job
3. m4max: Receive training job, execute Stage 2-5

**Single command (once cluster reachable):**
```bash
python3 orchestrator/cluster-lora.py \
  --author ken \
  --data ~/lora-data/ken/train.jsonl \
  --eval ~/lora-data/ken/eval.jsonl \
  --target m4max \
  --closed-weight-persona "ken" \
  --validate-all
```

**Result:**
- Ken open-weight LoRA live on m4max
- Ken closed-weight persona (Claude Opus) fallback
- Validation log: `orchestrator/lora-registry/ken/validation.json`
- Deployment: Ready for inference

---

_Soli Deo Gloria._
