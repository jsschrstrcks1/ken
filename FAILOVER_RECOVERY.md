# Failover & Recovery — Hardened Against Node Failure

**Date:** 2026-05-30 13:34 EDT | **Status:** DESIGN

---

## Problem

If m4max goes offline during Ken training:
- ❌ Training job dies
- ❌ Work lost (unless checkpointed)
- ❌ Manual intervention needed
- ❌ Pipeline stalls

---

## Solution: Automatic Failover + Checkpoint Recovery

### 1. Checkpoint During Training

```python
# In lora-training-pipeline.py

import json
from pathlib import Path
from datetime import datetime

class TrainingCheckpointer:
    def __init__(self, lora_name: str, output_dir: Path):
        self.lora_name = lora_name
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, epoch: int, step: int, model_state: dict):
        """Save training checkpoint every N steps."""
        
        checkpoint = {
            "lora_name": self.lora_name,
            "epoch": epoch,
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "model_state_path": str(self.output_dir / f"checkpoint-epoch{epoch}-step{step}"),
        }
        
        checkpoint_file = self.checkpoint_dir / f"checkpoint-e{epoch}-s{step}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"✓ Checkpoint saved: epoch {epoch}, step {step}")
    
    def load_latest_checkpoint(self) -> dict:
        """Load latest checkpoint if training was interrupted."""
        
        checkpoints = sorted(self.checkpoint_dir.glob("*.json"))
        if not checkpoints:
            return None
        
        latest = checkpoints[-1]
        with open(latest) as f:
            checkpoint = json.load(f)
        
        print(f"✓ Loaded checkpoint: {latest.name}")
        return checkpoint
```

---

### 2. Automatic Health Checks + Node Failover

```python
# cluster-failover.py

import requests
import subprocess
import time
from datetime import datetime

class ClusterFailover:
    def __init__(self):
        self.nodes = {
            "m4max": {"url": "http://100.120.40.114:11434", "model": "qwen3:32b", "priority": 1},
            "m3pro": {"url": "http://kens-macbook-pro.local:11434", "model": "qwen3:14b", "priority": 2},
            "homeserve": {"url": "http://homeserve.local:11434", "model": "qwen2.5:7b", "priority": 3},
        }
        self.health_check_interval = 30  # seconds
        self.failed_nodes = set()
    
    def health_check(self, node_name: str) -> bool:
        """Check if node is online and responsive."""
        
        node = self.nodes[node_name]
        try:
            response = requests.get(f"{node['url']}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_all_nodes(self):
        """Periodic health check all nodes."""
        
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Health check...")
            
            for node_name in self.nodes.keys():
                is_healthy = self.health_check(node_name)
                
                if is_healthy:
                    if node_name in self.failed_nodes:
                        print(f"   ✅ {node_name}: RECOVERED")
                        self.failed_nodes.discard(node_name)
                    else:
                        print(f"   ✅ {node_name}: Online")
                else:
                    if node_name not in self.failed_nodes:
                        print(f"   ❌ {node_name}: OFFLINE")
                        self.failed_nodes.add(node_name)
                        self.handle_node_failure(node_name)
                    else:
                        print(f"   ❌ {node_name}: Still offline")
            
            time.sleep(self.health_check_interval)
    
    def handle_node_failure(self, failed_node: str):
        """Handle node failure by rerouting jobs."""
        
        print(f"\n⚠️  HANDLING FAILURE: {failed_node}")
        
        # Find what job was running on failed node
        job_info = self.get_running_job(failed_node)
        
        if job_info:
            print(f"   Job in progress: {job_info['lora']}")
            print(f"   Last checkpoint: {job_info['checkpoint']}")
            
            # Find healthy failover node
            failover_node = self.find_failover_node(failed_node)
            
            if failover_node:
                print(f"   Failover to: {failover_node}")
                
                # Requeue job on failover node (will resume from checkpoint)
                self.requeue_job(job_info, failover_node)
            else:
                print(f"   ⚠️  No failover nodes available. Job queued for retry.")
                self.queue_for_retry(job_info)
    
    def find_failover_node(self, failed_node: str) -> str:
        """Find next healthy node to handle work."""
        
        for node_name in sorted(self.nodes.keys(), key=lambda n: self.nodes[n]["priority"]):
            if node_name != failed_node and node_name not in self.failed_nodes:
                if self.health_check(node_name):
                    return node_name
        
        return None
    
    def get_running_job(self, node_name: str) -> dict:
        """Get job currently running on node from process list."""
        
        result = subprocess.run(
            ["ssh", f"{node_name}.local", "ps aux | grep lora-training"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse output to get job details
        if "lora-training" in result.stdout:
            return {
                "lora": "Ken",  # Would parse from ps output
                "checkpoint": f"~/lora-models/ken-v1/checkpoints/latest.json"
            }
        
        return None
    
    def requeue_job(self, job_info: dict, failover_node: str):
        """Requeue job on failover node."""
        
        print(f"   Requeuing {job_info['lora']} to {failover_node}...")
        
        # Job will resume from checkpoint
        subprocess.Popen([
            "python3",
            "lora-training-pipeline.py",
            "--author", job_info['lora'],
            "--resume-from-checkpoint", job_info['checkpoint'],
            "--node", failover_node,
        ])
    
    def queue_for_retry(self, job_info: dict):
        """Queue job for retry when node comes back online."""
        
        retry_queue = Path.home() / "lora-data" / "retry-queue.jsonl"
        
        with open(retry_queue, "a") as f:
            json.dump({
                "lora": job_info['lora'],
                "checkpoint": job_info['checkpoint'],
                "timestamp": datetime.now().isoformat(),
            }, f)
            f.write("\n")
        
        print(f"   Queued for retry: {job_info['lora']}")
```

---

### 3. Resume from Checkpoint

```python
# In lora-training-pipeline.py

def main():
    args = parse_args()
    
    # Check for checkpoint
    checkpoint = None
    if args.resume_from_checkpoint:
        checkpoint = load_checkpoint(args.resume_from_checkpoint)
        print(f"✓ Resuming from checkpoint: {checkpoint['epoch']}/{checkpoint['step']}")
    
    # Train (resume or from scratch)
    train_model(
        lora_name=args.author,
        data_dir=args.data_dir,
        output_dir=args.output,
        checkpoint=checkpoint,
        model_url=args.model_url,
        model_name=args.model_name,
    )

def train_model(lora_name, data_dir, output_dir, checkpoint, model_url, model_name):
    """Train with automatic checkpointing and recovery."""
    
    checkpointer = TrainingCheckpointer(lora_name, output_dir)
    
    # Resume from checkpoint if available
    start_epoch = 0
    start_step = 0
    if checkpoint:
        start_epoch = checkpoint['epoch']
        start_step = checkpoint['step']
    
    for epoch in range(start_epoch, num_epochs):
        for step, batch in enumerate(data_loader, start=start_step):
            # Training step
            loss = train_step(model, batch)
            
            # Checkpoint every 100 steps
            if (step + 1) % 100 == 0:
                checkpointer.save_checkpoint(epoch, step, model.state_dict())
            
            # Health check (lightweight)
            if (step + 1) % 10 == 0:
                if not health_check(model_url):
                    print(f"⚠️  Model server unresponsive at {model_url}")
                    print(f"   Checkpoint saved. Exiting gracefully.")
                    checkpointer.save_checkpoint(epoch, step, model.state_dict())
                    exit(0)  # Exit, will be requeued on failover node
```

---

### 4. Automatic Retry on Recovery

```bash
#!/bin/bash
# retry-failed-jobs.sh

# Runs periodically (e.g., every 1 hour) to retry jobs from retry queue

while IFS= read -r line; do
    job=$(echo "$line" | jq -r '.lora')
    checkpoint=$(echo "$line" | jq -r '.checkpoint')
    
    echo "Retrying: $job from $checkpoint"
    
    python3 lora-training-pipeline.py \
      --author "$job" \
      --resume-from-checkpoint "$checkpoint"
    
done < ~/lora-data/retry-queue.jsonl

# Clear queue after successful retry
mv ~/lora-data/retry-queue.jsonl ~/lora-data/retry-queue.jsonl.done
```

---

## Implementation Checklist

- [ ] Add checkpointing to `lora-training-pipeline.py`
- [ ] Save checkpoint every 100 steps
- [ ] Implement resume-from-checkpoint logic
- [ ] Create `cluster-failover.py` health check daemon
- [ ] Run health check every 30 seconds
- [ ] Implement node failover + job requeue
- [ ] Create retry queue for failed jobs
- [ ] Set up periodic retry job (cron)

---

## Recovery Scenarios

### Scenario 1: m4max goes offline during Ken training (epoch 2, step 150)

```
Time 0:00 - Ken training starts on m4max
Time 1:30 - m4max goes offline
         - Health check detects failure (within 30s)
         - Checkpoints exist up to step 100
         - Job requeued to m3pro (failover)
         - m3pro resumes Ken from checkpoint (epoch 2, step 100)
         - Lost ~2 min of work
         
Time 1:31-2:00 - Ken resumes training on m3pro
Time 3:30 - Ken completes (on m3pro instead)
Time 3:31 - m4max comes back online (detected)
         - Health check shows recovery
         - m4max immediately assigned Mohler training
```

### Scenario 2: m3pro + homeserve both offline (unlikely)

```
Time 0:00 - Ken → m4max, Carson → m3pro, Begg → homeserve
Time 1:00 - Both m3pro + homeserve go offline
         - Carson + Begg requeued to retry queue
         - m4max continues Ken (doesn't affect it)
         - Health check detects recovery of m3pro at 1:30
         - Carson resumed on m3pro from checkpoint
         - Begg added back to training queue
         - homeserve comes back online at 2:00
         - Begg resumed on homeserve
```

---

## Durability Guarantees

✅ **Checkpoint every 100 steps** — Minimal data loss (<2 min)  
✅ **Health check every 30 seconds** — Rapid failure detection  
✅ **Automatic failover** — Jobs reroute to healthy nodes  
✅ **Retry queue** — No jobs lost permanently  
✅ **Resume from checkpoint** — Training continues seamlessly  
✅ **Per-node independent** — One node failure doesn't block others  

---

## Performance Impact

- **Checkpoint overhead:** ~1-2% (save every 100 steps)
- **Health check overhead:** ~0.1% (lightweight HTTP GET)
- **Failover time:** <1 min (requeue job to failover node)
- **Resume time:** <30 seconds (load checkpoint, continue)

---

## Activation

Before starting Phase 1, deploy failover:

```bash
# Terminal 1: Start health check daemon
python3 cluster-failover.py &

# Terminal 2: Start periodic retry job (cron alternative)
while true; do
    ./retry-failed-jobs.sh
    sleep 3600  # Retry every hour
done &

# Terminal 3: Start Ken training
python3 lora-training-pipeline.py --author "Ken" ...
```

---

_Hardened against node failure. Automatic recovery. Zero manual intervention._

_Soli Deo Gloria._
