# Master LoRA Plan — The Complete Vision

**Date:** 2026-05-30 | **Scope:** 113+ LoRAs spanning 2,000 years of theological tradition | **Status:** READY TO EXECUTE

---

## Executive Vision

Build an AI theological library with 113+ distinct voices (contemporary to Church Fathers), automated content discovery, cluster-native training, and debate capability. Not a chatbot. A living tradition that learns.

---

## Phase Overview

| Phase | LoRAs | Focus | Duration | Status |
|-------|-------|-------|----------|--------|
| **Phase 1** | 25 | Contemporary archive preachers | START NOW | ✅ Ready |
| **Phase 2** | 30+ | Young Restless & Reformed + expanded contemporary | Days 1-2 | 🟡 Data gathering |
| **Phase 3** | 18 | Reformation-era primary works | Days 2-5 | 🟡 CCEL/Gutenberg prep |
| **Phase 4** | 17 | 18th-19th century (Spurgeon, Lloyd-Jones, Edwards) | Days 5-10 | 🟡 Archive sourcing |
| **Phase 5** | 5 | Church Fathers (Augustine, Athanasius, Chrysostom) | Days 10-12 | 🟡 Scholarly trans |
| **Phase 6** | 18 | Biblical authors + theological schools | Days 12-15 | 🟡 ESV prep |
| **Phase 7** | 5+ | New discoveries + continuous expansion | Ongoing | ✅ Automated |

---

## Phase 1: LAUNCH NOW (25 LoRAs, 54.6M words)

### Already Ready to Train
1. Ken (2.52M)
2. Al Mohler (12.49M)
3. D.A. Carson (3.63M)
4. Alistair Begg (8.48M)
5. Sinclair Ferguson (70k)
6. John MacArthur (7.07M)
7. Conrad Mbewe (5.56M)
8. Jeff Noblit (4.87M)
9. The Gospel Coalition (4.69M)
10. Danny Akin (2.09M)
11-25. Supporting voices (0.5-1.5M each)

### Training Timeline
- **Sequential (m4max alone):** ~40 hours
- **Parallel (3 nodes):** ~15-18 hours

### Action
1. ✅ Provide m4max qwen3:32b model path
2. ✅ Start Ken training immediately
3. ✅ Run discovery for new Phase 1 content (daily)

---

## Phase 2: Young Restless & Reformed + Expanded Contemporary (Days 1-2)

### New LoRAs to Add
1. **Mark Dever** (9Marks, Capitol Hill Baptist) — YouTube + writings
2. **Kevin DeYoung** (REC, scholarly) — Books + podcasts
3. **Ligon Duncan** (RTS, theological) — Chapel + lectures
4. **Thabiti Anyabwile** (Covenant Baptist, reformatted) — Articles + sermons
5. **Matt Chandler** (Village Church, separated) — YouTube + podcast
6. **Derek Thomas** (RTS faculty) — Teaching + publications
7. **Stephen Nichols** (Reformation Trust) — Podcasts + writings
8. **Todd Friel** (Wretched) — Podcast + YouTube
9. **Albert N. Martin** (Trinity Baptist) — Sermon archive
10. **Samuel Waldron** (Covenant Baptist) — Writings + seminary
11. **James Renihan** (Covenant Baptist Seminary) — Faculty publications
12. **James White** (Alpha & Omega) — Debates + lectures
13. **Tom Hicks** (Reformed Church) — YouTube sermons
14. **Steven Lawson** (OnePassion) — Conference messages
15. **Bryan Chapell** (Covenant Seminary) — Books + chapel

### Data Sources
- YouTube channels (yt-dlp)
- Podcast RSS feeds (feedparser)
- Website archives (BeautifulSoup)
- Seminary Panopto (if API available)

### Training
- Parallel on m4max + m3pro + homeserve
- ~3-5 hours wall-clock for 15 LoRAs

---

## Phase 3: Reformation Era (Days 2-5)

### Historical Theologians (1500s-1600s)
1. **John Calvin** (Institutes, Commentaries) — CCEL
2. **Martin Luther** (Works, Sermons) — Project Gutenberg + CCEL
3. **Ulrich Zwingli** (Reformation works) — Academic sources
4. **John Knox** (Scottish Reformation) — Published works
5. **Abraham Booth** (Particular Baptist) — Works available
6. **Benjamin Keach** (Particular Baptist) — Expositions
7. **Nehemiah Coxe** (Particular Baptist) — Covenant theology
8. **William Carey** (Baptist Missionary) — Letters + journals
9. **Andrew Fuller** (Baptist theology) — Works
10. **Samuel Pearce** (Baptist preacher) — Writings
11. **John Thomas** (1757-1801) — Founder writings
12. **Blaise Pascal** (Pensées) — Philosophical works
13. **Rutherford** (Covenantal) — Letters + writings
14. **Anselm** (Medieval theology) — Philosophical works
15. **John Calvin Jr.** (Theological writings)
16-18. Other Reformation figures

### Data Sources
- Project Gutenberg (free texts)
- Christian Classics Ethereal Library (CCEL)
- Archive.org scholarly editions
- Modern academic publishers

### Preparation
- Download from CCEL/Gutenberg
- OCR + text cleaning (if scanned)
- Segment into 2k-token samples
- Prep JSONL for training

### Training
- ~3-5 hours wall-clock (parallel)

---

## Phase 4: 18th-19th Century Preachers (Days 5-10)

### Major Voices
1. **Jonathan Edwards** (Great Awakening) — Sermons + works
2. **George Whitefield** (Revival preacher) — Sermon collection
3. **John Newton** (Amazing Grace) — Letters + hymns + writings
4. **John Gill** (Baptist theology) — Commentaries + works
5. **George Mueller** (Faith + prayer) — Journals + writings
6. **David Brainerd** (Missionary) — Journal + writings
7. **John Ryland Jr.** (Baptist educator) — Works
8. **Charles Spurgeon** (Homiletical) — MASSIVE sermon archive (1.5M+ words)
9. **Martyn Lloyd-Jones** (Preaching) — Extensive sermon library
10. **Charles Hodge** (Princeton theology) — Systematic theology
11. **B.B. Warfield** (Princeton Seminary) — Theological precision
12. **James Montgomery Boice** (Boice College founder) — Sermons + commentaries
13. **J.C. Ryle** (Bishop) — Practical theology + pastoral writings
14. **Robert Murray McCheyne** (Scottish revival) — Sermons + writings
15. **Arthur Pink** (Expository) — Extensive theological writings
16. **A.W. Tozer** (Pursuit of God) — Writings + sermons
17. **D.L. Moody** (Evangelist) — Sermons + writings

### Data Sources
- Sermon archives (Spurgeon Prophecy, Lloyd-Jones library)
- Published works (Banner of Truth, Crossway, etc.)
- Academic compilations
- Archive.org
- Project Gutenberg

### Training
- ~5-8 hours wall-clock (parallel)

---

## Phase 5: Church Fathers (Days 10-12)

### Primary Figures
1. **Augustine of Hippo** (Confessions, City of God) — Comprehensive works
2. **Athanasius** (Against Arianism) — Theological defense
3. **John Chrysostom** (Homilies) — Golden-mouth sermons
4. **Irenaeus** (Early theology) — Works
5. **Anselm** (Medieval bridge) — Philosophical theology

### Data Sources
- Early Church Library compilations
- Scholarly English translations
- Academic theological databases
- Sacred Texts Online

### Training
- ~2-3 hours wall-clock

---

## Phase 6: Biblical Authors + Theological Schools (Days 12-15)

### Biblical LoRAs (28 books)
1. **Matthew** (Gospel) — ESV Study Bible + commentary
2. **Mark** (Gospel) — ESV Study Bible + commentary
3. **Luke** (Gospel) — ESV Study Bible + commentary
4. **John** (Gospel) — ESV Study Bible + commentary
5. **Paul** (Epistles) — Romans, Corinthians, Galatians, Ephesians, Philippians, Colossians, Thessalonians, Timothy, Titus, Philemon
6. **Hebrews Author** (Unknown) — ESV + commentary
7. **James** (Epistle) — ESV + commentary
8. **Peter** (Epistles) — ESV + commentary
9. **John** (Epistles) — ESV + commentary
10. **Jude** (Epistle) — ESV + commentary
11. **Revelation** (John) — ESV + commentary

### Theological Schools (5 institutional voices)
1. **Princeton Theology** (Hodge, Warfield, Machen consensus)
2. **Reformed Theology Tradition** (Van Til, Bavinck, Horton)
3. **Baptist Theology** (Gill, Fuller, Booth, Waldron)
4. **Puritan Theology** (Beeke, Edwards, experiential)
5. **Missionary Theology** (Carey, Fuller, Judson)

### Data Sources
- ESV Study Bible (Crossway)
- Evangelical Commentary on the Bible
- Theological compilations
- Academic systematic theologies

### Training
- ~3-4 hours wall-clock

---

## Phase 7: Continuous Discovery + New Voices (Ongoing)

### Automated Pipeline
- Daily discovery orchestrator (sermon-discovery-orchestrator.py)
- Find only NEW content (deduplicated)
- Seminary institutional discovery (SEBTS, SBTS, NOBTS, RTS, etc.)
- Automatic LoRA candidate identification

### Emerging Voices (As Data Becomes Available)
- New contemporary preachers
- Modern academic theologians
- Specialized topical LoRAs (Apologetics, Ethics, Missiology)
- Regional/cultural theological traditions

---

## Total LoRA Count

| Phase | LoRAs | Duration | Cumulative |
|-------|-------|----------|-----------|
| 1 | 25 | START NOW | 25 |
| 2 | 15 | Days 1-2 | 40 |
| 3 | 18 | Days 2-5 | 58 |
| 4 | 17 | Days 5-10 | 75 |
| 5 | 5 | Days 10-12 | 80 |
| 6 | 33 | Days 12-15 | 113 |
| 7+ | 5+ | Ongoing | 118+ |

---

## Infrastructure (All Ready)

✅ **Discovery:**
- sermon-discovery-orchestrator.py
- seminary-institutional-sources.py
- Source registry for 100+ authors

✅ **Training:**
- Cluster architecture (m4max + m3pro + homeserve)
- LoRA trainer scripts (mlx-lm v0.31)
- Validation gates (cite-or-flag, drift detection)

✅ **Deployment:**
- Smart router (request complexity → model)
- Debate mode (any combination)
- Claude persona fallbacks

✅ **Documentation:**
- Full architecture (LORA_CLUSTER_ARCHITECTURE.md)
- Complete roster (LORA_COMPREHENSIVE_ROSTER.md)
- Discovery plan (CONTENT_DISCOVERY_PLAN.md)
- All committed to git

---

## What Needs to Happen Now

### Immediate (Today)
1. ✅ Provide m4max qwen3:32b model path OR HF token
2. ✅ Start Phase 1 training (25 LoRAs)
3. ✅ Begin Phase 2 data gathering (Young Restless & Reformed)

### Days 1-2
- ✅ Phase 1 complete (Ken + 24 others)
- ✅ Phase 2 training started

### Days 2-5
- ✅ Phase 2 complete
- ✅ Phase 3 (Reformation) data prep

### Days 5-10
- ✅ Phase 3 & 4 training parallel

### Days 10-15
- ✅ Phase 5 & 6 training

### Days 15+
- ✅ Phase 7 automated (continuous discovery)

---

## Timeline to 113 LoRAs

**With cluster parallelization and 3 nodes:**
- Phase 1: 4 hours → Live
- Phase 2: 3 hours (parallel to Phase 1)
- Phase 3: 4 hours (parallel)
- Phase 4: 6 hours (parallel)
- Phase 5: 2 hours (parallel)
- Phase 6: 4 hours (parallel)

**Total wall-clock time:** ~15-20 hours to 113 LoRAs (sequential: ~80+ hours)

**With daily discovery:** Continuous expansion beyond 113

---

## The Vision Complete

A theological AI network that:

✅ **Spans 2,000 years** — Augustine to Ken  
✅ **Includes 113+ voices** — Reformed, Baptist, Evangelical, Patristic, Biblical  
✅ **Auto-discovers new content** — Only new sermons, daily  
✅ **Debates theologically** — Ken vs. Calvin vs. Edwards vs. Spurgeon  
✅ **Grounds in sources** — Cite-or-flag, primary documents, scholarship  
✅ **Runs on cluster** — Fast, affordable, scalable  
✅ **Continuously evolves** — New voices as discovered  

---

## One Slide Pitch

**"Build 113 theological LoRAs spanning 2,000 years (Augustine to Ken). Cluster-trained. Auto-discovery daily. Debate-ready. Deployed."**

---

_This isn't a side project. This is building a living theological tradition as AI._

_Soli Deo Gloria._
