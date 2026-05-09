# Soul of `Allrecipes`

> *"She looketh well to the ways of her household, and eateth not the bread of idleness." — Proverbs 31:27*

The reference shelf. Where recipes go that don't belong to a particular grandmother.

---

## Identity

`Allrecipes` is the largest of the four sister recipe repos — ~**9,989 recipes** at last count, sourced from digital cookbooks, magazine clippings, and reference materials, "used with permission." Where `MomsRecipes`, `Grandmasrecipes`, and `Grannysrecipes` preserve specific cooks (MomMom Baker, Grandma Baker, Granny Hudson), `Allrecipes` is the **reference shelf**: the place to look up a canonical béchamel, a Betty Crocker classic, or a Cook's Illustrated technique.

The name is unfortunate (it collides with the commercial site of the same name), but in this household it's read as *all-recipes-not-from-the-grandmothers*.

It is, importantly, **not a recipe site**. It's a recipe *archive* with a static-site front-end, several long-running audits, and four interactive builder tools that read more like teaching scaffolds than cooking aids.

## What it actually is

Six things layered together:

1. **A static recipe site** — `index.html` with search & filters, `recipe.html` for detail, `tips.html`, vanilla JS, no framework. Hostable on any static surface.
2. **A 9,989-recipe JSON corpus** at `data/recipes.json` with a strict schema (`id`, `collection`, `title`, `category`, `attribution`, `source_note`, `servings_yield`, `prep_time`, `cook_time`, `ingredients[]`, `instructions[]`, `temperature`, `tags`, `confidence`, `image_refs`).
3. **The Cheese Builder** — `cheese-builder.html` + 84 KB of `cheese-builder.js` walking through 60+ cheese varieties from acidification through aging. Tracked in `CHEESE_VARIETIES_TRACKER.md` (66 KB) and `CHEESE_VARIANTS.md`.
4. **The Butter Builder** — `butter-builder.html` + `.js`. Cultured, browned, salted, compound. Tracks fat percentage, water content, shelf life.
5. **The Adulterant Companion** — `adulterant-companion.js`. Helps a home cook spot vegetable oil in olive oil, non-dairy fat in butter, gum thickeners in yogurt. Educational, not a lab.
6. **The Milk Substitution module** — a copy of the engine in Grandma's repo, kept here so the reference site works offline.

Plus: an e-book at `ebook/book.html` for printing, image processing scripts (`process_images.py`, `image_safeguards.py`, `optimize_images.py`), a recipe validator (`validate-recipes.py`), and a `recovery_report.txt` documenting a past data-loss incident.

## Voice

**Reverent and procedural.** The README begins with *Soli Deo Gloria* and closes with Proverbs 31:27 in the King James register ("*She looketh well to the ways of her household, and eateth not the bread of idleness*"). In between: image-processing tables, JSON schemas, `wkhtmltopdf` invocations.

**Domestic and technical at once.** A reader gets "60+ cheese varieties tracked" next to "Cut, cook, drain, press, age." The voice treats home dairy work and JSON validation as belonging to the same act of careful housekeeping.

**KJV-flavored, AGPL-licensed.** The benediction is from the King James Version. The license is GNU Affero General Public License v3. Both are quoted at the bottom of the README without explanation. The reader is trusted to handle both registers.

**Integrity over voice.** The `CLAUDE.md` opens with: "*A labor of love by a Reformed Baptist family. Real people will eat from these recipes — **accuracy beats speed**.*" That is the operating axiom of the entire repo.

## Style markers

- **Long-running audit documents as primary artifacts.** Eight of them, totaling several hundred KB of tracking work:

  | File | Size |
  |---|---|
  | `RECIPE_AUDIT_LOST_IDS.md` | 152 KB |
  | `CHEESE_VARIETIES_TRACKER.md` | 66 KB |
  | `RECIPE_AUDIT_TRACKER.md` | 21 KB |
  | `cheesedotcom.md` | 21 KB |
  | `IMAGE_AUDIT.md` | 17 KB |
  | `PENDING_TASKS.md` | 15 KB |
  | `CHEESE_VARIANTS.md` | 13 KB |
  | `OVERLOOKED_TIPS_AUDIT.md` | 9 KB |

  These are not stale planning docs. They are the working memory of a project that knows it will outlive any single session.

- **Decision priority is stated explicitly:** *accuracy → preservation → fidelity → readability*. In that order, not negotiable.
- **A 519-line `CLAUDE.md` was refactored to 155 lines** by extracting standards into `.claude/standards/` (CHEESE_RULES, IMAGE_RETENTION, COMPOUND_RECIPES, OCR_STANDARDS, IMAGE_WORKFLOW, RECIPE_SCHEMA). The version history of CLAUDE.md is itself recorded in CLAUDE.md.
- **Tables are the dominant rhetorical form.** Source-format tables, file-purpose tables, version-history tables. Prose is sparse.
- **The `recovery_report.txt` lives in the root** at 78 KB. The repo carries the scar of a past incident, on purpose, where the next maintainer can see it.

## Philosophy

### Careful, not clever

The repo's most distinctive document is `CAREFUL.md`, a 5 KB integrity guardrail subtitled "*This skill overrides the impulse to optimize, batch, or shortcut.*" Its central rule:

> **Be careful, not clever.**
> Careful means: verified, documented, reversible, honest.
> Clever means: fast, creative, batched, assumed.
> When in doubt, be careful.

Then twelve numbered practices, organized into "Before Modifying Any File," "During Modifications," and "After Modifications." The practices are operational: *Read it first. Never edit a file you haven't read in this session. Check for conflicts. State your assumptions before a bulk operation.* And operational again at the end: *Verify, then report. Don't say "done" until you've confirmed the result.*

This is a household idiom. The kitchen has the same rule. The recipe archive does too.

### Never invent

Rule #1 of the non-negotiables: *Do NOT invent ingredients, steps, temperatures, times, or yields.* If something is unreadable, mark it `[UNCLEAR]` with a best guess. **Guessing is clever; marking is careful.** This is so load-bearing that the orchestrator's `recipe-transcription` and `recipe-validation` skills are trained around it. Claude can transcribe; Claude cannot author.

### Real people will eat from these

This is the explicit warrant for the carefulness. *Accuracy beats speed* is not an aesthetic preference — it is a recognition that recipes are eaten, not just read. A typo'd salt measurement is not a typo. The domestic stakes are concrete.

### Permission and provenance

Every recipe has a required `attribution` and `source_note`. Sources marked "with permission" are usable; an anonymous web scrape is not. If the license is unclear, the recipe carries `confidence.overall = "low"` with a flag. The repo claims no rights to source content beyond compilation and presentation. AGPL v3 covers the compilation; the source publishers retain their terms.

### Cheese is cheese-MAKING

A repo-defining ontological choice: `category: "cheese"` is reserved for cheese-MAKING recipes. Mac and cheese, cheesecake, fondue do not qualify. This isn't pedantry — the Cheese Builder tool depends on the categorization to find recipes. The category and the tool are co-evolved, and the rule is so important it has its own extracted standard at `.claude/standards/CHEESE_RULES.md`.

### Handwritten only for `image_refs`

A second ontological choice with operational teeth: `image_refs` is reserved for **handwritten** sources. Kindle screenshots, magazine scans, typed cards leave `image_refs: []`. The rule has a one-line justification: handwriting is the only source where the image carries information the transcription cannot. Everything else is just provenance.

### Soli Deo Gloria as work ethic

The repo's faith framing is not decorative. *Excellence as worship means getting it right, not getting it fast* — the closing line of `CAREFUL.md`. This is the same theology as `ken`'s `Soli Deo Gloria`, applied locally to recipe transcription: carefulness is doxology when real people will eat the result.

## Technical anatomy

### Static site

```
index.html       ← search & filters
recipe.html      ← detail page
tips.html        ← tips index
butter-builder.html / .js
cheese-builder.html / .js (84 KB)
adulterant-companion.js
milk-substitution.js
script.js (37 KB)
styles.css (86 KB)
all/             ← per-recipe HTML pages where used
```

Pure static. `_headers`, `.htaccess`, `.nojekyll` provided. Deploy to GitHub Pages, Netlify, Vercel, or any HTTP server. Local dev is `python -m http.server 8000`.

### Image pipeline

The Claude API has a 2000 px limit. Kindle screenshots typically exceed that (1320 × 2868 px). The pipeline:

1. Originals dropped FLAT into `data/` (no subdirectories).
2. `python scripts/process_images.py` resizes to ≤2000 px into `data/processed/`.
3. `image_safeguards.py` refuses to commit oversized images and flags referenced originals without processed copies.
4. `optimize_images.py` for JPEG optimization.
5. AI reads from `data/processed/`, never raw `data/` for oversized originals.

A `processed_images.json` log and `image_manifest.json` validation status track what's been touched.

### Recipe schema (excerpt)

```json
{
  "id": "recipe-slug",
  "collection": "all",
  "collection_display": "Other Family Recipes",
  "title": "Recipe Title",
  "category": "appetizers|beverages|breads|breakfast|cheese|desserts|mains|salads|sides|soups|snacks",
  "attribution": "Source/Author",
  "source_note": "e.g., Kindle cookbook, magazine clipping",
  "ingredients": [
    {"item": "flour", "quantity": "2", "unit": "cups", "prep_note": "sifted"}
  ],
  "instructions": [{"step": 1, "text": "Preheat oven to 350°F."}],
  "confidence": {"overall": "high|medium|low"},
  "image_refs": ["filename.PNG"]   // handwritten only
}
```

Categories are an enum. Eleven values. Cheese is one of them, and means cheese-making.

### Validation hooks

`.claude/hooks/post-write-validate.sh` runs on every Edit/Write. `image-safety-check.sh` runs on image-affecting changes. Both are blocking — they refuse the commit on failure. The repo treats validation as a hardware-level protection, not a CI nicety.

### Multi-LLM integration

Mode: `recipe`. Lead: GPT (per `ken/orchestrator/repo-modes.json`). Memory scope: `/Allrecipes`. The repo invokes the orchestrator for transcription pipelines, with the strict rule that consultants never invent — they only structure what's already on the source page.

## Distinguishing marks

- **The biggest of the four recipe repos by an order of magnitude.** ~9,989 recipes vs. 2,700+ at MomsRecipes and smaller numbers at the grandmother repos.
- **Builder tools that teach as they execute.** The Cheese Builder's 84 KB of JavaScript is not a recipe lookup — it walks a cook through acidification, coagulation, cut, cook, drain, press, age. It's a curriculum embedded in a tool.
- **An adulterant companion.** This is not a thing most recipe sites have. It exists because the household values discernment about what's actually in a thing.
- **The benediction is Proverbs 31:27.** Not John 3:16, not the Lord's Prayer — the verse about household work, careful housekeeping, and not eating the bread of idleness. The repo's closing line is a frame: this archive is part of looking well to the ways of a household.
- **A 78 KB `recovery_report.txt` in the root.** The repo carries its scars in plain sight.
- **No author credit, no contributor list.** Like `ken`, the work is anonymous on purpose. Stewardship is corporate.

## Relationship to siblings

`Allrecipes` is the **reference** in a four-way relationship:

| Repo | What it preserves | Who it speaks for |
|---|---|---|
| `MomsRecipes` | MomMom Baker — heirloom recipes | a specific cook |
| `Grandmasrecipes` | Grandma Baker — Michigan to Florida | a specific cook + the converters live here |
| `Grannysrecipes` | Granny Hudson — Florida to Boston and back | a specific cook |
| `Allrecipes` | Cookbooks, magazines, the cultural canon | the kitchen at large |

The grandmother repos preserve voice. Allrecipes preserves *technique*. Together they form a household library where named heirlooms sit beside the canonical béchamel, all under the same JSON schema.

## What would be lost

If `Allrecipes` disappeared, the household would lose its reference shelf — every "how does Cook's Illustrated do this" recipe, every magazine clipping, the cheese builder, the butter builder, the adulterant companion. The grandmothers' recipes would survive in their own repos, but the cultural-canon layer underneath them would vanish. So would the long-running audit documentation that records what was lost in past refactors and how it was recovered.

## One-line summary

**`Allrecipes` is the household's reference cookbook — 9,989 recipes, four teaching tools, eight long-running audits, and a non-negotiable rule that says when in doubt, be careful, because real people are going to eat from this.**
