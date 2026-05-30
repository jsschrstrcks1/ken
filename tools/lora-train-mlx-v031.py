#!/usr/bin/env python3
"""
LoRA Training via MLX-LM v0.31+ — Llama-3.1-8B

Corrected for mlx-lm 0.31+ CLI arguments.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_MODEL = "Llama-3.1-8B"
LORA_WEIGHTS = Path.home() / "lora-weights"
LORA_WEIGHTS.mkdir(parents=True, exist_ok=True)

class LoRATrainer:
    def __init__(self, author: str, data_path: str, eval_path=None, sanity=False):
        self.author = author
        self.data_path = Path(data_path)
        self.eval_path = Path(eval_path) if eval_path else None
        self.sanity = sanity
        self.output_dir = LORA_WEIGHTS / author
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if sanity:
            self.config = {
                "r": 8,
                "alpha": 16,
                "batch_size": 2,
                "lr": 1e-4,
                "iters": 100,
            }
            self.run_name = f"{author}-sanity"
        else:
            self.config = {
                "r": 16,
                "alpha": 32,
                "batch_size": 4,
                "lr": 2e-5,
                "iters": 5000,
            }
            self.run_name = f"{author}-full"
    
    def validate_data(self) -> bool:
        """Check if training data is valid JSONL."""
        if not self.data_path.exists():
            print(f"❌ Training data not found: {self.data_path}")
            return False
        
        try:
            count = 0
            with open(self.data_path) as f:
                for line in f:
                    count += 1
                    json.loads(line)
            print(f"✅ Valid JSONL: {count} training samples")
            return True
        except Exception as e:
            print(f"❌ Invalid JSON: {e}")
            return False
    
    def build_mlx_command(self) -> list:
        """Build mlx-lm v0.31+ training command."""
        # mlx-lm 0.31+ uses: python -m mlx_lm lora [args]
        cmd = [
            "python3", "-m", "mlx_lm", "lora",
            "--model", BASE_MODEL,
            "--data", str(self.data_path),
            "--adapter-path", str(self.output_dir),
            "--batch-size", str(self.config["batch_size"]),
            "--learning-rate", str(self.config["lr"]),
            "--iters", str(self.config["iters"]),
            "--lora-dims", str(self.config["r"]),
        ]
        
        if self.eval_path:
            cmd.extend(["--val-batches", "10"])
        
        return cmd
    
    def train(self) -> bool:
        """Run training locally (blocking)."""
        print(f"\n🚀 Starting LoRA training: {self.run_name}")
        print(f"   Model: {BASE_MODEL}")
        print(f"   Data: {self.data_path}")
        print(f"   Output: {self.output_dir}")
        print(f"   Config: r={self.config['r']}, α={self.config['alpha']}, "
              f"batch={self.config['batch_size']}, lr={self.config['lr']}, "
              f"iters={self.config['iters']}")
        
        if not self.validate_data():
            return False
        
        cmd = self.build_mlx_command()
        
        print(f"\nCommand: {' '.join(cmd)}\n")
        
        try:
            start_time = datetime.now()
            result = subprocess.run(cmd, check=True)
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
            
            print(f"\n📝 Log saved: {log_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Training failed: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏸️  Training interrupted")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Train LoRA with mlx-lm v0.31+")
    parser.add_argument("--author", required=True, help="Author/model name")
    parser.add_argument("--data", required=True, help="Training data JSONL path")
    parser.add_argument("--eval", help="Eval data JSONL path")
    parser.add_argument("--sanity", action="store_true", help="Sanity check mode (100 iters)")
    
    args = parser.parse_args()
    
    trainer = LoRATrainer(
        author=args.author,
        data_path=args.data,
        eval_path=args.eval,
        sanity=args.sanity,
    )
    
    success = trainer.train()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
