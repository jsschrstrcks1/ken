# Logos.com Manual Extraction Guide

## Overview
Due to Logos copy-paste limits, extraction must be done in chunks.
This guide provides the process.

## Resources to Extract (Priority Order)

### 1. Carson Sermon Library (Highest Priority)
**Logos Location:** Search "D.A. Carson Sermon Library"
**Process:**
1. Open in Logos
2. Copy sermons in chunks (10–15 at a time)
3. Paste into individual .md files
4. Save as: `/carson-harvest/sermons/sermon-XXXX.md`

**Fields to capture:**
- Date preached
- Title
- Bible text
- Full sermon text
- Any notes/context

### 2. Gospel of John Commentary
**Logos Location:** Search "Gospel According to John Carson"
**Process:**
1. Open by book chapter
2. Copy chapter sections (Logos may limit per chapter)
3. Save as: `/carson-harvest/logos-books/gospel-john-Ch01.md` (etc.)

### 3. Exegetical Fallacies
**Logos Location:** Search "Exegetical Fallacies Carson"
**Process:**
1. Copy chapter by chapter
2. Save as: `/carson-harvest/logos-books/exegetical-fallacies-Ch01.md` (etc.)

### 4. Divine Sovereignty & Human Responsibility
**Similar process as above**

### 5. Christ and Culture Revisited
**Similar process as above**

### 6. The Gagging of God (Largest; ~200k words)
**Process:**
1. This is long; expect 15–20 sessions
2. Copy section by section
3. Save progressively

## File Naming Convention

```
/carson-harvest/
├─ sermons/
│  ├─ sermon-2024-001-john-516.md
│  ├─ sermon-2024-002-romans-3.md
│  └─ ...
│
├─ logos-books/
│  ├─ gospel-john-Ch01.md
│  ├─ gospel-john-Ch02.md
│  ├─ exegetical-fallacies-Ch01.md
│  ├─ divine-sovereignty-Ch01.md
│  ├─ christ-culture-Ch01.md
│  └─ gagging-god-Pt1-Ch01.md
│
└─ EXTRACTION_LOG.json
```

## Front Matter for Each File

Every extracted file should include:

```yaml
---
source: "Logos.com"
resource_title: "[Logos resource name]"
author: "D.A. Carson"
type: "[sermon|commentary|book]"
extraction_date: "2026-05-30"
logos_copy_limit: "restricted"
notes: "[Any special notes about extraction]"
---

[Content here]
```

## Tracking Progress

After each extraction session:
1. Record in `EXTRACTION_LOG.json`:
   ```json
   {
     "date": "2026-05-30",
     "resource": "Carson Sermon Library",
     "sermons_extracted": 15,
     "words_extracted": 12500,
     "status": "in_progress"
   }
   ```
2. Commit to git: `git commit -m "harvest: Carson [resource] — X sermons/chapters extracted"`
3. Update inventory

## Estimated Timeline

- **Carson Sermon Library:** 20 sessions × 1–2 hours = 20–40 hours
- **Gospel of John:** 21 chapters × 30 min = 10.5 hours
- **Exegetical Fallacies:** 8 chapters × 20 min = 2.7 hours
- **Divine Sovereignty:** 10 chapters × 30 min = 5 hours
- **Christ and Culture:** 6 chapters × 25 min = 2.5 hours
- **Gagging of God:** 40+ sections × 20 min = 13+ hours
- **Total:** 50–70 hours of focused extraction

## Tips for Efficient Extraction

1. **Batch similar work:** Do all sermon extraction together, then all books
2. **Use Logos' native export if available:** Check for "Export" option
3. **Screenshot + OCR fallback:** If copy fails, take screenshot + OCR
4. **Track word counts:** Use `wc -w` to verify extraction completeness
5. **Deduplication:** Check for overlaps across resources later

## When Complete

1. Consolidate all files into unified corpus
2. Count total words: `find /carson-harvest -name "*.md" | xargs wc -w`
3. Commit with: `git commit -m "harvest: Carson complete — [total] words extracted from Logos"`
4. Ready for LoRA training

---

**This is a long but systematic process. Break it into small sessions.**
