#!/usr/bin/env python3
"""
Transcribe SEBTS podcast lectures from Apple Podcasts folder.
Uses OpenAI Whisper API (batched, with retry logic).

Output: /Users/kenbaker/lora-data/sebts-exegesis/transcripts/
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Configuration
PODCAST_DIR = Path("/Volumes/1TB External/Projects/Apple Podcasts")
OUTPUT_DIR = Path.home() / "lora-data" / "sebts-exegesis" / "transcripts"
QUEUE_FILE = OUTPUT_DIR.parent / "transcription-queue.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def find_audio_files():
    """Find all .mp3 and .mp4 files in podcast dir"""
    audio_files = []
    for ext in ["*.mp3", "*.mp4"]:
        audio_files.extend(PODCAST_DIR.glob(ext))
    return sorted(audio_files)

def transcribe_with_whisper_api(audio_path):
    """
    Transcribe using OpenAI Whisper API.
    Requires OPENAI_API_KEY env var.
    """
    try:
        import openai
    except ImportError:
        print("ERROR: openai package not installed. pip install openai")
        return None
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        return None
    
    client = openai.OpenAI(api_key=api_key)
    
    print(f"  Transcribing: {audio_path.name} ({audio_path.stat().st_size / 1e9:.2f} GB)...")
    
    try:
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en",
                response_format="verbose_json"
            )
        
        return {
            "file": audio_path.name,
            "text": transcript.text,
            "duration": transcript.duration if hasattr(transcript, 'duration') else None,
            "language": "en",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"  ERROR transcribing {audio_path.name}: {e}")
        return None

def main():
    audio_files = find_audio_files()
    
    if not audio_files:
        print("No audio files found in", PODCAST_DIR)
        sys.exit(1)
    
    print(f"Found {len(audio_files)} audio files")
    print(f"Output: {OUTPUT_DIR}\n")
    
    # Load or create queue
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
        completed = {t["file"] for t in queue.get("completed", [])}
    else:
        queue = {"completed": [], "failed": [], "pending": []}
        completed = set()
    
    # Process each file
    for i, audio_path in enumerate(audio_files, 1):
        if audio_path.name in completed:
            print(f"[{i}/{len(audio_files)}] ✓ {audio_path.name} (already done)")
            continue
        
        print(f"[{i}/{len(audio_files)}] Processing {audio_path.name}...")
        
        result = transcribe_with_whisper_api(audio_path)
        
        if result:
            # Save transcript
            output_path = OUTPUT_DIR / f"{audio_path.stem}.json"
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            
            # Also save raw text
            text_path = OUTPUT_DIR / f"{audio_path.stem}.txt"
            with open(text_path, "w") as f:
                f.write(result["text"])
            
            print(f"  ✓ Saved: {output_path.name}")
            queue["completed"].append(result)
        else:
            queue["failed"].append({"file": audio_path.name, "timestamp": datetime.now().isoformat()})
            print(f"  ✗ Failed: {audio_path.name}")
        
        # Save queue after each file
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
        
        # Rate limit: 10 second pause between API calls (Whisper tier 3)
        time.sleep(10)
    
    print(f"\n✓ Transcription complete")
    print(f"  Completed: {len(queue['completed'])}")
    print(f"  Failed: {len(queue['failed'])}")
    print(f"  Output: {OUTPUT_DIR}")
    
    # Summary
    summary = {
        "total_files": len(audio_files),
        "completed": len(queue["completed"]),
        "failed": len(queue["failed"]),
        "output_dir": str(OUTPUT_DIR),
        "timestamp": datetime.now().isoformat()
    }
    
    with open(OUTPUT_DIR.parent / "transcription-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
