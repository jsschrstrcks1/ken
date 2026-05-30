# SEBTS Podcast Extraction Plan — Audio to .md LoRA Data

**Date:** 2026-05-30 | **Status:** DESIGN | **Priority:** INSTITUTIONAL HIGH

---

## Executive Summary

**Goal:** Extract all SEBTS seminary podcast audio → transcribe → feed into:
1. **SEBTS Institutional LoRA** (all faculty blended)
2. **Individual faculty LoRAs** (Tom Schreiner, Gregg Allison, etc.)

**Approach:** Systematic podcast discovery → audio extraction → Whisper → dedup → LoRA data

**Timeline:** 4-6 hours (download + transcription)

**Output:** 100-200 episodes = 5-10 hours audio = 500k-1M words

---

## SEBTS Podcast Discovery

### 1. Primary Podcast Feeds

**SEBTS Official Channels:**

| Feed | URL | Episodes | Focus |
|------|-----|----------|-------|
| **SEBTS Chapel** | https://www.sebts.edu/chapel/ (RSS) | 200-300 | Faculty chapel services |
| **SEBTS Podcast Series** | https://www.sebts.edu/podcast/ (RSS) | 100-150 | Guest lectures + faculty |
| **Faculty Individual Feeds** | Per faculty member | Varies | Specialist topics |
| **Southeastern Today** | Official magazine podcast | 50-100 | Seminary news/interviews |

### 2. Known Faculty Podcasters

| Name | Topic | Feed/Channel | Status |
|------|-------|-------------|--------|
| **Russell Moore** | Ethics + culture | SEBTS podcast | Active |
| **Gregg Allison** | Theology + ecclesiology | SEBTS podcast | Active |
| **Owen Strachan** | Apologetics + worldview | SEBTS podcast | Active |
| **Keith Whitfield** | New Testament | SEBTS Chapel | Active |
| **Dan Doriani** | Old Testament | SEBTS Chapel | Active |
| **Matthew Barrett** | Systematic theology | SEBTS podcast | Active |
| **Jason Thacker** | Ethics + technology | SEBTS podcast | Active |

---

## Discovery Strategy

### Step 1: Find All SEBTS RSS Feeds

```bash
# Search for SEBTS podcasts
curl -s "https://www.sebts.edu/podcast/" | grep -i "feed\|rss\|podcast"

# Try common podcast feed patterns
for pattern in podcast chapel seminary audio; do
    echo "Testing: https://www.sebts.edu/$pattern/feed/"
    curl -s -I "https://www.sebts.edu/$pattern/feed/" | head -1
done
```

**Expected:** 3-5 RSS feeds (chapel, podcast, possibly faculty-specific)

---

### Step 2: Parse All Episodes

```python
#!/usr/bin/env python3
import feedparser
import json
from pathlib import Path

SEBTS_FEEDS = {
    "chapel": "https://www.sebts.edu/chapel/feed/",
    "podcast": "https://www.sebts.edu/podcast/feed/",
    "seminary": "https://www.sebts.edu/seminary/feed/",
}

output_dir = Path.home() / "lora-data" / "sebts-discovery"
output_dir.mkdir(parents=True, exist_ok=True)

for feed_name, feed_url in SEBTS_FEEDS.items():
    print(f"🔄 Parsing {feed_name}...")
    
    try:
        feed = feedparser.parse(feed_url)
        episodes = feed.entries
        
        feed_data = {
            "feed_name": feed_name,
            "feed_url": feed_url,
            "title": feed.feed.get('title', 'Unknown'),
            "total_episodes": len(episodes),
            "episodes": []
        }
        
        for episode in episodes:
            # Extract audio URL
            audio_url = None
            
            # Try various audio link patterns
            for link in episode.get('links', []):
                if link.get('type', '').startswith('audio'):
                    audio_url = link['href']
                    break
            
            # Try media content
            if not audio_url and hasattr(episode, 'media_content'):
                audio_url = episode.media_content[0]['url']
            
            # Try enclosure (standard podcast format)
            if not audio_url and hasattr(episode, 'enclosures'):
                for enc in episode.enclosures:
                    if 'audio' in enc.type:
                        audio_url = enc.href
                        break
            
            episode_data = {
                "title": episode.get('title', 'Unknown'),
                "published": episode.get('published', 'Unknown'),
                "audio_url": audio_url,
                "duration": episode.get('itunes_duration', 'Unknown'),
                "summary": episode.get('summary', '')[:200],  # First 200 chars
                "link": episode.get('link', '')
            }
            
            feed_data["episodes"].append(episode_data)
        
        # Save feed data
        output_file = output_dir / f"{feed_name}-discovery.json"
        with open(output_file, "w") as f:
            json.dump(feed_data, f, indent=2)
        
        print(f"✓ {len(episodes)} episodes found")
        
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✅ Discovery complete: {output_dir}")
```

**Output:** JSON files with episode metadata + audio URLs

---

## Audio Extraction

### Step 3: Download Audio from Podcast Feeds

```bash
#!/bin/bash

# Create audio queue directory
mkdir -p ~/lora-data/sebts-audio-queue

# Download all podcast audio files
python3 << 'EOF'
import json
import urllib.request
import os
from pathlib import Path

discovery_dir = Path.home() / "lora-data" / "sebts-discovery"
audio_queue = Path.home() / "lora-data" / "sebts-audio-queue"
audio_queue.mkdir(parents=True, exist_ok=True)

for discovery_file in discovery_dir.glob("*-discovery.json"):
    with open(discovery_file) as f:
        feed_data = json.load(f)
    
    feed_name = feed_data["feed_name"]
    episodes = feed_data["episodes"]
    
    print(f"\n📥 Downloading {feed_name} episodes...")
    
    for i, episode in enumerate(episodes[:50], 1):  # First 50 per feed
        audio_url = episode.get("audio_url")
        title = episode.get("title", f"episode-{i}").replace("/", "-")[:50]
        
        if not audio_url:
            print(f"  ⚠️  No audio URL: {title}")
            continue
        
        output_file = audio_queue / f"{feed_name}-{i:03d}-{title}.mp3"
        
        if output_file.exists():
            print(f"  ✓ Already downloaded: {title}")
            continue
        
        try:
            print(f"  📥 {title}...", end=" ", flush=True)
            urllib.request.urlretrieve(audio_url, output_file)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")

print(f"\n✅ Audio download complete: {audio_queue}")
print(f"   Total files: {len(list(audio_queue.glob('*.mp3')))}")

EOF
```

**Output:** MP3 files in `~/lora-data/sebts-audio-queue/`

---

## Panopto Extraction (Alternative/Supplementary)

### Step 4: Access SEBTS Panopto Lectures

**Note:** Ken has direct login credentials

```bash
# Panopto API approach (if Ken has API access)
curl -X POST "https://sebts.panopto.com/api/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Result: Auth token for API calls

# List all videos
curl -X GET "https://sebts.panopto.com/api/v1/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Download video metadata
curl -X GET "https://sebts.panopto.com/api/v1/sessions/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Alternative:** Use Panopto's public links (if available)

```python
# If Panopto videos have public share links
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

# Navigate to Panopto share link
driver.get("https://sebts.panopto.com/Panopto/Pages/Viewer.aspx?id=...")

# Extract video source
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Find video player source URL
video_src = soup.find('video')['src']
print(f"Video URL: {video_src}")

# Download video
import urllib.request
urllib.request.urlretrieve(video_src, "lecture.mp4")
```

---

## Transcription Pipeline

### Step 5: Batch Whisper Transcription

```bash
#!/bin/bash

# Transcribe all SEBTS audio
python3 << 'EOF'
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

audio_dir = Path.home() / "lora-data" / "sebts-audio-queue"
output_dir = Path.home() / "lora-data" / "sebts-transcriptions"
output_dir.mkdir(parents=True, exist_ok=True)

audio_files = sorted(audio_dir.glob("*.mp3"))

print(f"🎙️  Transcribing {len(audio_files)} SEBTS episodes...\n")

for i, audio_file in enumerate(audio_files, 1):
    print(f"[{i}/{len(audio_files)}] {audio_file.name[:60]}", end=" ", flush=True)
    
    try:
        # Extract faculty name from filename
        parts = audio_file.name.split("-")
        feed_name = parts[0]
        episode_num = parts[1] if len(parts) > 1 else "unknown"
        
        # Transcribe
        result = subprocess.run([
            'whisper',
            str(audio_file),
            '--model', 'medium',  # Or 'base' for speed
            '--output_format', 'txt',
            '--output_dir', str(output_dir),
            '--fp16',
            '--device', 'cuda:0'
        ], capture_output=True, timeout=3600)
        
        # Read transcript
        txt_file = output_dir / f"{audio_file.stem}.txt"
        if txt_file.exists():
            with open(txt_file) as f:
                transcript = f.read()
            
            # Convert to .md format
            md_file = output_dir / f"{feed_name}-{episode_num}.md"
            md_content = f"""# SEBTS — {feed_name.upper()} Episode {episode_num}

**Source:** SEBTS Podcast — {feed_name}  
**Audio File:** {audio_file.name}  
**Transcribed:** {datetime.now().isoformat()}  
**Model:** Whisper Medium  
**Language:** English  

---

{transcript}
"""
            
            with open(md_file, "w") as f:
                f.write(md_content)
            
            # Save metadata
            metadata = {
                "source": "SEBTS",
                "feed": feed_name,
                "episode": episode_num,
                "audio_file": audio_file.name,
                "transcript_file": md_file.name,
                "words": len(transcript.split()),
                "model": "whisper-medium",
                "date_transcribed": datetime.now().isoformat()
            }
            
            metadata_file = output_dir / f"{feed_name}-{episode_num}-metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✓ {len(transcript.split())} words")
            
            # Delete .txt (keep .md)
            os.remove(txt_file)
        else:
            print(f"✗ No transcript generated")
        
    except subprocess.TimeoutExpired:
        print("✗ Timeout (too long)")
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✅ Transcription complete: {output_dir}")

# Summary
md_files = list(output_dir.glob("*.md"))
total_words = sum(
    len(open(f).read().split()) 
    for f in md_files 
    if f.exists()
)
print(f"   Total episodes: {len(md_files)}")
print(f"   Total words: {total_words:,}")

EOF
```

**Output:** `.md` transcripts + `.json` metadata

---

## Cleanup & Storage Optimization

### Step 6: Delete Audio, Keep Transcripts

```bash
#!/bin/bash

# Delete all audio files after transcription
echo "🗑️  Cleaning up audio files..."
rm -rf ~/lora-data/sebts-audio-queue/

# Keep only transcripts and metadata
ls -lh ~/lora-data/sebts-transcriptions/
du -sh ~/lora-data/sebts-transcriptions/

# Result: X MB of .md files (audio deleted)
```

**Storage saved:** ~100-200 MB (audio removed)

---

## Faculty Routing (LoRA Assignment)

### Step 7: Identify Faculty & Route to Individual LoRAs

```python
#!/usr/bin/env python3
"""
Route SEBTS transcripts to:
1. SEBTS Institutional LoRA (all faculty combined)
2. Individual faculty LoRAs (Schreiner, Allison, Strachan, etc.)
"""

import json
from pathlib import Path

# Faculty name detection patterns
FACULTY_PATTERNS = {
    "Russell Moore": ["moore", "russell"],
    "Gregg Allison": ["allison", "gregg"],
    "Owen Strachan": ["strachan", "owen"],
    "Keith Whitfield": ["whitfield", "keith"],
    "Dan Doriani": ["doriani", "dan"],
    "Matthew Barrett": ["barrett", "matthew"],
    "Jason Thacker": ["thacker", "jason"],
    "Tom Schreiner": ["schreiner", "tom"],
}

transcription_dir = Path.home() / "lora-data" / "sebts-transcriptions"
routing = {
    "sebts-institutional": [],  # All episodes
    "individual": {}  # By faculty
}

# Initialize individual faculty lists
for faculty_name in FACULTY_PATTERNS.keys():
    routing["individual"][faculty_name] = []

# Process each transcript
for md_file in transcription_dir.glob("*.md"):
    with open(md_file) as f:
        content = f.read()
    
    # Add to institutional (all)
    routing["sebts-institutional"].append({
        "file": str(md_file),
        "source": "SEBTS Podcast"
    })
    
    # Detect faculty speaker
    detected_faculty = None
    for faculty_name, patterns in FACULTY_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in content.lower():
                detected_faculty = faculty_name
                break
        if detected_faculty:
            break
    
    # Add to individual faculty LoRA
    if detected_faculty:
        routing["individual"][detected_faculty].append({
            "file": str(md_file),
            "confidence": "high"  # or "medium" if uncertain
        })
    else:
        # Generic if faculty unclear
        routing["individual"]["SEBTS Faculty (Unknown)"] = routing["individual"].get("SEBTS Faculty (Unknown)", [])
        routing["individual"]["SEBTS Faculty (Unknown)"].append({
            "file": str(md_file),
            "confidence": "low"
        })

# Save routing map
routing_file = transcription_dir / "routing-map.json"
with open(routing_file, "w") as f:
    json.dump(routing, f, indent=2)

print("✅ Routing complete")
print(f"   Institutional: {len(routing['sebts-institutional'])} episodes")
for faculty, episodes in routing["individual"].items():
    if episodes:
        print(f"   {faculty}: {len(episodes)} episodes")

```

**Output:** Routing map showing which transcripts go to which LoRAs

---

## LoRA Data Preparation

### Step 8: Convert to JSONL Training Format

```python
#!/usr/bin/env python3
"""
Convert SEBTS transcripts → JSONL training files for:
1. SEBTS Institutional LoRA
2. Individual faculty LoRAs
"""

import json
from pathlib import Path
from datetime import datetime

transcription_dir = Path.home() / "lora-data" / "sebts-transcriptions"
lora_data_dir = Path.home() / "lora-data"

# Load routing map
routing_file = transcription_dir / "routing-map.json"
with open(routing_file) as f:
    routing = json.load(f)

# Prepare SEBTS Institutional LoRA
sebts_samples = []

for entry in routing["sebts-institutional"]:
    md_file = Path(entry["file"])
    with open(md_file) as f:
        content = f.read()
    
    # Remove markdown header
    lines = content.split("\n")
    body = "\n".join(lines[10:])  # Skip header lines
    
    # Segment into 2k-token chunks
    words = body.split()
    for i in range(0, len(words), 500):  # ~2k tokens per segment
        chunk = " ".join(words[i:i+500])
        if len(chunk) > 100:
            sebts_samples.append({
                "text": chunk,
                "author": "SEBTS Faculty",
                "source": md_file.stem,
                "institution": "SEBTS",
                "date_transcribed": datetime.now().isoformat()
            })

# Save SEBTS Institutional training data
sebts_train = Path(lora_data_dir) / "sebts" / "train.jsonl"
sebts_train.parent.mkdir(parents=True, exist_ok=True)

with open(sebts_train, "w") as f:
    for i, sample in enumerate(sebts_samples):
        if i % 20 == 0:  # Use 5% for eval
            continue
        f.write(json.dumps(sample) + "\n")

sebts_eval = Path(lora_data_dir) / "sebts" / "eval.jsonl"
with open(sebts_eval, "w") as f:
    for i, sample in enumerate(sebts_samples):
        if i % 20 != 0:  # 5% for eval
            continue
        f.write(json.dumps(sample) + "\n")

print(f"✅ SEBTS Institutional LoRA data: {sebts_train}")
print(f"   Train: {sum(1 for line in open(sebts_train))} samples")
print(f"   Eval: {sum(1 for line in open(sebts_eval))} samples")

# Prepare Individual Faculty LoRAs
for faculty_name, episodes in routing["individual"].items():
    if not episodes:
        continue
    
    faculty_samples = []
    
    for entry in episodes:
        md_file = Path(entry["file"])
        with open(md_file) as f:
            content = f.read()
        
        lines = content.split("\n")
        body = "\n".join(lines[10:])
        
        words = body.split()
        for i in range(0, len(words), 500):
            chunk = " ".join(words[i:i+500])
            if len(chunk) > 100:
                faculty_samples.append({
                    "text": chunk,
                    "author": faculty_name,
                    "source": md_file.stem,
                    "institution": "SEBTS",
                    "date_transcribed": datetime.now().isoformat()
                })
    
    # Save individual faculty data
    faculty_dir = Path(lora_data_dir) / faculty_name.lower().replace(" ", "-")
    faculty_dir.mkdir(parents=True, exist_ok=True)
    
    faculty_train = faculty_dir / "train.jsonl"
    faculty_eval = faculty_dir / "eval.jsonl"
    
    with open(faculty_train, "w") as f:
        for i, sample in enumerate(faculty_samples):
            if i % 20 == 0:
                continue
            f.write(json.dumps(sample) + "\n")
    
    with open(faculty_eval, "w") as f:
        for i, sample in enumerate(faculty_samples):
            if i % 20 != 0:
                continue
            f.write(json.dumps(sample) + "\n")
    
    print(f"✅ {faculty_name}: {faculty_train}")
    print(f"   Train: {sum(1 for line in open(faculty_train))} samples")
    print(f"   Eval: {sum(1 for line in open(faculty_eval))} samples")

```

**Output:** 
- `~/lora-data/sebts/train.jsonl` + `eval.jsonl` (SEBTS Institutional)
- `~/lora-data/gregg-allison/train.jsonl` + `eval.jsonl` (Individual faculty)
- etc. for all faculty identified

---

## Complete SEBTS Extraction Script

### All-in-One Execution

```bash
#!/bin/bash
set -e

echo "🚀 SEBTS PODCAST EXTRACTION PIPELINE"
echo "===================================="

# Step 1: Discovery
echo "1️⃣  Discovering SEBTS podcast feeds..."
python3 << 'DISCOVERY_PYTHON'
import feedparser
import json
from pathlib import Path

SEBTS_FEEDS = {
    "chapel": "https://www.sebts.edu/chapel/feed/",
    "podcast": "https://www.sebts.edu/podcast/feed/",
}

output_dir = Path.home() / "lora-data" / "sebts-discovery"
output_dir.mkdir(parents=True, exist_ok=True)

for feed_name, feed_url in SEBTS_FEEDS.items():
    print(f"  📡 {feed_name}...", end=" ", flush=True)
    try:
        feed = feedparser.parse(feed_url)
        episodes = feed.entries
        print(f"✓ {len(episodes)} episodes")
    except:
        print("✗ Error")

DISCOVERY_PYTHON

# Step 2: Download
echo "2️⃣  Downloading audio files..."
python3 << 'DOWNLOAD_PYTHON'
# ... (download code)
DOWNLOAD_PYTHON

# Step 3: Transcribe
echo "3️⃣  Transcribing with Whisper..."
python3 << 'TRANSCRIBE_PYTHON'
# ... (transcription code)
TRANSCRIBE_PYTHON

# Step 4: Route & Prepare
echo "4️⃣  Routing to LoRAs and preparing training data..."
python3 << 'ROUTING_PYTHON'
# ... (routing + JSONL preparation code)
ROUTING_PYTHON

# Step 5: Cleanup
echo "5️⃣  Cleaning up audio files..."
rm -rf ~/lora-data/sebts-audio-queue/

# Results
echo ""
echo "✅ COMPLETE"
echo "   Transcripts: ~/lora-data/sebts-transcriptions/"
echo "   SEBTS Institutional LoRA: ~/lora-data/sebts/train.jsonl"
echo "   Faculty LoRAs: ~/lora-data/*/train.jsonl"
```

---

## Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Discovery | 15 min | Find all SEBTS podcast feeds + episodes |
| Download | 30-60 min | Download 100-200 audio files (~5-10 GB) |
| Transcription | 2-4 hours | Whisper batch on GPU |
| Cleanup | 5 min | Delete audio, keep .md + .json |
| Routing | 10 min | Detect faculty, route to LoRAs |
| JSONL Prep | 10 min | Segment into 2k-token samples |
| **Total** | **3-6 hours** | Audio → training data |

---

## Expected Output

### SEBTS Institutional LoRA
- **File:** `~/lora-data/sebts/train.jsonl`
- **Samples:** 1,000-2,000 (2k-token segments)
- **Words:** 500k-1M
- **Training time:** 1-2 hours

### Individual Faculty LoRAs
- **Russell Moore:** 200-300 samples, 100k-150k words
- **Gregg Allison:** 150-250 samples, 80k-120k words
- **Owen Strachan:** 100-200 samples, 50k-100k words
- **Others:** Proportional to podcast appearances

---

## Integration with Existing Pipeline

**Add to `integrated-mega-pipeline.py`:**

```python
# Phase 4: SEBTS Institutional Sources
print("🏫 SEBTS Podcast Extraction...")
subprocess.run(['python3', 'tools/sebts-podcast-extraction.py'])

# Result: SEBTS Institutional + individual faculty LoRAs
```

**Update `discovery-log.jsonl`:**
- Add SEBTS Chapel entries
- Add SEBTS Podcast entries
- Add faculty detection

---

## Notes

✅ **Ken has Panopto access** — Can also extract SEBTS Panopto lectures (500-1,000+ videos)  
✅ **Chapel services likely public** — YouTube channel scraping feasible  
✅ **Faculty identification** — Explicit in episode titles or metadata  
✅ **Dual-feed approach** — Both Institutional + Individual LoRAs  

---

## Next: Implement

1. Test SEBTS feed URLs (may differ from documented)
2. Implement discovery script
3. Run audio extraction
4. Verify transcription quality
5. Route to LoRAs
6. Queue for training

---

_SEBTS Institutional LoRA + Faculty LoRAs incoming._

_Soli Deo Gloria._
