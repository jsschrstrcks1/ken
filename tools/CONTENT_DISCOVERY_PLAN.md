# Content Discovery Plan — Finding New Sermons Across All Authors

**Goal:** Continuously discover NEW (unpublished to archive) sermon content for all 25+ authors, automatically preparing training data.

---

## Discovery Strategies by Source Type

### 1. YouTube Discovery (yt-dlp)

**For:** Most preachers have YouTube channels

**Implementation:**
```bash
yt-dlp -j --flat-playlist https://youtube.com/@ChannelName > videos.json
# Extract: video_id, title, date, duration, thumbnail
# Filter: date > last_check
# Download: captions (auto-generated) or use Whisper
```

**Authors with YouTube:**
- Alistair Begg: https://www.youtube.com/@TruthForLife
- MacArthur (GTY): https://www.youtube.com/@MacArthurPastor
- Al Mohler: https://www.youtube.com/@albertmohler
- Ligonier (Sproul): https://www.youtube.com/@LigonierMinistries
- 9Marks (Dever): https://www.youtube.com/@9Marks
- Founders (Ascol): https://www.youtube.com/@FoundersMinistries
- David Platt: https://www.youtube.com/@DavidPlattResources
- Stephen Davey: https://www.youtube.com/@WisdomInternational
- HeartCry (Washer): https://www.youtube.com/@HeartCryMissionary

---

### 2. Podcast RSS Feeds

**For:** Most preachers publish podcasts

**Implementation:**
```python
import feedparser

feed = feedparser.parse(feed_url)
for entry in feed.entries:
    if entry.published > last_check:
        # Extract: title, pubDate, mp3_url, duration
        # Queue for Whisper transcription
        harvest_audio(entry.link, author_name)
```

**Authors with RSS:**
- Al Mohler: https://www.albertmohler.com/feed/podcast
- Alistair Begg: https://www.truthforlife.org/feed/podcast
- MacArthur (GTY): https://feeds.gty.org/podcast
- Danny Akin: https://www.danielakin.org/feed
- Ligonier: https://www.ligonier.org/podcast/feed
- TGC: https://www.thegospelcoalition.org/feed/podcast
- HeartCry (Washer): https://www.heartcrymissionary.com/podcast

---

### 3. Direct Website Scraping

**For:** Authors who publish sermon archives on personal sites

**Implementation:**
```python
from bs4 import BeautifulSoup
import requests

response = requests.get(website_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Parse sermon links (framework-specific parsing)
for link in soup.find_all('a', class_='sermon-link'):
    sermon_url = link['href']
    title = link.text
    # Download PDF or text
    if sermon_url.endswith('.pdf'):
        harvest_pdf(sermon_url, author_name)
    elif sermon_url.endswith('.mp3'):
        harvest_audio(sermon_url, author_name)
    else:
        harvest_webpage(sermon_url, author_name)
```

**Authors with websites:**
- MacArthur (Grace to You): https://www.gty.org/library
- Truthforlife (Begg): https://www.truthforlife.org
- Ligonier (Sproul): https://www.ligonier.org
- TGC: https://www.thegospelcoalition.org/resources
- David Platt (Radical): https://www.radical.net/resources
- 9Marks (Dever): https://www.9marks.org
- Founders (Ascol): https://www.founders.org
- Stephen Davey (TruthNetwork): https://www.truthnetwork.com

---

### 4. PDF Sermon Downloads

**Implementation:**
```python
import PyPDF2
from pathlib import Path

def harvest_pdf(url, author_name):
    """Download PDF and extract text"""
    response = requests.get(url)
    pdf_path = Path(f"/tmp/{author_name}-{uuid4()}.pdf")
    
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    
    # Extract text
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = "".join(page.extract_text() for page in reader.pages)
    
    # Save to archive
    save_to_archive(author_name, text, url, "pdf")
```

**Source sites:**
- Ligonier (PDF archives)
- TruthNetwork (PDF archives)
- Logos.com (requires login, see API section)

---

### 5. Audio Transcription (Whisper)

**For:** MP3 podcasts and YouTube audio

**Implementation:**
```python
import subprocess

def harvest_audio(audio_url, author_name):
    """Download audio and transcribe with Whisper"""
    # Download
    audio_path = download_audio(audio_url)
    
    # Transcribe
    result = subprocess.run([
        'whisper', audio_path,
        '--model', 'base',
        '--output_format', 'txt',
        '--language', 'en'
    ], capture_output=True)
    
    transcript = Path(result.stdout).read_text()
    
    # Save to archive
    save_to_archive(author_name, transcript, audio_url, "podcast")
```

**Speed:** ~2x duration (1 hour sermon = ~2 min transcription on local GPU)

---

### 6. Logos.com API

**For:** Structured access to sermon collections

**Implementation:**
```python
import requests

def harvest_logos_api(author_name, logos_id):
    """Query Logos API for author's resources"""
    headers = {
        "Authorization": f"Bearer {LOGOS_API_TOKEN}",
    }
    
    response = requests.get(
        f"https://api.logos.com/v1/resources/{logos_id}/recent",
        headers=headers,
        params={"since": last_check}
    )
    
    for resource in response.json()['resources']:
        if resource['type'] == 'sermon':
            # Extract text or download PDF
            save_to_archive(author_name, resource['text'], resource['url'], "logos")
```

**Requires:** `LOGOS_API_TOKEN` (need to request from Logos)

---

### 7. Twitter/Social Monitoring (Optional)

**For:** Announcements of new content

**Implementation:**
```python
import tweepy

def monitor_twitter(author_twitter_handle):
    """Monitor tweets for sermon links"""
    tweets = client.get_users_tweets(
        id=user_id,
        max_results=10,
        tweet_fields=['created_at']
    )
    
    for tweet in tweets.data:
        if tweet.created_at > last_check:
            # Extract URLs from tweet
            urls = extract_urls(tweet.text)
            for url in urls:
                if is_sermon_url(url):
                    # Queue for harvesting
                    queue_harvest(author_name, url)
```

**Authors on Twitter:**
- @drcrusumohler
- @truthforlife
- @daveplatt
- And many more...

---

## Full Content Discovery Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  sermon-discovery-orchestrator.py (Main Controller)     │
└──────────────────────┬──────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┬───────────────┐
    │                  │                  │               │
    ▼                  ▼                  ▼               ▼
YouTube            Podcast RSS      Website Scrape     Logos API
(yt-dlp)           (feedparser)      (BeautifulSoup)    (requests)
    │                  │                  │               │
    └──────────────────┼──────────────────┴───────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
        Text-based           Audio-based
        (PDFs, HTML)         (MP3, YouTube)
            │                     │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  Whisper (if audio) │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ Dedup + Validation  │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ Save to Archive +   │
            │ Queue for LoRA prep │
            └─────────────────────┘
```

---

## Deduplication & State Tracking

### Existing Content Hash
```python
# Hash first 1000 chars of each existing file
existing_hashes = {
    "md5(content[:1000])",
    ...
}

# New content: check if hash in set (O(1) lookup)
if hashlib.md5(new_content[:1000]).hexdigest() in existing_hashes:
    print("Duplicate found")
else:
    save_new_content()
```

### Discovery State File
```json
{
  "authors": {
    "al-mohler": {
      "last_check": "2026-05-30T10:59:00",
      "youtube_last_video": "youtube_video_id_123",
      "podcast_feed_last_entry": "https://..."
    },
    "alistair-begg": {...}
  },
  "discovery_log": "/path/to/discovery-log.jsonl"
}
```

---

## Implementation Roadmap

### Phase 1: Basic Infrastructure (Today)
- ✅ Discovery orchestrator skeleton
- ✅ Author source registry
- ✅ Deduplication system
- ✅ State tracking

### Phase 2: Core Sources (Days 1-2)
- YouTube discovery (yt-dlp integration)
- Podcast RSS parsing (feedparser)
- Basic website scraping (BeautifulSoup)

### Phase 3: Audio Processing (Days 2-3)
- Whisper transcription pipeline
- MP3 download + queue
- YouTube captions fallback

### Phase 4: Advanced (Days 3-5)
- Logos API integration
- PDF text extraction (PyPDF2)
- Social media monitoring

### Phase 5: Deployment (Days 5+)
- Cron job: Daily discovery
- Auto-queue to Whisper
- LoRA data pipeline integration

---

## Usage

### Run Discovery Manually
```bash
python3 sermon-discovery-orchestrator.py
```

### Run Specific Author
```bash
python3 sermon-discovery-orchestrator.py --author al-mohler
```

### Run with Whisper Transcription
```bash
python3 sermon-discovery-orchestrator.py --transcribe-audio
```

### Schedule Daily Discovery (Cron)
```bash
0 6 * * * cd /path && python3 sermon-discovery-orchestrator.py >> discovery.log 2>&1
```

---

## Output Files

```
~/lora-data/
├── discovery-log.jsonl          # All discovered content (append-only)
├── discovery-state.json         # Last check times, state
└── discovery-queue/
    ├── to-transcribe/           # Audio files awaiting Whisper
    ├── to-validate/             # New content pending manual review
    └── ready-for-lora/          # Content ready to add to training data
```

---

## Cost Estimation

| Source | Cost | Notes |
|--------|------|-------|
| YouTube (yt-dlp) | Free | No authentication |
| Podcast RSS | Free | Direct feeds |
| Website scraping | Free | Respects robots.txt |
| Whisper (local) | ~$0.004/min audio | Runs on local GPU (~2x speed) |
| Logos API | TBD | Need to request access |
| Twitter API | $200/month | Elevated access required |

**Recommendation:** Start with free sources (YouTube, RSS, scraping), add Whisper later.

---

## Success Metrics

- [ ] Discover 50+ new sermons/month for top authors
- [ ] <5% duplicate rate
- [ ] 90%+ transcription accuracy (Whisper)
- [ ] Zero false negatives (no content missed)
- [ ] Automatic LoRA data prep pipeline

---

_Soli Deo Gloria._
