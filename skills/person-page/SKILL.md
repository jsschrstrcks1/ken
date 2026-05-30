---
name: person-page
description: "Build or rebuild person pages section-by-section using the v2 template. Prevents timeout on data-rich pages by writing incrementally with checkpoint saves between sections."
version: 1.0.0
triggers:
  - "/person-page"
  - "rebuild.*person page"
  - "write.*person page"
  - "flagship page"
---

# Person Page Builder

> Build pages section by section. Never time out. Never lose work.

## The Problem This Solves

Data-rich person pages (Captain Juan MDO, Maurice Stokes, Velma) require synthesizing 7+ source files into 200+ lines of narrative. Writing the full page in a single generation attempt times out. Three consecutive timeouts = lost work + frustrated user.

## Usage

```
/person-page <person-name> [rebuild|new|section <name>]
```

**Examples:**
```
/person-page "Captain Juan Montes de Oca" rebuild
/person-page "Velma Stokes" section story
/person-page "Anna Hilliard" new
```

## How It Works: Sectional Writing Protocol

**CRITICAL RULE: Never attempt to write a full page in one tool call.** Break every page into sections. Write each section as a separate Edit or Write call. Save between sections.

### Phase 1: Gather (READ ONLY — no writing)

1. Read the existing person page (if rebuilding)
2. Read PERSON-PAGE-TEMPLATE.md for section structure
3. Identify all source files mentioning this person:
   ```
   grep -rl "Person Name" sources/ people/
   ```
4. Read relevant sections from those source files (use offset/limit — don't read 150KB files whole)
5. Compile a **section plan** — which template sections will be populated, which skipped

**Output of Phase 1:** A numbered list of sections to write, with the key data points for each.

### Phase 2: Write Section by Section

Write the page in this order, one section per tool call:

| Step | Section | Tool | Notes |
|------|---------|------|-------|
| 1 | Header + Summary + Heritage Lines | Write | Create the file with first 3 sections |
| 2 | Family | Edit | Append family section |
| 3 | Timeline | Edit | Append timeline table |
| 4 | The Story (part 1: early life) | Edit | First half of narrative |
| 5 | The Story (part 2: later life) | Edit | Second half of narrative |
| 6 | In Their Own Words | Edit | Oral history vignettes (if available) |
| 7 | Key Artifacts | Edit | Photos, documents, records |
| 8 | Sources | Edit | Standardized citations |
| 9 | Unresolved Questions + Research Leads | Edit | Final sections |

**RULES:**
- **Never combine more than 2-3 sections in one Edit call.** The Story must be split into parts for complex people.
- **After step 1 (Write), every subsequent step uses Edit** to append to the existing file.
- **If any step feels like it might be large, split it further.** Two small writes > one timeout.
- **After step 5 (Story complete), do a git add + status check** as a checkpoint. This ensures the narrative is saved before adding apparatus sections.

### Phase 3: Checkpoint and Commit

After all sections are written:
1. `git add people/<filename>.md`
2. `git diff --staged --stat` — verify the file looks right
3. Commit with descriptive message
4. Push

If the session dies mid-page, the file exists with whatever sections were completed. The next session can pick up from the last written section.

## The Story: Split Protocol

For data-rich people, split The Story into chronological chunks:

**Captain Juan MDO (5 chunks):**
1. Origins and arrival in Tampa (birth → ~1830)
2. Fort Brooke: translator, first wife, Victoria (~1830 → ~1842)
3. Second Seminole War service (~1835 → ~1842)
4. Second wife Mary, children, land grant battles (~1845 → 1857)
5. Legacy: displacement, cultural erasure, the tragic irony

**Maurice Stokes (4 chunks):**
1. Childhood: father's death, Howard as stepfather (1929 → 1950)
2. Military + education: Korea, Alaska SIGINT, GI Bill (1950 → ~1957)
3. Engineering career + marriage to Kathryn (1955 → 1965)
4. Second marriage, wealth, death, estate (1967 → 1994)

**Velma (3 chunks):**
1. Growing up: Juanita, sisters, chores, hard times (1933 → ~1960)
2. Charlie: the tent dress, the waltz, Minnesota, Lockheed (~1960 → Charlie's death)
3. Mac, Pat, later years (after Charlie → present)

## Template Reference

See `/home/user/Family-History/PERSON-PAGE-TEMPLATE.md` for the full v2 template with section definitions, rules, and examples.

## Page Tiers

| Tier | Approach | Sections |
|------|----------|----------|
| **Stub** | Single Write call | Header + Family + Sources |
| **Developing** | 3-4 Edit calls | + Timeline + short Story + Research Leads |
| **Well-documented** | 5-7 Edit calls | + full Story + Unresolved Questions + Artifacts |
| **Oral History Rich** | 7-9 Edit calls | + In Their Own Words |
| **Flagship** | 9-12 Edit calls | All sections, Story split into 3-5 chunks |

## Anti-Timeout Heuristics

1. **If a section will exceed ~80 lines of output, split it.** 80 lines is the safe zone.
2. **If synthesizing from 3+ source files, write a brief outline first** (as a comment block or in conversation), then fill in the prose. This prevents the "gathering + writing" double-cost.
3. **Never read more than 200 lines from a source file at once.** Use offset/limit. Read what you need for the current section, not the whole file.
4. **The Story is always the largest section.** Budget 2-5 Edit calls for it on flagship pages.
5. **If you feel the generation getting long, STOP and emit what you have.** A partial section saved is better than a timeout that saves nothing.

## Verify Mode

```
/person-page verify "Maurice Dewey Stokes"
```

Queries FamilySearch, Find a Grave, and other sources to check existing page data. Presents findings for human review — never auto-commits. See PERSON-PAGE-TEMPLATE.md for details.

---

*Built after 3 consecutive timeouts on Captain Juan MDO's flagship page. The cure: never try to write a cathedral in one breath. Lay one stone at a time.*
