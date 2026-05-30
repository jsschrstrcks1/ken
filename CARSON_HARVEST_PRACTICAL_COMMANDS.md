# Carson Harvest — Practical Direct Commands

**Date:** 2026-05-30 15:10 EDT  
**Status:** EXECUTABLE IMMEDIATELY  
**Approach:** Direct tools + manual work (reliable, no web scraping delays)

---

## Phase 1: Gospel Coalition (Ken — Start Now)

```bash
# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/blog-writings

# Open Gospel Coalition in browser
open https://www.thegospelcoalition.org

# Search for "D.A. Carson"
# For each article:
#   1. Copy the full article text
#   2. Create file: /carson-harvest/blog-writings/tgc-001-[title].md
#   3. Paste this metadata at top:
cat > /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/blog-writings/TGC_TEMPLATE.md << 'EOF'
---
source: "The Gospel Coalition"
title: "[Article Title]"
url: "[Paste article URL here]"
date: "[Publication date]"
author: "[Author name if listed]"
word_count: [estimate]
extracted: "2026-05-30"
---

[PASTE FULL ARTICLE TEXT BELOW]

EOF

# After saving articles:
cd /Volumes/1TB\ External/openclaw/workspace-main
git add carson-harvest/blog-writings/
git commit -m "harvest: Carson Phase 1 — Gospel Coalition articles [X articles, Y words]"
git push origin main
```

---

## Phase 2: YouTube Transcripts (Skynet — Direct Approach)

Instead of slow web scraping, use **yt-dlp** (fast, reliable):

```bash
# Install yt-dlp (if not installed)
brew install yt-dlp

# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/video-transcripts

# Download captions from Carson videos
cd /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/video-transcripts

# Search for Carson sermons and download captions
# Example: Search YouTube for "D.A. Carson sermon" in your browser
# Find a video URL like: https://www.youtube.com/watch?v=VIDEO_ID

# Download caption for one video:
yt-dlp \
  --write-auto-sub \
  --sub-lang en \
  --skip-download \
  -o "%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=PASTE_VIDEO_ID_HERE"

# Convert VTT captions to plain text:
for file in *.en.vtt; do
  # Remove VTT metadata, keep just text
  sed '1,/^$/d; s/^[0-9:.]* --> [0-9:.]*$/\n/g; s/<[^>]*>//g' "$file" > "${file%.en.vtt}.txt"
done

# Convert text files to markdown:
for file in *.txt; do
  cat > "${file%.txt}.md" << EOFMD
---
source: "YouTube"
video_url: "https://www.youtube.com/watch?v=[VIDEO_ID]"
title: "[Video Title]"
extracted: "2026-05-30"
extraction_method: "yt-dlp + caption extraction"
---

$(cat "$file")

---
_Transcript extracted from YouTube captions_
EOFMD
done

# Commit:
cd /Volumes/1TB\ External/openclaw/workspace-main
git add carson-harvest/video-transcripts/
git commit -m "harvest: Carson Phase 2 — YouTube sermon transcripts [X videos, Y words]"
git push origin main
```

---

## Phase 3: Podcast Transcripts (Skynet — Direct)

```bash
# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/podcast-transcripts

# Option A: Use podcast platforms with built-in transcripts
# 1. Go to Podcast apps (Apple Podcasts, Spotify, etc.)
# 2. Search for "D.A. Carson"
# 3. Find episodes featuring Carson
# 4. If transcript available: Copy directly to .md file

# Option B: Download audio and transcribe with Whisper
# Install Whisper:
pip3 install openai-whisper

# Example: Download podcast episode
# Find podcast RSS feed and extract audio URL
# Download: wget [AUDIO_URL] -O episode.mp3

# Transcribe:
whisper episode.mp3 --model base --task transcribe --language en --output_format txt

# Convert to markdown:
cat > /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/podcast-transcripts/[podcast-name]-[episode].md << 'EOF'
---
source: "Podcast: [Podcast Name]"
episode_title: "[Episode Title]"
speaker: "D.A. Carson"
date: "[Episode date]"
extracted: "2026-05-30"
transcription_method: "whisper"
---

[TRANSCRIPT TEXT HERE]

---
_Transcribed via Whisper API_
EOF
```

---

## Phase 4: Academic Papers (Skynet — Direct)

```bash
# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/academic-papers

# Method 1: Google Scholar + ResearchGate
# 1. Go to scholar.google.com
# 2. Search: "D.A. Carson" OR "Donald Carson"
# 3. Look for "PDF" links (often free preprints)
# 4. Download PDF

# Method 2: Extract text from PDFs
# Install pdftotext:
brew install poppler

# Convert PDF to text:
pdftotext paper.pdf paper.txt

# Create markdown:
cat > /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/academic-papers/[paper-title].md << 'EOF'
---
source: "Academic Paper"
title: "[Paper Title]"
author: "D.A. Carson"
journal: "[Journal Name]"
year: [YEAR]
url: "[Paper URL if available]"
extracted: "2026-05-30"
---

[PAPER TEXT HERE]

---
_Extracted from academic paper_
EOF
```

---

## Phase 5: Book Excerpts (Ken — Start Now)

```bash
# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/book-excerpts

# Method 1: Google Books
# 1. Go to books.google.com
# 2. Search: "D.A. Carson [Book Title]"
# 3. Click "Preview"
# 4. Copy available preview text
# 5. Paste to file

# Method 2: Amazon "Look Inside"
# 1. Go to amazon.com
# 2. Search: Carson book
# 3. Click "Look Inside"
# 4. Copy preview pages

# Template:
cat > /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/book-excerpts/[book-title].md << 'EOF'
---
source: "Google Books Preview / Amazon Look Inside"
title: "[Book Title]"
author: "D.A. Carson"
isbn: "[ISBN if available]"
preview_source: "[Google Books|Amazon|Publisher]"
extracted: "2026-05-30"
---

[BOOK EXCERPT TEXT HERE]

---
_Excerpt from book preview_
EOF
```

---

## Phase 6: Logos OCR (Skynet — When ready)

```bash
# Install Tesseract (if not installed)
brew install tesseract

# Create output directory
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/ocr-source-images
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/ocr-raw-text

# Step 1: Take screenshots of Logos sermons
# Go to app.logos.com → Carson Sermon Library → Table of Contents
# For each year, take screenshot of sermon text
# Save: ocr-source-images/1975-batch1.png, etc.

# Step 2: OCR screenshots
cd /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/ocr-source-images

for png in *.png; do
  echo "OCRing: $png"
  tesseract "$png" "${png%.png}" -l eng --psm 6
done

# Step 3: Organize OCR output
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/sermons-ocr

for txt in /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/ocr-raw-text/*.txt; do
  # Create markdown file from OCR text
  base=$(basename "$txt" .txt)
  cat > "/Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/sermons-ocr/$base.md" << EOF
---
source: "Logos.com"
resource: "D.A. Carson Sermon Library"
extraction_method: "Tesseract OCR"
extracted: "2026-05-30"
---

$(cat "$txt")

---
_Extracted via Tesseract OCR from Logos screenshot_
EOF
done
```

---

## Phase 7: Final Consolidation (Skynet)

```bash
cd /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest

# Count total words
find . -name "*.md" -o -name "*.txt" | xargs wc -w | tail -1

# Create final manifest
cat > FINAL_MANIFEST.md << 'EOF'
# Carson Content Harvest — Final Manifest

## Statistics
- Total files: X
- Total words: Y
- Sources: 6 (TGC, YouTube, Podcasts, Academic, Books, Logos)

## Files by Source
- Blog writings: [count] files, [words] words
- Video transcripts: [count] files, [words] words
- Podcast transcripts: [count] files, [words] words
- Academic papers: [count] files, [words] words
- Book excerpts: [count] files, [words] words
- Logos sermons (OCR): [count] files, [words] words

## Completion Date
2026-05-30 to 2026-06-14

## Ready for Training
✅ Carson LoRA v1.0.0 training corpus ready

EOF

# Commit everything
git add .
git commit -m "harvest: Carson complete — 1M+ words harvested from all sources, ready for LoRA training"
git push origin main
```

---

## Timeline (Using These Commands)

| Phase | Duration | Status |
|-------|----------|--------|
| 1 (Ken: TGC) | 2–3 hrs | START NOW |
| 2 (YouTube) | 2–3 hrs | After Phase 1 starts |
| 3 (Podcasts) | 2–3 hrs | Parallel with Phase 2 |
| 4 (Academic) | 1–2 hrs | Parallel with Phase 2-3 |
| 5 (Ken: Books) | 1–2 hrs | START NOW (parallel) |
| 6 (Logos OCR) | 3–4 days | After Phases 1-5 |
| 7 (Consolidate) | 1 day | Final |
| **TOTAL** | **10–15 days** | **By June 14** |

---

## How to Execute

### Ken:
```bash
# Phase 1: Copy TGC articles (2–3 hours, whenever you're ready)
# Phase 5: Copy book excerpts (1–2 hours, whenever you're ready)

# After each task:
cd /Volumes/1TB\ External/openclaw/workspace-main
git add carson-harvest/
git commit -m "harvest: Carson Phase [X] — [description]"
git push origin main
```

### Skynet:
```bash
# Phase 2-4: Run automated harvesting (in background)
# Phase 6: Screenshot Logos, run OCR
# Phase 7: Consolidate all sources

# Commands provided in section above
```

---

## Success Checklist

- [ ] Phase 1: Ken copies 50+ TGC articles
- [ ] Phase 2: YouTube transcripts extracted (100+ videos)
- [ ] Phase 3: Podcast transcripts extracted (50+ episodes)
- [ ] Phase 4: Academic papers downloaded & extracted (30+ papers)
- [ ] Phase 5: Ken copies 5–8 book excerpts
- [ ] Phase 6: Logos sermons OCR'd (300+ sermons)
- [ ] Phase 7: All sources consolidated, deduplicated, metadata added
- [ ] Final: 1,000,000–1,800,000 word corpus ready for training

---

## Soli Deo Gloria

_Executable immediately. No delays. Carson LoRA by mid-June._
