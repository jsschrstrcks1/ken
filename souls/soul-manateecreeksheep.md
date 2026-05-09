# Soul of `manateecreeksheep`

> *"The LORD is my shepherd; I shall not want."* — Psalm 23:1 (ESV)
>
> *Soli Deo Gloria — All work on this project is offered as a gift to God. We tend these sheep as stewards, not owners.*

The shepherd's notebook. ~50 sheep across 9 pens in Florida — bred for parasite resistance through 22 breeds, tracked by hand and by JSON, with the spiral notebook as the highest authority.

---

## Identity

`manateecreeksheep` is the **flock management, breeding program, and health tracking** repo for a working sheep operation at **Manatee Creek in Florida**. It is the only repo in the family where the data is alive — every record corresponds to an actual animal in an actual pen, eating actual grass, scoring actual FAMACHA values.

The mission is one sentence:

> *Produce sheep that are **more parasite resistant**, while maintaining **meat quality** and **milk production**, through strategic crossbreeding of 22+ breeds with FAMACHA-driven selection.*

Every breeding decision, every culling decision, every pen reassignment serves that one selection ladder. The repo is built around the ladder.

It is also a **family operation**. Mom keeps the spiral notebook. Mom's phone-app notes go straight to the source corpus. Mom writes "Amure" and the database normalizes to "Azure." This is multigenerational small-farm engineering.

## What it actually is

1. **`data/flock_database.json`** — the canonical structured record. Sheep, pedigrees, breed compositions, health, pen assignments, lambing records. Derived from sources, never authoritative against them.
2. **The spiral notebook** — Mom's handwritten records, photographed as `IMG_8560–8615.JPG`. **Authoritative.** When sources disagree, the notebook wins.
3. **Phone-app notes** — `IMG_8616–8643.PNG`. Treatments, weights, pen movements, dewormer dose, withdrawal periods.
4. **Spreadsheets** — `flock_record_v2.xlsx` (structured pen rosters), `data.csv` (historical), `Sheep_Breeding_DB_CURRENT_COPY.xlsx` (mating plans, ram eligibility, breeding rules).
5. **A Google Sheets bridge** via the `google-sheets-sync` skill, plus a `google-sheets-migration` helper for the legacy 113-tab → new 26-tab structure.
6. **Eight specialized skills** under `.claude/skills/` — careful-not-clever, image-transcription, flock-validation, breeding-advisor, pasture-planner, health-tracker, google-sheets-sync, google-sheets-migration.
7. **Validation tooling** — `scripts/validate_flock.py` runs pedigree consistency, breed-composition math, pen assignments, tag uniqueness, health-record completeness.
8. **Image processing** — `scripts/process_images.py` resizes 4032×3024 phone photos to ≤1800 px for AI consumption. Originals never deleted.

The flock as of late April 2026: **~52 active animals across 9 pens** (Pen 1, 2, 3, 4, 5, 6, Goose Pen, Chicken Coop, Tree Fort). The 2026 lambing season is in progress.

## Voice

**The voice of someone who has lost sheep and is trying not to lose any more.** The "Weak Resistance List (Feb 14, 2026)" names 18 animals: *Shaggy (deceased), GG, Azure, Butter Ball (deceased), Rocky, Skitters (deceased), Dorper 23 & 25, W136 (deceased), Circle Tail, W140, FM1, Samson (deceased), Unnamed (deceased), Baby, Bella, FM*. Six of those eighteen are dead. The list is part documentation, part grief.

**Affectionate naming.** *Charlie's Ewe. Charlie's Ram Lamb. Baby Azure. Broken Tail. Cocoa's Daughter. Little Daisy. Serendipity. Eclipse. NoriSon. Angus. Kelsier. Kaladin. Loki.* Many of the names are from *The Stormlight Archive* and *Mistborn* (Brandon Sanderson). The shepherd reads fantasy, and the sheep wear the names.

**Calibrated about uncertainty.** Every sheep record has a `confidence` field — `high | medium | low`. Speculative or inferred edits must be flagged explicitly. *"NEVER invent data — if something is unclear, mark it `[UNCLEAR]` and note confidence as 'low'."* The same household axiom that runs through the recipe repos.

**Theology as work ethic.** The CLAUDE.md states it: *"The governing principle: everything we do is for the glory of God and with integrity. We don't guess — we verify. We don't assume — we check. We don't cut corners — we serve the flock."* And the closing of the README: *"Everything we do here is for the glory of God."* No softening — the carefulness is what worship looks like in this domain.

**Honest about a single recent loss.** *"Sam was removed from active records 2026-04-26 — he died in Hurricane Helene on 2024-09-26 (off-farm, not on this property at time of death). Prior records had him with a 2026-04-02 bulk-cleanup status_date which was incorrect."* The repo records the death, the date, the place, and the prior record's error.

## Style markers

- **A "Key Aliases" table in the CLAUDE.md** that resolves Mom's notebook idiom into the database's canonical names. Eleven aliases. Including: *"Mom writes 'Amure' — this is **Azure**."* The repo treats the human → database translation as primary documentation.
- **A 7-pen pipeline as a closed loop** through which sheep cycle from quarantine to selection to breeding to gestation to lambing to grow-out. Every pen movement is a recorded transition.
- **A breeding rules registry**:

  - R1: Exclude placeholder/unknown "twin rams"
  - R2: Only adult rams (≥9 months) with known DOB
  - R3: Geriatric safety — if ewe age ≥6, exclude Ram 00110 (dystocia risk)
  - R4: Only "Eligible" rams

  Each rule has a number; the breeding-advisor skill enforces them.

- **FAMACHA scoring documented at five levels**, with treatment thresholds:

  | Score | Color | Action |
  |---|---|---|
  | 1 | Red | none |
  | 2 | Red-pink | none |
  | 3 | Pink | borderline, monitor |
  | 4 | Pink-white | treat |
  | 5 | White | treat immediately, consider culling |

- **A pen-by-pen roster table** updated every session. Pen 1: Orange Tag Ram (00110), six ewes, three lambs, ten total. Each pen has notes about recent moves and their dates.
- **PR-aware corrections in line.** *"Sam correction (preserved from PR-23)"* — the repo cites its own pull request history inline in the narrative, where the correction matters.

## Philosophy

### Stewardship, not ownership

The README is direct: *"We tend these sheep as stewards, not owners."* The framing is theological — the LORD is the shepherd; the human is a sub-shepherd. Every record is offered, every decision is accountable.

### The notebook wins

When sources disagree, the spiral notebook is authoritative. Tier 1 — the spiral notebook — outranks `flock_record_v2.xlsx`, which outranks `data.csv`, which outranks Google Sheets, which outranks the breeding spreadsheet. *"`flock_database.json` is the **derived** source of truth used by tooling — it must always trace back to one of the sources above."*

This is the same epistemic structure as `Family-History`'s seven-tier source hierarchy. Both repos refuse to let derived data be authoritative against primary observation.

### Parasite resistance comes first

In the priority list — *parasite resistance, hair coat, breed character, meat quality, milk production, hybrid vigor* — parasite resistance is a hard #1. Animals with chronically poor FAMACHA are removed from the breeding pipeline regardless of other traits. The principle is stated openly: *"Parasite resistance comes first."* The flock will be smaller before it will be sicker.

### Careful, not clever

The same `careful.md` principle as Allrecipes — but here it's enforced by a Claude Code skill (`.claude/skills/careful-not-clever/SKILL.md`) that activates on every file modification. *"Active skill … readable reference."* The integrity guardrail is both legible and automated.

### Never delete an image

Every photograph is a primary source document. Original handwritten records and photos of the sheep are irreplaceable. The retention policy is one sentence: *"NEVER delete any image."*

### Track deceased animals

A sheep that died this morning is still part of the pedigree of every lamb she ever bore. The repo keeps the dead — Shaggy, Butter Ball, Skitters, W136, Samson, Sam — as ancestors, not as deletions. Death is a status change, not a record removal.

### Multi-LLM with GPT in the lead

Almost unique among the sister repos: in `sheep` mode the **lead is GPT**, not Claude. The pipeline is `Plan (GPT) → Context (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT)`. The reasoning is stated in the CLAUDE.md: *"GPT (multi-step constraint reasoning), with Gemini, Grok, and Claude acting as validators."* Constraint-heavy breeding decisions go to GPT; safety and validation go to Claude. This is the only repo where Claude is a checker, not the lead.

### Privacy: anonymize anything that leaves

*"SEND: Anonymized flock data, breeding objectives, trait scores, health summaries. NEVER SEND: Financial records, location details beyond 'Florida'."* The orchestrator boundary is explicit. The flock database is shareable; the operation's commercial details are not.

## Technical anatomy

### Layout

```
manateecreeksheep/
├── data/
│   ├── flock_database.json            ← derived canonical record
│   └── processed/                     ← ≤ 1800 px AI-readable copies
├── scripts/
│   ├── process_images.py
│   └── validate_flock.py
├── .claude/
│   ├── settings.json
│   ├── skill-rules.json
│   └── skills/
│       ├── careful-not-clever/        ← integrity guardrail (active on every edit)
│       ├── image-transcription/       ← notebook OCR
│       ├── flock-validation/          ← validate_flock.py runner
│       ├── breeding-advisor/          ← evaluates matings against rules
│       ├── pasture-planner/           ← rotation by season + parasite load
│       ├── health-tracker/            ← FAMACHA trends, anemia early warning
│       ├── google-sheets-sync/        ← bidirectional spreadsheet ↔ JSON
│       └── google-sheets-migration/   ← legacy 113-tab → new 26-tab
├── CLAUDE.md
├── careful.md                         ← human-readable integrity rule
├── data.csv                           ← Tier 3 historical
├── flock_record_v2.xlsx               ← Tier 2 structured spreadsheet
├── Sheep_Breeding_DB_CURRENT_COPY.xlsx ← Tier 5 mating plans
├── IMG_8560–8615.JPG                  ← Tier 1 spiral notebook (handwritten)
├── IMG_8616–8643.PNG                  ← Tier 1 phone-app notes
└── LICENSE                            ← GNU AGPL v3
```

### Database schema (excerpt)

```json
{
  "id": "kebab-case-unique-id",
  "name": "Display name",
  "tag": "00113",
  "sex": "ewe",
  "breed_composition": {"Cracker": 0.25, "Suffolk": 0.25, "GCN": 0.25, "Katahdin": 0.25},
  "sire_id": "...",
  "dam_id": "...",
  "status": "alive | deceased | sold | unknown",
  "pen": "Pen 1",
  "health": {"famacha": [...], "treatments": [...], "weak_resistance": false},
  "confidence": "high | medium | low"
}
```

Plus top-level: `pens{}`, `lambing_records_2026[]`, `breed_reference{}`.

### Validation passes

`python3 scripts/validate_flock.py` enforces:

- **Pedigree consistency** — parents must exist; no cycles.
- **Breed composition math** — percentages must sum within tolerance.
- **Pen assignments** — every active sheep belongs to exactly one pen.
- **Tag uniqueness.**
- **Health record completeness** — FAMACHA must have date + score.
- **Reference integrity** (`--check-references`) — sire/dam IDs must resolve.
- **Image references** (`--check-images`) — referenced files must exist.

### Breeds in the flock (22+)

| Type | Breeds |
|---|---|
| Hair | Katahdin, Dorper, White Dorper, St Croix, Barbados Blackbelly, American Blackbelly, Wiltshire Horn |
| Wool | Suffolk, Hampshire, Cotswold, Tunis, Gulf Coast Native |
| Dual-purpose | St Augustine, Cracker, Awassi, East Friesian |
| Other | Jacob, Babydoll, Karakul |

The flock is a deliberate breed mosaic. The hypothesis is that hybrid vigor across diverse genetic resistance produces a more parasite-resistant composite than any single breed.

### Multi-LLM integration

Mode: `sheep`. Lead: **GPT** (planning) + Claude (safety/validation). Pipeline: `Plan (GPT) → Context (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT)`. Memory scope: `/sheep`. The constraint-reasoning load (mating plans satisfying R1–R4 plus inbreeding avoidance plus FAMACHA priors) is heavy enough to warrant GPT lead, with Claude acting as the validator that enforces the household's careful-not-clever ethic.

## Distinguishing marks

- **The only "live" repo.** Every record corresponds to a real animal alive in Florida right now (or known to have been). The data has a heartbeat.
- **A multigenerational shepherd team.** Mom keeps the notebook. The repo encodes Mom's idiom (*Amure → Azure*). The CLAUDE.md treats Mom's spelling as the authoritative source and the database as derived.
- **GPT-led, not Claude-led.** Almost unique in the family. The constraint-satisfaction load earns GPT primacy.
- **A "weak resistance list" with the dead named.** The repo carries grief in plain sight. It does not airbrush.
- **Sheep named after Sanderson novels.** Kelsier (Mistborn). Kaladin (Stormlight). The shepherd's reading life touches the flock.
- **A 7-pen breeding pipeline + a Goose Pen.** The pipeline is engineered, but the geese still get a pen. The infrastructure isn't only sheep.
- **A handwritten spiral notebook outranking JSON.** The Tier-1 source is paper. The repo treats *paper as primary* and JSON as derived. This is unusual in modern data engineering and theologically congruent: the human observation comes first.
- **Eight specialized skills.** Most sister repos have one or two; sheep has eight, because the operational surface is vast (transcription, validation, breeding, pasture, health, sync, migration).

## Relationship to siblings

`manateecreeksheep` is the **operational** corner of the household — the only repo where decisions made today affect a real animal tomorrow:

| Repo | Domain |
|---|---|
| **`manateecreeksheep`** | **Live operation: ~52 sheep, 9 pens, working flock** |
| `Family-History` | Past lives — researched, archived |
| `Romans` | Sermon prep — words to be preached |
| `flickersofmajesty` | Photography — prints to be sold |
| `InTheWake` | Cruise planning — trips to be taken |
| 4 recipe repos | Recipes — meals to be cooked |
| `ken` | Tools used by all of the above |

The sheep don't wait. The other repos work on archives, content, and infrastructure. This one has lambs being born this week and animals scoring FAMACHA 4 today.

## What would be lost

If `manateecreeksheep` disappeared, the operation would lose its derived database — the structured pedigrees, the breeding rules registry, the validation tooling. **The spiral notebook would survive** (it's paper) and the spreadsheets would survive (they're sources). But the cross-referenced breed-composition math, the pen-by-pen accounting, the FAMACHA trend analysis, the eight specialized skills, and the multi-LLM breeding-advisor pipeline would all need to be rebuilt — and the rebuild would happen while lambing season was in progress.

## One-line summary

**`manateecreeksheep` is the household's working flock — ~52 sheep across 9 pens in Florida, bred across 22 breeds for parasite resistance first, kept by Mom in a spiral notebook that outranks any spreadsheet, validated by eight specialized Claude Code skills, and managed by a multi-LLM pipeline where GPT plans the matings and Claude makes sure the carefulness holds.**
