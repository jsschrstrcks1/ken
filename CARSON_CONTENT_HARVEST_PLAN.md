# D.A. Carson Content Harvest Plan

**Date:** 2026-05-30 14:47 EDT | **Status:** PLANNING | **Purpose:** Full Carson data extraction for LoRA training

---

## Overview

Ken owns substantial D.A. Carson resources in Logos.com (copy-paste restricted). Goal: Extract all available Carson writings for LoRA v1.0.0+ training.

**Constraint:** Logos has per-resource copy limits; need to work within restrictions.

---

## Content Sources to Harvest

### 1. Logos.com (Ken's Library)

**Known Resources:**
- ✅ D.A. Carson Sermon Library (full collection)
- ✅ The Gospel According to John (Carson commentary)
- ✅ Exegetical Fallacies
- ✅ Divine Sovereignty and Human Responsibility
- ✅ Christ and Culture Revisited
- [More to discover via Logos search]

**Action:** Systematically search Logos for all Carson content Ken owns; list with copy-limit status

**Extraction Method:** Respect copy-paste limits; extract in chunks if needed

### 2. D.A. Carson Official Blog/Website

**Source:** https://www.dcarsontheology.com/ (or official blog)

**Content Types:**
- Blog posts (all years)
- Articles
- Teaching notes
- Theological reflections

**Action:** Crawl/fetch all blog content (publicly available)

### 3. Published Books (Non-Logos)

**Known titles:**
- The Intolerance of Tolerance
- Basics for Believers
- Showing the Spirit
- Love in Hard Places
- Praying with Paul
- The God Who Is There (and The God Who Is Here)
- Counterfeit Gospels
- How Long, O Lord?
- Jesus' Sermon on the Mount and His Confrontation with the World
- [Others to identify]

**Action:** Identify which are digitally available; extract where possible

### 4. Academic Articles & Journal Papers

**Sources:**
- Trinity Journal (Carson is editor)
- Evangelical Theological Society publications
- Southern Baptist Journal of Theology
- Other peer-reviewed publications

**Action:** Identify which are publicly available; fetch/extract

### 5. Interview Transcripts

**Types:**
- Podcast interviews
- Video interviews
- Conference talks (transcribed)

**Action:** Locate and transcribe/extract

---

## Extraction Strategy

### Phase 1: Logos.com Inventory (Week 1)
1. Search Logos for all "Carson" materials
2. Document each resource:
   - Title
   - Type (sermon, book, commentary, etc.)
   - Copy-paste limit status
   - Approximate word count
3. Prioritize by richness for LoRA (commentaries > sermons > articles)

### Phase 2: Logos.com Extraction (Week 2–3)
1. Extract each resource respecting copy limits
2. Save as:
   - `.md` files (sermon transcripts, blog posts)
   - `.txt` files (article excerpts)
   - Structured JSON (metadata + content)
3. Document extraction date & source

### Phase 3: Web Harvest (Week 3–4)
1. Crawl official Carson sites/blogs
2. Extract all public writings
3. Save with source URL & date

### Phase 4: Academic & Interview (Week 4–5)
1. Locate papers (Google Scholar, ResearchGate, etc.)
2. Locate interview transcripts (podcast platforms, YouTube)
3. Extract & organize

### Phase 5: Consolidation (Week 5–6)
1. Combine all Carson sources
2. De-duplicate content
3. Create unified Carson corpus
4. Count total words/samples

---

## Storage Structure

```
/Volumes/1TB External/openclaw/workspace-main/
├─ carson-harvest/
│  ├─ logos-books/
│  │  ├─ exegetical-fallacies.md
│  │  ├─ gospel-john-commentary.md
│  │  ├─ sermon-library/
│  │  │  ├─ sermon-001.md
│  │  │  ├─ sermon-002.md
│  │  │  └─ ...
│  │  └─ [other Logos books]
│  │
│  ├─ blog-writings/
│  │  ├─ blog-post-2025-01.md
│  │  ├─ blog-post-2025-02.md
│  │  └─ ...
│  │
│  ├─ academic-papers/
│  │  ├─ paper-title-1.md
│  │  ├─ paper-title-2.md
│  │  └─ ...
│  │
│  ├─ interviews/
│  │  ├─ podcast-interview-2024.md
│  │  ├─ video-interview-2023.md
│  │  └─ ...
│  │
│  └─ CARSON_HARVEST_LOG.md (tracking sheet)
```

---

## Data Processing

Once extracted, each file should contain:

```yaml
---
source: "Logos.com | Blog | Academic | Interview"
title: "[Title]"
author: "D.A. Carson"
date: "[Publication or extraction date]"
url: "[Original source URL if available]"
word_count: "[Estimated word count]"
copy_limit_status: "[Restricted | Unrestricted | Partial]"
notes: "[Any special handling notes]"
---

[Content here]
```

---

## Known Challenges

1. **Logos Copy Limits:** Can't extract entire books at once; need to chunk
2. **Copyright:** Some materials may be restricted; only extract what's legally available
3. **Blog Archives:** Some older posts may be gone; Internet Archive may help
4. **Video Transcripts:** Manual transcription needed if not already available
5. **Academic Papers:** Access may be paywalled; use preprints when available

---

## Timeline

| Week | Phase | Deliverable |
|------|-------|-------------|
| Week 1 | Logos inventory | Complete list of Carson materials Ken owns |
| Week 2–3 | Logos extraction | All Logos content extracted & organized |
| Week 3–4 | Web harvest | Blog posts, articles, public writings extracted |
| Week 4–5 | Academic & interviews | Papers & transcripts collected |
| Week 5–6 | Consolidation | Unified Carson corpus ready for training |

---

## Success Criteria

- [ ] All Carson resources Ken owns in Logos extracted
- [ ] Official blog/website content harvested
- [ ] Academic papers identified & sourced
- [ ] Interview transcripts collected
- [ ] Content deduplicated & organized
- [ ] Total corpus: ~50,000–100,000+ words (target)
- [ ] Ready for LoRA Carson training

---

## Integration with LoRA Training

Once Carson corpus is ready:
1. Combine with existing Carson sermon data (6,000+ samples estimated)
2. Apply confessional layer architecture (1689, Abstract, BFM, Heidelberg, Westminster)
3. Check for paedobaptism tensions (Sproul-like scenario)
4. Train Carson LoRA v1.0.0
5. Release with Carson content fully represented

---

## Notes

- This is a COMPREHENSIVE harvest (not just Logos)
- Respect copyright & fair use
- Document every source for attribution
- Extract intelligently (don't waste on low-signal content)
- Goal: Rich Carson voice for LoRA training

---

_All of Carson's work. Everything available. Build the complete Carson model._

_Soli Deo Gloria._
