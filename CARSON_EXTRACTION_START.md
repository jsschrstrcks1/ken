# Carson Logos Extraction — Harvest Started

**Date:** 2026-05-30 14:50 EDT | **Status:** FRAMEWORK READY

---

## What's Been Set Up

✅ **Carson harvest directory structure created:**
- `/carson-harvest/sermons/` — For sermon transcripts
- `/carson-harvest/logos-books/` — For book chapters
- `/carson-harvest/blog-writings/` — For blog posts (future)
- `/carson-harvest/academic-papers/` — For papers (future)
- `/carson-harvest/interviews/` — For interview transcripts (future)

✅ **Extraction guides created:**
- `LOGOS_INVENTORY.md` — Full list of Carson resources Ken owns (6 major works, 530k+ words)
- `EXTRACTION_GUIDE.md` — Step-by-step how-to for each resource
- `EXTRACTION_LOG.json` — Tracking file for progress

✅ **Automation script created:**
- `tools/carson-logos-extractor.py` — Framework for organization & tracking

---

## The 6 Logos Resources to Extract

| Resource | Type | Estimated Words | Status |
|----------|------|-----------------|--------|
| **Carson Sermon Library** | Sermons | Unknown (priority) | Ready |
| **Gospel of John Commentary** | Commentary | 150,000 | Ready |
| **Exegetical Fallacies** | Book | 40,000 | Ready |
| **Divine Sovereignty & Human Responsibility** | Book | 80,000 | Ready |
| **Christ and Culture Revisited** | Book | 60,000 | Ready |
| **The Gagging of God** | Book | 200,000 | Ready |
| **TOTAL** | — | **530,000+** | — |

---

## How to Extract (Process Overview)

1. **Go to app.logos.com** (Ken is already logged in)
2. **Use the EXTRACTION_GUIDE.md** for step-by-step instructions
3. **Copy each resource in chunks** (Logos has per-copy limits)
4. **Save to `/carson-harvest/` with proper naming:**
   - Sermons: `/carson-harvest/sermons/sermon-XXXX.md`
   - Books: `/carson-harvest/logos-books/gospel-john-Ch01.md` (etc.)
5. **Include front matter** in each file:
   ```yaml
   ---
   source: "Logos.com"
   resource_title: "[Title]"
   author: "D.A. Carson"
   type: "[sermon|commentary|book]"
   extraction_date: "2026-05-30"
   logos_copy_limit: "restricted"
   ---
   ```
6. **Commit progress regularly:**
   ```bash
   git commit -m "harvest: Carson [Resource] — X sermons/chapters extracted"
   ```

---

## Estimated Effort

- **Total extraction time:** 50–70 hours
- **Format:** Batched sessions (10–15 sermons/chapter per session = 1–2 hours)
- **Expected timeline:** 25–35 extraction sessions over 2–4 weeks
- **Yield:** 530,000+ words of Carson content for LoRA training

---

## After Extraction Complete

1. **Consolidate:** Merge all files into unified Carson corpus
2. **Count:** `find /carson-harvest -name "*.md" | xargs wc -w`
3. **Deduplicate:** Check for overlaps across resources
4. **Prepare for training:** Add to Carson LoRA training pipeline
5. **Release:** Carson LoRA v1.0.0 with full Logos content

---

## Files Committed

- ✅ `tools/carson-logos-extractor.py` — Framework script
- ✅ `carson-harvest/LOGOS_INVENTORY.md` — Resource list
- ✅ `carson-harvest/EXTRACTION_GUIDE.md` — Step-by-step instructions
- ✅ `carson-harvest/EXTRACTION_LOG.json` — Progress tracker

---

## Next Action

**Ken:** Follow the `EXTRACTION_GUIDE.md` in `/carson-harvest/` and begin extracting from Logos systematically.

**Skynet:** Monitor progress, consolidate files, prepare for LoRA training once extraction is 50%+ complete.

---

_530,000+ words of D.A. Carson content. Systematic extraction. Ready to build Carson LoRA with everything he's written._

_Soli Deo Gloria._
