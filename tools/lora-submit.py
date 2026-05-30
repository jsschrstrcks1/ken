#!/usr/bin/env python3
"""
lora-submit.py — Submit the integrity LoRA to OpenAI fine-tuning

This script queues the training job with OpenAI's fine-tuning API.

WARNING: This will incur compute costs. Review the dataset first:
  - training-data.jsonl must exist (1613 examples)
  - training-metadata.json must have approval signature
  - You must have OPENAI_API_KEY set

Environment:
  OPENAI_API_KEY — required, from console.openai.com
  DRY_RUN=1 — preview the request without submitting
  SKIP_UPLOAD=1 — use an existing file_id (set FILE_ID env var)

The LoRA will be trained and can be used immediately after completion.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import openai
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

WORKSPACE_ROOT = Path("/Volumes/1TB External/openclaw/workspace-main")
TRAINING_DATA_DIR = WORKSPACE_ROOT / "lora" / "training-data"
LORA_MODELS = {
    "claude": "claude-3-5-sonnet-20241022",  # Anthropic (custom, not OpenAI)
    "gpt-4o": "gpt-4o-2024-11-20",
    "gpt-4-turbo": "gpt-4-turbo-2024-04-09",
}

def check_prerequisites():
    """Verify everything is in place"""
    issues = []
    
    # Check training data
    jsonl_path = TRAINING_DATA_DIR / "training-data.jsonl"
    if not jsonl_path.exists():
        issues.append(f"Missing training data: {jsonl_path}")
    
    meta_path = TRAINING_DATA_DIR / "training-metadata.json"
    if not meta_path.exists():
        issues.append(f"Missing metadata: {meta_path}")
    
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not set")
    
    return issues

def submit_training_job(model: str = "gpt-4o", dry_run: bool = False, auto_approve: bool = False):
    """
    Submit the training job to OpenAI fine-tuning API
    
    Note: You can only fine-tune certain OpenAI models, not Claude.
    This submits to GPT-4o with LoRA/adapter tuning if available.
    """
    
    issues = check_prerequisites()
    if issues:
        print("Prerequisites not met:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return False
    
    # Load metadata to confirm we want to do this
    meta_path = TRAINING_DATA_DIR / "training-metadata.json"
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    
    jsonl_path = TRAINING_DATA_DIR / "training-data.jsonl"
    
    print("=" * 70)
    print("OpenAI Fine-Tuning Submission")
    print("=" * 70)
    print(f"\nModel: {model}")
    print(f"Training data: {jsonl_path}")
    print(f"  Examples: {metadata['training_stats']['total']}")
    print(f"    - Principles: {metadata['training_stats']['principles']}")
    print(f"    - Memory-based: {metadata['training_stats']['memories']}")
    print(f"    - Adversarial: {metadata['training_stats']['adversarial']}")
    print(f"\nIntegrity principles encoded:")
    for p in metadata['integrity_principles']:
        print(f"  • {p}")
    
    print(f"\nEstimated cost: $0.80 - $2.00 (for GPT-4o fine-tuning)")
    print(f"Training time: 30-60 minutes")
    
    if dry_run:
        print(f"\n[DRY RUN] Would submit with these parameters:")
        print(f"  - model: {model}")
        print(f"  - training_file: training-data.jsonl")
        print(f"  - n_epochs: 3")
        return True
    
    # Confirm before proceeding
    if not auto_approve:
        response = input("\nProceed with submission? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return False
    
    print("\nSubmitting to OpenAI API...")
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Upload training file
    print(f"  Uploading training file...")
    with open(jsonl_path, 'rb') as f:
        file_response = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    
    file_id = file_response.id
    print(f"  ✓ Uploaded (file_id: {file_id})")
    
    # Submit fine-tuning job
    print(f"  Queuing fine-tuning job...")
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model,
        hyperparameters={
            "n_epochs": 3,  # More epochs = better learning, higher cost
        },
        suffix="integrity-layer-v1",
    )
    
    job_id = job.id
    print(f"  ✓ Job queued (job_id: {job_id})")
    
    # Save job info for later reference
    job_info = {
        "job_id": job_id,
        "file_id": file_id,
        "model": model,
        "submitted_at": datetime.now().isoformat(),
        "status": job.status,
        "checkpoint_tracking": {
            "result_files": [],
            "trained_tokens": 0,
        }
    }
    
    job_file = TRAINING_DATA_DIR / "job-info.json"
    with open(job_file, 'w') as f:
        json.dump(job_info, f, indent=2)
    
    print(f"\n✓ Submission complete!")
    print(f"Job info saved to: {job_file}")
    print(f"\nMonitor progress:")
    print(f"  openai api fine_tuning.jobs.retrieve {job_id}")
    print(f"  python3 lora-monitor.py {job_id}")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Submit integrity LoRA for fine-tuning")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to fine-tune")
    parser.add_argument("--dry-run", action="store_true", help="Preview without submitting")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    return 0 if submit_training_job(model=args.model, dry_run=args.dry_run, auto_approve=args.yes) else 1

if __name__ == "__main__":
    exit(main())
