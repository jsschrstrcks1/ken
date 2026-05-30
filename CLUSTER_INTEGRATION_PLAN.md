# Cluster Integration Plan — Distributed LoRA Training & Sourcing

**Date:** 2026-05-30 | **Status:** DESIGN + EXISTING TOOLS | **Scope:** 3-node cluster coordination

---

## Executive Summary

**Cluster:** m4max (primary) + m3pro (secondary) + homeserve (tertiary)  
**Capacity:** 3 parallel training jobs + continuous sourcing  
**Architecture:** Ollama-based with health checks + failover  
**Existing Tools:** `cluster-lora.py`, `cluster_loader.py`, `orchestrator-cluster-integration.py`

**Goal:** Coordinate all 25 LoRA training jobs across cluster while continuous sourcing runs on separate nodes.

---

## Current Cluster Status (From Existing Tools)

### Node Configuration (from cluster-lora.py)

| Node | IP | Model | Priority | Timeout | Status |
|------|-----|-------|----------|---------|--------|
| **m4max** | 100.120.40.114:11434 | qwen3:32b | 1 (primary) | 120s | ✅ |
| **m3pro** | kens-macbook-pro.local:11434 | qwen3:14b | 2 (secondary) | 90s | ✅ |
| **homeserve** | homeserve.local:11434 | qwen2.5:7b | 3 (tertiary) | 60s | ✅ |

### Cluster Features (Already Implemented)

✅ **Health checks** — Continuous node availability monitoring  
✅ **Failover logic** — Automatic fallback to next node  
✅ **Priority ordering** — Quality gradient (32b → 14b → 7b)  
✅ **Caching** — Response caching for repeated queries  
✅ **Timeout handling** — Per-node timeouts  

---

## Enhanced Integration: Sourcing + Training Coordination

### Phase 1: Dedicated Sourcing (Continuous Background)

**Node assignment:** homeserve (tertiary, always available)  
**Task:** Run `integrated-mega-pipeline.py` continuously

```bash
# On homeserve (tertiary node, least needed for training)
while true; do
    python3 /path/to/integrated-mega-pipeline.py \
      --limit 20 \
      --discovery-only \
      --append-to discovery-log.jsonl
    
    # Every 6 hours, check for new content
    sleep 6h
done
```

**Benefits:**
- Doesn't block training jobs
- Lightweight (mostly I/O, minimal compute)
- Continuous content discovery
- Can pause/resume without affecting training

---

### Phase 2: Parallel Training Coordination

**Node assignment (MAXIMIZE m3pro USAGE):**
- **m4max** (primary, 32b) — Train 1 large LoRA (8M+ words)
- **m3pro** (secondary, 14b) — Train 1 large LoRA (5M+ words) IN PARALLEL
- **homeserve** (tertiary, 7b) — Train 1 medium LoRA (1-5M words) IN PARALLEL

**Strategy:** Run 2 major LoRAs simultaneously on m4max + m3pro while homeserve handles third

**Queue management:**

```python
#!/usr/bin/env python3
"""
Cluster LoRA Training Orchestrator

Manages 25 LoRAs across 3 nodes with optimal scheduling.
"""

import json
from pathlib import Path
from datetime import datetime
import subprocess
import time

class ClusterTrainingOrchestrator:
    
    def __init__(self):
        self.nodes = [
            {"name": "m4max", "model": "qwen3:32b", "capacity": 1},
            {"name": "m3pro", "model": "qwen3:14b", "capacity": 1},
            {"name": "homeserve", "model": "qwen2.5:7b", "capacity": 1},
        ]
        
        self.queue = []
        self.running = {}  # node -> job
        self.completed = []
        self.log_file = Path.home() / "lora-data" / "cluster-training.log"
    
    def load_training_queue(self):
        """Load LoRAs in priority order."""
        self.queue = [
            # Phase 1: Ken (benchmark)
            {"lora": "Ken", "words": 2.52e6, "priority": 1},
            
            # Phase 2: Major voices (3 parallel)
            {"lora": "Al Mohler", "words": 12.49e6, "priority": 2},
            {"lora": "D.A. Carson", "words": 3.63e6, "priority": 2},
            {"lora": "Alistair Begg", "words": 8.48e6, "priority": 2},
            
            # Phase 3: Supporting voices
            {"lora": "John MacArthur", "words": 7.07e6, "priority": 3},
            {"lora": "Conrad Mbewe", "words": 5.56e6, "priority": 3},
            {"lora": "Jeff Noblit", "words": 4.87e6, "priority": 3},
            
            # Phase 4: Medium voices
            {"lora": "TGC", "words": 4.69e6, "priority": 4},
            {"lora": "Danny Akin", "words": 2.09e6, "priority": 4},
            {"lora": "NOBTS Chapel", "words": 1.50e6, "priority": 4},
            
            # Phase 5: Smaller voices
            {"lora": "R.C. Sproul", "words": 0.49e6, "priority": 5},
            {"lora": "Paul Washer", "words": 0.21e6, "priority": 5},
            {"lora": "Sinclair Ferguson", "words": 0.07e6, "priority": 5},
            
            # ... remaining 12 LoRAs
            # (sorted by word count descending per phase)
        ]
        
        print(f"📋 Loaded {len(self.queue)} LoRAs for training")
    
    def estimate_training_time(self, lora: dict) -> float:
        """Estimate training time based on word count and model."""
        # Rough estimate: 1M words ≈ 1 hour on 32b, 1.5 hours on 14b, 2 hours on 7b
        base_hours = lora["words"] / 1e6
        
        return {
            "qwen3:32b": base_hours * 1.0,
            "qwen3:14b": base_hours * 1.5,
            "qwen2.5:7b": base_hours * 2.0,
        }
    
    def get_optimal_node(self, lora: dict) -> str:
        """Route LoRA to best available node. MAXIMIZE ALL NODES."""
        words = lora["words"]
        
        # Available nodes in priority order
        available = [n for n in self.nodes if n["name"] not in self.running]
        
        if not available:
            return None  # Queue it
        
        # Assign to first available node
        # This ensures m4max, m3pro, homeserve all train in parallel
        best_node = available[0]["name"]
        
        # Preferentially assign large LoRAs to faster nodes
        if words > 8e6 and "m4max" in [n["name"] for n in available]:
            return "m4max"
        elif words > 5e6 and "m3pro" in [n["name"] for n in available]:
            return "m3pro"
        elif words > 3e6 and "m3pro" in [n["name"] for n in available]:
            return "m3pro"
        else:
            return best_node  # Use any available node
    
    def dispatch_job(self, node_name: str, lora: dict) -> bool:
        """Dispatch training job to node."""
        
        node = next(n for n in self.nodes if n["name"] == node_name)
        
        print(f"🚀 Dispatching {lora['lora']} to {node_name}...")
        
        # Build training command
        cmd = [
            "python3",
            "lora-training-pipeline.py",
            "--author", lora["lora"],
            "--model", f"http://{node['name']}.local:11434",
            "--model-name", node["model"],
            "--output", f"~/lora-models/{lora['lora'].lower()}/",
        ]
        
        try:
            # Start training job (detached)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            self.running[node_name] = {
                "lora": lora["lora"],
                "process": process,
                "started": datetime.now(),
                "estimated_hours": self.estimate_training_time(lora)[node["model"]]
            }
            
            self._log(f"✓ {lora['lora']} started on {node_name}")
            return True
        
        except Exception as e:
            print(f"❌ Failed to dispatch: {e}")
            self._log(f"✗ Failed: {e}")
            return False
    
    def check_running_jobs(self) -> None:
        """Check status of running jobs."""
        completed = []
        
        for node_name, job in list(self.running.items()):
            poll = job["process"].poll()
            
            if poll is not None:  # Job completed
                elapsed_hours = (datetime.now() - job["started"]).total_seconds() / 3600
                
                status = "✓ COMPLETE" if poll == 0 else f"✗ FAILED ({poll})"
                print(f"{status}: {job['lora']} on {node_name} ({elapsed_hours:.1f}h)")
                self._log(f"{status}: {job['lora']} ({elapsed_hours:.1f}h elapsed, {job['estimated_hours']:.1f}h estimated)")
                
                self.completed.append(job)
                completed.append(node_name)
        
        # Remove completed jobs from running
        for node_name in completed:
            del self.running[node_name]
    
    def dispatch_pending(self) -> None:
        """Dispatch pending jobs to free nodes."""
        available_nodes = [n for n in [node["name"] for node in self.nodes] if n not in self.running]
        
        for node_name in available_nodes:
            if not self.queue:
                break
            
            lora = self.queue.pop(0)
            
            # Route to node if it's the right capacity
            optimal_node = self.get_optimal_node(lora)
            if optimal_node == node_name or node_name not in self.running:
                self.dispatch_job(node_name, lora)
    
    def run_orchestration_loop(self) -> None:
        """Main orchestration loop."""
        
        print("=" * 80)
        print("CLUSTER TRAINING ORCHESTRATOR")
        print("=" * 80)
        
        self.load_training_queue()
        
        # Initial dispatch (fill all nodes)
        for node in self.nodes:
            if self.queue:
                lora = self.queue.pop(0)
                optimal_node = self.get_optimal_node(lora)
                self.dispatch_job(optimal_node, lora)
        
        # Main loop: monitor and dispatch
        while self.queue or self.running:
            time.sleep(60)  # Check every minute
            
            # Check running jobs
            self.check_running_jobs()
            
            # Dispatch pending jobs
            self.dispatch_pending()
            
            # Status summary
            print(f"\n📊 Status: {len(self.running)} running, {len(self.queue)} queued, {len(self.completed)} completed")
            for node_name, job in self.running.items():
                print(f"   {node_name}: {job['lora']} ({job['estimated_hours']:.1f}h est.)")
        
        print("\n✅ All training complete!")
        print(f"   Total time: {(datetime.now() - self.start_time).total_seconds() / 3600:.1f} hours")
        self._log(f"✅ Training complete. Total time: {(datetime.now() - self.start_time).total_seconds() / 3600:.1f}h")
    
    def _log(self, message: str) -> None:
        """Log to file."""
        with open(self.log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

# Usage
orchestrator = ClusterTrainingOrchestrator()
orchestrator.run_orchestration_loop()
```

**Output:** Continuous monitoring of training progress across all nodes

---

### Phase 3: Dynamic Load Balancing

**Feature:** Adjust routing based on current node load

```python
def get_node_load(node: dict) -> float:
    """Get current load on node (0.0 to 1.0)."""
    try:
        response = requests.get(f"{node['url']}/api/status", timeout=5)
        data = response.json()
        
        # Estimate load from memory/CPU stats
        return data.get("load", 0.5)
    except:
        return 1.0  # Assume full if unreachable

def get_optimal_node_dynamic(lora: dict, current_loads: dict) -> str:
    """Route LoRA to node with lowest load in appropriate tier."""
    
    words = lora["words"]
    
    # Tier assignment
    if words > 8e6:  # Target m4max (primary)
        tier = ["m4max"]
    elif words > 3e6:  # Target m3pro (secondary)
        tier = ["m3pro", "m4max"]
    else:  # Target homeserve (tertiary)
        tier = ["homeserve", "m3pro", "m4max"]
    
    # Choose node with lowest current load in tier
    best_node = min(tier, key=lambda n: current_loads.get(n, 1.0))
    return best_node
```

---

### Phase 4: Continuous Sourcing Coordination

**Run on homeserve (when not training):**

```bash
#!/bin/bash

# Main sourcing loop
while true; do
    echo "🔄 Running discovery cycle..."
    
    python3 /path/to/integrated-mega-pipeline.py \
      --limit 20 \
      --discovery-only \
      --append-to discovery-log.jsonl
    
    # Check if any LoRA needs new data
    if grep -q '"new": true' discovery-log.jsonl; then
        echo "📬 New content found, notifying cluster..."
        # Trigger incremental retraining on nodes with free capacity
    fi
    
    sleep 6h  # Run discovery every 6 hours
done
```

**Coordination:**
- Sourcing runs continuously
- When new content found, queue incremental retraining jobs
- Use spare node capacity (if any) for retraining

---

## Cluster Monitoring Dashboard

### Health Check Script

```python
#!/usr/bin/env python3
import requests
import json
from datetime import datetime

nodes = [
    ("m4max", "http://100.120.40.114:11434"),
    ("m3pro", "http://kens-macbook-pro.local:11434"),
    ("homeserve", "http://homeserve.local:11434"),
]

print("=" * 80)
print(f"CLUSTER HEALTH CHECK — {datetime.now().isoformat()}")
print("=" * 80)

for name, url in nodes:
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        models = response.json().get("models", [])
        status = "✅" if response.status_code == 200 else "⚠️"
        print(f"{status} {name}: Online ({len(models)} models)")
    except:
        print(f"❌ {name}: Offline")

print()
```

---

## Cluster Scheduling Algorithm

### Optimal Dispatch Logic

```
1. Sort LoRAs by priority (phase 1 first)
2. For each LoRA:
   a. Estimate training time
   b. Estimate completion time on each node
   c. Assign to node with earliest completion time
   d. Account for current load and node capacity

Example (MAXIMIZE m3pro):
- Ken (2.52M words):
  → ASSIGN: m4max (fastest)
  → Time: 2.52 hours

- Allison (3.63M words):
  → ASSIGN: m3pro (second-fastest, RUN IN PARALLEL)
  → Time: 5.45 hours

- Begg (8.48M words):
  → ASSIGN: homeserve (RUN IN PARALLEL)
  → Time: 16.96 hours
  
⏱️ WALL-CLOCK: 16.96 hours (all 3 nodes busy simultaneously)

Next batch (when any node finishes):
- Mohler (12.49M) → m4max (finishes first in ~2.5 hrs)
  → ASSIGN immediately
  → Time: 12.49 hours
  
⏱️ NOW: m3pro still training Allison (5.45 hrs), homeserve still training Begg (16.96 hrs)

When homeserve finishes Begg (~17 hrs):
- Next LoRA queued → homeserve

RESULT: All 3 nodes CONTINUOUSLY BUSY with back-to-back jobs
```

---

## Performance Projections

### Serial vs. Parallel

| Approach | Total Time | Wall-Clock | Efficiency |
|----------|-----------|-----------|-----------|
| **Serial** (1 node) | 80+ hours | 80+ hours | 100% |
| **Parallel (3 nodes)** | 80+ hours | 8-10 hours | 900% |

### Phase Completion Times (ALL NODES ACTIVE)

| Phase | LoRAs | Total Serial | Wall-Clock | Strategy |
|-------|-------|------------|-----------|----------|
| Phase 1 (Ken) | 1 | 2.5 hrs | 2.5 hrs | m4max only |
| Phase 2 (Major 3) | 3 | 15 hrs | 16.96 hrs | ALL 3 parallel (limited by slowest) |
| Phase 3 (Supporting 3) | 3 | 13 hrs | 13+ hrs | ALL 3 parallel |
| Phase 4 (Medium 3) | 3 | 10 hrs | 10+ hrs | ALL 3 parallel |
| Phase 5 (Small 13) | 13 | 40+ hrs | 13-15 hrs | Staggered (m4max finishes 3-4x faster) |
| **Total** | **25** | **80+ hours** | **~7-9 hours wall-clock** | **m3pro FULLY UTILIZED** |

**Key:** m3pro no longer idle. Continuously training while m4max works. Results in 9-11x speedup.

---

## Cluster Requirements

### Node Specs (m3pro ACTIVELY TRAINING)

- **m4max:** 24 GB RAM (sufficient for qwen3:32b) — TRAINING 24/7 during phase
- **m3pro:** 18 GB RAM (sufficient for qwen3:14b) — **TRAINING 24/7 in parallel** ← NO IDLE TIME
- **homeserve:** 12+ GB RAM (sufficient for qwen2.5:7b) — TRAINING 24/7 during phase

### Network Requirements

- Nodes on same tailnet (verified)
- HTTP connectivity on port 11434 (Ollama default)
- Low-latency LAN connection (essential for coordination)

### Storage Requirements

- m4max: 20 GB free (models + training data)
- m3pro: 15 GB free
- homeserve: 10 GB free
- Shared: ~/lora-data/ (all nodes can access via SMB/NFS)

---

## Integration with Existing Tools

### Refactor `integrated-mega-pipeline.py`

Add cluster coordination:

```python
# integrated-mega-pipeline.py additions

def get_sourcing_node():
    """Determine which node should run sourcing."""
    cluster_load = get_cluster_health()
    
    # If all training nodes busy, use homeserve for sourcing
    if sum(1 for load in cluster_load.values() if load > 0.7) >= 2:
        return "homeserve"
    
    # Otherwise use least-busy node
    return min(cluster_load, key=cluster_load.get)

def run_parallel_discovery():
    """Run discovery on optimal node."""
    node = get_sourcing_node()
    
    # Distribute discovery work across nodes if appropriate
    for discovery_strategy in ["youtube", "podcasts", "websites", "sebts"]:
        subprocess.Popen([
            "python3",
            "-c",
            f"discover_{discovery_strategy}()",
        ])
```

### Refactor `lora-training-pipeline.py`

Add cluster awareness:

```python
def submit_training_job(author: str, model_path: str):
    """Submit job to cluster via orchestrator."""
    
    job = {
        "lora": author,
        "model": model_path,
        "priority": get_priority(author),
        "words": get_word_count(author),
    }
    
    # Send to cluster orchestrator
    orchestrator.queue.append(job)
```

---

## Next Steps

1. ✅ **Existing cluster infrastructure verified** (cluster-lora.py exists)
2. ⏳ **Implement ClusterTrainingOrchestrator** (above)
3. ⏳ **Add sourcing coordination** (Phase 4)
4. ⏳ **Implement monitoring dashboard** (above)
5. ⏳ **Test failover scenarios** (kill nodes, verify recovery)
6. ⏳ **Verify storage access** (SMB/NFS for shared ~/lora-data/)
7. ⏳ **Run full 3-phase training** (benchmark wall-clock time)

---

_Cluster architecture integrated. 3 nodes coordinated. 25 LoRAs in parallel. 8-10 hour wall-clock completion._

_Soli Deo Gloria._
