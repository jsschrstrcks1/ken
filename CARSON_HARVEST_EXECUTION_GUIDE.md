# Carson Content Harvest — Practical Execution Guide

**Date:** 2026-05-30 14:59 EDT  
**Status:** READY FOR MANUAL + AUTOMATED HARVEST  
**Target:** 500,000+ words from public sources in 5-7 days

---

## Strategic Overview

Given web scraping complexities and rate limiting, we'll use a **hybrid approach**:

1. **Manual Copy-Paste** (Ken): TGC, Ligonier, dcarsontheology.com
   - Ken pastes directly; I organize and process
   - Fast for focused sources (10-15 articles = 50,000+ words in 1-2 hours)

2. **Automated Harvesting** (Skynet): YouTube, Podcasts, Academic databases
   - I run youtube-dl, Whisper transcription, academic paper downloads
   - Parallel to Ken's work

3. **OCR Pipeline** (Skynet): Logos Sermons (after external harvest)
   - Screenshot → Tesseract OCR → Post-process → Deduplicate

---

## Phase 1: Blog & Website Content (Ken's Work — 2-3 hours)

### Sources
- **The Gospel Coalition** (gospelcoalition.org)
  - Carson Center podcast
  - Carson blog posts & articles
  - Search: "D.A. Carson"
  - Estimated: 50+ articles, 150,000+ words

- **Ligonier Ministries** (ligonier.org)
  - Search: "D.A. Carson"
  - Estimated: 20+ articles, 30,000+ words

- **dcarsontheology.com** (if active)
  - Official Carson blog
  - All posts
  - Estimated: 20+ posts, 30,000+ words

### How Ken Executes

1. Go to each website
2. Search/browse for Carson content
3. **For each article:**
   - Copy article text (no copy-paste restrictions on TGC/Ligonier)
   - Create file: `/carson-harvest/blog-writings/[source]-[title].md`
   - Include metadata at top:
     ```yaml
     ---
     source: "The Gospel Coalition"
     title: "[Article Title]"
     url: "[URL]"
     date: "[Publication Date]"
     author: "[Author if listed]"
     ---
     ```
   - Paste article content below metadata

4. **Save to:** `/carson-harvest/blog-writings/`

### Time Estimate
- **50 articles × 3-4 min/article** = 2.5–3.5 hours
- **Yield:** 100,000–150,000 words

---

## Phase 2: YouTube Sermon Transcripts (Skynet's Work — 2-3 hours)

### Strategy
I'll systematically download YouTube captions and transcripts from:
- Carson sermon videos
- Carson interview videos
- Carson teaching playlists

### Execution
```bash
# Find YouTube videos with Carson content
youtube-dl \
  --skip-download \
  --write-auto-sub \
  --sub-lang en \
  -o "%(title)s.%(ext)s" \
  "https://www.youtube.com/results?search_query=D.A.+Carson+sermon"

# Extract transcripts
for vtt_file in *.en.vtt; do
  # Convert VTT to plain text
  sed 's/^[0-9]*$//' "$vtt_file" | grep -v "^--$" > "${vtt_file%.en.vtt}.txt"
done

# Save to carson-harvest/video-transcripts/
```

### Sources
- YouTube Carson sermons (100+ videos available)
- YouTube Carson interviews
- Carson conference talks

### Yield Estimate
- **100+ videos × 5,000 words/transcript** = 500,000+ words

---

## Phase 3: Podcast Transcripts (Parallel)

### Platforms
1. **The Briefing** (Al Mohler) — Carson episodes available
2. **Gospel Coalition Podcast** — Carson episodes
3. **Ask Pastor John** (John Piper) — Carson episodes
4. **Renewing Your Mind** (Ligonier) — Carson content

### Method
- Download podcast episodes (mp3)
- Use Whisper API to transcribe (if no captions available)
- Extract captions if available natively
- Save to `carson-harvest/podcast-transcripts/`

### Yield Estimate
- **50+ episodes × 6,000–10,000 words/transcript** = 300,000–500,000 words

---

## Phase 4: Academic Papers (Parallel)

### Sources
1. **Google Scholar** — Search "D.A. Carson"
   - Many papers have free PDF links
   - Download PDFs; extract text with pdftotext

2. **ResearchGate** — Carson profile
   - Authors often share PDFs
   - Download and extract

3. **Trinity Evangelical Divinity School**
   - Faculty papers
   - Published works

4. **Trinity Journal** (Carson is editor)
   - Full archives available
   - Download and extract

### Method
```bash
# Extract text from PDFs
pdftotext paper.pdf paper.txt

# Save to carson-harvest/academic-papers/
```

### Yield Estimate
- **30+ papers × 4,000–8,000 words** = 120,000–240,000 words

---

## Phase 5: Book Excerpts (Optional)

### Sources
- **Google Books** — Carson books with preview text
- **Amazon "Look Inside"** — Preview text from books
- **Publisher Websites** — Sample chapters
- **Kindle Unlimited** — If Ken has access

### Method
- Copy preview text where available
- Save to `carson-harvest/book-excerpts/`
- Include source and ISBN

### Yield Estimate
- **5–8 books × 10,000–15,000 words preview** = 50,000–120,000 words

---

## Consolidated Harvest Summary

| Phase | Source | Words | Time | Responsibility |
|-------|--------|-------|------|-----------------|
| 1 | Blog/Website | 100,000–150,000 | 2–3 hrs | Ken (copy-paste) |
| 2 | YouTube | 500,000 | 2–3 hrs | Skynet (youtube-dl + Whisper) |
| 3 | Podcasts | 300,000–500,000 | 2–3 hrs | Skynet (podcast platforms + Whisper) |
| 4 | Academic Papers | 120,000–240,000 | 1–2 hrs | Skynet (Google Scholar + pdftotext) |
| 5 | Books | 50,000–120,000 | 1–2 hrs | Ken (copy preview text) |
| **TOTAL** | **All Sources** | **1,070,000–1,510,000** | **5–7 days parallel** | **Hybrid** |

---

## After Phase 5: Logos OCR Strategy

Once we have 500,000+ words from external sources, we'll:

1. **Take screenshots** of Carson Sermon Library sections (organized by year)
2. **Run Tesseract OCR** on screenshots
3. **Post-process** OCR output (fix errors, add metadata)
4. **Deduplicate** with external sources
5. **Final combined corpus:** 1,000,000+ words ready for LoRA training

---

## File Organization

```
/carson-harvest/
├─ blog-writings/
│  ├─ tgc-001-[title].md
│  ├─ tgc-002-[title].md
│  ├─ ligonier-001-[title].md
│  └─ ...
│
├─ video-transcripts/
│  ├─ youtube-sermon-001.md
│  ├─ youtube-sermon-002.md
│  └─ ...
│
├─ podcast-transcripts/
│  ├─ briefing-001.md
│  ├─ gospel-coalition-001.md
│  └─ ...
│
├─ academic-papers/
│  ├─ paper-2024-001.txt
│  ├─ paper-2024-002.txt
│  └─ ...
│
├─ book-excerpts/
│  ├─ intolerance-of-tolerance.md
│  └─ ...
│
├─ HARVEST_LOG.json
└─ FINAL_MANIFEST.md
```

---

## Front Matter Format

Every file should include:
```yaml
---
source: "[Source Type]"
title: "[Title]"
url: "[URL or source reference]"
date: "[Date if available]"
author: "[Author/Creator]"
word_count: [number]
extracted: "[ISO timestamp]"
---

# Content here

_Source: [attribution]_
```

---

## Success Criteria

✅ 500,000+ words harvested from public sources  
✅ All files have proper metadata (source, date, URL)  
✅ No copyright violations (all public domain or fair use)  
✅ Organized by type and source  
✅ Deduplicated (no redundant content)  
✅ Ready for Carson LoRA training  

---

## Timeline

- **Days 1-2:** Phase 1 (Ken: Blog harvest) + Phase 2 (Skynet: YouTube)
- **Days 2-3:** Phase 3 (Skynet: Podcasts) + Phase 4 (Skynet: Academic)
- **Day 4:** Phase 5 (Ken: Book excerpts) + Consolidation
- **Days 5-6:** OCR pipeline for Logos sermons
- **Day 7:** Final deduplication, metadata audit, ready for training

---

## Commits & Tracking

After each phase:
```bash
git commit -m "harvest: Carson Phase [N] — [source] [word count] words extracted"
git push origin main
```

---

## Next Action

**For Ken:** Start Phase 1 immediately
- Go to gospelcoalition.org and search for Carson
- Copy articles to `/carson-harvest/blog-writings/`
- Include metadata

**For Skynet:** Prepare Phase 2-4 automation
- Create YouTube transcript harvester
- Create Podcast transcript harvester  
- Prepare academic paper downloader
- Run in parallel while Ken works on Phase 1

---

## Questions?

This guide is your execution roadmap. Start with Phase 1 (Ken copy-pasting TGC articles) and Phase 2-4 (Skynet's automation) in parallel. By day 5, we'll have 500,000+ words and be ready for OCR on Logos sermons.

**Soli Deo Gloria.**

_Building Carson LoRA comprehensively, systematically, with no delays._
