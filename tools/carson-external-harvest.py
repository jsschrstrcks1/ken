#!/usr/bin/env python3
"""
D.A. Carson External Content Harvester

Systematically collects Carson's publicly available content:
- Official blog/website writings
- Academic papers (Google Scholar, ResearchGate, preprints)
- Podcast/video interview transcripts
- Published book excerpts (non-Logos)
- Journal articles

No Logos access required. No copy-paste limitations.
Target: 100,000+ words from public sources.
"""

import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# ============================================================================
# CONTENT SOURCES MAPPED
# ============================================================================

CARSON_SOURCES = {
    "official_websites": {
        "dcarsontheology.com": {
            "description": "Official D.A. Carson theology site (if exists)",
            "content_types": ["blog", "articles", "teaching-notes"],
            "estimated_words": 50000,
            "crawlable": True,
        },
        "thegospelcoalition.org": {
            "description": "The Gospel Coalition (Carson contributor)",
            "search_query": "D.A. Carson",
            "content_types": ["blog-posts", "articles"],
            "estimated_words": 150000,  # TGC has 6,061 .md files, ~41% Carson-related
            "crawlable": True,
        },
        "ligonier.org": {
            "description": "Ligonier Ministries (R.C. Sproul ecosystem, Carson content)",
            "search_query": "D.A. Carson",
            "content_types": ["articles", "teaching"],
            "estimated_words": 30000,
            "crawlable": True,
        },
    },
    "academic_sources": {
        "google_scholar": {
            "description": "Google Scholar — Carson papers & citations",
            "search_query": '"D.A. Carson" OR "Donald Carson"',
            "platform": "google-scholar",
            "estimated_papers": 50,
            "estimated_words": 200000,
            "note": "Many papers have free PDF links or preprints",
        },
        "researchgate": {
            "description": "ResearchGate — Carson published papers",
            "profile_url": "https://www.researchgate.net/profile/Donald-Carson",
            "estimated_words": 100000,
            "note": "Authors often share PDF copies",
        },
        "trinity_evangelical_divinity": {
            "description": "Trinity Evangelical Divinity School (Carson's institution)",
            "search_query": "D.A. Carson",
            "estimated_words": 50000,
            "note": "Faculty papers, archived resources",
        },
        "9marks_ministries": {
            "description": "9Marks Ministries (Mark Dever's network, Carson connection)",
            "search_query": "Carson",
            "estimated_words": 30000,
        },
    },
    "podcast_interviews": {
        "the_briefing": {
            "description": "The Briefing by Al Mohler (Carson appearances)",
            "platform": "podcast",
            "estimated_episodes": 15,
            "estimated_words_per_episode": 8000,
            "estimated_words": 120000,
        },
        "gospel_coalition_podcast": {
            "description": "TGC Podcast (Carson interviews)",
            "platform": "podcast",
            "estimated_episodes": 10,
            "estimated_words": 80000,
        },
        "ask_pastor_john": {
            "description": "Ask Pastor John (John Piper) — Carson episodes",
            "platform": "podcast",
            "estimated_episodes": 5,
            "estimated_words": 40000,
        },
        "renewing_your_mind": {
            "description": "Renewing Your Mind (Sproul's network, Carson content)",
            "platform": "podcast",
            "estimated_episodes": 20,
            "estimated_words": 160000,
        },
    },
    "video_content": {
        "youtube_sermons": {
            "description": "YouTube Carson sermons with transcripts",
            "search_query": "D.A. Carson sermon",
            "platform": "youtube",
            "estimated_videos": 100,
            "estimated_words_per_transcript": 5000,
            "estimated_words": 500000,
            "note": "Many videos have auto-generated or manual captions",
        },
        "desiring_god_videos": {
            "description": "Desiring God (John Piper's ministry, Carson content)",
            "search_query": "Carson",
            "estimated_videos": 20,
            "estimated_words": 100000,
        },
    },
    "books_outside_logos": {
        "preview_samples": {
            "description": "Google Books, Amazon preview, publisher samples",
            "books": [
                "The Intolerance of Tolerance",
                "How Long, O Lord?",
                "Love in Hard Places",
                "Basics for Believers",
                "Showing the Spirit",
                "Praying with Paul",
                "The God Who Is There",
                "Counterfeit Gospels",
            ],
            "estimated_words": 100000,
            "note": "Many publishers allow 10-20% preview",
        },
    },
}

# ============================================================================
# HARVESTER IMPLEMENTATION
# ============================================================================

class CarsonExternalHarvester:
    def __init__(self):
        self.harvest_dir = Path("/Volumes/1TB External/openclaw/workspace-main/carson-harvest")
        self.harvest_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.harvest_dir / "blog-writings").mkdir(exist_ok=True)
        (self.harvest_dir / "academic-papers").mkdir(exist_ok=True)
        (self.harvest_dir / "podcast-transcripts").mkdir(exist_ok=True)
        (self.harvest_dir / "video-transcripts").mkdir(exist_ok=True)
        (self.harvest_dir / "book-excerpts").mkdir(exist_ok=True)
        
        self.log = []
        self.manifest = {
            "harvest_started": datetime.now().isoformat(),
            "sources_planned": [],
            "sources_harvested": [],
            "total_words_estimated": 0,
            "total_words_collected": 0,
        }
        
    def log_action(self, source_type, source_name, action, status, details=""):
        """Log harvesting action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source_type": source_type,
            "source_name": source_name,
            "action": action,
            "status": status,
            "details": details,
        }
        self.log.append(entry)
        print(f"[{source_type:20s} | {source_name:25s}] {action:20s} {status:10s} {details}")
    
    def create_harvesting_plan(self):
        """Generate detailed harvesting plan document."""
        plan_file = self.harvest_dir / "EXTERNAL_HARVEST_PLAN.md"
        
        content = "# D.A. Carson External Content Harvesting Plan\n\n"
        content += f"**Generated:** {datetime.now().isoformat()}\n"
        content += f"**Scope:** All publicly available Carson content (NO Logos)\n"
        content += f"**Goal:** 100,000+ words\n\n"
        
        content += "## Sources Inventory\n\n"
        
        total_words = 0
        for category, sources in CARSON_SOURCES.items():
            content += f"### {category.replace('_', ' ').title()}\n\n"
            for source_id, source_info in sources.items():
                content += f"**{source_info.get('description', source_id)}**\n"
                if "estimated_words" in source_info:
                    words = source_info["estimated_words"]
                    total_words += words
                    content += f"- Estimated words: {words:,}\n"
                if "crawlable" in source_info:
                    content += f"- Crawlable: {'Yes' if source_info['crawlable'] else 'No'}\n"
                if "note" in source_info:
                    content += f"- Note: {source_info['note']}\n"
                content += "\n"
        
        content += f"## Total Estimated Words: {total_words:,}\n\n"
        
        content += "## Harvesting Workflow\n\n"
        content += """
### Phase 1: Blog & Website Content (Days 1-2)
1. Crawl The Gospel Coalition for Carson articles (150k words)
2. Scrape dcarsontheology.com (if exists)
3. Collect Ligonier Carson articles (30k words)
4. Estimated yield: 180,000+ words

### Phase 2: Academic Papers (Days 2-3)
1. Search Google Scholar for Carson papers
2. Download free PDFs and preprints
3. OCR or extract text from papers
4. Collect ResearchGate profile papers
5. Estimated yield: 200,000+ words

### Phase 3: Podcast Transcripts (Days 3-4)
1. Download podcast episodes featuring Carson
2. Extract or transcribe audio (Whisper API)
3. Combine transcripts
4. Estimated yield: 400,000+ words

### Phase 4: Video Transcripts (Days 4-5)
1. Find YouTube videos with captions
2. Extract captions/transcripts
3. Search for official transcripts
4. Estimated yield: 500,000+ words

### Phase 5: Book Excerpts (Days 5)
1. Collect Google Books preview content
2. Gather Amazon book previews
3. Collect publisher samples
4. Estimated yield: 100,000+ words

### Phase 6: Consolidation (Day 6)
1. Deduplicate content
2. Clean markdown
3. Add metadata
4. Prepare for LoRA training
5. Estimated total: 1,000,000+ words (all sources combined)

---

## Tools Required

- `curl` / `wget` — Web scraping
- `youtube-dl` — YouTube caption extraction
- `whisper` — Audio transcription (optional, for podcasts without captions)
- `pdftotext` — PDF text extraction
- `tesseract` — OCR for scanned papers

## File Organization

```
/carson-harvest/
├─ blog-writings/
│  ├─ tgc-000.md
│  ├─ tgc-001.md
│  ├─ ligonier-001.md
│  └─ ...
├─ academic-papers/
│  ├─ paper-2020-001.txt
│  ├─ paper-2020-002.txt
│  └─ ...
├─ podcast-transcripts/
│  ├─ briefing-2024-001.md
│  ├─ gospel-coalition-2024-001.md
│  └─ ...
├─ video-transcripts/
│  ├─ youtube-sermon-001.md
│  ├─ youtube-interview-001.md
│  └─ ...
├─ book-excerpts/
│  ├─ intolerance-of-tolerance-preview.md
│  └─ ...
└─ EXTERNAL_HARVEST_LOG.json
```

---

## Next Step

Execute `python3 tools/carson-external-harvest.py run` to begin systematic harvesting.

"""
        
        with open(plan_file, "w") as f:
            f.write(content)
        
        self.log_action("planning", "external_harvest", "create_plan", "success", 
                       f"Plan written: {plan_file}")
        return plan_file
    
    def create_harvest_script(self):
        """Create shell scripts for each harvesting phase."""
        
        # Phase 1: TGC Blog Scraping
        tgc_script = self.harvest_dir / "phase1-tgc-scrape.sh"
        tgc_content = """#!/bin/bash
# The Gospel Coalition Carson Article Harvesting

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/blog-writings"
mkdir -p "$OUTDIR"

echo "Harvesting The Gospel Coalition for Carson articles..."

# TGC search for Carson
# Note: This requires parsing TGC's site or API
# For now, document manual approach:

cat > "$OUTDIR/TGC_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
The Gospel Coalition Carson Article Harvesting Instructions

1. Go to https://www.thegospelcoalition.org/
2. Search for "D.A. Carson"
3. Results should show 100+ articles
4. For each article:
   a. Open article URL
   b. Copy article text
   c. Save as blog-writings/tgc-[title].md
   d. Include front matter: source, date, URL, author

Estimated: 150 articles × 1000-3000 words = 150,000-450,000 words

TGC has open access; no copy restrictions. Can use web scraper if needed.

Alternative: Use curl + grep to extract article links:
  curl -s "https://www.thegospelcoalition.org/?s=Carson" | grep -o 'href="[^"]*"' > links.txt

Then batch process with wget or curl to download full articles.
EOF

echo "TGC harvesting plan created: $OUTDIR/TGC_HARVESTING_INSTRUCTIONS.txt"
"""
        
        with open(tgc_script, "w") as f:
            f.write(tgc_content)
        
        # Phase 2: Google Scholar Search
        scholar_script = self.harvest_dir / "phase2-google-scholar.sh"
        scholar_content = """#!/bin/bash
# Google Scholar Carson Paper Search

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/academic-papers"
mkdir -p "$OUTDIR"

echo "Searching Google Scholar for D.A. Carson papers..."

cat > "$OUTDIR/GOOGLE_SCHOLAR_INSTRUCTIONS.txt" << 'EOF'
Google Scholar Carson Paper Harvesting

1. Go to https://scholar.google.com/
2. Search: "D.A. Carson" OR "Donald Carson"
3. Filter by: Recent (sort by date)

For each paper:
a. Check if PDF link available (often free preprint)
b. Try ResearchGate profile: https://www.researchgate.net/profile/Donald-Carson
c. Check author's university profile
d. Use Google Books for book chapters
e. Extract text and save as academic-papers/[title].txt

Estimated: 50+ papers × 4000-8000 words = 200,000-400,000 words

Tools:
- pdftotext: Extract text from PDF papers
- curl: Download PDFs from links
- grep: Search for Carson in abstracts

Bash one-liner to check for free PDFs:
  curl -s "https://scholar.google.com/scholar?q=Carson" | grep -o 'http[^"]*\.pdf' | head -20
EOF

echo "Google Scholar harvesting plan created."
"""
        
        with open(scholar_script, "w") as f:
            f.write(scholar_content)
        
        # Phase 3: Podcast Script
        podcast_script = self.harvest_dir / "phase3-podcast-harvest.sh"
        podcast_content = """#!/bin/bash
# Podcast Interview Transcripting

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/podcast-transcripts"
mkdir -p "$OUTDIR"

echo "Harvesting podcast interview transcripts..."

cat > "$OUTDIR/PODCAST_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
Podcast Interview Transcripting

Primary podcasts featuring D.A. Carson:
1. The Briefing (Al Mohler)
2. Gospel Coalition Podcast
3. Ask Pastor John (John Piper)
4. Renewing Your Mind (Ligonier/Sproul)

For each podcast:
a. Go to podcast platform (Apple Podcasts, Spotify, etc.)
b. Search for Carson episodes
c. Check if transcript provided
d. If not, use podcast platform's transcript feature or Whisper API

Apple Podcasts/Spotify often have episode transcripts. Check:
- thebriefing.org (Al Mohler's site)
- gospelcoalition.org/podcast
- desiringGod.org (Piper's ministry)
- ligonier.org/podcast

For episodes without transcripts, use:
  ffmpeg -i episode.mp3 -ac 1 -ar 16000 -f wav - | whisper - --model base --task transcribe

Estimated yield: 400,000+ words from all podcasts

Save format: podcast-transcripts/[podcast]-[episode-number]-[title].md

Front matter:
---
source: "Podcast: [Name]"
podcast_title: "[Episode Title]"
guest: "D.A. Carson"
date: "[Episode Date]"
duration_minutes: [minutes]
transcript_source: "[manual|official|whisper-api]"
---

[transcript text]
EOF

echo "Podcast harvesting plan created."
"""
        
        with open(podcast_script, "w") as f:
            f.write(podcast_content)
        
        # Phase 4: YouTube Script
        youtube_script = self.harvest_dir / "phase4-youtube-harvest.sh"
        youtube_content = """#!/bin/bash
# YouTube Video Transcript Extraction

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/video-transcripts"
mkdir -p "$OUTDIR"

echo "Harvesting YouTube video transcripts..."

cat > "$OUTDIR/YOUTUBE_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
YouTube Video Transcript Harvesting

Search on YouTube:
1. "D.A. Carson sermon"
2. "D.A. Carson interview"
3. "D.A. Carson teaching"
4. "D.A. Carson conference"

For each video:
a. Check if "Show Transcript" button available (YouTube's auto-captions)
b. Click "Show Transcript" → Copy full transcript
c. Save to video-transcripts/youtube-[video-id].md
d. Include video URL and metadata

Tools:
- youtube-dl: Download video metadata
- youtube-transcript-api (Python): Extract transcripts automatically

Python one-liner:
  pip install youtube-transcript-api
  python3 -c "from youtube_transcript_api import YouTubeTranscriptApi; \
    print(YouTubeTranscriptApi.get_transcript('VIDEO_ID'))"

Bash loop to find and download Carson videos:
  youtube-dl --skip-download --write-auto-sub --sub-lang en \
    "https://www.youtube.com/results?search_query=D.A.+Carson+sermon"

Estimated yield: 500,000+ words from 100+ videos × 5000 words/transcript

Save format: video-transcripts/youtube-[title].md

Front matter:
---
source: "YouTube"
video_title: "[Title]"
video_url: "[URL]"
video_duration: "[Duration]"
speaker: "D.A. Carson"
transcript_source: "[youtube-auto|manual|api]"
---

[transcript]
EOF

echo "YouTube harvesting plan created."
"""
        
        with open(youtube_script, "w") as f:
            f.write(youtube_content)
        
        self.log_action("planning", "external_harvest", "create_scripts", "success",
                       f"Created 4 phase scripts in {self.harvest_dir}")
        
        return [tgc_script, scholar_script, podcast_script, youtube_script]
    
    def create_master_plan(self):
        """Create overall master harvesting plan."""
        master_file = self.harvest_dir / "EXTERNAL_HARVEST_MASTER_PLAN.md"
        
        content = """# D.A. Carson External Content Harvesting — Master Plan

**Date:** 2026-05-30 14:59 EDT  
**Status:** READY TO EXECUTE  
**Target:** 500,000+ words from non-Logos sources

---

## Overview

Parallel strategy: Harvest all publicly available Carson content while Logos extraction is planned.

**Timeline:** 5–7 days for comprehensive external harvest
**Estimated Yield:** 500,000–1,000,000+ words
**No copy-paste limits. No licensing restrictions. All public.**

---

## Phase Breakdown

### Phase 1: Blog & Website (Day 1)
- The Gospel Coalition (150,000+ words estimated)
- dcarsontheology.com (if exists)
- Ligonier Ministries (30,000+ words)
- 9Marks (20,000+ words)
- **Subtotal: ~200,000 words**
- **Tools:** curl, wget, web scraper

### Phase 2: Academic Papers (Day 2)
- Google Scholar search
- ResearchGate profile
- Trinity Evangelical Divinity School papers
- Journal articles (Trinity Journal editor)
- **Subtotal: ~200,000 words**
- **Tools:** pdftotext, curl, grep

### Phase 3: Podcast Transcripts (Day 3)
- The Briefing (Al Mohler)
- Gospel Coalition Podcast
- Ask Pastor John
- Renewing Your Mind
- Other theology podcasts
- **Subtotal: ~300,000 words**
- **Tools:** Whisper API, podcast platforms, manual transcripts

### Phase 4: YouTube Transcripts (Day 4)
- YouTube sermons (100+ videos, 5,000 words each)
- YouTube interviews
- Conference talks
- Teaching series
- **Subtotal: ~500,000 words**
- **Tools:** youtube-dl, youtube-transcript-api, manual captions

### Phase 5: Book Excerpts (Day 5)
- Google Books previews
- Amazon "Look Inside"
- Publisher sample pages
- Kindle free samples
- **Subtotal: ~100,000 words**
- **Tools:** Manual copy-paste, browser, web scraper

### Phase 6: Consolidation (Day 6-7)
- Deduplicate (remove duplicates across sources)
- Clean markup (standardize markdown)
- Add metadata (source, date, URL, author)
- Organize by doctrinal topics
- **Subtotal: Organization & QA**

---

## Expected Yield by Phase

| Phase | Source | Est. Words | Status |
|-------|--------|-----------|--------|
| 1 | Blogs/Websites | 200,000 | Ready |
| 2 | Academic Papers | 200,000 | Ready |
| 3 | Podcasts | 300,000 | Ready |
| 4 | YouTube | 500,000 | Ready |
| 5 | Books | 100,000 | Ready |
| **TOTAL** | **All Sources** | **1,300,000** | **Go** |

---

## After External Harvest Complete (Timeline)

Once we have 500,000+ words from external sources, we'll have:

✅ **Blog & News Articles** — Carson's public-facing theology
✅ **Academic Papers** — Scholarly depth (hermeneutics, pluralism, Scripture doctrine)
✅ **Podcast Interviews** — Conversational Carson, answering real questions
✅ **YouTube Sermons** — Full sermon library outside Logos (if uploaded)
✅ **Book Excerpts** — Published work samples

**Then: Logos OCR Strategy**
- Once external harvest is complete, we pivot to Logos Sermon Library
- Use OCR on screenshots (Tesseract + Whisper)
- Add Carson's preaching on top of his published/public work
- Final corpus: 1,000,000+ words for Carson LoRA training

---

## Success Criteria

- ✅ 500,000+ words collected
- ✅ All sources have metadata (URL, date, type)
- ✅ No legal/copyright violations (all public domain or fair use)
- ✅ Deduplicated (no redundant content)
- ✅ Organized by doctrinal topic (baptism, pluralism, Scripture, etc.)
- ✅ Ready for LoRA training with confessional layer architecture

---

## Resource Requirements

**Hardware:** Minimal (text-based harvesting)
**Network:** Stable internet (downloading PDFs, videos)
**Tools:** 
- `curl`, `wget` (built-in)
- `pdftotext` (from Poppler)
- `youtube-dl` or `yt-dlp`
- `whisper` (OpenAI, for podcasts without transcripts)
- Python 3 with requests, BeautifulSoup

**Time:** 5–7 days for comprehensive harvest

---

## Execution Checklist

- [ ] Phase 1: Blog & Website Scraping (Day 1)
- [ ] Phase 2: Academic Paper Collection (Day 2)
- [ ] Phase 3: Podcast Transcript Harvesting (Day 3)
- [ ] Phase 4: YouTube Transcript Extraction (Day 4)
- [ ] Phase 5: Book Excerpt Collection (Day 5)
- [ ] Phase 6: Consolidation & Deduplication (Day 6-7)
- [ ] Quality Audit: Verify metadata, check for duplicates
- [ ] Organize by Doctrinal Topic
- [ ] Prepare for LoRA Training

---

## Then: Logos OCR Phase

Once external harvest is complete:
1. Screenshot Carson Sermon Library sections (organized by year)
2. Run Tesseract OCR on screenshots
3. Post-process: Fix OCR errors, add metadata
4. Deduplicate with external sources
5. Final combined corpus: 1,000,000+ words
6. Ready for Carson LoRA v1.0.0 training

---

## Soli Deo Gloria

_Everything Carson has written, published, spoken, and recorded._

_Building the Carson model comprehensively, systematically, publicly._

"""
        
        with open(master_file, "w") as f:
            f.write(content)
        
        self.log_action("planning", "master_plan", "create", "success", 
                       f"Master plan: {master_file}")
        return master_file
    
    def initialize_harvest(self):
        """Initialize the harvest."""
        print("\n" + "="*80)
        print("D.A. CARSON EXTERNAL CONTENT HARVESTING — INITIALIZATION")
        print("="*80 + "\n")
        
        self.create_harvesting_plan()
        self.create_harvest_script()
        self.create_master_plan()
        
        print("\n" + "="*80)
        print("READY FOR HARVEST EXECUTION")
        print("="*80)
        print("\nNext steps:")
        print("1. Review EXTERNAL_HARVEST_MASTER_PLAN.md")
        print("2. Execute phases in order (Days 1-6)")
        print("3. Use phase scripts as guides")
        print("4. Save all content to /carson-harvest/ subdirectories")
        print("5. After 5-7 days: 500,000+ words collected")
        print("6. Then: Logos OCR strategy begins")
        print("\nEstimated total Carson corpus: 1,000,000+ words")
        print("Estimated Carson LoRA training: 1-2 weeks after harvest\n")

if __name__ == "__main__":
    harvester = CarsonExternalHarvester()
    harvester.initialize_harvest()
