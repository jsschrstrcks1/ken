# Sourcing Commands — Execute Now

**Status:** READY TO HARVEST | **Start:** Immediately | **Duration:** 2-3 hours (Phase 1-2)

---

## Installation (Prerequisite)

```bash
# yt-dlp (YouTube)
brew install yt-dlp

# Python packages
pip3 install feedparser beautifulsoup4 requests

# ffmpeg (audio processing for Whisper)
brew install ffmpeg

# Whisper (transcription)
pip3 install openai-whisper
```

---

## Phase 1-2: Contemporary Preachers Sourcing

### 1. YouTube Discovery (yt-dlp)

**Extract metadata from YouTube channels (NO downloads, just metadata):**

```bash
# Create output directory
mkdir -p ~/lora-data/youtube-discovery

# Al Mohler
yt-dlp -j --flat-playlist https://www.youtube.com/@albertmohler > ~/lora-data/youtube-discovery/al-mohler.json

# Alistair Begg (Truth for Life)
yt-dlp -j --flat-playlist https://www.youtube.com/@TruthForLife > ~/lora-data/youtube-discovery/truthforlife.json

# Grace to You (MacArthur)
yt-dlp -j --flat-playlist https://www.youtube.com/@MacArthurPastor > ~/lora-data/youtube-discovery/gty-macarthur.json

# Ligonier (Sproul & others)
yt-dlp -j --flat-playlist https://www.youtube.com/@LigonierMinistries > ~/lora-data/youtube-discovery/ligonier.json

# 9Marks (Mark Dever)
yt-dlp -j --flat-playlist https://www.youtube.com/@9Marks > ~/lora-data/youtube-discovery/9marks.json

# Founders Ministries (Jeff Noblit, Tom Ascol)
yt-dlp -j --flat-playlist https://www.youtube.com/@FoundersMinistries > ~/lora-data/youtube-discovery/founders.json

# Wretched (Todd Friel)
yt-dlp -j --flat-playlist https://www.youtube.com/@WretchedNetwork > ~/lora-data/youtube-discovery/wretched.json

# OnePassion (Steven Lawson)
yt-dlp -j --flat-playlist https://www.youtube.com/c/OnePassionMinistries > ~/lora-data/youtube-discovery/onepassion.json

# Village Church (Matt Chandler)
yt-dlp -j --flat-playlist https://www.youtube.com/@TheVillageChurch > ~/lora-data/youtube-discovery/village-church.json

# David Platt
yt-dlp -j --flat-playlist https://www.youtube.com/@DavidPlattResources > ~/lora-data/youtube-discovery/davidplatt.json
```

**Result:** JSON files with video metadata (title, date, video_id, duration, description)

---

### 2. Podcast RSS Discovery (Python)

```python
#!/usr/bin/env python3
import feedparser
import json
from pathlib import Path
from datetime import datetime

output_dir = Path.home() / "lora-data" / "rss-discovery"
output_dir.mkdir(parents=True, exist_ok=True)

rss_feeds = {
    "al-mohler": "https://www.albertmohler.com/feed/podcast",
    "truthforlife": "https://www.truthforlife.org/feed/podcast",
    "gty": "https://feeds.gty.org/podcast",
    "danny-akin": "https://www.danielakin.org/feed",
    "ligonier": "https://www.ligonier.org/podcast/feed",
    "tgc": "https://www.thegospelcoalition.org/feed/podcast",
    "heartcry": "https://www.heartcrymissionary.com/podcast",
}

print("📡 Parsing RSS feeds...\n")

for name, feed_url in rss_feeds.items():
    print(f"🔄 {name}...", end=" ", flush=True)
    
    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries
        
        # Extract podcast metadata
        podcast_data = {
            "feed_name": name,
            "feed_url": feed_url,
            "title": feed.feed.get('title', 'N/A'),
            "entries_count": len(entries),
            "recent_episodes": [
                {
                    "title": e.get('title', 'N/A'),
                    "link": e.get('link', 'N/A'),
                    "audio_url": e.get('media_content', [{}])[0].get('url', e.links[0]['href'] if e.links else 'N/A') if hasattr(e, 'media_content') else (e.links[0]['href'] if e.links else 'N/A'),
                    "published": e.get('published', 'N/A'),
                    "duration": e.get('itunes_duration', 'N/A'),
                }
                for e in entries[:10]
            ]
        }
        
        # Save to JSON
        output_file = output_dir / f"{name}.json"
        with open(output_file, "w") as f:
            json.dump(podcast_data, f, indent=2)
        
        print(f"✓ {len(entries)} episodes")
        
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✅ RSS discovery complete. Files in {output_dir}")
```

**Result:** JSON files with podcast episodes (title, URL, date, duration)

---

### 3. Website Scraping (Python)

```python
#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import json
from pathlib import Path

output_dir = Path.home() / "lora-data" / "website-discovery"
output_dir.mkdir(parents=True, exist_ok=True)

websites = {
    "truthforlife": "https://www.truthforlife.org/sermons",
    "gty": "https://www.gty.org/library/sermons",
    "ligonier": "https://www.ligonier.org/rc-sproul",
    "9marks": "https://www.9marks.org/resources/articles",
}

print("🌐 Scraping websites...\n")

for name, url in websites.items():
    print(f"🔄 {name}...", end=" ", flush=True)
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'sermon' in href.lower() or 'article' in href.lower() or href.endswith('.pdf'):
                links.append({
                    "title": a.text.strip()[:100],
                    "url": href
                })
        
        # Save to JSON
        output_file = output_dir / f"{name}.json"
        with open(output_file, "w") as f:
            json.dump({
                "site": name,
                "url": url,
                "links_found": len(links),
                "sample_links": links[:20]
            }, f, indent=2)
        
        print(f"✓ {len(links)} sermon/article links")
        
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✅ Website scraping complete. Files in {output_dir}")
```

**Result:** JSON files with sermon/article URLs

---

### 4. Deduplication & Queue

```bash
# Run discovery orchestrator to find new content
cd /Volumes/1TB\ External/openclaw/workspace-main
python3 tools/sermon-discovery-orchestrator.py
```

**Result:** discovery-log.jsonl (all new content, deduplicated)

---

### 5. Audio Transcription (Whisper) — If Audio URLs Found

```bash
# Example: Download one audio file and transcribe
wget https://example.com/sermon.mp3 -O ~/lora-data/sermon-temp.mp3
whisper ~/lora-data/sermon-temp.mp3 --model base --output_format txt
cat ~/lora-data/sermon-temp.txt >> ~/lora-data/transcriptions.txt
```

---

## Phase 3: Historical Works (Reformation Era)

### Project Gutenberg Downloads

```bash
# Calvin: Institutes of the Christian Religion
wget https://www.gutenberg.org/cache/epub/4456/pg4456.txt -O ~/lora-data/reformation/calvin-institutes.txt

# Pascal: Pensées
wget https://www.gutenberg.org/cache/epub/1234/pg1234.txt -O ~/lora-data/reformation/pascal-pensees.txt

# Luther: Various works
wget https://www.gutenberg.org/cache/epub/7/pg7.txt -O ~/lora-data/reformation/luther-works.txt
```

### CCEL Web Scraping

```bash
# Calvin's Institutes (CCEL)
wget -r https://www.ccel.org/ccel/calvin/institutes/ -O ~/lora-data/reformation/ccel-calvin/

# Spurgeon's sermons (CCEL)
wget -r https://www.ccel.org/ccel/spurgeon/ -O ~/lora-data/reformation/ccel-spurgeon/

# Edwards' works (CCEL)
wget -r https://www.ccel.org/ccel/edwards/ -O ~/lora-data/reformation/ccel-edwards/
```

---

## Phase 4: Modern Archives

### Spurgeon's Sermon Archive

```bash
# Metropolitan Tabernacle Pulpit (3,561 sermons)
wget -r https://www.spurgeon.org/ -O ~/lora-data/spurgeon-archive/
```

### Lloyd-Jones Sermon Collection

```bash
# Westminster Chapel recordings
wget -r https://www.mlj.org.uk/ -O ~/lora-data/lloyd-jones/
```

---

## Execution Timeline

| Step | Command | Duration |
|------|---------|----------|
| YouTube discovery (10 channels) | yt-dlp x10 | ~10-15 min |
| Podcast RSS (7 feeds) | feedparser script | ~5 min |
| Website scraping (4 sites) | BeautifulSoup script | ~10 min |
| Deduplication | discovery orchestrator | ~5 min |
| **Total Phase 1-2** | All above | **~30-45 min** |
| Audio transcription (if needed) | Whisper | 2-4x audio duration |

---

## Next: Prep for LoRA Training

```bash
# After all content sourced:
python3 tools/sermon-discovery-orchestrator.py
# Produces: ~/lora-data/discovery-log.jsonl

# Convert to LoRA training format:
python3 << 'EOF'
import json
from pathlib import Path

discovery_log = Path.home() / "lora-data" / "discovery-log.jsonl"
output_train = Path.home() / "lora-data" / "phase1-2-train.jsonl"
output_eval = Path.home() / "lora-data" / "phase1-2-eval.jsonl"

samples = []
with open(discovery_log) as f:
    for line in f:
        data = json.loads(line)
        # Convert to training format
        samples.append({
            "text": data.get("content", ""),
            "author": data.get("author"),
            "source": data.get("source_url"),
        })

# 95/5 split
split = int(len(samples) * 0.95)
with open(output_train, "w") as f:
    for s in samples[:split]:
        f.write(json.dumps(s) + "\n")
with open(output_eval, "w") as f:
    for s in samples[split:]:
        f.write(json.dumps(s) + "\n")

print(f"✅ Training data ready:")
print(f"   Train: {len(samples[:split])} samples")
print(f"   Eval: {len(samples[split:])} samples")
EOF
```

---

## Status

- ✅ Commands ready
- ✅ Dependencies documented
- ⏳ Ready to execute immediately
- 🚀 Start with YouTube discovery

**Begin now.**

---

_Soli Deo Gloria._
