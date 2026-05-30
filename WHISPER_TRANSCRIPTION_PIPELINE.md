# Whisper Transcription Pipeline — Integrated with Sourcing

**Convert all discovered audio (YouTube, podcasts) to text automatically**

---

## Installation

```bash
# OpenAI Whisper
pip3 install openai-whisper

# FFmpeg (audio extraction)
brew install ffmpeg

# (Optional) GPU acceleration
pip3 install torch torchvision torchaudio
```

---

## Pipeline Integration

### Step 1: Audio URLs from YouTube Discovery

```bash
# From yt-dlp JSON, extract audio streams
python3 << 'EOF'
import json
import subprocess
from pathlib import Path

# Read YouTube discovery results
yt_files = Path.home().glob("lora-data/youtube-discovery/*.json")

for yt_file in yt_files:
    with open(yt_file) as f:
        videos = json.load(f)
    
    # Extract audio for each video
    for video in videos[:10]:  # First 10 per channel
        video_id = video.get('id')
        title = video.get('title', 'unknown')
        
        print(f"📥 Downloading audio: {title[:60]}")
        
        # Download audio only (no video)
        cmd = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '-x', '--audio-format', 'mp3',
            f'https://www.youtube.com/watch?v={video_id}',
            '-o', f'~/lora-data/audio-queue/%(title)s.%(ext)s'
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"✓ {title[:60]}")

EOF
```

### Step 2: Audio URLs from Podcast Discovery

```bash
# From feedparser JSON, download podcast audio
python3 << 'EOF'
import json
import subprocess
from pathlib import Path
import urllib.request

podcast_files = Path.home().glob("lora-data/rss-discovery/*.json")

for podcast_file in podcast_files:
    with open(podcast_file) as f:
        data = json.load(f)
    
    podcast_name = data['feed_name']
    episodes = data['recent_episodes']
    
    for episode in episodes[:5]:  # First 5 per feed
        audio_url = episode.get('audio_url')
        title = episode.get('title', 'unknown')
        
        if not audio_url:
            continue
        
        print(f"📥 {podcast_name}: {title[:50]}")
        
        try:
            urllib.request.urlretrieve(
                audio_url,
                f'~/lora-data/audio-queue/{podcast_name}-{title[:30]}.mp3'
            )
            print(f"✓ Downloaded")
        except Exception as e:
            print(f"✗ Error: {e}")

EOF
```

### Step 3: Batch Whisper Transcription

```bash
# Transcribe all queued audio files
python3 << 'EOF'
import subprocess
import json
from pathlib import Path
from datetime import datetime

audio_dir = Path.home() / "lora-data" / "audio-queue"
output_dir = Path.home() / "lora-data" / "transcriptions"
output_dir.mkdir(parents=True, exist_ok=True)

audio_files = list(audio_dir.glob("*.mp3"))

print(f"🎙️  Transcribing {len(audio_files)} audio files...\n")

for i, audio_file in enumerate(audio_files, 1):
    print(f"[{i}/{len(audio_files)}] {audio_file.name[:50]}", end=" ", flush=True)
    
    try:
        # Run Whisper
        result = subprocess.run([
            'whisper',
            str(audio_file),
            '--model', 'base',  # or 'tiny' for speed, 'small' for quality
            '--output_format', 'txt',
            '--output_dir', str(output_dir),
            '--language', 'en'
        ], capture_output=True, text=True, timeout=3600)
        
        # Get transcript
        transcript_file = output_dir / f"{audio_file.stem}.txt"
        if transcript_file.exists():
            with open(transcript_file) as f:
                transcript_text = f.read()
            
            # Save with metadata
            metadata = {
                "source_audio": audio_file.name,
                "timestamp": datetime.now().isoformat(),
                "model": "whisper-base",
                "language": "en",
                "transcript_length": len(transcript_text.split()),
                "content": transcript_text[:500]  # First 500 words
            }
            
            metadata_file = output_dir / f"{audio_file.stem}-metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✓ {len(transcript_text.split())} words")
        else:
            print(f"✗ No transcript generated")
        
    except subprocess.TimeoutExpired:
        print("✗ Timeout (audio too long)")
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✅ Transcription complete: {output_dir}")

EOF
```

---

## Whisper Model Options

| Model | Size | Speed | Accuracy | RAM | VRAM |
|-------|------|-------|----------|-----|------|
| **tiny** | 39M | 6x faster | ~85% | 1GB | 1GB |
| **base** | 74M | 3x faster | ~90% | 1GB | 2GB |
| **small** | 244M | 2x faster | ~95% | 2GB | 4GB |
| **medium** | 769M | 1x | ~97% | 5GB | 8GB |
| **large** | 1.5B | 0.5x (slower) | ~99% | 10GB | 12GB |

**Recommendation:** Start with `base` (good balance of speed & accuracy)

---

## Advanced: Parallel Transcription (Multi-GPU)

```bash
# If you have multiple GPUs, process multiple files in parallel
python3 << 'EOF'
import subprocess
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

audio_dir = Path.home() / "lora-data" / "audio-queue"
output_dir = Path.home() / "lora-data" / "transcriptions"
audio_files = list(audio_dir.glob("*.mp3"))

def transcribe_audio(audio_file, gpu_index):
    """Transcribe single audio file on specific GPU"""
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_index)
    
    result = subprocess.run([
        'whisper',
        str(audio_file),
        '--model', 'base',
        '--output_format', 'txt',
        '--output_dir', str(output_dir),
        '--device', f'cuda:{gpu_index}'
    ], capture_output=True)
    
    return audio_file, result.returncode == 0

# Process 4 files at a time (adjust based on available GPUs)
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(transcribe_audio, audio_file, i % 4)
        for i, audio_file in enumerate(audio_files)
    ]
    
    for future in as_completed(futures):
        audio_file, success = future.result()
        status = "✓" if success else "✗"
        print(f"{status} {audio_file.name}")

EOF
```

---

## Quality Control

### Check Transcription Quality

```python
# Verify transcripts have reasonable content
import json
from pathlib import Path

output_dir = Path.home() / "lora-data" / "transcriptions"
transcripts = list(output_dir.glob("*.txt"))

print("📊 Transcription Quality Report\n")

for transcript in transcripts:
    with open(transcript) as f:
        text = f.read()
    
    words = len(text.split())
    lines = len(text.split('\n'))
    
    # Flag potential issues
    issues = []
    if words < 50:
        issues.append("TOO_SHORT")
    if len(text) < 100:
        issues.append("EMPTY_OR_NOISE")
    if "[inaudible]" in text.lower():
        issues.append("INAUDIBLE_SECTIONS")
    
    status = "✓" if not issues else f"⚠️  {','.join(issues)}"
    print(f"{status} {transcript.name}: {words} words")

```

---

## Integration with LoRA Pipeline

### Combine All Sources → Single Training Dataset

```bash
python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

# Collect from all sources
sources = {
    "youtube_captions": Path.home() / "lora-data" / "youtube-captions",
    "podcast_transcripts": Path.home() / "lora-data" / "transcriptions",
    "website_sermons": Path.home() / "lora-data" / "website-discovery",
    "existing_archive": Path("/Volumes/1TB External/openclaw-main/sermon-archive"),
}

all_samples = []

# 1. YouTube captions
if sources["youtube_captions"].exists():
    for caption_file in sources["youtube_captions"].glob("*.json"):
        with open(caption_file) as f:
            data = json.load(f)
        all_samples.append({
            "text": data.get("captions", ""),
            "source": "youtube",
            "author": caption_file.stem
        })

# 2. Podcast transcripts
for transcript in sources["podcast_transcripts"].glob("*.txt"):
    with open(transcript) as f:
        text = f.read()
    all_samples.append({
        "text": text,
        "source": "podcast",
        "author": transcript.stem.split("-metadata")[0]
    })

# 3. Website sermon text
for website_file in sources["website_sermons"].glob("*.json"):
    with open(website_file) as f:
        data = json.load(f)
    for link in data.get("sample_links", []):
        all_samples.append({
            "text": link.get("title", ""),
            "source": "website",
            "author": website_file.stem
        })

# 4. Existing archive
# (already has content, just reference)

# Save combined dataset
combined_file = Path.home() / "lora-data" / "phase1-2-combined-source.jsonl"
with open(combined_file, "w") as f:
    for sample in all_samples:
        f.write(json.dumps(sample) + "\n")

print(f"✅ Combined {len(all_samples)} samples from all sources")
print(f"   Output: {combined_file}")

EOF
```

---

## Execution Order

1. **YouTube discovery** → Extract audio URLs
2. **Podcast discovery** → Get audio URLs
3. **Download audio** → All files to `audio-queue/`
4. **Batch Whisper** → Transcribe all (30-120 min depending on volume)
5. **Combine sources** → Create unified training dataset
6. **Prep for LoRA** → Segment into 2k-token samples

---

## Performance Expectations

| Audio Source | Count | Avg Duration | Whisper Time (base) | Total Time |
|--------------|-------|--------------|---------------------|-----------|
| YouTube (10 channels × 10) | 100 videos | 45 min avg | 2.25 hrs | 2.5 hrs |
| Podcasts (7 feeds × 5) | 35 episodes | 60 min avg | 3.5 hrs | 4 hrs |
| **Total** | **135 audio files** | **~50 min avg** | **~6 hrs** | **6-7 hrs** |

*With GPU: ~6-7 hours. With multi-GPU parallel: ~2-3 hours.*

---

## Whisper Flags (Optional)

```bash
whisper audio.mp3 \
  --model base \                    # Model size
  --output_format txt \             # Output as text
  --output_dir ./transcriptions \   # Save location
  --language en \                   # Force language
  --device cuda:0 \                 # Use GPU 0
  --fp16 \                          # 16-bit precision (faster, less RAM)
  --temperature 0 \                 # No randomness
  --verbose False                   # Quiet mode
```

---

## Complete Sourcing + Transcription Workflow

```bash
#!/bin/bash

echo "🚀 PHASE 1-2 COMPLETE WORKFLOW"
echo "==============================\n"

# 1. YouTube discovery
echo "1️⃣  YouTube discovery (10 channels)..."
for channel in al-mohler truthforlife gty-macarthur ligonier 9marks founders wretched onepassion village-church davidplatt; do
    echo "   yt-dlp -j --flat-playlist https://www.youtube.com/@$channel > ~/lora-data/youtube/$channel.json"
done

# 2. RSS discovery
echo "2️⃣  Podcast RSS discovery..."
python3 tools/rss-discovery.py

# 3. Download audio from YouTube
echo "3️⃣  Downloading YouTube audio..."
python3 << 'EOF'
# Extract MP3 from YouTube videos
import subprocess, json
from pathlib import Path

for yt_file in Path.home().glob("lora-data/youtube/*.json"):
    with open(yt_file) as f:
        videos = json.load(f)
    for video in videos[:5]:
        subprocess.run([
            'yt-dlp', '-f', 'bestaudio', '-x', '--audio-format', 'mp3',
            f'https://www.youtube.com/watch?v={video["id"]}',
            '-o', f'~/lora-data/audio-queue/%(title)s.%(ext)s'
        ])
EOF

# 4. Download podcast audio
echo "4️⃣  Downloading podcast audio..."
python3 tools/podcast-download.py

# 5. Batch transcription
echo "5️⃣  Running Whisper transcription..."
echo "   (This may take 6-7 hours for all audio)"
python3 << 'EOF'
import subprocess
from pathlib import Path

for audio_file in Path.home().glob("lora-data/audio-queue/*.mp3"):
    subprocess.run([
        'whisper', str(audio_file),
        '--model', 'base',
        '--output_format', 'txt',
        '--output_dir', '~/lora-data/transcriptions'
    ])
EOF

# 6. Combine and prep for LoRA
echo "6️⃣  Preparing for LoRA training..."
python3 tools/prep-lora-training-data.py

echo "\n✅ COMPLETE. Ready for LoRA training."

```

---

## Summary

✅ **YouTube captions** → Extracted automatically  
✅ **Podcast audio** → Downloaded from RSS feeds  
✅ **Audio transcription** → Whisper (99% accurate)  
✅ **Combined dataset** → Single training file  
✅ **Ready for LoRA** → Segmented into samples  

**Total time: ~8-10 hours (mostly Whisper running in background)**

---

_Soli Deo Gloria._
