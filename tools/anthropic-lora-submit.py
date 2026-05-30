#!/usr/bin/env python3
"""
Anthropic LoRA Fine-Tuning Submission
Trains the 1,665-example integrity + Romans dataset on Claude 3.5 Sonnet
"""

import json
import sys
import os
from pathlib import Path

import anthropic

def load_training_data(dataset_path):
    """Load JSONL training data."""
    examples = []
    with open(dataset_path, 'r') as f:
        for line in f:
            examples.append(json.loads(line))
    return examples

def convert_to_anthropic_format(examples):
    """
    Convert OpenAI JSONL format to Anthropic fine-tuning format.
    
    Anthropic expects:
    {
        "custom_id": "unique-id",
        "params": {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    }
    """
    anthropic_examples = []
    for i, example in enumerate(examples):
        # Handle both OpenAI format and our custom format
        if "messages" in example:
            messages = example["messages"]
        else:
            # Fallback: construct from prompt/completion
            messages = [
                {"role": "user", "content": example.get("prompt", "")},
                {"role": "assistant", "content": example.get("completion", "")}
            ]
        
        anthropic_examples.append({
            "custom_id": f"integrity-lora-{i:06d}",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "messages": messages
            }
        })
    
    return anthropic_examples

def submit_for_training(examples, dataset_name="integrity-lora-v1-romans"):
    """Submit to Anthropic for fine-tuning."""
    client = anthropic.Anthropic()
    
    # Convert to Anthropic format
    anthropic_examples = convert_to_anthropic_format(examples)
    
    print(f"📊 Dataset: {dataset_name}")
    print(f"📦 Examples: {len(anthropic_examples)}")
    
    # Create temporary JSONL file for upload
    temp_file = f"/tmp/{dataset_name}.jsonl"
    with open(temp_file, 'w') as f:
        for example in anthropic_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"📝 Temp file: {temp_file}")
    
    # Upload file
    print("📤 Uploading to Anthropic...")
    with open(temp_file, 'rb') as f:
        file_response = client.beta.files.upload(
            file=(dataset_name + ".jsonl", f, "application/jsonl"),
        )
    
    file_id = file_response.id
    print(f"✅ File uploaded: {file_id}")
    
    # Submit for fine-tuning
    print("🚀 Submitting for fine-tuning...")
    job_response = client.beta.model_training.jobs.create(
        model="claude-3-5-sonnet-20241022",
        training_type="supervised",
        hyperparameters={
            "epochs": 3,
            "learning_rate": 0.0001,
            "batch_size": 8,
        },
        training_file=file_id,
    )
    
    job_id = job_response.id
    print(f"✅ Training job submitted: {job_id}")
    print(f"📊 Status: {job_response.status}")
    
    # Save job info
    job_info = {
        "job_id": job_id,
        "file_id": file_id,
        "dataset": dataset_name,
        "examples": len(anthropic_examples),
        "status": job_response.status,
        "model": "claude-3-5-sonnet-20241022",
        "created_at": str(job_response.created_at) if hasattr(job_response, 'created_at') else "unknown"
    }
    
    with open(f"/Volumes/1TB External/Projects/lora/anthropic-job-{job_id}.json", 'w') as f:
        json.dump(job_info, f, indent=2)
    
    print(f"\n💾 Job info saved: anthropic-job-{job_id}.json")
    print(f"\n🔗 Track status with: python3 tools/anthropic-lora-status.py {job_id}")
    
    return job_id

def main():
    dataset_path = "/Volumes/1TB External/Projects/lora/training-data/lora-v1-romans-integrity.jsonl"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        sys.exit(1)
    
    print("🔄 Loading training data...")
    examples = load_training_data(dataset_path)
    print(f"✅ Loaded {len(examples)} examples")
    
    print("\n" + "="*60)
    print("ANTHROPIC LoRA FINE-TUNING SUBMISSION")
    print("="*60)
    
    job_id = submit_for_training(examples)
    
    print("\n" + "="*60)
    print(f"✅ JOB SUBMITTED: {job_id}")
    print("="*60)
    print("\nYour LoRA is training. Check status with:")
    print(f"  python3 tools/anthropic-lora-status.py {job_id}")

if __name__ == "__main__":
    main()
