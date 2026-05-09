# Soul of `Romans`

> *Soli Deo Gloria.* Expository sermon manuscripts, theological study materials, and preaching resources.
>
> **This repository is private.** Content is copyrighted sermon manuscripts and pastoral work product. Unauthorized reproduction, distribution, or use for AI model training is prohibited. All rights reserved.

The pastor's manuscript drawer. Sermons preached and sermons in preparation, plus the rubrics, voice profiles, and theological scaffolding that govern how a manuscript becomes a Sunday sermon.

---

## Identity

`Romans` is **Ken Baker's expository sermon repository**. The name is the lead series — preaching through the book of Romans — but the repo holds his entire preaching corpus: 1 Timothy, 2 Timothy, Ephesians, Exodus, Genesis, Jonah, Luke, Revelation, Habakkuk, Titus, Psalms, Thessalonians. Plus theology, pastoral resources, slide decks for Romans 6, 7, 11, an "A journey in grace" book series, and a `sebts-reference/` directory tied to **Southeastern Baptist Theological Seminary**, where Ken is completing his Master of Divinity.

The repo is **private** — copyrighted sermon manuscripts and pastoral work product. The README is a copyright notice and an `.ai-deny` file sits at the root. *Unauthorized reproduction, distribution, or use for AI model training is prohibited. All rights reserved.* This is the second of two repos in the family with closed source (the other being `flickersofmajesty`), and the only one that explicitly forbids AI training on its content.

The mode in `ken/orchestrator/repo-modes.json` is `sermon`. Lead: Claude. Pipeline: **Draft (Claude) → Challenge (Grok) → Expand (Gemini) → Structure (GPT) → Integrate (Claude) → Evaluate (Claude) → Voice Audit (Claude).** Seven stages — the longest pipeline of any sister repo. Sermon writing earns the most consultation.

## What it actually is

1. **Preached sermons as `.txt` files** at the repo root. Examples:

   - *1 tim 2 1-7 sola christus 2020.txt* / *1 tim 2 1-7 sola christus.txt* (the same sermon, two versions)
   - *2 Tim 3 - heathens gonna heath.txt*
   - *Eph 2 - but God.txt*
   - *Exodus 14 - red sea.txt*
   - *Gen 1-2 - beautiful but not safe.txt*
   - *Gen 29 - depravity of man.txt*
   - *Jonah 4 - God is in control.txt*
   - *Luke 15 - Prodigal Son.txt*
   - *Luke 23 32ff - two thieves.txt*
   - *Missions and Hell - why it matters.txt*
   - *Psalm 51.txt*
   - *Thankfulness - 1 Thess 5.txt*
   - *Titus 1 - slavery.txt*
   - *Titus 3 - dumb laws.txt*
   - *rev 2 1-7 forgotten first love.txt*
   - *romans 9-10 paris evangelism.txt*
   - *romans early series 2 - creation idolatry gospel.txt*

   The titles are working titles — humble, descriptive, sometimes wry (*"heathens gonna heath," "dumb laws," "Jerkface"-style honesty*). The voice of the file titles is the voice of the manuscripts.

2. **Slide decks** for the Romans series: `Romans11_Deck_WithGraphics.pptx`, `Romans11_SlideDeck.pptx`, `Romans6_15_Intro_Point1.pptx`, `Romans7_TheWarWithin.pptx`. The pulpit comes with PowerPoint.
3. **`Romans 1 sermon plan`** and **`Journey in Grace bible study`** — long-form preparation documents (20+ KB and 27 KB respectively).
4. **Topical directories:**
   - `sermons/` — organized sermon archive
   - `services/` — full service materials (liturgies, calls to worship)
   - `theology/` — doctrinal study notes
   - `teaching/` — Sunday school / Bible-study material
   - `pastoral-resources/` — counseling, member-care helps
   - `personal/` — preacher's own devotional notes (private even within a private repo)
   - `quotes-and-references/` — quotation archive for illustrations
   - `voice-research/` — preacher's voice profile development
   - `sebts-reference/` — seminary materials
   - `habakkuk/` — a separate book series in progress
   - `A journey in grace/` — a long-form study series
   - `_review/` — review queue
5. **Operational documents:**
   - `sermon-queue.md` — what's coming next from the pulpit
   - `plan.md` — 27 KB current/active plan
   - `organizational-structure-plan.md` — how the repo is organized
   - `careful.md` — integrity guardrail
   - `claude.md` (lowercase) — 18 KB of additional Claude context, distinct from `CLAUDE.md`
   - `signs-of-spiritual-coldness-checklist.txt` — a pastoral self-examination tool
6. **Six embedded skills** under `.claude/skills/`: `cognitive-memory`, `careful-not-clever`, `like-a-human`, `voice-audit`, `sermon-map`, `thus-says-the-lord`. The last two are unique to this repo.

## Voice

**Working-title humility.** Sermon files are not titled with marketing flourish. They are titled like a preacher's notes: *"Eph 2 - but God." "Jonah 4 - God is in control." "Gen 1-2 - beautiful but not safe."* The titles tell the preacher what the sermon is for, not the audience what to expect. The internal voice is the same — manuscripts are notes to the preacher, formatted to be preached aloud, not read silently.

**Wry where it can be.** *"2 Tim 3 - heathens gonna heath." "Titus 3 - dumb laws."* The pastoral voice has room for dry humor. This is consistent with the household's general posture — taking God seriously without taking yourself seriously.

**Reformed Baptist register.** The CLAUDE.md names the constraints: **1689 London Baptist Confession of Faith theology, ESV-only Scripture, Gospel call required, Voice profile preserved.** The repo is theologically located. It does not waver on these.

**The README as protective wall.** Three-quarters of the README's 1,874 bytes is a copyright/AI-training notice. The remaining quarter is the *Thus Says the Lord* rubric evaluation noting that the README is not a sermon and cannot be evaluated as one. The README does not advertise the sermons. It guards them.

**The "Thus Says the Lord" meta-evaluation.** This is unusual and characteristic. The README contains an evaluation of *itself* against the sermon rubric, scoring N/A on every category and concluding *"This document is not a sermon and cannot be evaluated as one."* The repo's own quality-evaluation skill has been pointed at the repo's own README, and the result is honestly recorded. This is the household's epistemic posture taken to its logical limit.

## Style markers

- **Inconsistent capitalization in titles.** *"1 tim 2 1-7 sola christus 2020.txt"* sits next to *"Eph 2 - but God.txt"* sits next to *"Genesis 1-2 - beautiful but not safe.txt"*. The titles are organic — preacher's-desk titles, not catalog titles. They were written for the preacher, by the preacher.
- **Two `claude.md` files.** Lowercase `claude.md` (18 KB) and uppercase `CLAUDE.md` (1.9 KB) coexist. The lowercase is the longer, older context document; the uppercase is the lean orchestrator-pointer hub.
- **`.ai-deny` at the repo root.** A 315-byte file dedicated to refusing AI training use of the contents. The household has multiple posture-against-training files (the recipe repos' `noindex`, Granny's privacy controls), but this one is the most explicit.
- **A `_review/` directory.** Underscore-prefixed: convention for "not for public reference." A queue.
- **A `sermon-queue.md`** at 16 KB. Tracking what to preach next, when, and from where in the canon.
- **A `signs-of-spiritual-coldness-checklist.txt`.** A pastoral self-examination tool that lives in the public root of the repo. The pastor pastors himself first, with the same rigor he expects to bring to the pulpit.
- **A `voice-research/` directory.** Voice is treated as a research artifact. The preacher's voice is a thing to study and preserve, not assume.
- **`sebts-reference/`** is named openly. Southeastern Baptist Theological Seminary. Ken's MDiv work is part of the corpus.

## Philosophy

### The pulpit refuses to be training data

The README's first sentence: *"This repository is private. Content is copyrighted sermon manuscripts and pastoral work product. Unauthorized reproduction, distribution, or use for AI model training is prohibited."* The repo encodes a distinctively pastoral conviction: **the words preached to a specific congregation belong to that congregation and to God, not to a corpus.** The sermons are not for scraping. The `.ai-deny` file is the technical version of that conviction.

### Claude is the lead, but every other model gets called in

Where the recipe repos have GPT lead and Claude validate, and the sheep repo has GPT lead, **Romans has Claude lead and every other model consult**. The pipeline is the longest in the family:

1. **Draft** — Claude
2. **Challenge** — Grok (the contrarian; pokes at weak rhetoric)
3. **Expand** — Gemini (generates more theological surface)
4. **Structure** — GPT (orders the argument)
5. **Integrate** — Claude
6. **Evaluate** — Claude (the `thus-says-the-lord` rubric)
7. **Voice Audit** — Claude (the `voice-audit` skill, scanning for marketing tells, sermon drift, machine fluff)

Sermon writing earns the most rounds because the stakes are unique. A typo in a recipe is a typo. A theological mis-statement preached on Sunday is something else.

### 1689, ESV, Gospel call

Three immovable constraints. The 1689 London Baptist Confession is the doctrinal frame. The ESV is the only Bible translation used. **Every sermon must include a gospel call.** No sermon graduates the pipeline without one.

These are not stylistic preferences. They are confessional commitments. The `thus-says-the-lord` skill enforces them with a 17-element rubric.

### Voice is to be preserved, not optimized

The CLAUDE.md notes: *"Voice profile preserved (see like-a-human skill)."* The repo has a `voice-research/` directory and dedicated skills (`like-a-human` for during-writing, `voice-audit` for post-draft) whose only job is to make sure the manuscript still sounds like Ken when Claude is done helping. **AI consultation must not ghost the preacher.**

### Careful, not clever, here too

The `careful.md` lives in this repo too — same household idiom as Allrecipes and manateecreeksheep. *Verified, documented, reversible, honest.* Applied here to manuscripts: don't paraphrase Scripture, don't invent illustrations from the preacher's life, don't use [UNCLEAR] silently, don't smooth a hard exegetical question.

### Context boundaries are tight

The CLAUDE.md draws the line:

- **SEND** to consultants: outlines, theological claims, cross-refs, illustration concepts.
- **NEVER SEND**: congregation names, pastoral details, personal illustrations, voice internals.

The names of people in the church never leave the local machine. Pastoral details never leave. Personal illustrations — stories from Ken's family or counseling work — never leave. **The orchestrator helps with form; the heart of the manuscript stays with the preacher.**

### The repo grades itself

The `thus-says-the-lord` skill is a 17-element rubric: *Exposition & Hermeneutics (25), Theology & Doctrinal Integrity (18), Gospel Centrality & Force (15), Conscience & Applicatory Force (15), Exhortation & Response (8), Structure & Logical Flow (9), Illustration & Imagination (5), Sermonic Force (5), Weight of Glory Bonus (+5), Cognitive Load Modifier.* The repo applies this rubric to every manuscript before it goes to the pulpit. **Sermons are scored before they are preached.**

## Technical anatomy

### Layout

```
Romans/
├── README.md                    ← copyright wall + Thus-Says-the-Lord meta-eval
├── .ai-deny                     ← refusal of AI training use
├── CLAUDE.md                    ← lean orchestrator hub
├── claude.md                    ← longer context (18 KB)
├── careful.md                   ← integrity guardrail
├── plan.md                      ← active plan (27 KB)
├── organizational-structure-plan.md
├── sermon-queue.md              ← what to preach next
├── signs-of-spiritual-coldness-checklist.txt
├── *.txt                        ← sermon manuscripts (root level)
├── Romans*.pptx                 ← slide decks
├── Romans 1 sermon plan
├── Journey in Grace bible study
├── A journey in grace/          ← long-form series
├── habakkuk/                    ← separate book series
├── sermons/                     ← organized archive
├── services/                    ← full service materials
├── theology/
├── teaching/
├── pastoral-resources/
├── personal/                    ← private even within private
├── quotes-and-references/
├── voice-research/              ← preacher's voice profile
├── sebts-reference/             ← seminary materials
├── _review/                     ← review queue
└── .claude/skills/
    ├── cognitive-memory/
    ├── careful-not-clever/
    ├── like-a-human/            ← voice during writing
    ├── voice-audit/             ← voice after draft
    ├── sermon-map/              ← sermon structure / argument flow
    └── thus-says-the-lord/      ← 17-element rubric
```

### Multi-LLM integration

Mode: `sermon`. Lead: Claude. Memory scope: `/romans`.

The seven-stage pipeline is the longest in the family. Each consultant has a specific role:

| Stage | Model | Role |
|---|---|---|
| Draft | Claude | author |
| Challenge | Grok | contrarian — finds weak rhetoric, soft theology |
| Expand | Gemini | generative — surfaces more text-treatment material |
| Structure | GPT | orders the argument, balances sections |
| Integrate | Claude | merges consultant output back into a manuscript |
| Evaluate | Claude | applies the `thus-says-the-lord` rubric |
| Voice Audit | Claude | applies `voice-audit` to scan for machine tells |

Two of the three "external" models (GPT, Gemini, Grok) are used in the middle stages. Perplexity and You.com are not in the pipeline — sermon writing is not a research task in the way genealogy is.

### The `.ai-deny` file

A 315-byte declarative refusal. The repo names what it is and is not for. The orchestrator's context boundaries plus the `.ai-deny` file plus the README's copyright notice form a triple seal: technical, normative, and legal.

## Distinguishing marks

- **The longest LLM pipeline in the family.** Seven stages. Sermon writing earns the most rounds.
- **The strictest privacy posture in the family.** Even stricter than Granny's recipes — that repo is private but the recipes can be sent to AI for transcription. Romans manuscripts cannot.
- **An `.ai-deny` file at the root.** The only repo that explicitly disclaims AI training use.
- **A README that grades itself.** The "Thus Says the Lord" rubric is applied to the README itself, with N/A on every category, and a recommendation to add a brief description of the sermon series to serve its indexing function.
- **Two `claude.md` files** — one lowercase, one uppercase, different content. The repo carries its own history forward.
- **A `signs-of-spiritual-coldness-checklist.txt`** in the root. The pastor's self-examination tool, in plain sight.
- **`sebts-reference/`.** The repo names the seminary openly. The MDiv work is part of the preaching corpus.
- **Confessional location.** 1689 LBCF, ESV, gospel call required. Three constraints that are non-negotiable.
- **Working-title humility.** *"Eph 2 - but God."* The titles tell the preacher what the sermon is, not the audience.
- **Voice as research.** A whole directory studying how Ken sounds when Ken is preaching.
- **A `personal/` subdirectory inside a private repo.** Two layers of privacy. The preacher's own devotional notes are even more closed than the manuscripts.

## Relationship to siblings

`Romans` is the **pastoral** corner of the household:

| Repo | Domain |
|---|---|
| **`Romans`** | **What the pastor preaches** |
| `Family-History` | Whom the family came from |
| `manateecreeksheep` | What the household tends |
| 4 recipe repos | What the household cooks |
| `flickersofmajesty` | What the photographer captures |
| `InTheWake` | Where the family travels |
| `ken` | The tools that serve them all |

Of the eleven repos, only two are private: this one and `Grannysrecipes`. Of those two, only this one explicitly forbids AI training use. The repo carries the household's most protected work.

The `careful.md` ethic, the `like-a-human` voice skill, and the `voice-audit` skill all originated or were refined here, then propagated to other parts of the family. The preacher's discipline of preserved voice has become a household-wide standard.

## What would be lost

If `Romans` disappeared, the family would lose the pastor's **entire preaching archive** — every manuscript preached and every manuscript in the queue, the slide decks, the seminary reference materials, the sermon-evaluation rubric, the voice-research corpus that knows what the pastor sounds like, and the seven-stage sermon pipeline that the orchestrator runs against. The congregation would have heard the sermons; the manuscripts would not exist to revise, repreach, or hand to a successor.

## One-line summary

**`Romans` is the pastor's manuscript drawer — Ken Baker's preached and in-progress sermons across the canon, governed by 1689 LBCF theology and the ESV, written through the family's longest seven-stage LLM pipeline, scored against a 17-element rubric, voice-audited to make sure Claude doesn't ghost the preacher, and walled off from AI training by a `.ai-deny` file and a copyright-only README.**
