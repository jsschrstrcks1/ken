# Soul of `Family-History`

> *Tell their story in a cogent manner. Connect their facts into their life story. — Ken Baker, in CLAUDE.md*

The archaeology project. Florida pioneer ancestry traced to **1198 Spain**, **1594 St. Augustine**, and **1596 England** — written as connected lives, not name-and-date trees.

---

## Identity

`Family-History` is **Ken Baker's family archaeology project** — a genealogy repository covering eleven major lines: **Baker, Raulerson, Stokes, Montes de Oca / Montesdoca, Solana, Myers, Carlton, Peay, Corwin, Taft, Blount**, plus Native American heritage in the **Chickasaw, Catawba, Patawomeck, and Lumbee** lineages.

The first paragraph of the README states the project's distinguishing premise:

> *This isn't just names and dates — it's stories, voices, primary source discoveries, and honest assessments of what's proven versus what's claimed.*

That's the whole repo in one sentence.

The current state: **255 person pages, 53 source files, 11 family lines, oldest documented ancestor in 1198 Spain (Villavicencio noble family), oldest American ancestor in 1594 St. Augustine (Solana), oldest English ancestor in 1596 (Corwin of Southold).**

This is the most ambitious of the 11 sister repos by raw scope. It treats genealogy as research, not as collection — primary sources, debunked myths, parish-record citations, FOIA requests, oral history transcripts, and a rigorous source hierarchy.

## What it actually is

1. **`people/`** — 255 individual markdown person pages, one file per ancestor, cross-linked with relative paths. Format defined in `PERSON-PAGE-TEMPLATE.md`.
2. **`sources/`** — 53 research documents. Source analyses, transcribed books, lineage chain studies, ancestor-by-nation tracking, presidential-connection research, Oak Island connections, debunking reports.
3. **`transcripts/`** — Audio transcriptions of oral history conversations, primarily with **Velma Stokes**.
4. **`photos/`** — `photos/people/` for individual portraits, `photos/book-scans/` for scanned book pages (cropped per coordinates encoded in `scripts/process_book_scans.py`).
5. **`data/family_data.json`** — explicitly out of date (40 entries vs. 255 person pages). The repo names it as low priority and moves on.
6. **`scripts/`** — image processing, book-scan auto-cropping with predefined coordinates per page.
7. **`tools/resize-for-claude.py`** — image safeguard. Claude Code crashes on images >2000px, so the script resizes to 1920px max before any read.

The **family chains** documented to completion:

| Chain | Generations | Span |
|---|---|---|
| Solana | 11 generations | 1594–present |
| Corwin | 11 generations | c.1596–present |
| Myers | 6 generations | 1731–1905 |
| Ken → Captain Juan MDO | 7 confirmed generations | c.1809–present |

Plus chains to: **King Philip III of France** (via Plantagenet investigations, 5 paths broken), **Battle of Las Navas de Tolosa, 1212** (Cabeza de Vaca), **Spanish marquessate** (Villavicencio, traced to 1198), **Mayflower** (Sarah Thomas, disputed), **President Taft** (5th–6th cousins, confirmed), and **William Howard Taft's shared ancestor** Robert Taft Sr. (c.1640).

## Voice

**Narrative, not bullet points.** The CLAUDE.md is explicit: "*Tell stories, don't just list facts. Connect dates and records into a coherent life narrative.*" Person pages don't read like database printouts — they read like miniature biographies with sources cited. Quoted directly from Ken in the CLAUDE.md: *"Tell their story in a cogent manner. Connect their facts into their life story."*

**Refusing to sanitize.** Another quoted directive: *"Don't sanitize — record the hard truths (Granger's alcoholism, Maurice's abuse, etc.)."* The family history is told with the alcoholism, the abuse, the murders, the children fathered out of wedlock, the burial #94 records. The repo's commitment is to truth, not hagiography.

**Honest about what's not proven.** The README has dedicated sections for "Confirmed from PRIMARY Cathedral Parish Records," "Resolved from Independent Research," and "Debunked / Reclassified." The Vespucci connection: debunked. The Moytoy Cherokee dynasty: flagged fictitious. Plantagenet/Charlemagne descent: 5 paths investigated, all broken; "*statistically near-certain for anyone of English ancestry but no documented chain exists.*" The Eleanor Panther Clan claim: corrected from Cherokee to Chickasaw.

**Refusing not to be condensed.** From CLAUDE.md: *"Ken explicitly requested: 'I don't want the results to be condensed' — save full research to repo files."* Most genealogy software produces summaries; this repo produces transcripts of 127-page books, full census-record contexts, and multi-page research narratives.

**The voice of a researcher, not a family memoirist.** The Session Handoff Notes from April 17, 2026 read like a working historian's lab notebook: nine items "what was accomplished" — including *"DISPROVED the Lettice Knollys connection — extensive web research confirmed that Lettice Knollys (1543-1634) married Sir Christopher Blount of Kidderminster, NOT Thomas Blount of Astley."* This is the voice of someone willing to delete a flattering claim from his own tree.

## Style markers

- **Source hierarchy as a numbered list, in order of authority:**

  1. **Family Bible** — takes precedence over **ALL** other sources
  2. **Cathedral Parish Records** — PRIMARY sacramental records (St. Augustine 1594–1821)
  3. **Ken's direct family knowledge** (from Velma, other living relatives)
  4. **Primary records** (certificates, census, probate, military, property/land)
  5. **Books** (*Piney Wood Rooters* by Doris Moody Lewis — 127 pages fully transcribed)
  6. **Secondary sources** (obituaries, Find a Grave, Willingham genealogy)
  7. **Ancestry.com** — lowest tier; **all claims flagged as UNVERIFIED per Ken's instruction**

  Each source is named, ranked, and the sources at each tier are listed by document. The hierarchy is not advisory — it is enforced.

- **Specific record numbers cited.** The README quotes baptism #4210, burial #94, marriage #1135, marriage #1011 — these are line items from St. Augustine Cathedral Parish records, transcribed by the **Cuban Genealogy Club (Stephen Renouf, 2020)**. The repo treats archival numbers as the address of a fact.

- **A nation-by-nation tracker.** `sources/ancestors-by-nation.md` is updated every time a new ancestor is added, with **17 categories of interest**: Royalty & Nobility, Military service, Church history, Culture & Arts, Law & Government, Explorers & Colonists, Land grants (especially Spanish), Rebels & Revolutionaries, Executed by the Crown, Institutions founded, Oak Island connections, Presidential connections, Native American leadership, Shakespeare characters, Victims of historical violence, American/European history connections, Cultural producers.

- **A Session Handoff Notes section in CLAUDE.md** that gets *overwritten* every session, with three required parts: what was accomplished, what still needs doing, git state. The repo's continuity model is identical in philosophy to `ken/keeper-plan.md`.

- **Multi-LLM use is heavy.** The repo cites the orchestrator scripts directly: `orchestra.py` for fan-out consultation, `research_orchestra.py` with `--deep` flag for staged pipelines and sub-orchestras, `smart_routing.py` for conditional round-robin and weighted voting. The genealogy work uses every tool the family hub exposes.

## Philosophy

### History done with sources, not opinion

The seven-tier source hierarchy is the load-bearing methodological commitment. *Anything claimed gets a tier number*. A baptism record from St. Augustine outranks a Find a Grave entry, which outranks an Ancestry.com tree, which is flagged UNVERIFIED by default. **The repo is structured so that the strength of every claim is visible by source.**

### Debunk your own tree

The README has a *Debunked / Reclassified* section. This is unusual and load-bearing. Most genealogy projects accumulate flattering claims and rarely subtract. This one publishes the corrections:

- *Vespucci connection* — debunked (no evidence, gateway ancestor myth).
- *Moytoy Cherokee dynasty* — flagged fictitious (Geni, Starr's genealogy silent).
- *Plantagenet/Charlemagne descent* — 5 paths investigated, all broken.
- *Eleanor Panther Clan* — corrected from Cherokee to Chickasaw.
- *Mayflower (Sarah Thomas)* — disputed, two women conflated.
- *Deep MDO chain to 1528* — contradicted by baptism indexes.
- *Lettice Knollys connection* — disproved via Worcester County Record Office wills (1636–1637).

Each debunking is documented with the source that revealed the error. The repo refuses the pull toward flattering-but-wrong.

### Tell the story, don't sanitize

The CLAUDE.md instructs Claude to write *narratives*, not factual summaries — and to tell *the hard truths*, not the comfortable ones. *Granger's alcoholism. Maurice's abuse.* These are part of who these people were, and the repo refuses to airbrush.

This is more than a stylistic choice. It is a theological one. If history is offered to God (as the family-wide *Soli Deo Gloria* implies elsewhere in the family), then half-truth is an offering of half. The repo treats fullness as worship.

### Stories cost more space; spend the space

*"I don't want the results to be condensed — save full research to repo files."* This is why the repo has 53 source files and 255 person pages instead of one big database. Each life gets its own document. Each source gets its full transcription. **The repo refuses summarization as a default.**

### Native ancestry treated with care, not romance

Four Native American lines are tracked: Chickasaw (confirmed), Catawba (name confirmed as Catawba paramount chief's name), Patawomeck (plausible, 0.6% Indigenous DNA), Lumbee (link unestablished, "Strickland is core surname"). The plausibility levels are stated alongside the claims. The repo does not claim what it cannot show, and corrects when evidence shifts (Eleanor Panther Clan moved from Cherokee to Chickasaw mid-research).

### Process agent results immediately

A specific operational rule from the CLAUDE.md: *"When background research agents complete, their results MUST be fully processed and saved to the appropriate repository files BEFORE moving on to other work. Never defer agent result processing — treat completed agent results as the highest priority task."* The reasoning is stated openly: context window compaction will lose them. The repo treats research output as something fragile that must be persisted to disk immediately.

### Research is iterative; the repo records the iterations

The Session Handoff Notes for April 17, 2026 list nine accomplishments, twelve items still to do, and the exact git state. The notes include the specific NARA microfilm numbers needed (M804 for Major John Jacob Myers's pension, M881 for David Stokes), the SF-180 form to be filed at vetrecs.archives.gov for Kenneth H. Baker's military OMPF, and a contact name (Donald Corwin in Roscommon MI, "Frances's living brother as of 2013"). The handoff is the next session's first instruction.

## Technical anatomy

### Layout

```
Family-History/
├── CLAUDE.md                    ← Project rules + Session Handoff Notes
├── PERSON-PAGE-TEMPLATE.md      ← canonical person-page format
├── README.md                    ← project overview + family lines + discoveries
├── data/family_data.json        ← out of date (40 entries vs. 255 pages); low priority
├── people/                      ← 255 markdown person pages
├── sources/                     ← 53 research documents
├── transcripts/                 ← oral history (primarily Velma Stokes)
├── photos/
│   ├── people/                  ← individual portraits
│   └── book-scans/              ← cropped page images
├── scripts/
│   ├── process_book_scans.py    ← auto-crop with predefined coordinates
│   └── save_and_crop.py         ← base64 helper
└── tools/resize-for-claude.py   ← image safeguard, ≤ 1920 px
```

### Person page format (per `PERSON-PAGE-TEMPLATE.md`)

Family links, life narratives, sources, notes. Cross-linked with relative paths (e.g., `[Kathryn](kathryn-l-stokes.md)`). The CLAUDE.md treats the Markdown pages as the canonical store; `data/family_data.json` is allowed to fall behind.

### Image safeguard

```bash
python3 tools/resize-for-claude.py <image_path>
```

Mandatory before any image read. Outputs the safe path to stdout — resized copy in `/tmp/` if needed, or original path if already within 2000 px. Aspect ratio preserved, LANCZOS resampling, originals never modified. Same posture as the recipe repos' image safeguards: refuse oversized inputs at the tool layer.

### Multi-LLM integration (heaviest of any sister repo)

Mode: `family-history`. Lead: Claude (per `ken/orchestrator/repo-modes.json`). Memory scope: `/family-history`.

- **`orchestra.py`** — fan-out consultation: all models respond independently, then Claude + GPT deliberate.
- **`research_orchestra.py`** with `--deep` flag — staged pipeline (research models first, then synthesis, then analysts), iteration + sub-orchestras.
- **`smart_routing.py`** — conditional round-robin (6 trigger conditions), weighted voting, intelligent routing.

Models used: GPT, Grok, Perplexity (web-grounded), You.com (web-grounded). Gemini adapter has the cffi issue documented in `ken`'s README.

The genealogy work is the heaviest researcher of all the sister repos because **every claim is something a record could disprove**, and the orchestrator's multi-source verification compresses what would otherwise be weeks of one-source-at-a-time research.

## Distinguishing marks

- **The longest documented chains in the family.** Solana (11 generations, 1594–present) and Corwin (11 generations, 1596–present) are some of the longest documented European-American lineages anywhere.
- **Confirmed presidential cousin.** William Howard Taft, 5th–6th cousins via Robert Taft Sr. (c.1640, Mendon, MA).
- **Native American heritage held with calibrated uncertainty.** Confirmed (Chickasaw), confirmed-by-name (Catawba), plausible (Patawomeck), unestablished (Lumbee). Each tier is named.
- **A "Debunked / Reclassified" section in the README.** The repo names what was claimed and is no longer claimed — Vespucci, Moytoy, Plantagenet, the Eleanor Panther Clan misattribution, the deep MDO chain to 1528, the Lettice Knollys story. **It corrects in public.**
- **17 categories of historical interest.** Royalty, military, church, arts, law, explorers, land grants, rebels, executed, institutions founded, Oak Island, presidential, Native American leadership, *Shakespeare characters*, victims of violence, American/European history, cultural producers. Genealogy as a many-axis history project.
- **Quoted directives in the CLAUDE.md.** Three direct quotes from Ken — *"Tell their story in a cogent manner."* *"I don't want the results to be condensed."* *"Don't sanitize — record the hard truths."* The repo carries its owner's voice as policy.
- **The Family Bible is the highest authority.** Tier 1, above parish records, above primary records, above books, above Ancestry. The repo encodes a theology of household memory: the Bible is the family's first witness.
- **`data/family_data.json` is openly out of date and the repo names it.** The Markdown is canonical; the JSON is legacy. The repo doesn't pretend.

## Relationship to siblings

`Family-History` is the **research** corner of the household:

| Repo | What it preserves |
|---|---|
| Recipe repos | What the household *cooked* |
| `Romans` | What the household *believes* |
| `manateecreeksheep` | What the household *farms* |
| `flickersofmajesty` | What the household *photographs* |
| `InTheWake` | What the household *travels* |
| **`Family-History`** | **Who the household *came from*** |
| `ken` | The tools that serve all of the above |

The genealogy is also the deepest reach back. The recipes go back to MomMom. The sermons go back to seminary. The photographs go back to a few years. *Family-History* goes back to **1198 Spain**, **1212 Battle of Las Navas de Tolosa**, **1594 St. Augustine**. It is the family's longest memory.

## What would be lost

If `Family-History` disappeared, the family would lose:

- 255 individual life narratives — each carefully sourced, story-driven, refusing summary.
- 53 research documents including a full transcription of *Piney Wood Rooters* (127 pages), Solana chain research (1594–1851), Myers chain (Baron Rudolph to Holmes Rutledge), Spanish Land Grants, the Villavicencio noble research traced to 1198.
- Velma Stokes's oral history transcripts — irreplaceable once she's gone.
- The accumulated debunking work — every myth that's been investigated and disproved.
- The seven-tier source hierarchy that calibrates every claim.
- The handoff notes, the next-session research leads, the FOIA-pending list.

Most of all, the repo would lose its *honesty*. The hard truths about Granger and Maurice would be the first things sanitized in a casual family-tree rebuild.

## One-line summary

**`Family-History` is Ken Baker's family archaeology project — 255 stories, 53 sources, eleven lineage lines, traced back to 1198 Spain and 1594 St. Augustine, written as connected lives with their sins included, debunked in public when the evidence demands it, and held under a seven-tier source hierarchy where the Family Bible outranks Ancestry.com.**
