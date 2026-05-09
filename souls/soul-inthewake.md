# Soul of `InTheWake`

> *Soli Deo Gloria. Every line of code and every word of content is stewardship. Excellence as worship means getting it right, not getting it fast.*

The cruise blog. *cruisinginthewake.com.* **Christ-shaped cruise planning** for ordinary cruise travelers — 1,241 pages, 295 ships, 387 ports, with the most rigorous validator chain in the family.

---

## Identity

`InTheWake` is the source repo for **[cruisinginthewake.com](https://cruisinginthewake.com)** — a static cruise-planning website serving "ordinary cruise travelers" who are making real decisions with budgets on the line. The README's first sentence says it plainly: *"A Christ-shaped cruise planning website for ordinary cruise travelers."*

The mission is sized to that audience: every port page, ship page, and tool answers a question someone is actually asking. Not aspirational travel marketing. Not lifestyle content. **Decision support for people about to spend money on a cruise.**

The repo is the **largest by page count** in the family by an order of magnitude — ~1,241 pages, ~4,475 WebP images, 1,310 JSON data files. It is also the **parent of two protocols** that govern the family's other content sites: **ITW-Lite v3.010** (the AI-first/human-first content protocol later adapted to `flickersofmajesty` as **FOM-Lite**), and the layered "new-standards" system (`foundation/` + `v3.010/`) that may eventually govern other sister sites.

## What it actually is

The numbers ground everything:

| Metric | Value |
|---|---|
| Total pages | **~1,241** |
| Ship pages | 295 across 5 cruise lines (RCL, NCL, Virgin, MSC, Carnival) |
| Port pages | 387 |
| Restaurant / venue pages | many across all five lines |
| Solo travel articles | dedicated section under `/solo/articles/` |
| WebP images | **4,475** (682 are ship images) |
| JSON data files | **1,310** in `assets/data/` |
| Service Worker | v14.3.0 |
| Page template | v3.010.305 (some at v3.010.300 / v3.010.400) |

Beyond pages, the site ships **eight interactive tools** that handle real money:

| Tool | Purpose |
|---|---|
| Drink Calculator (v1 + v2) | Compares drink packages across **15 cruise lines** |
| Drink Packages overview | Side-by-side package comparison |
| Stateroom Checker | Validates a stateroom against **270 ship-data JSON files** |
| Countdown | Trip countdown widget |
| Packing Lists | Checklists by trip type |
| Search | Site-wide search |
| First Cruise | Onboarding for first-timers |
| Internet at Sea | Wi-Fi packages compared |

Plus a dedicated **Solo Travel** planner (`solo.html` + `solo/articles/`).

The site is a **Progressive Web App**: `manifest.webmanifest`, `sw.js` (precaching, offline fallback), `offline.html`, plus host-level cache rules in `_headers`, `.htaccess`, and `nginx-cache-headers.conf`.

## Voice

**Honest, calm, concrete.** This is the explicit voice rule, stated in the Content Standards section:

> *Honest, calm, concrete. Facts over superlatives.*
>
> *Specific over generic. "The 9 a.m. tender to Cabo San Lucas runs every 20 minutes" beats "tenders run regularly".*

The example in the README is doing real work — it tells the reader what the voice looks like in practice. The 9-a.m.-tender sentence is the kind of sentence the site is built for.

**Negative reviews are surfaced, not hidden.** Another explicit rule: *"Negative reviews are surfaced and contextualized, not hidden."* The site is willing to tell a reader the buffet is mediocre, the venue runs cold, the wifi is unreliable. **Cruise lines pay marketing departments to hide this. The repo refuses.**

**Christ-shaped, not sermonizing.** The framing is the same as `ken`'s: *Soli Deo Gloria* opens and closes the README. The phrase "Christ-shaped" appears once in the first sentence, and then never again. The body of the README is technical: validator chains, page templates, JSON-data counts. The faith is in the *posture* — the carefulness, the refusal to invent, the *Soli Deo Gloria* comment that must appear in every HTML file before line 20 — not in the prose.

**Standards-document register.** The README is dense and orderly. Tables for everything. The voice is the voice of someone who has shipped 1,241 pages and is documenting how to ship 1,242 without a regression.

## Style markers

- **Page metric tables that stay honest.** *"Numbers are ground-truth as of the last claude.md audit. They drift — the canonical source is whatever the validator reports today."* The README itself flags its own measurements as point-in-time. **The validator is canonical, not the README.**
- **A *Soli Deo Gloria* comment in every HTML file before line 20.** *"This is immutable — not for SEO, not for performance, not for anything."* The faith framing is enforced as a code invariant — the validator checks for it on every page.
- **Layered standards system in two trees.** `new-standards/foundation/` (the persistent superset: v3.007.010, v3.100, v3.008, v3.007) and `new-standards/v3.010/` (the active version: PORT_PAGE, LOGBOOK_ENTRY, SHIP_PAGE_CHECKLIST, MOBILE). Plus a `standards/` directory for legacy gold-standard files.
- **Five-tier conflict resolution.** When standards conflict, defer in this order: (1) `careful-not-clever/CAREFUL.md`, (2) `claude.md`, (3) `admin/claude/TECHNICAL_STANDARDS.md`, (4) `new-standards/`, (5) `admin/UNFINISHED_TASKS.md`. The repo names its hierarchy.
- **Three-task-management files.** `admin/UNFINISHED_TASKS.md` (master P0–P4 list), `admin/IN_PROGRESS_TASKS.md` (current session), `admin/COMPLETED_TASKS.md` (log). Triage system, not just a TODO.
- **Three validation hooks.** Claude Code post-write hook, git pre-commit hook, page-type dispatcher (`admin/validate.js`). Three independent enforcement points. The validator is *not* optional.
- **Two `CAREFUL.md` files.** `.claude/skills/careful-not-clever/CAREFUL.md` for process integrity, `admin/CAREFUL.md` for technical integrity (CSS semantics, pre-commit checks). The household idiom forks into two layers here.
- **Legacy validator preserved as `admin/legacy/validate-ship-page.js`** — kept *for reference only* — with a strict note: *"Do not resurrect it without porting its checks into the canonical shell validator first."* The repo carries its own evolution and refuses to regress.

## Philosophy

### The validator is canonical

The repo's deepest commitment: **whatever the validator says, that's the truth.** The README's metrics are point-in-time. The `claude.md` audit is point-in-time. The current state of the site is whatever passes the page-type dispatcher today. The validator is the document; everything else is commentary.

This shows up in the *Critical "Never Do" Rules*:

> ❌ **Never game the validator.** Reverse-engineering regex patterns to pass automated checks is a blocking integrity failure.

The validator can be honored or it can be cheated. Cheating is named and treated as a more serious failure than failing the validator outright.

### Never use training data as a source

The site's most distinctive integrity rule:

> **Never use training data as a source.** Ship stats, IMO numbers, crew counts, tonnage, build dates, etc. come from on-page data, repo JSON, or original research (`WebSearch`, `WebFetch`, `/consult`, `/investigate`).

A cruise-info site is constantly tempted to fill in numbers an LLM "knows." The repo refuses categorically. **Every ship statistic must trace to either the page itself, a JSON data file in the repo, or an original-research call.** Training data is not a citation.

This is the cruise-blog version of the household-wide *never invent* axiom. The recipe repos refuse to invent steps; this one refuses to invent IMO numbers.

### Christ-shaped, hospitality-shaped

"Christ-shaped" is the framing word. What it means in practice:

- The voice is calm and honest because the reader is a real person making a real decision.
- Negative information is surfaced because hospitality without honesty is sales.
- Specifics over generics because vagueness wastes the reader's time.
- *Soli Deo Gloria* is in every page comment because the work is offered, not just deployed.

The repo treats writing for a cruise audience as a way of loving neighbors. It is not a Christian cruise site. It is a cruise site that is built Christianly.

### ITW-Lite as the parent protocol

`InTheWake` invented the **ITW-Lite Protocol** — *AI-first, human-first, hidden by design*. Three principles:

1. AI assistants get structured content they can describe accurately.
2. Human users never see the AI scaffolding.
3. **When the two conflict, humans win.**

This protocol was adapted to `flickersofmajesty` as FOM-Lite. The pattern (meta tags, fit-guidance sections, AI breadcrumbs, Schema.org coverage) was *born here* and ported there. The current iteration is **ITW-Lite v3.010**, governed by the consolidated standards in `new-standards/`.

### PWA because the reader is on a cruise

The repo ships a Progressive Web App. The Service Worker is at v14.3.0. There is an offline fallback page. The reasoning is cruise-specific: **a person reading this site is, eventually, on a ship with bad wifi**, and the site needs to keep working when the connection drops.

The PWA isn't a feature flex. It's hospitality at sea.

### Accessibility is foundational, not optional

The standards directory has its own document for it: `new-standards/foundation/WCAG_2.1_AA_STANDARDS_v3.100.md`. The 12-link primary nav has its own ARIA standard at `NAVIGATION_STANDARDS_ADDENDUM_v3.008.md`. Mobile breakpoints have their own document at `MOBILE_STANDARDS_v1.000.md`. Touch targets, screen readers, keyboard navigation — none of it is afterthought.

### Page-template versioning is part of the language

`v3.010.305`, `v3.010.300`, `v3.010.400` — pages are versioned to the patch level. New pages get `?v=3.010.400` on the CSS query string for cache-busting. The repo treats every template change as a versioned event, because at 1,241 pages, you need to know which template a page was last regenerated against.

### Cache-busting and host-level caching as a discipline

`_headers` (Cloudflare/Netlify), `.htaccess` (Apache), `nginx-cache-headers.conf` (Nginx) — three host-level cache configurations shipped together. The repo doesn't assume a single hosting target. **It serves whoever serves it.**

## Technical anatomy

### Layout

```
InTheWake/
├── index.html                           ← homepage (hero + compass pattern)
├── ships/index.html                     ← ships hub (NOT /ships.html)
├── ships/<line>/<slug>.html             ← 295 ship pages
├── ports/                               ← 387 port pages
├── restaurants/                         ← venue pages across 5 lines
├── solo/                                ← solo travel section
│   ├── solo.html
│   └── articles/
├── tools/                               ← drink calc, stateroom check, etc.
├── articles/                            ← logbook entries
├── assets/
│   ├── css/styles.css?v=3.010.400
│   ├── data/                            ← 1,310 JSON files
│   └── ships/                           ← 682 WebP ship images (4,475 total WebP)
├── new-standards/
│   ├── foundation/
│   │   ├── Unified_Modular_Standards_v3.007.010.md   ← complete superset
│   │   ├── SHIP_PAGE_STANDARDS_v3.007.010.md
│   │   ├── WCAG_2.1_AA_STANDARDS_v3.100.md
│   │   ├── PWA_CACHING_STANDARDS_v3.007.md
│   │   └── NAVIGATION_STANDARDS_ADDENDUM_v3.008.md
│   └── v3.010/
│       ├── PORT_PAGE_STANDARD_v3.010.md
│       ├── LOGBOOK_ENTRY_STANDARD_v3.010.md
│       ├── SHIP_PAGE_CHECKLIST_v3.010.md
│       └── MOBILE_STANDARDS_v1.000.md
├── standards/                           ← legacy gold-standards (SHIP_PAGE v2.0)
├── admin/
│   ├── validate-ship-page.sh           ← canonical validator
│   ├── validate.js                     ← page-type dispatcher
│   ├── legacy/validate-ship-page.js    ← old JS validator (reference only)
│   ├── UNFINISHED_TASKS.md
│   ├── IN_PROGRESS_TASKS.md
│   ├── COMPLETED_TASKS.md
│   ├── CAREFUL.md                      ← technical integrity
│   └── claude/
│       ├── TECHNICAL_STANDARDS.md
│       ├── SITE_REFERENCE.md
│       ├── IMAGE_WORKFLOW.md
│       ├── WORKFLOW.md
│       ├── CODEBASE_GUIDE.md
│       ├── SKILLS_REFERENCE.md
│       └── CLAUDE.md
├── .claude/
│   ├── skills/careful-not-clever/CAREFUL.md  ← process integrity
│   └── hooks/
│       ├── ship-page-validator.sh
│       └── session-start-guardrail.sh
├── .githooks/pre-commit
├── claude.md                           ← top-level Claude guide
├── manifest.webmanifest
├── sw.js                               ← Service Worker v14.3.0
├── offline.html
├── _headers / .htaccess / nginx-cache-headers.conf
└── README.md
```

### Validator chain

```
Claude writes a page
    └─ .claude/hooks/ship-page-validator.sh fires (post-write)
       └─ admin/validate-ship-page.sh (canonical shell validator)
          └─ admin/validate.js (page-type dispatcher routes to the right validator)

git commit
    └─ .githooks/pre-commit fires
       └─ blocks: placeholder images, invalid JSON, missing SDG comment

Result: any path to production is gated by validation.
```

### URL conventions

- All internal links are **absolute HTTPS URLs**. No relative paths in production.
- The ships hub is `/ships/index.html`, **not** `/ships.html`. The latter does not exist.
- WebP-only images. The single exception is `logo_wake.png` (transparency required).
- Wikimedia Commons images require attribution.

### Multi-LLM integration

Mode: `cruising`. Lead: Claude. Memory scope: `/InTheWake`. Pipeline: `Read Standards (Claude) → Generate (Claude) → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate (Claude)`.

The cruising pipeline is the **prototype** for the family. It was built here, then adapted (mostly unchanged) for `flickersofmajesty`. The five-stage flow is the template for any AI-first/human-first content site in the household.

**Context boundaries** are strict:

- **Send**: page requirements, content outlines, SEO targets, public cruise/travel data.
- **Never send**: full codebase, internal standards docs, analytics data.

All output must comply with **ITW-Lite v3.010**, hero + compass pattern, right-side rail, accessibility, canonical URLs.

## Distinguishing marks

- **The largest static site in the family.** ~1,241 pages, 4,475 WebP images, 1,310 JSON files, 295 ship pages across 5 cruise lines. By page count, more than 10× any sister repo.
- **The parent of two protocols.** ITW-Lite (adapted to FOM-Lite) and the new-standards layered system. Patterns invented here propagate to other sister sites.
- **The most rigorous validator chain in the family.** Three independent enforcement points (post-write hook, pre-commit hook, page-type dispatcher) plus the legacy validator preserved as a reference and forbidden from being resurrected without proper porting.
- **A *Soli Deo Gloria* comment as a build invariant.** Every HTML file. Before line 20. *Immutable.* The validator enforces it.
- **Page versioning to the patch level.** `v3.010.305`, `v3.010.300`, `v3.010.400`. At 1,241 pages, this is the only way to know what was regenerated when.
- **Three host-level cache configurations shipped together.** `_headers`, `.htaccess`, `nginx-cache-headers.conf`. The repo serves whoever serves it.
- **A drink calculator covering 15 cruise lines.** This is more cruise lines than the site has ship pages for (5). The calculator is for the *whole* cruise market, even though the deeper coverage is on five lines.
- **A stateroom checker that validates against 270 ship-data JSON files.** Real-money decisions get real-data validation.
- **Negative reviews surfaced and contextualized, not hidden.** This is unusual for any commercial-adjacent site. The repo's hospitality includes telling the reader what *won't* work.
- **A Solo Travel section.** A whole sub-site for solo cruisers, an audience the major lines historically underserve.
- **The 9 a.m. tender to Cabo San Lucas.** A specific sentence in the README that doubles as the voice exemplar. The repo teaches its voice with one example.

## Relationship to siblings

`InTheWake` is the **content-platform** corner of the household:

| Repo | Surface | Page count |
|---|---|---|
| **`InTheWake`** | **cruisinginthewake.com** | **~1,241 pages** |
| `flickersofmajesty` | flickersofmajesty.com | growing (storefront) |
| `Romans` | private (sermons) | manuscripts as `.txt` |
| `Family-History` | private (genealogy) | 255 person pages |
| `manateecreeksheep` | flock data + skills | live operation |
| 4 recipe repos | static recipe sites | 5 / 9,989 / 2,700+ / smaller |
| `ken` | hub (orchestrator + tz + keeper) | 1 hub README |

Among the public content sites, `InTheWake` is dominant by page count, and *its protocols govern its sibling*. `flickersofmajesty`'s FOM-Lite is ITW-Lite renamed. The `careful-not-clever` skill, the validator-as-canonical posture, and the absolute-URL rule all originated or were perfected here.

When the household adds a new public content site, it will start from this repo's protocols.

## What would be lost

If `InTheWake` disappeared, the household would lose:

- The largest static-site corpus in the family — 1,241 pages of cruise planning content, 295 ship pages, 387 port pages, 1,310 JSON data files, 4,475 WebP images, 270 stateroom-data files.
- The eight interactive tools (drink calculator, stateroom checker, countdown, packing lists, internet-at-sea calculator, etc.).
- The Solo Travel section.
- The PWA shell that lets the site work at sea.
- **The ITW-Lite Protocol** in its canonical home. FOM-Lite (in `flickersofmajesty`) is a port; the original would be gone.
- The triple validator chain that enforces every standard.
- The layered new-standards system that may eventually govern other sister sites.

## One-line summary

**`InTheWake` is the family's largest content engine — 1,241 pages of Christ-shaped cruise planning at *cruisinginthewake.com*, governed by ITW-Lite v3.010, locked down by a triple validator chain, voiced as honest-calm-concrete with negative reviews surfaced not hidden, refusing to use training data as a source, and shipping every HTML file with a *Soli Deo Gloria* comment before line 20 because excellence is worship and the reader, eventually, will be on a ship with bad wifi.**
