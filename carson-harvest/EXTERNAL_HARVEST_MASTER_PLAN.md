# D.A. Carson External Content Harvesting — Master Plan

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

