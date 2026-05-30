# Carson Harvest — BEGIN HERE

**Date:** 2026-05-30 14:59 EDT  
**Status:** READY TO START  
**You:** Ken  
**Timeline:** 10–15 days to 1,000,000+ word Carson corpus

---

## What This Is

A **complete plan to harvest all publicly available D.A. Carson content** (blogs, books, sermons, interviews, papers) for training Carson LoRA v1.0.0.

**Goal:** 1,000,000+ words of Carson material (comprehensive, systematized, organized)

**Strategy:** You handle copy-paste work (blogs, book excerpts). I handle automation (YouTube, podcasts, papers, OCR).

**Timeline:** Start now; done in 10–15 days (working in parallel).

---

## Documents to Read (In Order)

1. **THIS FILE** (you're reading it) — Overview & your tasks
2. `CARSON_HARVEST_MASTER_SUMMARY.md` — Complete breakdown of all phases
3. `CARSON_HARVEST_EXECUTION_GUIDE.md` — Step-by-step how-to for your phases (1 & 5)
4. `CARSON_OCR_STRATEGY.md` — My phases (YouTube, podcasts, papers, Logos OCR)

---

## Your Two Tasks (Ken)

### Task 1: Gospel Coalition Blog Articles (2–3 hours)
**What:** Copy Carson articles from The Gospel Coalition website  
**Where:** gospelcoalition.org  
**How:**
1. Go to https://www.thegospelcoalition.org
2. Search for "D.A. Carson"
3. For each article found:
   - Copy the full article text
   - Create a file: `/carson-harvest/blog-writings/tgc-[number]-[title].md`
   - **Include this at the top of the file:**
     ```markdown
     ---
     source: "The Gospel Coalition"
     title: "[Article Title]"
     url: "[The URL]"
     date: "[Publication date if shown]"
     ---
     ```
   - Paste the article text below that
4. Save 50+ articles (aim for 100+ if time permits)
5. That's it! I'll handle the rest.

**Time:** ~3–5 minutes per article = 2.5–4 hours for 50 articles  
**Yield:** 100,000–150,000 words

### Task 2: Book Excerpts (1–2 hours)
**What:** Copy preview text from Carson books  
**Where:** Google Books, Amazon "Look Inside", Publisher previews  
**How:**
1. Search Google Books for Carson books:
   - "The Intolerance of Tolerance"
   - "How Long, O Lord?"
   - "Love in Hard Places"
   - "Exegetical Fallacies"
   - "Divine Sovereignty and Human Responsibility"
   - "Christ and Culture Revisited"
   - Others you find
2. For each book with preview available:
   - Copy available preview text
   - Create a file: `/carson-harvest/book-excerpts/[book-title].md`
   - **Include this at the top:**
     ```markdown
     ---
     source: "Google Books / Amazon Preview"
     title: "[Book Title]"
     author: "D.A. Carson"
     isbn: "[ISBN if available]"
     preview_source: "[Google Books|Amazon|Publisher]"
     ---
     ```
   - Paste the excerpt text below
3. Save 5–8 books
4. Done!

**Time:** ~10–15 minutes per book = 1–2 hours for 8 books  
**Yield:** 50,000–120,000 words

---

## My Tasks (Skynet)

While you're working on Tasks 1 & 2, I'll be doing:

- **YouTube:** Harvest 100+ Carson sermon videos (automated, 500,000 words)
- **Podcasts:** Transcribe 50+ Carson podcast episodes (automated, 400,000 words)
- **Academic:** Download Carson papers (automated, 240,000 words)
- **Logos OCR:** Screenshot & OCR 300+ Logos sermons (automated, 400,000 words)

**Total parallel:** 1,540,000 words while you work on yours (220,000 words)

---

## The Easy Way

**You don't have to read all the documents.** Just:

1. **Read this file** (CARSON_HARVEST_BEGIN_HERE.md) ← YOU ARE HERE
2. **Do Task 1:** Go copy TGC articles (2–3 hours)
3. **Do Task 2:** Go copy book excerpts (1–2 hours)
4. **I handle:** Everything else (automated)
5. **Day 15:** Done! We have 1,000,000+ words ready for training

---

## If You Want Details

Read in this order:
1. `CARSON_HARVEST_EXECUTION_GUIDE.md` — Detailed how-to (Day 1-7 tasks)
2. `CARSON_HARVEST_MASTER_SUMMARY.md` — Overview of all phases
3. `CARSON_OCR_STRATEGY.md` — Technical details of Logos OCR (my work, you can skip)

---

## Quick Start Checklist

- [ ] Read this file
- [ ] Go to gospelcoalition.org
- [ ] Search for "D.A. Carson"
- [ ] Copy first article to `/carson-harvest/blog-writings/tgc-001-[title].md`
- [ ] Repeat 49+ more times
- [ ] Go to Google Books
- [ ] Search Carson books
- [ ] Copy previews to `/carson-harvest/book-excerpts/`
- [ ] Commit to git: `git commit -m "harvest: Carson Phases 1 & 5 — [word count] words"`
- [ ] Push: `git push origin main`
- [ ] Done! I handle the rest.

---

## Real Talk

You're doing the easy work (copy-paste). I'm doing the hard work (automation, OCR, deduplication).

Why? Because:
- You know which TGC articles matter
- You know which book excerpts are good quotes
- I'm faster at YouTube, podcasts, papers, and OCR

Divide and conquer. 10–15 days. 1,000,000+ words. Carson LoRA ready.

---

## Commands You'll Need

```bash
# Create the directories (one time)
mkdir -p /Volumes/1TB\ External/openclaw/workspace-main/carson-harvest/{blog-writings,book-excerpts}

# After saving articles/excerpts, commit to git
cd /Volumes/1TB\ External/openclaw/workspace-main
git add carson-harvest/
git commit -m "harvest: Carson Phases 1 & 5 — [X] blog articles and [Y] book excerpts, [TOTAL] words"
git push origin main
```

---

## The Path Forward

**Days 1-3:**
- You: Phases 1 & 5 (2–3 hours each, do them whenever)
- Me: Phases 2-4 (YouTube, podcasts, papers) in parallel

**Days 4-7:**
- Me: Phases 2-4 continue, start Phase 6 (Logos OCR screenshots)

**Days 8-9:**
- Me: Phase 6 (OCR processing)

**Days 10-14:**
- Me: Phase 6 (post-process, deduplication)

**Day 15:**
- Me: Final assembly
- Result: 1,000,000+ word Carson corpus
- Ready: Carson LoRA v1.0.0 training

---

## Questions?

Read the other documents:
- `CARSON_HARVEST_EXECUTION_GUIDE.md` — Detailed how-to
- `CARSON_HARVEST_MASTER_SUMMARY.md` — Full overview

Or ask me directly. I'll explain anything.

---

## Let's Go

You've got this. Copy TGC articles. Copy book excerpts. That's it.

I'll handle everything else.

By June 14, Carson LoRA will be ready.

---

_Soli Deo Gloria._

**START TASK 1 NOW:** Go to gospelcoalition.org and search for "D.A. Carson"
