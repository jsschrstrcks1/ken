#!/usr/bin/env python3
"""
LoRA Training via MLX-LM — Llama-3.1-8B on m4max cluster node

Trains a LoRA adapter using mlx-lm on a specified cluster node.
Can run locally or delegate to m4max/m3pro depending on availability.

Usage:
  python3 lora-train-mlx.py --author ken --data ~/lora-data/ken/train.jsonl \\
                            --eval ~/lora-data/ken/eval.jsonl \\
                            --node m4max

  # Sanity check (10k tokens, r=8):
  python3 lora-train-mlx.py --author ken --data ~/lora-data/ken/train.jsonl \\
                            --sanity --steps 100

  # Status:
  python3 lora-train-mlx.py status
"""

import json
import sys
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Configuration
BASE_MODEL = "Llama-3.1-8B"  # Must be installed in mlx_lm format
WORKSPACE = Path("/Volumes/1TB External/openclaw/workspace-main")
LORA_WEIGHTS = Path.home() / "lora-weights"
LORA_WEIGHTS.mkdir(parents=True, exist_ok=True)

NODES = {
    "m4max": "100.120.40.114",
    "m3pro": "kens-macbook-pro.local",
    "homeserve": "homeserve.local",
}

class LoRATrainer:
    def __init__(self, author: str, data_path: str, eval_path: Optional[str] = None,
                 node: str = "auto", sanity: bool = False):
        self.author = author
        self.data_path = Path(data_path)
        self.eval_path = Path(eval_path) if eval_path else None
        self.node = node
        self.sanity = sanity
        self.output_dir = LORA_WEIGHTS / author
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Hyperparameters
        if sanity:
            self.config = {
                "r": 8,
                "alpha": 16,
                "batch_size": 2,
                "lr": 1e-4,
                "epochs": 1,
                "steps": 100,
                "data_limit": 10000,  # 10k tokens only
            }
            self.run_name = f"{author}-sanity"
        else:
            self.config = {
                "r": 16,
                "alpha": 32,
                "batch_size": 4,
                "lr": 2e-5,
                "epochs": 2,
                "steps": None,  # Let it run to completion
                "data_limit": None,
            }
            self.run_name = f"{author}-full"
    
    def validate_data(self) -> bool:
        """Check if training data exists and is valid JSONL."""
        if not self.data_path.exists():
            print(f"❌ Training data not found: {self.data_path}")
            return False
        
        try:
            count = 0
            with open(self.data_path) as f:
                for line in f:
                    count += 1
                    if not count % 100:
                        print(f"  Validating... {count} lines", end="\r")
                    json.loads(line)
            print(f"✅ Valid JSONL: {count} training samples")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.data_path}: {e}")
            return False
    
    def check_mlx_lm(self) -> bool:
        """Check if mlx-lm is installed and accessible."""
        try:
            result = subprocess.run(
                ["python3", "-c", "import mlx_lm; print(mlx_lm.__version__)"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"✅ mlx-lm installed: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ mlx-lm import failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ mlx-lm check failed: {e}")
            return False
    
    def build_mlx_command(self) -> list:
        """Build the mlx-lm training command."""
        cmd = [
            "python3", "-m", "mlx_lm.lora",
            "--model", BASE_MODEL,
            "--train",
            "--data", str(self.data_path),
            "--output-dir", str(self.output_dir),
            "--lora-r", str(self.config["r"]),
            "--lora-alpha", str(self.config["alpha"]),
            "--batch-size", str(self.config["batch_size"]),
            "--learning-rate", str(self.config["lr"]),
            "--epochs", str(self.config["epochs"]),
        ]
        
        if self.eval_path:
            cmd.extend(["--val-data", str(self.eval_path)])
        
        if self.config.get("steps"):
            cmd.extend(["--max-steps", str(self.config["steps"])])
        
        return cmd
    
    def train_local(self) -> bool:
        """Run training locally (blocking)."""
        print(f"\n🚀 Starting local LoRA training: {self.run_name}")
        print(f"   Output: {self.output_dir}")
        print(f"   Config: r={self.config['r']}, α={self.config['alpha']}, "
              f"batch={self.config['batch_size']}, lr={self.config['lr']}")
        
        if not self.validate_data():
            return False
        
        if not self.check_mlx_lm():
            print("❌ mlx-lm not available locally")
            return False
        
        cmd = self.build_mlx_command()
        
        print(f"\nCommand: {' '.join(cmd)}\n")
        
        try:
            start_time = datetime.now()
            result = subprocess.run(cmd, check=True, capture_output=False, text=True)
            end_time = datetime.now()
            
            elapsed = (end_time - start_time).total_seconds()
            hours = elapsed / 3600
            
            print(f"\n✅ Training complete in {hours:.2f} hours")
            
            # Log result
            log_entry = {
                "author": self.author,
                "run": self.run_name,
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "elapsed_seconds": elapsed,
                "config": self.config,
                "output_dir": str(self.output_dir),
                "adapter_path": str(self.output_dir / "adapter.safetensors"),
            }
            
            log_path = self.output_dir / "training-log.json"
            with open(log_path, "w") as f:
                json.dump(log_entry, f, indent=2)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Training failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏸️  Training interrupted by user")
            return False
    
    def train_remote(self, node: str) -> bool:
        """Delegate training to a cluster node via SSH."""
        if node not in NODES:
            print(f"❌ Unknown node: {node}")
            return False
        
        host = NODES[node]
        print(f"\n🚀 Delegating training to {node} ({host})")
        print(f"   Model: {BASE_MODEL}")
        print(f"   Data: {self.data_path}")
        
        # Copy data to remote
        print(f"\n📤 Copying training data to {node}...")
        remote_data_dir = f"~/{self.author}-training-data"
        
        try:
            # Create remote dir
            subprocess.run(
                ["ssh", f"kenbaker@{host}", "mkdir", "-p", remote_data_dir],
                check=True, capture_output=True
            )
            
            # Copy files
            subprocess.run(
                ["scp", str(self.data_path), f"kenbaker@{host}:{remote_data_dir}/train.jsonl"],
                check=True, capture_output=True
            )
            
            if self.eval_path:
                subprocess.run(
                    ["scp", str(self.eval_path), f"kenbaker@{host}:{remote_data_dir}/eval.jsonl"],
                    check=True, capture_output=True
                )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to copy data: {e}")
            return False
        
        # Build remote command
        cmd = [
            "ssh", f"kenbaker@{host}",
            "python3", "-m", "mlx_lm.lora",
            "--model", BASE_MODEL,
            "--train",
            "--data", f"{remote_data_dir}/train.jsonl",
            "--output-dir", f"~/lora-weights/{self.author}",
            "--lora-r", str(self.config["r"]),
            "--lora-alpha", str(self.config["alpha"]),
            "--batch-size", str(self.config["batch_size"]),
            "--learning-rate", str(self.config["lr"]),
            "--epochs", str(self.config["epochs"]),
        ]
        
        if self.eval_path:
            cmd.extend(["--val-data", f"{remote_data_dir}/eval.jsonl"])
        
        print(f"\n🔄 Running on {node}...")
        print(f"Command: {' '.join(cmd[3:])}\n")
        
        try:
            result = subprocess.run(cmd, check=True)
            print(f"\n✅ Training complete on {node}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Training failed: {e}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Train LoRA adapters with mlx-lm")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Train subcommand
    train_parser = subparsers.add_parser("train", help="Train a LoRA")
    train_parser.add_argument("--author", required=True, help="Author/model name")
    train_parser.add_argument("--data", required=True, help="Training data JSONL path")
    train_parser.add_argument("--eval", help="Eval data JSONL path")
    train_parser.add_argument("--node", default="auto", help="Node: m4max, m3pro, homeserve, or auto")
    train_parser.add_argument("--sanity", action="store_true", help="Sanity check (10k tokens, 100 steps)")
    
    # Status subcommand
    status_parser = subparsers.add_parser("status", help="Check training status")
    
    args = parser.parse_args()
    
    if args.command == "train":
        trainer = LoRATrainer(
            author=args.author,
            data_path=args.data,
            eval_path=args.eval,
            node=args.node,
            sanity=args.sanity,
        )
        
        if args.node == "auto" or args.node not in NODES:
            success = trainer.train_local()
        else:
            success = trainer.train_remote(args.node)
        
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        print("LoRA training status:")
        for author_dir in sorted(LORA_WEIGHTS.iterdir()):
            if not author_dir.is_dir():
                continue
            
            log_file = author_dir / "training-log.json"
            if log_file.exists():
                with open(log_file) as f:
                    log = json.load(f)
                print(f"\n{log['author']} ({log['run']}):")
                print(f"  Elapsed: {log['elapsed_seconds'] / 3600:.2f} hours")
                print(f"  Output: {log['adapter_path']}")
                if Path(log['adapter_path']).exists():
                    size_mb = Path(log['adapter_path']).stat().st_size / 1e6
                    print(f"  Size: {size_mb:.1f} MB")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
