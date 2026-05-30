# Whisper + Cleanup Pipeline — Minimal Storage

**Convert audio → text → DELETE immediately. Keep only transcripts.**

---

## Optimized Workflow

```python
#!/usr/bin/env python3
"""
Audio Transcription + Immediate Cleanup

Process:
  1. Download audio (YouTube/podcast)
  2. Transcribe with Whisper
  3. Save transcript (.txt)
  4. DELETE audio file immediately
  5. Save metadata (JSON)
  
Result: Only text files remain, no audio/video kept.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

def transcribe_and_cleanup(audio_url, author_name, source_type):
    """
    Download → Transcribe → Delete audio → Keep only text
    """
    
    temp_dir = Path("/tmp/whisper-temp")
    temp_dir.mkdir(exist_ok=True)
    
    output_dir = Path.home() / "lora-data" / "transcriptions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Download
    print(f"📥 Downloading: {author_name}...", end=" ", flush=True)
    
    audio_file = temp_dir / f"temp-{datetime.now().timestamp()}.mp3"
    
    if source_type == "youtube":
        cmd_download = [
            'yt-dlp', '-f', 'bestaudio/best', '-x', '--audio-format', 'mp3',
            audio_url,
            '-o', str(audio_file)
        ]
    elif source_type == "podcast":
        import urllib.request
        urllib.request.urlretrieve(audio_url, audio_file)
    
    try:
        if source_type == "youtube":
            subprocess.run(cmd_download, capture_output=True, timeout=300)
        
        # Step 2: Transcribe
        print(f"🎙️ Transcribing...", end=" ", flush=True)
        
        transcript_file = output_dir / f"{author_name}-{datetime.now().timestamp()}.txt"
        
        result = subprocess.run([
            'whisper',
            str(audio_file),
            '--model', 'base',
            '--output_format', 'txt',
            '--output_dir', str(output_dir),
            '--fp16',  # 16-bit precision (faster, less RAM)
            '--device', 'cuda:0'  # Use GPU
        ], capture_output=True, timeout=3600)
        
        # Step 3: READ transcript
        if transcript_file.exists():
            with open(transcript_file) as f:
                transcript_text = f.read()
            
            word_count = len(transcript_text.split())
            
            # Save metadata (lightweight)
            metadata = {
                "author": author_name,
                "source": source_type,
                "timestamp": datetime.now().isoformat(),
                "words": word_count,
                "model": "whisper-base",
                "language": "en",
                "original_url": audio_url
            }
            
            metadata_file = output_dir / f"{author_name}-{datetime.now().timestamp()}-metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✓ {word_count} words")
            
            # Step 4: DELETE audio immediately
            if audio_file.exists():
                os.remove(audio_file)
                print(f"   🗑️  Cleaned up audio file")
            
            return {
                "status": "success",
                "transcript_file": str(transcript_file),
                "metadata_file": str(metadata_file),
                "words": word_count,
                "storage_mb": 0  # Audio deleted
            }
        
    except Exception as e:
        print(f"✗ Error: {e}")
        # Still delete audio on error
        if audio_file.exists():
            os.remove(audio_file)
    
    return {"status": "failed", "storage_mb": 0}


# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("=" * 80)
print("WHISPER TRANSCRIPTION + CLEANUP PIPELINE")
print("=" * 80)

# Example usage
youtube_videos = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "al-mohler-sermon-1"),
    ("https://www.youtube.com/watch?v=9bZkp7q19f0", "al-mohler-sermon-2"),
]

podcast_episodes = [
    ("https://example.com/podcast/episode1.mp3", "truthforlife-ep1"),
    ("https://example.com/podcast/episode2.mp3", "truthforlife-ep2"),
]

results = []

# Process YouTube
for url, author in youtube_videos:
    result = transcribe_and_cleanup(url, author, "youtube")
    results.append(result)

# Process podcasts
for url, author in podcast_episodes:
    result = transcribe_and_cleanup(url, author, "podcast")
    results.append(result)

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

successful = [r for r in results if r.get("status") == "success"]
failed = [r for r in results if r.get("status") == "failed"]

print(f"\n✅ Successful transcriptions: {len(successful)}")
print(f"❌ Failed: {len(failed)}")
print(f"📊 Total words transcribed: {sum(r.get('words', 0) for r in successful)}")
print(f"💾 Storage used: ~{sum(r.get('storage_mb', 0) for r in results)} MB (audio deleted)")
print(f"📁 Transcripts saved: {Path.home() / 'lora-data' / 'transcriptions'}")

```

---

## Cleanup Strategies

### Strategy 1: Delete After Transcription (RECOMMENDED)

```python
# After each transcription succeeds
if transcript_exists:
    os.remove(audio_file)  # Delete immediately
    print(f"✓ Transcribed. Audio deleted.")
```

**Storage:** ~200 bytes per transcript (text only)

---

### Strategy 2: Batch Process + Delete

```bash
#!/bin/bash

# 1. Download batch of audios
mkdir -p /tmp/audio-batch
yt-dlp -j --flat-playlist https://www.youtube.com/@albertmohler > videos.json
# Download first 10 videos
python3 << 'EOF'
import json, subprocess
videos = json.load(open('videos.json'))
for v in videos[:10]:
    subprocess.run(['yt-dlp', '-f', 'bestaudio', '-x', '--audio-format', 'mp3', 
                    f'https://www.youtube.com/watch?v={v["id"]}',
                    '-o', '/tmp/audio-batch/%(title)s.%(ext)s'])
EOF

# 2. Transcribe all
for file in /tmp/audio-batch/*.mp3; do
    whisper "$file" --model base --output_format txt --output_dir ~/lora-data/transcriptions
done

# 3. Delete entire batch
rm -rf /tmp/audio-batch

echo "✓ Batch processed. All audio deleted."
```

**Storage:** Minimal (only transcripts)

---

### Strategy 3: Stream + Process + Delete

```python
# For very large collections, stream process
import subprocess
from pathlib import Path

audio_queue = Path("/tmp/audio-stream")
transcript_output = Path.home() / "lora-data" / "transcriptions"

for audio_file in audio_queue.glob("*.mp3"):
    
    # Transcribe
    subprocess.run(['whisper', str(audio_file), '--model', 'base', ...])
    
    # Delete immediately (don't wait for batch)
    audio_file.unlink()
    
    print(f"✓ Transcribed + deleted: {audio_file.name}")
```

**Storage:** Always minimal (streaming cleanup)

---

## Disk Space Estimation

| Source | Count | Avg Duration | Audio Size | Transcript Size | Final Storage |
|--------|-------|--------------|-----------|-----------------|---------------|
| YouTube (100 videos) | 100 | 45 min | 30 MB each | 2 MB each | **200 MB** |
| Podcasts (35 episodes) | 35 | 60 min | 40 MB each | 3 MB each | **105 MB** |
| **Total** | **135** | **50 min avg** | **~4.5 GB temp** | **~675 MB** | **~300 MB** |

**With cleanup:** Only ~300 MB final (transcripts only)  
**Without cleanup:** ~4.5 GB (audio files persisted)

---

## Execution Commands

### Quick Start (Auto-Cleanup)

```bash
# 1. Download + Transcribe + Delete (all-in-one)
python3 << 'EOF'
import subprocess, os, tempfile
from pathlib import Path

def process_video(url, author):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        audio_path = tmp.name
    
    # Download
    subprocess.run(['yt-dlp', '-f', 'bestaudio', '-x', '--audio-format', 'mp3', 
                   url, '-o', audio_path])
    
    # Transcribe
    subprocess.run(['whisper', audio_path, '--model', 'base', 
                   '--output_format', 'txt', 
                   '--output_dir', str(Path.home() / 'lora-data' / 'transcriptions')])
    
    # Delete
    os.remove(audio_path)
    print(f"✓ {author}: transcribed + deleted")

# Process channels
channels = {
    "al-mohler": "https://www.youtube.com/@albertmohler",
    "truthforlife": "https://www.youtube.com/@TruthForLife",
}

for name, url in channels.items():
    # Get video URLs
    import json
    result = subprocess.run(['yt-dlp', '-j', '--flat-playlist', url], 
                          capture_output=True, text=True)
    videos = json.loads(result.stdout)
    
    for video in videos[:10]:
        video_url = f"https://www.youtube.com/watch?v={video['id']}"
        process_video(video_url, f"{name}-{video['id'][:8]}")

EOF
```

**Result:** Transcripts stored, zero audio files remain

---

## Cleanup Safety

### Prevent Accidental Deletion

```python
# Add verification before deletion
import hashlib

def safe_delete(audio_file, transcript_file):
    """Only delete if transcript exists and has content"""
    
    if not transcript_file.exists():
        print(f"⚠️  Skipping delete: no transcript for {audio_file.name}")
        return False
    
    with open(transcript_file) as f:
        transcript = f.read()
    
    if len(transcript) < 100:  # Sanity check
        print(f"⚠️  Skipping delete: transcript too short for {audio_file.name}")
        return False
    
    # Delete safely
    audio_file.unlink()
    print(f"✓ Verified + deleted: {audio_file.name}")
    return True
```

---

## Full Cleanup-Aware Pipeline

```bash
#!/bin/bash

echo "🚀 MINIMAL-STORAGE SOURCING PIPELINE"
echo "===================================="

# 1. YouTube discovery
echo "1️⃣  YouTube → Transcribe → Delete"
python3 tools/youtube-transcribe-delete.py

# 2. Podcasts discovery
echo "2️⃣  Podcasts → Transcribe → Delete"
python3 tools/podcast-transcribe-delete.py

# 3. Verify cleanup
echo "3️⃣  Verifying storage..."
du -sh /tmp/audio-stream
du -sh ~/lora-data/transcriptions
du -sh ~/lora-data/audio-queue

# 4. Cleanup any remaining
echo "4️⃣  Final cleanup..."
rm -rf /tmp/audio-stream
rm -rf ~/lora-data/audio-queue

# 5. Prepare for LoRA
echo "5️⃣  Preparing transcripts for LoRA training..."
python3 tools/prep-lora-from-transcripts.py

echo "✅ Complete. Transcripts ready. Storage minimized."
```

---

## Storage Comparison

| Approach | After Processing | Storage Impact |
|----------|------------------|----------------|
| Keep everything | 4.5 GB audio + 300 MB transcripts | ~4.8 GB |
| Delete after Whisper | 300 MB transcripts only | ✅ -4.5 GB |
| Stream + delete | 0 MB temp (real-time delete) | ✅ Minimal |

**Recommendation: Stream + delete (Strategy 3)**

---

## Summary

✅ **No video/audio files kept**  
✅ **Only text transcripts stored**  
✅ **Immediate cleanup after transcription**  
✅ **~300 MB final storage (vs 4.5 GB)**  
✅ **Ready for LoRA training**

---

_Minimal footprint. Maximum efficiency._

_Soli Deo Gloria._
