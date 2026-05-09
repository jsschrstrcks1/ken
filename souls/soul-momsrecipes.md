# Soul of `MomsRecipes`

> *"She looketh well to the ways of her household, and eateth not the bread of idleness." — Proverbs 31:27*

MomMom Baker's kitchen. Index cards, magazine clippings, foraged herbs from "Eat the Weeds," and ~2,700+ recipes that hold the deepest weight in the family.

---

## Identity

`MomsRecipes` is the recipe collection of **MomMom Baker** — index cards, magazine clippings, family treasures. The repo's title-case shows the affection: *MomMom's Kitchen*.

This is the **biggest of the family-cook repos** by recipe count: ~2,700+ recipes, dwarfing Grandma's five and Granny's smaller collection. Allrecipes is larger overall (9,989) but anonymous; MomMom's recipes are personal at scale.

It is also the most **operationally mature** of the four. The CLAUDE.md is a lean hub. The README points to four supporting documents: `DATA_SCHEMA.md`, `MAINTENANCE.md`, `SCRIPTS.md`, `TROUBLESHOOTING.md`. The repo is run like a kitchen — daily ops, not a one-off archive.

## What it actually is

1. **A static recipe site** — `index.html` with search & filters, `recipe.html` for detail, vanilla JS, no framework. Consistent shape with the other recipe sites.
2. **A 2,700+ recipe corpus** at `data/recipes.json`, with a generated browse index (`recipes-index.json`), per-category shards (`recipes-{cat}.json`), and `collections.json` metadata. Plus `foraging_tips.json` for the wild-edibles corner.
3. **The biggest cookbook ingestion pipeline in the family** — 37+ `add_*.py` scripts under `scripts/`, each one written for a specific source batch. New cookbooks get their own ingestion script rather than a generic loader.
4. **A PDF processing pipeline** in addition to image processing — `pdf_safeguards.py` for handling the multi-page Foxfire and BHG sources. The Claude API limit is 100 pages / 50 MB, and the safeguards refuse oversized PDFs without first running text extraction.
5. **A printable e-book** at `ebook/book.html` with `print.css` for Calibre/wkhtmltopdf/browser-print export.
6. **An "overlooked tips" audit** at `OVERLOOKED_TIPS_AUDIT.md` — small notes ("MomMom always added a pinch of nutmeg") that originally lived only in family memory.

## Voice

**Operationally serious.** The README has a *Maintenance* section that points at a runbook. The CLAUDE.md has a "Maintenance Cheat Sheet" with literal bash commands. *"After bulk recipe additions (10+): run validate-recipes, run create_shards."* This is the voice of a working kitchen.

**Honest about gaps.** *"If a card is illegible or instructions are missing, capture what's there and flag the rest with `confidence.overall = "low"` and a `flags` entry explaining what's uncertain. **Honest gaps are better than invented steps.**"* That's the family axiom in MomMom's voice.

**Affectionate naming.** *MomMom's Kitchen.* *MomMom's Cards.* *Recipe: add MomMom's apple butter.* The intimate diminutive runs through every layer of the repo, including commit messages.

**Same KJV bookend.** *Soli Deo Gloria* opens; Proverbs 31:27 closes. The family's antiphon.

## Style markers

- **Five top-level operational docs.** README, CLAUDE.md, DATA_SCHEMA.md, MAINTENANCE.md, SCRIPTS.md, TROUBLESHOOTING.md, OVERLOOKED_TIPS_AUDIT.md. The most documented of the four recipe repos. The repo has shipped enough that it has a full ops manual.
- **A "Recipe Sources" table in CLAUDE.md** that names the cookbooks and counts:

  | Source | Batches | Recipes |
  |---|---|---|
  | MomMom's Cards | — | ~800 |
  | Eat the Weeds | 1–12 | ~157 |
  | Honest Food | 1–5 | ~45 |
  | Foxfire Books | Multiple | ~35 |
  | BHG Cookbooks | 1 | Various |

  Each source has its own batches and ingestion scripts. The batch numbers are part of the ontology.

- **`add_*.py` scripts numbered 37+.** The ingestion isn't a loop over a directory — each cookbook gets a script that knows its layout. This is more careful and more code, but it makes each book's quirks legible.
- **Generated category shards** — `recipes-mains.json`, `recipes-desserts.json`, etc. The site loads only the relevant shard per page. A 2,700-recipe corpus needed sharding to stay snappy.
- **CLAUDE.md cut from ~391 lines to ~120** in the same 2026-05-01 lean-hub refactor that hit the other recipe repos. Standards extracted: OCR_STANDARDS, IMAGE_WORKFLOW, **PDF_WORKFLOW** (unique to this repo), RECIPE_SCHEMA, SESSION_MANAGEMENT.
- **A `requirements.txt` at the root.** The only recipe repo with one. The pipeline is Python-heavy enough to deserve a pinned dependency list.
- **iPhone photos as the dominant source format** — 4032 × 3024 px originals. The CLAUDE.md warns: *"DO NOT read directly."* Always use `data/processed/`.

## Philosophy

### Personal at scale

The repo holds 2,700+ recipes, but each one is from a specific cook. The family-wide rule applies in MomMom's voice: *Keep family names and attributions* — if MomMom called it "Aunt Velma's Banana Bread," the title carries the attribution forever. The scale doesn't dilute the personal.

### Honest gaps over invented steps

This is the line that captures the repo's character most clearly:

> *Honest gaps are better than invented steps.*

When a card is illegible, the recipe is saved with a `[UNCLEAR]` tag, a low confidence score, and a `flags` entry explaining what's missing. The recipe is preserved, the gap is acknowledged, the next person to find a clearer source can fix it. **The repo treats incompleteness as data**, not as a defect to hide.

### Foraging as a category

`foraging_tips.json` is a separate file from `recipes.json`. The "Eat the Weeds" series (~157 recipes) is wild edibles and foraging, and the safety rules need their own JSON because misidentifying a wild plant has different stakes than mistyping a sugar measurement. Foraging gets its own data shape and its own warnings.

### Wild game and unusual meats

The "Honest Food" series (~45 recipes) is wild game and unusual meats. The repo treats hunting, foraging, and pantry cooking as parts of one continuous household practice. There is no separation between "normal cooking" and "the weird stuff." MomMom's kitchen included all of it.

### PDF safeguards as a separate workflow

Most recipe repos process images. This one processes PDFs too — the Foxfire books are multi-page PDFs, and the API limit (100 pages / 50 MB) needs a separate `pdf_safeguards.py` and a `pdf_manifest.json`. The repo invents its tooling as the source material demands.

### Same family axiom

*"Real people will eat from these recipes — accuracy matters more than speed."* Same as Allrecipes, Grandmasrecipes, Grannysrecipes. *Decision priority: accuracy → preservation → fidelity → readability.*

### Sharding when the data outgrows a single fetch

A 2,700-recipe JSON file is too big to load on every page. The repo invents per-category shards, generated by `scripts/create_shards.py`, and the site loads only what it needs. This is engineering that the smaller recipe repos don't need — and it's done quietly, in the background, because the cook's experience must stay fast.

## Technical anatomy

### Layout

```
MomsRecipes/
├── index.html / recipe.html
├── styles.css (39 KB) / script.js (26 KB)
├── data/
│   ├── *.jpeg               ← iPhone originals (4032×3024)
│   ├── processed/           ← ≤ 2000 px AI copies
│   ├── recipes.json         ← ~2,700+ recipes
│   ├── recipes-index.json   ← generated browse index
│   ├── recipes-{cat}.json   ← generated per-category shards
│   ├── collections.json
│   ├── foraging_tips.json   ← Eat the Weeds safety rules
│   ├── image_manifest.json
│   └── pdf_manifest.json
├── scripts/
│   ├── validate-recipes.py
│   ├── process_images.py
│   ├── image_safeguards.py
│   ├── pdf_safeguards.py    ← unique to this repo
│   ├── optimize_images.py
│   ├── create_shards.py     ← regenerates per-category shards
│   └── add_*.py             ← 37+ ingestion scripts, one per source batch
├── ebook/{book.html, print.css}
├── requirements.txt
├── DATA_SCHEMA.md
├── MAINTENANCE.md
├── SCRIPTS.md
├── TROUBLESHOOTING.md
└── OVERLOOKED_TIPS_AUDIT.md
```

### Image and PDF pipeline

```
1. Drop iPhone photo or PDF into data/
2. python scripts/process_images.py    (or pdf_safeguards.py)
3. AI reads from data/processed/        (or extracted text)
4. Append to data/recipes.json
5. python scripts/create_shards.py      (regenerate shards)
6. python scripts/validate-recipes.py
7. Commit
```

### Recipe schema (excerpt)

```json
{
  "id": "recipe-slug",
  "collection": "mommom",
  "collection_display": "MomMom Baker",
  "title": "Recipe Title",
  "category": "appetizers|beverages|breads|breakfast|desserts|mains|salads|sides|soups|snacks",
  "ingredients": [{"item": "...", "quantity": "...", "unit": "...", "prep_note": "..."}],
  "instructions": [{"step": 1, "text": "..."}],
  "tips": ["..."],          // overlooked-tips set
  "confidence": {"overall": "high|medium|low", "flags": []},
  "image_refs": ["Moms Recipes - 1.jpeg"]
}
```

Required: `"collection": "mommom"` on every recipe. Required: never discard `image_refs`, even on merged duplicates. Required: every recipe traces to a real source — no anonymous recipes.

### Multi-LLM integration

Mode: `recipe`. Lead: GPT (per `ken/orchestrator/repo-modes.json`). Memory scope: `/MomsRecipes`. The `recipe-transcription` and `recipe-validation` skills run inside the pipeline. Same family rule: never invent, flag inferences, mark `[UNCLEAR]`.

### License

GNU AGPL v3 on the source code. Recipe text and images are family-private and not licensed for commercial reuse.

## Distinguishing marks

- **The biggest of the named-cook repos.** ~2,700+ recipes from one cook's gathered sources. Allrecipes is bigger but anonymous; this one is *named at scale*.
- **A PDF pipeline.** Only recipe repo that handles multi-page PDFs (Foxfire books). The `pdf_safeguards.py` and `PDF_WORKFLOW.md` are unique to MomMom's repo.
- **37+ source-specific ingestion scripts.** A `add_<cookbook>.py` per batch instead of a generic loader. Each cookbook gets its own treatment.
- **Sharded data.** The corpus is too big to load whole; generated category shards keep the site fast.
- **Foraging is a first-class concept.** `foraging_tips.json` and the "Eat the Weeds" batches mean the repo holds wild-edibles knowledge alongside cake recipes. The kitchen's edges go further than the supermarket aisle.
- **A `TROUBLESHOOTING.md`** that exists because real things have actually broken — image rotation, missing slugs, broken JSON, encoding glitches in old text. The repo carries its repair history forward.
- **The naming.** *MomMom.* The title-case form is the affection. Most projects abstract their subjects; this one names her.

## Relationship to siblings

`MomsRecipes` is the **operational** corner of the four-repo recipe family:

| Repo | Distinguishing trait |
|---|---|
| **`MomsRecipes`** | **Largest named cook (2,700+); most mature ops; PDF pipeline; sharded data** |
| `Grandmasrecipes` | Smallest named cook (5); converters live here; PWA + Pagefind |
| `Grannysrecipes` | Smaller named cook; private + anti-indexed; Memorial section |
| `Allrecipes` | Reference shelf; 9,989 anonymous; cheese/butter builders |

The four sites share a UI shell and JSON shape on purpose, so a future Family Recipe Hub can aggregate them. That hub already exists (in `Grandmasrecipes`), and `MomsRecipes` is its largest contributor.

## What would be lost

If `MomsRecipes` disappeared, the family would lose ~2,700+ named recipes — including ~800 from MomMom's own cards, 157 wild-edibles entries with safety rules, 45 wild-game recipes, 35 Foxfire-derived heritage recipes, and several hundred from other named sources. The PDF pipeline would have to be reinvented for any future Foxfire-style sources. The "overlooked tips" audit would lose its accumulated work.

## One-line summary

**`MomsRecipes` is MomMom Baker's kitchen at scale — 2,700+ named recipes from cards, magazines, foraging, and wild game, run like a working kitchen with a full ops manual and a sharded data layer because the love is too big to load on every page.**
