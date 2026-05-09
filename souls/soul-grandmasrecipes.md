# Soul of `Grandmasrecipes`

> *"She looketh well to the ways of her household, and eateth not the bread of idleness." — Proverbs 31:27*

The toolkit grandmother. Grandma Baker's recipes — Michigan to Florida — and the converters that the whole family of repos depends on.

---

## Identity

`Grandmasrecipes` is two things at once, by deliberate design:

1. **A recipe collection** — Grandma Baker's recipes from handwritten cards, newspaper clippings, magazine cuttings. Her life ran from Michigan to Florida, and the recipes carry both Northern and Southern habits.
2. **The converter and calculator host** for the entire recipe family. Five JavaScript engines — diabetic, heart-smart, milk-substitution, protein-substitution, and intelligent-scaling — live here and are loaded by the sister recipe sites.

The README puts it plainly: *"Grandma's repo doubles as the **aggregator** in the family — its calculators and substitutions can be linked into any of the others."* This is the only recipe repo that has a job beyond preserving one cook.

The collection itself is small but growing — the README lists five recipes by name in a "Current recipes" table. The repo is honest about it: **the converters are the most active area, and the recipe count is small.** Where Allrecipes preserves nine thousand recipes anonymously, this one preserves five recipes and tells you about each one's known issues.

## What it actually is

1. **A static recipe site** with **PWA support** — `sw.js` (8 KB service worker), `manifest.webmanifest`, offline-capable after first load. The only recipe repo with offline.
2. **Pagefind-indexed search** — the `_pagefind/` directory holds a pre-built search index, embedded in the static site. No server required.
3. **Five conversion engines:**

   | Module | Size | What it does |
   |---|---|---|
   | `diabetic-converter.js` | 18 KB | Substitutes high-glycemic ingredients, recalculates carbs and added sugar, refuses unsafe conversions |
   | `heart-smart-converter.js` | 23 KB | Reduces sodium and saturated fat, swaps cooking oils, preserves the cooking technique |
   | `milk-substitution.js` | 56 KB | Maps dairy milks to plant-based alternatives, accounts for fat content and sweetness |
   | `protein-substitution.js` | 16 KB | Swaps proteins (beef ↔ pork ↔ poultry ↔ plant) with cook-time corrections |
   | `scaling-intelligence.js` | 22 KB | Scales recipes by serving count, **not** by linear multiplication |

4. **A standalone calculator** at `calculator.html` (16 KB) that ties the five engines together for ad-hoc conversions outside any specific recipe.
5. **A 5-recipe corpus** at `data/recipes_master.json` with explicit known-issues callouts in the README:

   - *Ginger-Onion Lo Mein* — original clipping cut off; steps 5–7 inferred; "**If you find the original source, please update.**"
   - *Jubilie Jumbles* — original card showed "2 tsp" butter; corrected to "2 tbsp" per Carnation canonical; spelling "Jubilie" preserved.

6. **A nutrition-facts plan** at `PLAN-nutrition-facts.md` (10 KB) describing how the five converters will tie into a Nutrition Facts panel.
7. **A 174 KB `script.js`** (with minified `script.min.js`) handling the cross-repo aggregation logic.
8. **142 KB of `styles.css`** (with minified `.min.css`). The largest stylesheet in the family.

## Voice

**Honest about scope.** The README tells you up-front: "*Current status: small but growing recipe set; converter/calculator toolkit is the most active area.*" Most projects would bury that. This one leads with it.

**Inviting correction.** The known-issues section names two recipes by name and asks readers to fix them. *"If you find the original source, please update."* The voice treats the archive as a community work-in-progress, not a sealed artifact.

**Same family register.** *Soli Deo Gloria* opens. Proverbs 31:27 closes. *"A labor of love by a Reformed Baptist family. These recipes — many handwritten and irreplaceable — matter deeply. **Accuracy beats speed.**"* Identical idiom to MomsRecipes, Grannysrecipes, Allrecipes.

**Conservative engineering voice on the converters.** "*The converters are deliberately conservative: when a substitution would fundamentally change the recipe (e.g. butter in a laminated dough), they refuse and explain why.*" The same `[UNCLEAR]` discipline that governs transcription governs substitution: when in doubt, refuse and explain. Don't silently change a category or cuisine.

## Style markers

- **A "Current recipes" table** in the README that names every single recipe and rates its confidence. Five rows. Compare to Allrecipes' 9,989 recipes documented only as a count. This repo has fewer recipes, so each one earns its own line in the README.
- **A "Known issues & flags" section that names recipes by name** and explains exactly what was inferred or corrected. The repo treats the limitations as load-bearing documentation.
- **A `PLAN-nutrition-facts.md`** in the root — 10 KB of planning for an integration that hasn't shipped yet. Plans are tracked in the repo, not in private notes.
- **The CLAUDE.md was cut from ~394 lines to ~150** by extracting standards into `.claude/standards/` (OCR_STANDARDS, IMAGE_WORKFLOW, RECIPE_SCHEMA, GUARDRAILS, HUB_AGGREGATION). Same lean-hub pattern as the other recipe repos, with one extra extracted file: `HUB_AGGREGATION.md` for the cross-repo aggregation logic that lives only here.
- **CRITICAL: Image Path Structure** — a literal section heading in CLAUDE.md, with right-vs-wrong examples:

  ```
  CORRECT:   data/Grandmas-recipes - 12.jpeg
  WRONG:     data/grandma/Grandmas-recipes - 12.jpeg   (subdirectory does not exist)
  ```

  The repo has been bitten by this and writes the rule in capital letters.

- **The license file is named `license`, lowercase.** Every other recipe repo capitalizes `LICENSE`. Grandma's repo is older and predates the convention. The lowercase persists.

## Philosophy

### One repo can serve two purposes if the purposes don't fight

`Grandmasrecipes` collects Grandma Baker's recipes *and* hosts the family's converter toolkit. These could be separate repos. They aren't, because the same person maintains both, the converters were originally written for Grandma's recipes, and the JavaScript that runs Grandma's site is the JavaScript that runs every other family site's diabetic / heart-smart conversions.

The repo accepts the dual identity rather than splitting it. It's pragmatic, and the README names it openly.

### Conversion is preservation, not editing

The five converters do not change recipes. They generate **variants** — derivative views that the user can render on top of the original. Grandma's pound cake stays Grandma's pound cake; the diabetic-friendly variant is a separate output, and the original is never overwritten. This matches the family-wide rule: **never invent**, never silently mutate.

### Refuse, don't fudge

The converters' core invariant is this: when a substitution would fundamentally change the recipe (butter in a laminated dough, sugar in a Maillard reaction), they **refuse and explain why**. Refusal with explanation is the same posture as `[UNCLEAR]` in transcription. The repo's tools say "I don't know" or "this can't be safely done" rather than producing plausible junk.

### Scaling is not multiplication

`scaling-intelligence.js` is the most opinionated of the five engines. The README states the principle: *"Scales recipes by serving count, **not** by linear multiplication — it knows that doubling salt isn't doubling the dish."* This is craft knowledge encoded in 22 KB of JavaScript: bread benefits from longer fermentation, not more yeast; a stew's salt scales sublinearly with volume; a fried-rice ratio is different at 4× than at 2×.

### Preserve original spelling

Two non-negotiable rules from CLAUDE.md:

- *Spelling of original cards is preserved verbatim.*
- *Substitution converters never silently change a recipe's category or cuisine.*

When the card said "Jubilie Jumbles," the title is "Jubilie Jumbles." Possibly a typo for "Jubilee" — but it's *her* spelling, and the repo flags it without correcting it.

### Same household axiom

*"Hundreds of real people will use these recipes. **Accuracy beats speed.**"* Same line as the other recipe repos. Same priority order: **accuracy → preservation → fidelity → readability**.

## Technical anatomy

### The hub side

`Grandmasrecipes` is the canonical home of:

- **Cross-repo aggregation logic** — the `script.js` (174 KB) reads from sister repos and surfaces all four collections in one searchable view. The aggregation contract lives in `.claude/standards/HUB_AGGREGATION.md`.
- **A `FAMILY_COLLECTIONS` array** documented in the CLAUDE.md table, mapping each repo to its Pages URL and collection ID:

  | Collection | Pages site | Collection ID |
  |---|---|---|
  | Grandma Baker | jsschrstrcks1.github.io/Grandmasrecipes | `grandma-baker` |
  | MomMom Baker | jsschrstrcks1.github.io/MomsRecipes | `mommom-baker` |
  | Granny Hudson | jsschrstrcks1.github.io/Grannysrecipes | `granny-hudson` |
  | Other Recipes | jsschrstrcks1.github.io/Allrecipes | `all` |

- **The Pagefind search index** at `_pagefind/` — pre-built, deployed with the site.
- **The PWA wrapper** — `sw.js` and `manifest.webmanifest` deliver offline access.

### The collection side

```
Grandmasrecipes/
├── data/
│   ├── *.jpeg                ← FLAT (no subdirectories)
│   ├── processed/            ← ≤ 2000 px AI-friendly copies
│   ├── recipes_master.json   ← currently five recipes
│   ├── collections.json
│   └── processed_images.json
├── ebook/
│   ├── book.html
│   └── print.css
└── scripts/
    ├── validate-recipes.py
    ├── process_images.py
    └── image_safeguards.py
```

Categories are the standard 10 — `appetizers, beverages, breads, breakfast, desserts, mains, salads, sides, soups, snacks`. (No `cheese` here; cheese-making is Allrecipes' domain.)

### Multi-LLM integration

Mode: `recipe`. Lead: GPT (per `ken/orchestrator/repo-modes.json`). Memory scope: `/Grandmasrecipes`. The `milk-substitution` skill is published as a Claude Code skill that wraps `milk-substitution.js`, available at `.claude/skills/milk-substitution/`. This is the only recipe repo where a transcription engine is also exposed as a skill — because the engine has utility beyond this repo.

### License

GNU AGPL v3. Recipe text and images are family treasures; please use respectfully.

## Distinguishing marks

- **The only recipe repo that exports tooling to the others.** Five JavaScript modules and a calculator UI that any sister repo can embed.
- **The only recipe repo with PWA + Pagefind.** Offline-capable, full-text searchable, no server required.
- **The smallest by recipe count, the largest by JavaScript.** Five recipes; ~135 KB of converter logic; a 174 KB `script.js` aggregator. The repo's mass is in tooling, not content.
- **Honest about its known issues.** Two recipes with named flags in the README, with explicit asks for community correction. The README is itself a request.
- **Lowercase `license`.** A small artifact of the repo's age — it predates the family-wide capitalization convention.
- **Conservative converters.** The diabetic engine refuses sugar substitutions in butter caramels. The heart-smart engine refuses to swap olive oil for butter in a flaky pastry. Refusal with explanation is core engineering.

## Relationship to siblings

`Grandmasrecipes` is the **toolkit grandmother** in a four-repo family:

| Repo | Function | Differentiator |
|---|---|---|
| `MomsRecipes` | MomMom's collection | 2,700+ recipes |
| **`Grandmasrecipes`** | **Grandma's collection + family converters** | **PWA + Pagefind + 5 conversion engines + cross-repo aggregator** |
| `Grannysrecipes` | Granny Hudson's collection | private, anti-indexed |
| `Allrecipes` | Reference shelf | 9,989 recipes + cheese/butter builders |

`Grannysrecipes` was split out of *this* repo, the README notes — and the converters that work for Granny's site are the converters that live here. The split was for privacy posture, not for tooling.

## What would be lost

If `Grandmasrecipes` disappeared, the family would lose:

- Grandma Baker's preserved recipes (irreplaceable, since the source was handwriting).
- The diabetic, heart-smart, milk, protein, and scaling converters that the *other* recipe sites depend on. Three of those sister sites would lose a feature, not just a sibling.
- The cross-repo aggregator and Pagefind index that make the four collections searchable from one URL.
- The PWA shell that lets a cook use the site offline.
- The standalone `calculator.html` page.

This is the only recipe repo whose loss damages other recipe repos.

## One-line summary

**`Grandmasrecipes` is Grandma Baker's small but growing collection sitting on top of the family's largest engineering investment — five conservative conversion engines, a Pagefind-indexed PWA, and a cross-repo aggregator that quietly holds the rest of the family's sites together.**
