#!/usr/bin/env python3
"""Check status of Anthropic fine-tuning job."""

import sys
import json
from anthropic import Anthropic

def check_status(job_id):
    """Check training job status."""
    client = Anthropic()
    
    job = client.beta.model_training.jobs.retrieve(job_id)
    
    print(f"📊 Job ID: {job_id}")
    print(f"📈 Status: {job.status}")
    print(f"🕐 Created: {job.created_at if hasattr(job, 'created_at') else 'unknown'}")
    
    if hasattr(job, 'trained_tokens'):
        print(f"📦 Tokens trained: {job.trained_tokens}")
    
    if job.status == "succeeded":
        print(f"\n✅ TRAINING COMPLETE!")
        print(f"🎁 Model name: {job.fine_tuned_model}")
        return job.fine_tuned_model
    elif job.status == "failed":
        print(f"\n❌ TRAINING FAILED")
        if hasattr(job, 'error'):
            print(f"Error: {job.error}")
    else:
        print(f"\n⏳ Still training...")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 anthropic-lora-status.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    check_status(job_id)
