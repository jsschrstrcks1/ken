# Soul of `Grannysrecipes`

> *"She looketh well to the ways of her household, and eateth not the bread of idleness." — Proverbs 31:27*

The private one. Granny Hudson's recipes — Florida to Boston and back — kept inside the family.

---

## Identity

This is the recipe collection of **Granny Hudson**, whose life ran from Florida to Boston and back. Her recipes carry the marks of both — Southern habits beside New England influences. They were collected from handwritten cards, newspaper clippings, magazine cuttings, and other family treasures, and they live here as a static site, an e-book, a JSON corpus, and a Memorial section that holds tributes and stories tied to specific dishes.

The repo was split out of `Grandmasrecipes` "for better organization" — a one-line note in the README that conceals what's really a respectful separation: each grandmother gets her own house.

The defining decision is in the README's third paragraph: **"This is a private family archive."** Unlike the other recipe repos in the family, this one is intentionally hidden from search engines and AI crawlers. Privacy is not a deployment option here. It is the repo's primary commitment.

## What it actually is

1. **A static recipe site** — `index.html` (search & filters), `recipe.html` (detail), 56 KB of `styles.css`, 29 KB of `script.js`. Same shape as the other recipe repos but smaller in surface area.
2. **The recipe corpus** at `granny/recipes_master.json` — every recipe carries `"collection": "granny"`. Originals as `.jpeg` scans in `granny/`, AI-friendly resizes in `granny/processed/`.
3. **A Memorial section** at `Memorial/` — tribute pages with photos, stories, and the memories tied to specific recipes. Not just metadata; this is where a recipe earns its weight.
4. **An e-book** at `ebook/book.html` for printing or converting to EPUB/MOBI via Calibre.
5. **A privacy-enforcement layer** — `robots.txt` blocking all crawlers, `noindex, nofollow` meta tags on every HTML file, no `sitemap.xml`, a family-name gate on the front end, and a `pre-commit` git hook that refuses to commit if any of those controls weakens.
6. **An audit document** — `OVERLOOKED_TIPS_REPORT.md`, capturing small notes ("Granny always added a pinch of nutmeg") that originally lived only in family memory.

## Voice

**Tender and procedural at once.** The README tells you to set margins to "None or Minimum" for the PDF print, then a few lines later says memorial content must be treated "with the same care as the recipes themselves — preserve voice, never embellish, and never publish a memorial page without the family's explicit consent."

**Reverent without elevation.** The KJV closing — *"She looketh well to the ways of her household"* — frames the work, but the body of the README is a step-by-step guide: scan at 300 DPI, resize for AI, append to JSON, run validation. The reverence and the procedure are in the same voice. Neither overrides the other.

**Plainly protective.** The privacy section is more direct than anywhere else in the family: "*If you fork this repository, please maintain the privacy protections. These are real family recipes shared among relatives — not intended for public discovery.*" The voice asks rather than commands, but the asking is unambiguous.

**The same Proverbs 31 benediction** as Allrecipes, MomsRecipes, and Grandmasrecipes. The four recipe repos share a closing antiphon. They are siblings under one verse.

## Style markers

- **The privacy controls are listed in the README's table of contents** as their own section — `Privacy & anti-indexing` — and again under "If you fork this repository." The repo names its own boundary three times so no one misses it.
- **The pre-commit hook is one-line documented:** `git config core.hooksPath .githooks`. After that, every commit verifies the privacy posture. The repo treats privacy as a hardware-level invariant, not a policy.
- **The Memorial section gets its own subsection in the README**, but the contents are not described — just the rule: *"Treat memorial content with the same care as the recipes themselves."*
- **The CLAUDE.md was cut from ~609 lines to ~145** by extracting standards into `.claude/standards/` (OCR, IMAGE_WORKFLOW, FRAGMENT_HANDLING, RECIPE_SCHEMA, CONVERSIONS, NUTRITION_QUESTIONS, DUPLICATE_HANDLING, BLOAT_MANAGEMENT). The version history records the cut.
- **The "If you fork" paragraph is unusual.** Most repos don't address forkers as people with responsibilities. This one does.

## Philosophy

### Some things should not be searchable

This is the load-bearing decision. The household has a public photography site (`flickersofmajesty`), a public cruise blog (`InTheWake`), a sermon archive (`Romans`), four public recipe repos — and one private one. That asymmetry is intentional. Granny Hudson's recipes are shared with relatives. They are not for SEO, not for AI training, not for a stranger's Pinterest board.

The privacy is not paranoia. It is hospitality with a door. The family eats from this archive. Strangers don't.

### Privacy as a tested invariant

Three independent controls enforce the posture:

1. `robots.txt` — declarative refusal at the protocol level.
2. `<meta name="robots" content="noindex, nofollow">` on every HTML file — declarative refusal at the page level.
3. No `sitemap.xml` — refusal by absence.

Plus a fourth: a `pre-commit` hook (`scripts/check-noindex.sh`) that *re-runs all three checks* before every commit. If a developer accidentally writes a page without the noindex tag, the commit fails. If someone adds a sitemap, the commit fails. **The repo treats forgetting privacy the same way it treats invalid JSON — as a build failure.**

The README explicitly forbids `--no-verify`: "*if it fails, **fix the underlying file** rather than bypassing the hook.*"

### Memorial content has a stricter rule than recipes

The CLAUDE.md draws a line that nothing else in the family draws:

> Recipe content **may** be shared with AI models for transcription help.
> Memorial content (people's names, photos, stories) **must not** be sent to external models. Process it locally.

This is a two-tier privacy model, not a flat one. Recipes are shareable with AI for transcription help. Stories about people are not. Granny Hudson's name and the names of relatives in the Memorial section never leave the local machine. The orchestrator's `consult` and `orchestrate` skills are constrained accordingly.

### Same axiom as the other recipe repos

*"Hundreds of real people will use these recipes. **Accuracy beats speed.**"* The CLAUDE.md repeats the family's house rule: never invent, mark unclear text `[UNCLEAR]`, mark guesses `[GUESS]` with confidence levels. *Decision priority: accuracy → preservation → fidelity → readability.*

### Preservation, not improvement

Rule 3 of the non-negotiables: *Preserve original intent; normalize only spelling and formatting.* If Granny Hudson called something "MawMaw's Pecan Pie," the title stays "MawMaw's Pecan Pie." Rule 4: *Keep family names and attributions* — *"Aunt Linda's Pound Cake"* stays *"Aunt Linda's Pound Cake."* The names are the recipe.

## Technical anatomy

### Layout

```
Grannysrecipes/
├── index.html / recipe.html
├── styles.css (56 KB) / script.js (29 KB)
├── robots.txt           ← blocks ALL
├── .githooks/pre-commit ← privacy enforcement
├── granny/
│   ├── *.jpeg           ← original scans
│   ├── processed/       ← ≤ 2000 px AI-friendly copies
│   ├── recipes_master.json
│   ├── collections.json
│   ├── processed_images.json
│   └── image_manifest.json
├── Memorial/
│   └── Grandma/         ← (name preserved)
├── scripts/
│   ├── validate-recipes.py
│   ├── process_images.py
│   ├── image_safeguards.py
│   ├── optimize_images.py
│   └── check-noindex.sh
└── ebook/{book.html, print.css}
```

Static. Pure HTML+CSS+JS. AGPL v3 on the source code; recipe text, photos, and memorial content are family-private and explicitly *not* licensed for commercial reuse or republication.

### Privacy enforcement chain

```
Author commits → .githooks/pre-commit fires → check-noindex.sh runs:
  ├─ robots.txt blocks all crawlers? ✓
  ├─ no sitemap.xml exists? ✓
  └─ every HTML file has <meta robots noindex>? ✓
If any fail → commit refused.
```

### Recipe schema

Same shape as siblings, with `"collection": "granny"` mandatory:

```json
{
  "id": "recipe-slug",
  "collection": "granny",
  "title": "Aunt Linda's Pound Cake",
  "attribution": "Granny Hudson / Aunt Linda",
  "source_note": "Handwritten card, undated",
  "category": "desserts",
  "ingredients": [{"item": "...", "quantity": "...", "unit": "...", "prep_note": "..."}],
  "instructions": [{"step": 1, "text": "..."}],
  "confidence": {"overall": "high|medium|low", "flags": []},
  "image_refs": ["granny-XX.jpeg"]
}
```

Categories: 10 values (no `cheese` — Granny didn't make cheese). `image_refs` policy is permissive here (handwritten dominates the source mix), unlike Allrecipes which restricts `image_refs` to handwritten only.

### Multi-LLM integration

Mode: `recipe`. Lead: GPT (per `ken/orchestrator/repo-modes.json`). Memory scope: `/Grannysrecipes`. The orchestrator is invoked for transcription with the same family-wide rules: never invent, flag inferences, mark `[UNCLEAR]`. With one repo-specific addition: **memorial content never leaves the local machine.**

## Distinguishing marks

- **The only private repo in the family.** Public sermons, public cruises, public photography, three public recipe sites — and one closed door.
- **Florida → Boston → back.** The geographic memory is part of the framing in the README's first paragraph. It's not just biography; it explains why a recipe might use cornmeal next to brown bread.
- **The Memorial section.** No other recipe repo has one. Recipes here come with stories attached, and the stories have their own privacy posture (more strict than the recipes).
- **A `pre-commit` hook that enforces privacy.** This is a small, deeply meaningful piece of engineering — a refusal compiled into the build process.
- **`Memorial/Grandma/` exists inside `Grannysrecipes`.** A folder named `Grandma` lives inside a folder named `Granny`. The family has multiple grandmothers, and they exist in each other's archives. The repo doesn't draw hard ontological walls between people who lived alongside each other.
- **A "no `--no-verify`" rule, written down.** "*Fix the underlying file rather than bypassing the hook.*" This is the same posture as `ken`: refuse to bypass safety checks; address the underlying issue.

## Relationship to siblings

`Grannysrecipes` is the **inward-facing** corner of the recipe quartet:

| Repo | Audience | Privacy | Voice |
|---|---|---|---|
| `MomsRecipes` | family + friends | public | MomMom Baker — heirloom |
| `Grandmasrecipes` | family + curious | public, hosts converters | Grandma Baker — Michigan to Florida |
| `Grannysrecipes` | **family only** | **private + enforced** | Granny Hudson — Florida to Boston and back |
| `Allrecipes` | anyone | public | reference shelf |

It was split out of Grandmasrecipes once the privacy posture diverged. The split is acknowledged in the README and is the right call: a public repo and a private repo in the same git history is a leak waiting to happen.

## What would be lost

If `Grannysrecipes` disappeared, the family would lose the only recipe collection that holds *both* recipes and tributes — the only one where a pound-cake card sits next to a memorial page about the person who made it. The other recipe repos preserve technique. This one preserves people, and the preservation is private on purpose.

## One-line summary

**`Grannysrecipes` is the family's closed cookbook — Granny Hudson's recipes from Florida and Boston, alongside the people who made them, kept private by triple-locked anti-indexing and a pre-commit hook that refuses to forget.**
