#!/usr/bin/env python3
"""
Auto-transcribe Discord audio attachments using OpenAI Whisper API.
Run via cron or as a daemon to watch for new audio files.
"""
import os
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_WATCH_DIR = Path.home() / ".openclaw" / "audio-inbox"
TRANSCRIPT_DIR = Path.home() / ".openclaw" / "transcripts"
PROCESSED_LOG = Path.home() / ".openclaw" / "transcripts" / ".processed"

def ensure_dirs():
    """Create necessary directories."""
    AUDIO_WATCH_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not PROCESSED_LOG.exists():
        PROCESSED_LOG.touch()

def get_processed_files():
    """Load list of already-transcribed files."""
    if not PROCESSED_LOG.exists():
        return set()
    with open(PROCESSED_LOG, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def mark_processed(filename):
    """Mark a file as transcribed."""
    with open(PROCESSED_LOG, 'a') as f:
        f.write(f"{filename}\n")

def transcribe_audio(audio_path):
    """
    Transcribe audio file using OpenAI Whisper API.
    Returns transcript text or None on failure.
    
    Optimizations:
    - temperature=0.0: Most deterministic (exact transcription)
    - language=en: Hint to Whisper it's English
    - 120s timeout: Allows for larger files
    """
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return None
    
    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X", "POST",
                "https://api.openai.com/v1/audio/transcriptions",
                "-H", f"Authorization: Bearer {OPENAI_API_KEY}",
                "-F", f"file=@{audio_path}",
                "-F", "model=whisper-1",
                "-F", "language=en",
                "-F", "temperature=0.0"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "text" in data:
                return data["text"]
            else:
                print(f"ERROR: Unexpected API response: {data}", file=sys.stderr)
                return None
        else:
            print(f"ERROR: curl failed: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"ERROR: Transcription failed for {audio_path}: {e}", file=sys.stderr)
        return None

def main():
    """Main loop: watch for audio files and transcribe."""
    ensure_dirs()
    processed = get_processed_files()
    
    audio_extensions = {'.mp3', '.m4a', '.ogg', '.wav', '.flac', '.webm'}
    
    for audio_file in AUDIO_WATCH_DIR.glob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
            if audio_file.name in processed:
                continue
            
            print(f"Transcribing: {audio_file.name}")
            transcript = transcribe_audio(audio_file)
            
            if transcript:
                # Save transcript
                transcript_path = TRANSCRIPT_DIR / f"{audio_file.stem}.txt"
                with open(transcript_path, 'w') as f:
                    f.write(transcript)
                
                print(f"✓ Saved: {transcript_path}")
                print(f"Transcript:\n{transcript}\n")
                
                # Mark as processed
                mark_processed(audio_file.name)
                
                # Optional: Delete the source audio after transcription
                # audio_file.unlink()
            else:
                print(f"✗ Failed to transcribe: {audio_file.name}")

if __name__ == "__main__":
    main()
