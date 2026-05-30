# D.A. Carson External Content Harvesting Plan

**Generated:** 2026-05-30T15:01:06.997830
**Scope:** All publicly available Carson content (NO Logos)
**Goal:** 100,000+ words

## Sources Inventory

### Official Websites

**Official D.A. Carson theology site (if exists)**
- Estimated words: 50,000
- Crawlable: Yes

**The Gospel Coalition (Carson contributor)**
- Estimated words: 150,000
- Crawlable: Yes

**Ligonier Ministries (R.C. Sproul ecosystem, Carson content)**
- Estimated words: 30,000
- Crawlable: Yes

### Academic Sources

**Google Scholar — Carson papers & citations**
- Estimated words: 200,000
- Note: Many papers have free PDF links or preprints

**ResearchGate — Carson published papers**
- Estimated words: 100,000
- Note: Authors often share PDF copies

**Trinity Evangelical Divinity School (Carson's institution)**
- Estimated words: 50,000
- Note: Faculty papers, archived resources

**9Marks Ministries (Mark Dever's network, Carson connection)**
- Estimated words: 30,000

### Podcast Interviews

**The Briefing by Al Mohler (Carson appearances)**
- Estimated words: 120,000

**TGC Podcast (Carson interviews)**
- Estimated words: 80,000

**Ask Pastor John (John Piper) — Carson episodes**
- Estimated words: 40,000

**Renewing Your Mind (Sproul's network, Carson content)**
- Estimated words: 160,000

### Video Content

**YouTube Carson sermons with transcripts**
- Estimated words: 500,000
- Note: Many videos have auto-generated or manual captions

**Desiring God (John Piper's ministry, Carson content)**
- Estimated words: 100,000

### Books Outside Logos

**Google Books, Amazon preview, publisher samples**
- Estimated words: 100,000
- Note: Many publishers allow 10-20% preview

## Total Estimated Words: 1,710,000

## Harvesting Workflow


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

