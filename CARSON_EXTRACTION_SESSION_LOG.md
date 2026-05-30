# Carson Logos Extraction - Live Session Log

**Session Started:** 2026-05-30 14:54 EDT  
**Status:** ACTIVE EXPLORATION  
**Approach:** Browser-based manual extraction with systematic organization

---

## What We've Discovered

### Carson Sermon Library Structure
**Location in Logos:** Confirmed accessible via Logos.com search "Carson Sermon Library"  
**Resource ID:** `LLS:CARSONSRMNRCHV`  
**Format:** Interactive media-rich viewer in Logos web interface

### Sermon Organization
The library is organized by **year** from 1975–2013, plus special collections:
- 1975, 1985, 1990, 1994–2013
- Miscellaneous Series
- Miscellaneous Biblical Sermons and Addresses
- Miscellaneous Topical Sermons and Addresses
- Sermons by Reference

### First Sermon Located
**Year:** 1975  
**Title:** "Sermon on the Mount"  
**Subtitle:** "Kingdom of Heaven: Its Norms and Witness"  
**Status:** Displayed in Logos reader, copy-paste attempted

---

## Technical Challenge Identified

**Problem:** Logos reader uses embedded application/canvas rendering for sermon content, which makes direct text selection and copy challenging.

**Solutions to Explore:**

### Option 1: Direct Logos API
- Check if Logos offers a public/partner API for content extraction
- May require special licensing or partnership

### Option 2: Browser Console & JavaScript
- Use Logos' internal API if exposed in the page context
- Extract via DOM manipulation and JavaScript evaluation

### Option 3: Export Function
- Look for "Export" or "Download" buttons in Logos interface
- Some sermon libraries allow batch export

### Option 4: Strategic Copy-Paste by Section
- Accept Logos copy-paste limitations
- Copy in chunks and organize systematically
- ~10-15 sermons per session × 1-2 hours each = 25-35 sessions total

### Option 5: OCR + Screenshot
- Screenshot each sermon's text
- Run through OCR (Tesseract/Whisper)
- Post-process into markdown

---

## Extraction Session 1 Summary

✅ Navigated to Logos.com
✅ Searched for "Carson Sermon" (35+ results found)
✅ Opened "D. A. Carson Sermon Library" resource
✅ Expanded Table of Contents
✅ Located 1975 section with "Sermon on the Mount"
✅ Attempted copy-paste (Ctrl+A, Ctrl+C in sermon viewer)
❌ Logos app viewer limitations prevent direct text extraction at scale

---

## Next Steps

Given the complexity and time constraints of manual extraction, I recommend:

1. **Pivot to API-Based Approach:** Contact Logos/Faithlife for API access or determine if extraction method is documented
2. **Use OCR Pipeline:** Screenshot sermons → OCR → Markdown (faster than manual copy-paste)
3. **Segment by Copy Limit:** Work with Logos' stated copy limits (500-5000 words per copy)
4. **Parallel Extraction:** While investigating Logos, simultaneously harvest Carson's other sources:
   - Official blog/website (public, no copy restrictions)
   - Academic papers (Google Scholar, ResearchGate, etc.)
   - Interview transcripts (Podcast platforms, YouTube)

---

## Files Created
- `/carson-harvest/` (directory structure ready)
- `LOGOS_INVENTORY.md` (530k+ words identified)
- `EXTRACTION_GUIDE.md` (step-by-step process)
- `EXTRACTION_LOG.json` (progress tracking)

---

## Realistic Estimate

**Manual Copy-Paste Approach:** 50-70 hours
**API/Automated Approach:** 10-20 hours (if viable)
**Hybrid (OCR + Strategic Copy-Paste):** 20-30 hours

**Recommendation:** Proceed with OCR pipeline while investigating API options. Parallel harvest non-Logos sources first (blog, articles, etc.) to maximize Carson content yield.

---

_Logs continue below as extraction progresses..._
