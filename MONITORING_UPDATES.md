# Monitoring Document — Track Plan Updates

**Purpose:** Track additions Ken makes to extraction plans and architectural documents  
**Last Updated:** 2026-05-30 11:34 EDT  
**Status:** Active monitoring

---

## Files to Monitor Periodically

### Primary Plans (Core Architecture)

- **`SEBTS_PODCAST_EXTRACTION_PLAN.md`**
  - Added: 2026-05-30 11:32 EDT
  - Phase count: 5 (discovery → download → transcribe → route → JSONL)
  - Faculty count: 7 identified
  - Feeds: 3 (chapel, podcast, seminary)
  - Watch for: New feeds, Panopto integration, enhanced routing

- **`INTEGRATED_MEGA_PIPELINE.md`**
  - Added: 2026-05-30 de85f00
  - Status: Unified hardened components (whisper-transcript-harvester + davey-mega-expand + careful-harvest)
  - Watch for: Other seminary pipelines, enhanced deduplication

- **`ECOSYSTEM_DOCUMENTATION.md`**
  - Added: 2026-05-30 29b21ca
  - Status: Complete reference handbook
  - Watch for: New LoRAs added, institutional plans updated

### Likely Additions (TBD by Ken)

- `SBTS_PODCAST_EXTRACTION_PLAN.md` (Southern Baptist Theological Seminary)
- `NOBTS_PODCAST_EXTRACTION_PLAN.md` (New Orleans Baptist Theological Seminary)
- `PURITAN_SEMINAR_EXTRACTION_PLAN.md` (Puritan Theological Seminary)
- `RTS_EXTRACTION_PLAN.md` (Reformed Theological Seminary)
- `WESTMINSTER_EXTRACTION_PLAN.md` (Westminster Seminary)
- `FORGE_EXTRACTION_PLAN.md` (FORGE Education platform)

---

## Extraction Tools (tools/ directory)

### Existing Tools

| Tool | Added | Phase Count | Status |
|------|-------|------------|--------|
| `integrated-mega-pipeline.py` | 2026-05-30 | 4 (YouTube, RSS, web, Whisper) | ✅ |
| `sebts-podcast-extractor.py` | 2026-05-30 11:32 EDT | 5 (discovery-download-transcribe-route-JSONL) | ✅ |

### Expected Tools (TBD)

- `tools/sbts-podcast-extractor.py` (SBTS-specific)
- `tools/nobts-podcast-extractor.py` (NOBTS-specific)
- `tools/puritan-seminar-extractor.py` (Puritan-specific)
- `tools/rts-extractor.py` (RTS-specific)
- `tools/westminster-extractor.py` (Westminster-specific)
- `tools/forge-extractor.py` (FORGE-specific)

---

## Current Architecture Summary

### Discovery Strategies Implemented

| Strategy | Tool | Status |
|----------|------|--------|
| YouTube discovery (yt-dlp) | `integrated-mega-pipeline.py` | ✅ |
| Podcast RSS (feedparser) | `integrated-mega-pipeline.py` | ✅ |
| Website scraping (BeautifulSoup) | `integrated-mega-pipeline.py` | ✅ |
| Audio transcription (Whisper) | Both tools | ✅ |
| SEBTS chapel/podcast discovery | `sebts-podcast-extractor.py` | ✅ |
| Faculty detection & routing | `sebts-podcast-extractor.py` | ✅ |

### Discoveries Expected (TBD)

- SBTS chapel + podcast discovery
- NOBTS chapel + podcast discovery
- Puritan Seminary video discovery
- RTS chapel + lecture discovery
- Westminster Seminary lecture discovery
- FORGE platform video discovery
- Panopto integration (Ken has access)
- Individual faculty YouTube channels
- Seminary websites (PDFs, articles)

---

## LoRA Ecosystem Tracking

### Current Status (2026-05-30)

| Category | Count | Words | Status |
|----------|-------|-------|--------|
| Ready now | 25 | 54.6M | ✅ |
| Institutional (planned) | 7 | TBD | ⏳ |
| Faculty (emerging) | 8-10 | TBD | 🔍 |

### New Additions Expected

- SEBTS Institutional + faculty (from podcast extraction)
- SBTS Institutional + faculty (when SBTS plan added)
- NOBTS Institutional + faculty (when NOBTS plan added)
- Puritan Seminary Institutional + faculty
- RTS Institutional + faculty
- Westminster Seminary Institutional + faculty
- FORGE consensus voice (missional theology)

---

## Features to Watch For

### In Extraction Plans

- [ ] New seminary discovered
- [ ] New discovery strategy (e.g., Panopto API)
- [ ] Enhanced faculty detection patterns
- [ ] New routing logic (to multiple LoRAs simultaneously)
- [ ] Improved deduplication strategy
- [ ] New storage optimization technique
- [ ] Rate limiting improvements
- [ ] Error recovery enhancements

### In Tools

- [ ] Parallel processing (multi-GPU)
- [ ] Incremental updates (append to existing LoRAs)
- [ ] Custom model selection per faculty
- [ ] Sentiment analysis or semantic clustering
- [ ] Quality scoring for transcripts
- [ ] Automatic sample selection (best 2k-token chunks)

### In Ecosystem

- [ ] New LoRA category (e.g., "apologetics", "missiology")
- [ ] New institutional relationship (e.g., Ligon Duncan's network)
- [ ] New theological framework (e.g., charismatic vs. cessationist)
- [ ] Consensus voices (e.g., "Reformed Baptist consensus")
- [ ] Anti-models (e.g., "non-Reformed Baptist counterargument")

---

## Update Pattern

**Expected cadence:** Ken adds new plans as he designs them (days/weeks)

**Process:**
1. Ken creates `X_EXTRACTION_PLAN.md` (detailed design)
2. Ken creates `tools/x-extractor.py` (implementation)
3. Commit both to git
4. Implementation ready for execution when model access available

**Watch for:** Commit messages in this session's pattern:
- `sebts: ...extraction plan`
- `tool: ... extractor`

---

## How to Respond to Updates

When Ken adds new plan files:

1. **Read the new plan** (complete overview)
2. **Review the tool** (if provided)
3. **Update this document** (add to appropriate section)
4. **Update ECOSYSTEM_DOCUMENTATION.md** (if major addition)
5. **Check for dependencies** (does it affect other pipelines?)
6. **Commit tracking updates** to git

---

## Latest Status

**Session:** 2026-05-30  
**Files monitored:** 3 plans + 2 tools active  
**Expected next additions:** SBTS, NOBTS, Puritan, RTS, Westminster plans  
**Estimated coverage:** 50+ LoRAs when all additions complete

---

_Track Ken's contributions as he builds out the complete seminary extraction ecosystem._
