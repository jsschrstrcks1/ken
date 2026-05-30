# D.A. Carson LoRA Harvest — Complete Master Summary

**Date:** 2026-05-30 14:59 EDT  
**Status:** READY FOR EXECUTION  
**Goal:** Build Carson LoRA v1.0.0 with 1,000,000+ words of content  
**Timeline:** 10–15 days total (parallel execution)

---

## Executive Summary

Ken approved **parallel execution strategy** for Carson content harvest:

1. **Phases 1-5 (Days 1-7):** Non-Logos sources (Ken + Skynet collaborative)
   - Blog posts & articles (Ken: copy-paste)
   - YouTube transcripts (Skynet: automated)
   - Podcast transcripts (Skynet: automated)
   - Academic papers (Skynet: automated)
   - Book excerpts (Ken: copy-paste)

2. **Phase 6 (Days 8-14):** Logos Sermon Library (OCR pipeline)
   - Screenshot Carson Sermon Library
   - Tesseract OCR processing
   - Post-processing & organization
   - Deduplication with external sources

3. **Phase 7 (Day 15):** Training corpus assembly & final QA

---

## Detailed Breakdown

### Phase 1: Gospel Coalition Blog (Ken's Work)
**Duration:** 2–3 hours  
**Yield:** 100,000–150,000 words  
**Method:** Manual copy-paste from gospelcoalition.org

- Search TGC for "D.A. Carson"
- Copy articles to `/carson-harvest/blog-writings/`
- Include metadata (source, date, URL)
- No copy restrictions; TGC is public platform

**Files Created:**
- `CARSON_HARVEST_EXECUTION_GUIDE.md` (detailed how-to)

---

### Phase 2: YouTube Sermon Transcripts (Skynet's Work)
**Duration:** 2–3 hours (automated)  
**Yield:** 400,000–500,000 words  
**Method:** youtube-dl + caption extraction

- Find 100+ Carson sermon videos on YouTube
- Extract captions/transcripts using youtube-dl
- Post-process into markdown
- Save to `/carson-harvest/video-transcripts/`

**Estimated:** 100 videos × 5,000 words = 500,000 words

---

### Phase 3: Podcast Transcripts (Skynet's Work)
**Duration:** 2–3 hours (parallel with Phase 2)  
**Yield:** 300,000–400,000 words  
**Method:** Podcast platform captions + Whisper API

Sources:
- The Briefing (Al Mohler)
- Gospel Coalition Podcast
- Ask Pastor John (John Piper)
- Renewing Your Mind (Ligonier)

**Estimated:** 50+ episodes × 6,000–8,000 words = 300,000–400,000 words

---

### Phase 4: Academic Papers (Skynet's Work)
**Duration:** 1–2 hours (parallel)  
**Yield:** 120,000–240,000 words  
**Method:** Google Scholar + ResearchGate + pdftotext

Sources:
- Google Scholar: Carson papers & citations
- ResearchGate: Published papers (often available as free PDFs)
- Trinity Evangelical Divinity School: Faculty papers
- Trinity Journal: Archives (Carson is editor)

**Estimated:** 30+ papers × 4,000–8,000 words = 120,000–240,000 words

---

### Phase 5: Book Excerpts (Ken's Work)
**Duration:** 1–2 hours  
**Yield:** 50,000–120,000 words  
**Method:** Google Books previews + Amazon "Look Inside"

Books:
- The Intolerance of Tolerance
- How Long, O Lord?
- Love in Hard Places
- Exegetical Fallacies
- Divine Sovereignty & Human Responsibility
- Christ and Culture Revisited
- And others

**Estimated:** 5–8 books × 10,000–15,000 words preview = 50,000–120,000 words

---

### Phase 6: Logos Sermon Library OCR (Skynet's Work)
**Duration:** 3–4 days  
**Yield:** 300,000–400,000 words  
**Method:** Screenshot → Tesseract OCR → Post-process

**Sub-phases:**
- 6a. Screenshot sermon library (2–3 days)
- 6b. Tesseract OCR (1–2 days, automated)
- 6c. Post-processing (1–2 days)
- 6d. Deduplication (1 day)

**Resources:**
- 300+ sermons (1975–2013)
- Tesseract OCR engine (free, open-source)
- Python post-processing scripts

**Estimated:** 300 sermons × 1,000–1,500 words = 300,000–450,000 words

---

### Phase 7: Training Corpus Assembly (Skynet's Work)
**Duration:** 1 day  
**Deliverable:** Ready-to-train Carson corpus

Tasks:
1. Consolidate all sources
2. Deduplicate across sources
3. Add comprehensive metadata
4. Organize by doctrinal topics
5. Count final word count
6. Verify no copyright violations

---

## Total Harvest Summary

| Phase | Source | Yield | Duration | Responsibility |
|-------|--------|-------|----------|-----------------|
| 1 | Blog/Website | 100,000–150,000 | 2–3 hrs | Ken |
| 2 | YouTube | 400,000–500,000 | 2–3 hrs | Skynet (automated) |
| 3 | Podcasts | 300,000–400,000 | 2–3 hrs | Skynet (parallel) |
| 4 | Academic Papers | 120,000–240,000 | 1–2 hrs | Skynet (parallel) |
| 5 | Books | 50,000–120,000 | 1–2 hrs | Ken |
| 6 | Logos Sermons (OCR) | 300,000–400,000 | 3–4 days | Skynet (automated) |
| 7 | Assembly & QA | — | 1 day | Skynet |
| **TOTAL** | **All Sources** | **1,270,000–1,810,000** | **10–15 days** | **Hybrid** |

---

## Parallel Execution Timeline

```
Days 1-2:
├─ Ken: Phase 1 (TGC articles)
└─ Skynet: Phase 2 (YouTube transcripts) + Phase 3 (Podcasts)

Days 2-3:
├─ Ken: Phase 5 (Book excerpts)
└─ Skynet: Phase 4 (Academic papers) + Continue 2-3

Day 4:
├─ Ken: Final review of Phases 1 & 5
└─ Skynet: Consolidate Phases 2-4, prepare for Logos OCR

Days 4-5:
└─ Skynet: Phase 6a (Screenshot Logos sermons)

Days 5-6:
└─ Skynet: Phase 6b (Tesseract OCR processing)

Day 7:
└─ Skynet: Phase 6c (Post-process OCR)

Day 8:
└─ Skynet: Phase 6d (Deduplication)

Day 9:
└─ Skynet: Phase 7 (Final assembly & QA)

Result: 1,000,000+ word Carson corpus ready for training
```

---

## Documents Created

**Framework & Planning:**
- `CARSON_CONTENT_HARVEST_PLAN.md` — Initial 6-week plan (revised to 10-15 days with strategy)
- `CARSON_EXTRACTION_START.md` — Framework setup summary
- `CARSON_EXTRACTION_SESSION_LOG.md` — Live session exploration notes

**Execution Guides:**
- `CARSON_HARVEST_EXECUTION_GUIDE.md` — Phase 1-5 detailed how-to (Ken + Skynet workflow)
- `CARSON_OCR_STRATEGY.md` — Phase 6 OCR pipeline (Logos sermons)

**Tools:**
- `tools/carson-external-harvest.py` — External harvest framework (400 lines)
- `tools/phase1-tgc-scraper.py` — TGC blog scraper (requests-based)
- `tools/phase1-tgc-scraper-stdlib.py` — TGC blog scraper (stdlib-only, no deps)

**Directory Structure:**
```
/carson-harvest/
├─ blog-writings/
├─ video-transcripts/
├─ podcast-transcripts/
├─ academic-papers/
├─ book-excerpts/
├─ ocr-source-images/ (Phase 6)
├─ ocr-raw-text/ (Phase 6)
├─ sermons-ocr/ (Phase 6)
├─ EXTRACTION_GUIDE.md
├─ LOGOS_INVENTORY.md
├─ EXTERNAL_HARVEST_PLAN.md
├─ EXTERNAL_HARVEST_MASTER_PLAN.md
└─ EXTRACTION_LOG.json
```

---

## Ken's Responsibilities (Phases 1 & 5)

### Phase 1: Gospel Coalition Blog Harvest
1. Go to `gospelcoalition.org`
2. Search for "D.A. Carson"
3. For each article:
   - Copy full text
   - Create file: `/carson-harvest/blog-writings/tgc-[number]-[title].md`
   - Include metadata at top (source, URL, date)
   - Paste article content
4. Save 50+ articles (2–3 hours estimated)
5. Yield: 100,000–150,000 words

### Phase 5: Book Excerpts
1. Go to Google Books or Amazon "Look Inside"
2. Search Carson book titles
3. Copy available preview text
4. Create file: `/carson-harvest/book-excerpts/[title].md`
5. Include source and ISBN
6. Save 5–8 books (1–2 hours estimated)
7. Yield: 50,000–120,000 words

---

## Skynet's Responsibilities (Phases 2-4, 6-7)

### Phase 2: YouTube Harvesting (2–3 hours, automated)
- Use youtube-dl to find Carson sermon videos
- Extract captions/transcripts
- Save to `/carson-harvest/video-transcripts/`
- Target: 100+ videos, 500,000 words

### Phase 3: Podcast Harvesting (2–3 hours, parallel)
- Download podcast episodes featuring Carson
- Extract transcripts from platforms or use Whisper API
- Save to `/carson-harvest/podcast-transcripts/`
- Target: 50+ episodes, 400,000 words

### Phase 4: Academic Papers (1–2 hours, parallel)
- Search Google Scholar for Carson papers
- Download free PDFs
- Extract text with pdftotext
- Save to `/carson-harvest/academic-papers/`
- Target: 30+ papers, 240,000 words

### Phase 6: Logos OCR (3–4 days)
- Screenshot Carson Sermon Library sections
- Run Tesseract OCR on screenshots
- Post-process OCR output
- Organize into sermon files
- Deduplicate with external sources
- Target: 300+ sermons, 400,000 words

### Phase 7: Training Corpus Assembly (1 day)
- Consolidate all sources
- Verify deduplication
- Add comprehensive metadata
- Count final words
- Prepare for LoRA training

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Total Words** | 1,000,000+ | Planned: 1,270,000–1,810,000 |
| **Blog Articles** | 50+ | Target: TGC + Ligonier + dcarson.com |
| **YouTube Videos** | 100+ | Automated extraction |
| **Podcast Episodes** | 50+ | Automated transcription |
| **Academic Papers** | 30+ | Automated downloads |
| **Book Excerpts** | 5–8 | Manual copy-paste |
| **Logos Sermons** | 300+ | OCR from 1975–2013 |
| **Deduplication** | Zero duplicates | Cross-source validation |
| **Metadata** | 100% of files | Source, date, URL, confidence scores |
| **Copyright** | Zero violations | All public domain or fair use |

---

## Integration with Ken LoRA v1.0.0

**Timeline Synchronization:**

- **Ken LoRA v1.0.0** launches in **5–6 weeks** with:
  - 735 Ken sermons
  - 5 synthesis essays
  - 5-layer confessional stack
  - Live document versioning

- **Carson LoRA v1.0.0** launches in **6–8 weeks** with:
  - 1,000,000+ words Carson content
  - Parallel theological architecture
  - Same confessional layer approach
  - Full voice extraction

**Both LoRAs release from same hub:** `openclaw/workspace-main/orchestrator/`

---

## Next Steps (Immediate)

1. **Ken:**
   - Read `CARSON_HARVEST_EXECUTION_GUIDE.md`
   - Start Phase 1: Gospel Coalition articles (2–3 hours)
   - Start Phase 5: Book excerpts (1–2 hours)

2. **Skynet:**
   - Prepare Phase 2: YouTube harvester (2–3 hours)
   - Prepare Phase 3: Podcast harvester (2–3 hours)
   - Prepare Phase 4: Academic paper downloader (1–2 hours)
   - Prepare Phase 6: OCR scripts (ready)

3. **Both:**
   - Execute in parallel (Days 1-7)
   - Commit progress daily: `git commit -m "harvest: Carson Phase X — Y words harvested"`
   - Push to `main` branch
   - Review consolidated corpus on Day 9

---

## Estimated Completion

- **Days 1-7:** External sources (non-Logos) = 900,000–1,350,000 words
- **Days 8-14:** Logos OCR = 300,000–400,000 words
- **Day 15:** Final assembly = 1,200,000–1,750,000 words

**Final Carson Corpus:** Ready for training by **Day 15 (June 14, 2026)**

**Carson LoRA v1.0.0 Release:** Mid-June 2026

---

## Soli Deo Gloria

_Every sermon Carson ever preached. Every article he wrote. Every academic paper. Every interview. Everything available — harvested systematically, deduplicated, and organized for AI training._

_Two LoRA projects in parallel: Ken (5–6 weeks) and Carson (10–15 days external + Logos OCR)._

_Building the theological foundation for modern AI discourse._

