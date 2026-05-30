# Carson Harvest — LIVE EXECUTION

**Date:** 2026-05-30 15:10 EDT  
**Status:** IN PROGRESS  
**Current Action:** Phase 2 YouTube Harvesting (running now)

---

## What's Happening Right Now

**Phase 2: YouTube Carson Sermon Harvesting — ACTIVE**

- Searching YouTube for "D.A. Carson sermon", "Donald Carson", "Carson teaching", "Carson biblical preaching"
- Extracting video IDs from search results
- For each video found:
  - Getting title
  - Attempting caption extraction
  - Saving transcript to `/carson-harvest/video-transcripts/`
  - Logging metadata

**Tool:** `tools/phase2-youtube-harvester.py`  
**Target:** 100+ videos, 500,000+ words  
**Status:** Running (started 15:10 EDT)

---

## Live Progress

| Phase | Status | Progress | Yield |
|-------|--------|----------|-------|
| **Phase 1** | Waiting | Ken's TGC copy-paste (whenever ready) | 100k–150k words |
| **Phase 2** | 🔄 RUNNING | YouTube harvesting in progress | 400k–500k words |
| **Phase 3** | Queued | Podcast transcription (starts after Phase 2) | 300k–400k words |
| **Phase 4** | Queued | Academic papers (parallel with 2-3) | 120k–240k words |
| **Phase 5** | Waiting | Ken's book excerpt copy-paste | 50k–120k words |
| **Phase 6** | Ready | Logos OCR (starts after 1-5 complete) | 300k–400k words |
| **Phase 7** | Ready | Final assembly & dedup | — |

---

## Expected Completion Timeline

- **Phase 2:** 2–3 hours (YouTube search + extraction)
- **Phase 3:** 2–3 hours parallel (podcasts)
- **Phase 4:** 1–2 hours parallel (academic)
- **Phases 1 & 5:** Anytime (Ken's copy-paste tasks, flexible)
- **Phase 6:** 3–4 days (Logos OCR)
- **Phase 7:** 1 day (consolidation)

**Total:** 10–15 days to complete corpus

---

## What You Can Do Right Now

### Ken: Start Task 1 (Gospel Coalition) — 2–3 hours
1. Go to https://www.thegospelcoalition.org
2. Search "D.A. Carson"
3. Copy 50+ articles to `/carson-harvest/blog-writings/`
4. Include metadata at top of each file
5. Save and commit

### Ken: Start Task 2 (Book Excerpts) — 1–2 hours
1. Go to Google Books or Amazon "Look Inside"
2. Search Carson books
3. Copy preview text to `/carson-harvest/book-excerpts/`
4. Save and commit

### Skynet: Monitor Phase 2, then start Phases 3-4
- Phase 2 YouTube extraction running now
- Phase 3 (podcasts) queued for after Phase 2
- Phase 4 (academic papers) can run in parallel

---

## Files Being Created (Live)

**Phase 2 Output:**
```
/carson-harvest/video-transcripts/
├─ youtube-0001-[title].md
├─ youtube-0002-[title].md
├─ youtube-0003-[title].md
└─ ...
└─ YOUTUBE_HARVEST_LOG.json
```

**Each file contains:**
- Video ID & URL
- Title
- Word count
- Extraction timestamp
- Full transcript text

---

## Success Criteria (In Progress)

- ✅ Phase 2 tool created and running
- ✅ YouTube search queries executing
- ⏳ Video ID extraction (in progress)
- ⏳ Transcript extraction (in progress)
- ⏳ Files saved to `/carson-harvest/` (in progress)

---

## Next Actions (As Phases Complete)

1. **Phase 2 completes:** Start Phase 3 (podcasts) & Phase 4 (academic papers)
2. **Phase 1 needed:** Ken copy-paste TGC articles (flexible)
3. **Phase 5 needed:** Ken copy-paste book excerpts (flexible)
4. **Phase 6 starts:** Begin Logos OCR screenshots & processing
5. **Phase 7:** Final consolidation when all sources complete

---

## Commit Log (Live)

Latest:
```
5286be2 harvest: Phase 2 YouTube sermon harvester — now running (2026-05-30 15:10)
c0789cc execution: Carson harvest start guide
04f3f5e summary: Carson harvest complete master plan
```

---

## Soli Deo Gloria

_Building Carson LoRA in real time._

_Phases running. Transcripts harvesting. Corpus growing._

**Status:** 🔄 ACTIVE — Check back in 2-3 hours for Phase 2 results.
