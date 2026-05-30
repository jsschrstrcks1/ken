# Final Sourcing Strategy — Keep .md Files, Delete Audio/Video

**YouTube/podcast → Whisper → .md transcript → DELETE audio/video only**

---

## What We Keep

✅ **.md files** (Whisper transcripts converted to Markdown)
✅ **metadata.json** (per-file metadata)
✅ **discovery-log.jsonl** (all discoveries indexed)

## What We Delete

❌ **Audio files** (.mp3) — deleted immediately after transcription
❌ **Video files** (.mp4, .webm) — deleted immediately after audio extraction
❌ **Temporary files** — cleaned up automatically

---

## Directory Structure (Final State)

```
~/lora-data/
├── transcriptions/                    # KEEP
│   ├── al-mohler-sermon-1.md         # ✅ Transcript
│   ├── al-mohler-sermon-1-metadata.json
│   ├── truthforlife-ep-1.md          # ✅ Transcript
│   ├── truthforlife-ep-1-metadata.json
│   └── ... (all .md + .json files)
│
├── discovery-log.jsonl               # KEEP (all discoveries indexed)
│
├── youtube-discovery/                # KEEP (metadata only)
│   ├── al-mohler.json
│   └── ...
│
├── rss-discovery/                    # KEEP (metadata only)
│   ├── truthforlife.json
│   └── ...
│
├── website-discovery/                # KEEP (metadata only)
│   ├── 9marks.json
│   └── ...
│
├── phase1-2-train.jsonl             # KEEP (training data)
├── phase1-2-eval.jsonl              # KEEP (eval data)
│
# NOT PRESENT (deleted immediately after use):
# - audio-queue/ (deleted after Whisper)
# - youtube-temp/ (deleted after extraction)
# - /tmp/audio-stream/ (deleted immediately)
```

---

## Audio → .md Workflow

### Step 1: Download Audio (Temporary)

```bash
# Downloads to /tmp (temporary)
yt-dlp -f bestaudio -x --audio-format mp3 https://www.youtube.com/watch?v=... \
  -o /tmp/audio-stream/%(title)s.%(ext)s
```

**Location:** `/tmp/audio-stream/sermon.mp3` (temporary)

---

### Step 2: Transcribe to .md (KEEP)

```bash
# Whisper outputs .txt file
whisper /tmp/audio-stream/sermon.mp3 \
  --model base \
  --output_format txt \
  --output_dir ~/lora-data/transcriptions

# Rename to .md
mv ~/lora-data/transcriptions/sermon.txt ~/lora-data/transcriptions/sermon.md
```

**Result:** `~/lora-data/transcriptions/sermon.md` (KEEP)

---

### Step 3: Save Metadata (KEEP)

```json
# Save per-file metadata
{
  "source_file": "sermon.mp3",
  "author": "al-mohler",
  "source": "youtube",
  "url": "https://www.youtube.com/watch?v=...",
  "date_transcribed": "2026-05-30T11:30:00Z",
  "transcript_path": "~/lora-data/transcriptions/sermon.md",
  "words": 8543,
  "model": "whisper-base",
  "language": "en"
}
```

**Location:** `~/lora-data/transcriptions/sermon-metadata.json` (KEEP)

---

### Step 4: Delete Audio (CLEANUP)

```bash
# Delete immediately after transcription
rm /tmp/audio-stream/sermon.mp3
```

**Result:** Audio file gone, .md file remains

---

## Complete Python Pipeline

```python
#!/usr/bin/env python3
"""
YouTube/Podcast → Whisper → .md files → Delete audio
"""

import subprocess
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime

def process_audio_to_md(audio_url, author_name, source_type):
    """
    Download → Transcribe → .md file → Delete audio
    """
    
    # Directories
    temp_audio = Path(tempfile.gettempdir()) / "audio-stream"
    temp_audio.mkdir(exist_ok=True)
    
    transcript_dir = Path.home() / "lora-data" / "transcriptions"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Download to temp location
    print(f"📥 {author_name}...", end=" ", flush=True)
    
    audio_file = temp_audio / f"temp-{datetime.now().timestamp()}.mp3"
    
    if source_type == "youtube":
        subprocess.run([
            'yt-dlp', '-f', 'bestaudio/best', '-x', '--audio-format', 'mp3',
            audio_url,
            '-o', str(audio_file)
        ], capture_output=True)
    
    elif source_type == "podcast":
        import urllib.request
        urllib.request.urlretrieve(audio_url, audio_file)
    
    if not audio_file.exists():
        print("✗ Download failed")
        return False
    
    # Step 2: Transcribe with Whisper
    print(f"🎙️ Transcribing...", end=" ", flush=True)
    
    result = subprocess.run([
        'whisper',
        str(audio_file),
        '--model', 'base',
        '--output_format', 'txt',
        '--output_dir', str(transcript_dir),
        '--fp16',
        '--device', 'cuda:0'
    ], capture_output=True, timeout=3600)
    
    # Step 3: Convert .txt to .md
    txt_file = transcript_dir / f"{audio_file.stem}.txt"
    md_file = transcript_dir / f"{author_name}.md"
    
    if txt_file.exists():
        # Read transcript
        with open(txt_file) as f:
            transcript = f.read()
        
        # Convert to .md format
        md_content = f"""# {author_name}

**Source:** {source_type}  
**URL:** {audio_url}  
**Transcribed:** {datetime.now().isoformat()}  
**Model:** Whisper Base

---

{transcript}
"""
        
        # Write .md file
        with open(md_file, "w") as f:
            f.write(md_content)
        
        # Save metadata
        metadata = {
            "author": author_name,
            "source": source_type,
            "url": audio_url,
            "transcript_path": str(md_file),
            "words": len(transcript.split()),
            "model": "whisper-base",
            "language": "en",
            "date_transcribed": datetime.now().isoformat()
        }
        
        metadata_file = transcript_dir / f"{author_name}-metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        word_count = len(transcript.split())
        print(f"✓ {word_count} words")
        
        # Delete .txt (keep .md)
        os.remove(txt_file)
    
    # Step 4: DELETE audio file immediately
    if audio_file.exists():
        os.remove(audio_file)
        print(f"   🗑️  Audio deleted")
    
    return True


# EXECUTION
if __name__ == "__main__":
    
    print("=" * 80)
    print("AUDIO → MARKDOWN TRANSCRIPTION PIPELINE")
    print("=" * 80)
    print()
    
    # Example: YouTube channel
    youtube_urls = [
        "https://www.youtube.com/watch?v=...",
        "https://www.youtube.com/watch?v=...",
    ]
    
    # Example: Podcast episodes
    podcast_urls = [
        "https://example.com/podcast/ep1.mp3",
        "https://example.com/podcast/ep2.mp3",
    ]
    
    results = []
    
    # Process YouTube
    for i, url in enumerate(youtube_urls, 1):
        result = process_audio_to_md(url, f"youtube-sermon-{i}", "youtube")
        results.append(result)
    
    # Process podcasts
    for i, url in enumerate(podcast_urls, 1):
        result = process_audio_to_md(url, f"podcast-episode-{i}", "podcast")
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print(f"✅ Successful: {sum(results)}")
    print(f"📁 .md transcripts: ~/lora-data/transcriptions/")
    print(f"📝 Metadata: ~/lora-data/transcriptions/*-metadata.json")
    print(f"💾 Audio files: DELETED")
    print("=" * 80)
```

---

## Final Storage Breakdown

| Type | Location | Status |
|------|----------|--------|
| **.md transcripts** | `~/lora-data/transcriptions/` | ✅ KEEP |
| **metadata.json** | `~/lora-data/transcriptions/` | ✅ KEEP |
| **discovery-log.jsonl** | `~/lora-data/` | ✅ KEEP |
| **training-data.jsonl** | `~/lora-data/` | ✅ KEEP |
| **Audio files** | `/tmp/audio-stream/` | ❌ DELETE |
| **Video files** | `/tmp/video-stream/` | ❌ DELETE |
| **Temporary files** | `/tmp/` | ❌ DELETE |

---

## Final Storage Size

```
~/lora-data/transcriptions/  ~300 MB (.md + .json only)
├── 100 YouTube .md files           (~200 MB)
├── 35 podcast .md files            (~100 MB)
└── corresponding metadata.json     (~negligible)

Total: ~300 MB (no audio/video)
```

---

## Execution Order

1. **YouTube discovery** → Download (temp) → Transcribe → .md file → Delete audio
2. **Podcast discovery** → Download (temp) → Transcribe → .md file → Delete audio
3. **Website scraping** → Already text, no transcription needed
4. **Archive indexing** → Link to existing .md files
5. **Combine** → All .md files → discovery-log.jsonl → training-data.jsonl

---

## Summary

✅ **All transcripts: .md format**  
✅ **All metadata: .json format**  
✅ **Audio/video: DELETED immediately**  
✅ **Storage: ~300 MB final**  
✅ **Ready for LoRA training**

---

_Keep the words. Delete the waves._

_Soli Deo Gloria._
