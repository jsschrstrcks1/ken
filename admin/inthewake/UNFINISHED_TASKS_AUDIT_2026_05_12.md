# Unfinished Tasks Audit — 2026-05-12

**Scope:** `jsschrstrcks1/ken` + `jsschrstrcks1/Romans` + `jsschrstrcks1/open-claw-stuff`. The canonical `admin/UNFINISHED_TASKS.md` / `IN_PROGRESS_TASKS.md` / `COMPLETED_TASKS.md` live in the separate `jsschrstrcks1/InTheWake` repo, which is not in the audit scope. This audit reads what's available in `ken/admin/inthewake/` (admin tooling and audit docs).

**Audit branch:** `claude/audit-unfinished-tasks-pXfBb` (matched across all three repos).

**Method:** Read CLAUDE.md/SKILLS.md/settings/skill-rules/`.claude/**` in each repo, then collected status from every dated plan, audit, status, tracker, HANDOFF, and progress file. No inthewake live site repo was reached.

---

## Top of the queue (ordered by blast radius × readiness)

1. **Manatee Creek migration K1–K5** — `migration.gs` v2 still has not been run against the destination sheet (`1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`). HANDOFF dated 2026-03-29 still live at `.claude/skills/google-sheets-migration/HANDOFF.md`. Cognitive memory `--domain sheep` is empty — every durable decision from that thread will be re-learned from commits next session. Owner action required for K2; K4 (memory encoding) can run immediately.
2. **InTheWake cross-fleet dining hero** (`SHIP_AUDIT_FINDINGS.md`, 2026-04-06) — **291 of 295 ship pages** use `/assets/img/Cordelia_Empress_Food_Court.webp` as the dining hero. Wrong cruise line. High-visibility credibility hit, especially on luxury lines (Silversea, Regent, Seabourn, Cunard). Single-pass image swap fixes most of it; per-line replacements need actual imagery.
3. **InTheWake Tier-3 port validation** (`PORT_VALIDATION_STATUS.md`, 2026-04-09) — ~45 ports not yet started; fleet-wide blocker `recent_articles_validation_failed` affects every port including the gold standard cozumel (needs fleet-wide deployment, not per-port). Baseline batch run still "Pending" after the 2026-04-09 validator consolidation.
4. **Romans raw-draft verification flags** — `.claude/unfinished-work-tracker.md` (March 16, 2026) lists 12 raw drafts with ⚠️ flags and 46+ sermon-map entries with verification flags. Most "quick wins" (Section IX of that tracker) are done; remaining items are pastoral-judgement decisions.
5. **Romans People Group repair pass** — ~448 of ~517 sermons missing the People Group of the Week segment. Medium priority, resolved opportunistically during repair passes.
6. **ken P1#9 Continuous Learning** — Slice 0 (doctrine + 9 invariants + CI gate) and Slice 0.5 (mutation defense scaffolding, 5 helpers + 24 meta-tests) shipped to `claude/audit-unfinished-tasks-pXfBb` per recent commits. Slices 1–7.5 remain.
7. **ken `keeper` design** — `keeper-plan.md` says "design frozen post-orchestra. No code yet." Stage-1 MVP (5 commands: join, beat, complete, recover, help+new-id) not started.

---

## ken — Hub / Orchestrator Host

### Branch state

```
claude/audit-unfinished-tasks-pXfBb  (current, 5+ commits ahead of merge of #49)
last: 8436256 Merge pull request #49 from jsschrstrcks1/claude/document-repo-souls-rb8LH
ahead: P1#9 plan v5 → v4 → v3 → v2 → Slice 0 → Slice 0.5
working tree: clean
```

### Manatee Creek migration (HANDOFF still live)

Source: `.claude/skills/google-sheets-migration/HANDOFF.md` (2026-03-29) + `MANATEE_CREEK_REDESIGN_PLAN.md`.

| Phase | What | Status |
|---|---|---|
| K1 | Pre-flight: verify dest 26 tabs, source breed coverage, run against copy first | Not started |
| K2 | User pastes `migration.gs` v2, runs `migrateAll()` | Not started |
| K3 | Wire QC consults (GPT math check, Perplexity NSIP lookup, You.com public references) into `qc.sh`; output to `qc_results/YYYY-MM-DD_<model>.md` | Not started |
| K4 | Encode 7 durable decisions to cognitive memory `--domain sheep` (selection hierarchy, Kelsier, St Croix/BBB lesson, Dorper lesson, pipeline v3, tag convention, drought rule) | **Independent of K1–K3; can run today** |
| K5 | Delete `HANDOFF.md` once K1–K3 complete | Pending K1–K3 |

### P1#9 Continuous Learning (in flight on this branch)

Source: `orchestrator/CONTINUOUS_LEARNING_PLAN.md` v5 (Section 3 — "The nine slices").

| Slice | Title | Status |
|---|---|---|
| 0 | Doctrine + 9 invariants + CI gate | ✅ shipped (commit 1928f01) |
| 0.5 | Mutation defense (5 helpers + 24 meta-tests) | ✅ shipped (commit 1312c6f) |
| 1 | Kill-switch | Pending |
| 2 | Pull-based session extraction (no hooks) | Pending |
| 3A | Observation log infrastructure | Pending |
| 3B | Observation extraction | Pending |
| 3C | Log integrity | Pending |
| 4 | Confidence-promotion rules (not instinct-promotion) | Pending |
| 5 | Cross-session usage tracking | Pending |
| 6 | Always-on capture (ECC-shaped, default-on in single-operator profile) | Pending |
| 7 | Session-end auto-extract (v5) | Pending |
| 7.5 | Consensus auto-promotion eligibility (v5, NEW) | Pending |

Companion: `CONTINUOUS_LEARNING_DOCTRINE.md` (doctrine), `CONTINUOUS_LEARNING_REVIEWS.md` (review trail).

### `keeper` session-continuity tool

Source: `keeper-plan.md`.

- **Status field in plan:** "design frozen post-orchestra. No code yet."
- **9 review rounds applied:** 5-model chain + mclaude spike + CONTINUITY spike + memory-tool spike + orchestra triad
- **22 concepts lifted with attribution** (10 from mclaude, 6 from CONTINUITY, 3 from memory-tool spike, 3 from orchestra)
- **Stage 1 MVP scoped:** 5 commands (`join`, `beat`, `complete`, `recover`, `help`/`new-id`) — ~2 hours of implementation
- **Acceptance test defined** but no implementation
- **Open questions deferred:** repo name (lean `keeper`), migration of `.claude/state/session-pulse.json` → `families/default/`, SessionStart hook integration

### Skills audit (2026-03-25) — 8 priority action items

Source: `skills-audit.md`. Affects ken + all 9 jsschrstrcks1 repos.

| Priority | Action | Status |
|---|---|---|
| P0 | Deploy `cognitive-memory` to ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes | Pending (5 repos) |
| P0 | Add hooks to MomsRecipes (post-write-validate + image-safety-check) | Pending |
| P0 | Add hooks to Allrecipes (post-write-validate + image-safety-check) | Pending |
| P1 | Deploy `careful-not-clever` to Grandmasrecipes, Grannysrecipes | Pending |
| P1 | Create CLAUDE.md for InTheWake | Pending (live repo, not in audit scope) |
| P1 | Deploy `cognitive-memory` + `skill-developer` to ken | Pending |
| P2 | Audit InTheWake `Humanization` vs `like-a-human` equivalence | Pending |
| P2 | Consider relocating `skill-creator`/`skill-developer` from flickersofmajesty to ken | Pending |
| P2 | Deploy `careful-not-clever` to flickersofmajesty | Pending |
| P3 | Evaluate recipe repos for `like-a-human` (website copy) | Pending |

### New skills proposal (2026-03-25) — 10 new skills, 8 redeployments

Source: `new-skills-proposal.md`. 18 total action items.

**New skills (P1–P3):**
- `seo-schema-audit` (P1) → InTheWake + flickersofmajesty + 4 recipe repos
- `link-integrity` (P1) → InTheWake + flickersofmajesty
- `ebook-builder` (P2) → 3 recipe repos
- `nutrition-estimator` (P2) → 4 recipe repos
- `breeding-advisor` (P2) → manateecreeksheep
- `accessibility-audit` (P2) → InTheWake + flickersofmajesty
- `port-content-builder` (P2) → InTheWake
- `sermon-cross-reference` (P3) → Romans (**already published** in `Romans/.claude/skills/` — verify)
- `collection-sync` (P3) → Allrecipes
- `content-freshness` (P3) → InTheWake + flickersofmajesty

### tz / sync-clock (boot-time clock sync for Devuan)

Source: `plan.md`. Mature work, no unfinished tasks documented. Hardening iterations applied. No open items in the plan file.

---

## ken/admin/inthewake/ — InTheWake admin tooling (mirror of live-site work-in-progress)

Live site (`jsschrstrcks1/InTheWake`) is not in audit scope, so these are dev-side artifacts only. The canonical `admin/UNFINISHED_TASKS.md` lives in the InTheWake repo, not here.

### Most recent material (sorted by document date)

| Date | File | Subject |
|---|---|---|
| 2026-04-09 | `PORT_VALIDATION_STATUS.md` | Validator consolidation + 6 ports repaired |
| 2026-04-06 | `SHIP_AUDIT_FINDINGS.md` | Per-ship line-by-line audit (Silversea read first; cross-fleet finding) |
| 2026-04-06 | `FLEET_QUALITY_PLAN.md` | 6-phase fleet quality program |
| 2026-03-27 | `VENUE_RESEARCH_REPORT_2026_03_27.md` | Multi-LLM venue research pilot (19 venues) |
| 2026-03-08 | `plans/30-second-promise-audit-fixes.md` | 7 PARTIAL pages → PASS plan |
| 2026-03-04 | `VENUE_PAGE_AUDIT_2026_03_04.md` | Venue audit |
| 2026-02-21 | `DEPLOYMENT_AUDIT_2026_02_21.md` | Deployment audit |
| 2026-02-14 | `PROJECT_STATE_2026_02_14.md` | Comprehensive project state (most reliable backbone, 11 weeks stale) |
| 2025-11-18 | `ARTICLE_REVISION_STATUS.md` | Cruising After Loss article — content done, technical 0% |
| 2025-12-28 | `SHIP_VALIDATION_COMPLETION_GUIDE.md` | 6/9 historic ships remaining |
| 2025-11-16 | `SHIP_STATUS_SUMMARY.md` | Wiki Commons images for 19 ships |

### Cross-fleet ship issues (`SHIP_AUDIT_FINDINGS.md`, 2026-04-06)

- **Wrong dining hero image on 291 of 295 ship pages** — `/assets/img/Cordelia_Empress_Food_Court.webp` (Cordelia Cruises = budget Indian line) used as dining hero on Silversea/Regent/Seabourn/Cunard. Per-line replacements needed; quick win = bulk script swapping to a neutral placeholder while imagery is sourced.
- **Per-page issues already documented for Silver Nova, Silver Cloud, Silver Dawn** (audit in progress). Common patterns across the Silversea read:
  - GT mismatch between meta/quick-answer/specs vs fact-block/Key Facts/stats JSON
  - Duplicate Deck Plans sections
  - No `page-grid` / `col-1` (flat layout — uses `<main class="wrap">`)
  - Missing `no-js` class on `<html>`
  - Swiper @10 CSS / @11 JS version mismatch
  - Static copyright "2025"
  - Video loader no retry
  - Zero `<noscript>` fallbacks
  - All 5 FAQ answers boilerplate ("Specialty restaurants vary by ship.")
  - Content text wrong for luxury line ("to suit different travel styles and budgets")
  - "Dining placeholder / Logbook placeholder / Entertainment placeholder"
  - Planning Resources orphaned between `</aside>` and `</main>`
  - No `related:` field in ai-breadcrumbs

### Historic ship validation (`SHIP_VALIDATION_COMPLETION_GUIDE.md`, 2025-12-28)

ITW-SHIP-003 v1.0 — **3 of 9 ships passing** (Monarch, Nordic Empress, Majesty). 6 remain, each ~30–45 min:

| Ship | Slug | Logbook stories | Stories needed |
|---|---|:--:|:--:|
| Sovereign of the Seas (1988–2008) | sovereign-of-the-seas | 2 | +2 |
| Viking Serenade (1982–1998) | viking-serenade | 1 | +3 |
| Legend of the Seas (1995-built, 1995–2017) | legend-of-the-seas-1995-built | 1 | +3 |
| Sun Viking (1972–1998) | sun-viking | 2 | +2 |
| Nordic Prince (1971–1995) | nordic-prince | 2 | +2 |
| Song of America (1982–1999) | song-of-america | 2 | +2 |

Standard fix set per ship: `status: Retired Ship` in ai-breadcrumbs, year-range in `<title>` and `<h1>`, `rewind:false` on every `new Swiper`, "Is X still in service?" FAQ, JSON-LD FAQPage sync, logbook stories to reach minimum 4. Total: ~3–4.5 hours.

### "Cruising After Loss" article (`ARTICLE_REVISION_STATUS.md`, 2025-11-18)

- **Tier 1 content:** 100% complete (FAQ, fit-guidance, H1 dek, cross-links, ship-size section — 5 files, ~3,500 words drafted)
- **Tier 1 technical:** 0% — HTML conversion (2–3 hr), meta tags (30 min), article fragment for rail (15 min). **Total to publication: 3–4 hours.**
- **Tier 2 optional:** anticipatory grief section (~1–2 hr) — addresses 3 logbook stories ("Grandpa's Last Alaska," "Grandmother's Last Gift," etc.) currently unaddressed

### Port validation (`PORT_VALIDATION_STATUS.md`, 2026-04-09)

- **Baseline batch run:** Pending — validator consolidated 2026-04-09, run `node scripts/batch-validate.js` for fresh numbers
- **Tier 1 (high-traffic):** 15/15 repaired, range 32–88
- **Tier 2 (medium):** 16/19 repaired; 3 skipped pending logbook structural work (goa, halifax, panama-canal)
- **Tier 3 (lower):** ~45 ports not yet started — see `admin/UNFINISHED_TASKS.md` in the live repo for the list
- **Stub pages — P0 from issue #1384:** beijing, falmouth-jamaica, kyoto — redirect pages, delete or complete
- **Fleet-wide blocker:** `recent_articles_validation_failed` — all ports lack `#recent-rail-nav-top`, `#recent-rail-nav-bottom`, and article loader script. Fleet deployment, not per-port fix
- **Weather noscript:** 5 of 6 current-session ports need Yellow Lane content build (abu-dhabi blocker remaining)
- **Fleet-wide gaps from #1384 audit:**
  - `id="notices"`: 307 of 387 ports missing (79%)
  - `disclaimer-volatile-data`: ~287 missing (74%)
  - `id="credits"`: ~250+ missing (~65%)
  - `id="practical"`: ~250+ missing (~65%)

### Venue research (`VENUE_RESEARCH_REPORT_2026_03_27.md`)

- **Pilot batch:** 19 venues, ~$0.30 total API cost
- **Model scorecard:** Gemini 84% / 100% coverage; GPT 64% / 74% with 5 dangerous "free vs paid" hallucinations; Grok 0% (refused everything)
- **Remaining:** ~160 venues across NCL (73), Virgin (45), MSC (45), Carnival (20), RCL (140+ marked "Varies")
- **Recommendation:** Gemini-primary, web-verify any `MEDIUM/LOW` confidence; drop Grok for pricing entirely; GPT for non-price fields only

### 30-second-promise audit (`plans/30-second-promise-audit-fixes.md`, 2026-03-08)

7 PARTIAL pages → PASS plan, execution status unclear from local docs:

| # | Page | Phase | Risk |
|--:|---|---|---|
| 1 | `articles.html` | Add H1 + improve fit-guidance + page-specific FAQ + CTA | Low |
| 2 | `restaurants.html` | Add full ICP block + CTA + `<noscript>` fallback | Low |
| 3 | `disability-at-sea.html` | Add full ICP block + prominent CTA + FAQ + related links + 2025→2026 copyright | Medium (pastoral content) |
| 4 | `ports.html` | Insert main-column ICP, keep sidebar; H1 scope decision flagged | Low |
| 5 | `ships.html` | Same as ports; H1 scope decision flagged | Low |
| 6 | `solo.html` | Add ICP + trim 4-paragraph intro to 2 (preserve pastoral voice) | Medium |
| 7 | `travel.html` | Fix title/H1 mismatch + ICP block + TOC for 20 questions + slugified `id`s on each Q | Medium |

### Quiz work (design only, not executed)

- **`quiz-bugfix-plan.md`** — 3 bugs: NCL link dead (option A: make cards non-clickable); iPhone scroll on cruise-line dropdown (CSS `max-height: 60vh` + iOS smooth scroll); browser back restarts quiz (history.pushState per question + popstate listener). Plus multi-select cruise lines feature (deferred).
- **`quiz-regional-plan.md`** — dress-code question (4 options, scoring weights per line) + regional availability filter/penalty. Design only.

### Ship Tracker tool (`PORT_TRACKER_ROADMAP.md`)

Planned successor to Port Logbook. Many `[ ]` checkboxes — none executed:
- Interactive checklist of 27–28 Royal Caribbean ships
- Ship-class grouping (Oasis, Quantum, Freedom, Voyager, Vision, Radiance)
- Statistics dashboard (Total ships sailed, % of fleet, largest, total guest capacity, bingos)
- Achievement bingo cards
- Filters (class, year, home port, search by name, sort by size/capacity/year)
- Port Logbook integration ("show ports visited by ships I've sailed")

### Ship imagery (`SHIP_STATUS_SUMMARY.md`, 2025-11-16)

- 11 ships complete with FOM images, 7 future TBN (no photos available), 8 user-uploaded
- **19 Wiki Commons categories documented** — need user to download 3–4 each, convert via `python3 convert_to_webp.py`, attribute, integrate
- 2–5 ships still researching (Star of the Seas duplicate question, Nordic Prince)

### Fleet quality plan (`FLEET_QUALITY_PLAN.md`, 2026-04-06)

6 phases listed but execution status not in this file:
1. Validator — generalize RCL-biased checks; add Carnival/NCL/MSC/Explora/Celebrity/Regent/Princess/Cunard line-specific checks; cross-line universal checks
2. Data layer fixes — venues-v2.json refresh (64+ days stale, 12% price coverage), logbook JSON audit, stats JSON population, fleet listing pages
3. Template generator — identify, fix at source, regenerate affected pages
4. Regression prevention — pre-commit hook, fleet-wide validation report command, CI integration
5. Investigate skill update — line detection, per-line reference pages (MSC TBD), updated merge rules, validator reference
6. Close GitHub issues — fixed (close with refs), need more work, Carnival/NCL untouched

### Other inthewake docs reviewed (no new open items beyond above)

`MAINTENANCE_TASKS.md` (calendars and commands), `MAINTENANCE_TASKS_IDENTIFIED.md`, `PROJECT_STATE_2026_02_14.md` (backbone), `SESSION_LOG_2026_02_14.md`, `PHASE_3_GENERIC_REVIEW_ANALYSIS_2026_02_14.md`, `PLAN_RCL_FLEET_100_PERCENT_2026_02_14.md`, `PLAN_SHIP_PAGE_REVIEW_2026_02_14.md`, `SHIP_VALIDATION_AUDIT_2026_02_14.md`, `SHIP_VALIDATION_FIX_PROGRESS_2026_02_14.md`, `SHIP_VALIDATION_PROGRESS.md`, `STANDARDS_VERIFICATION_REPORT.md`, `STATEROOM-CHECK-EMBED-SNIPPET.md`, `TEMPLATE_IMPROVEMENTS.md`, `VANILLA-STORIES.md`, `VENUE_AUDIT_REPORT_2026_01_31.md`, `VENUE_PAGE_AUDIT_2026_03_04.md`, `EXTRACTION_PROGRESS.md`, `FRAGMENT_INVENTORY.md`, `LOGBOOK_AUDIT_2026-02-05.md`, `MSC_REPAIR_HANDOFF.md`, `NOSCRIPT_REPAIR_GUIDE.md`, `ORPHANED_IMAGES_CATALOG.md`, `ORPHAN_FILES_REPORT.md`, `PERFORMANCE_OPTIMIZATIONS_COMPLETED.md`, `POI_LAND_VALIDATION_PLAN.md`, `PORT_TRACKER_ROADMAP.md`, `REMAINING_FILES_ANALYSIS.md`, `SHIP_IMAGES_WIKIMEDIA_COMMONS.md`, `SHIP_IMAGE_AUDIT.md`, `SUGGESTED_ARTICLE_*` (5 files — sources for Cruising After Loss above), `TASK_7_COMPLETE.md`, `UNIQUE_FILES.txt`/`UNIQUE_FILES_LIST.md`, `CACHE_HEADERS_README.md`, `BULK_UPDATE_GUIDE.md`, `CLAUDE_WORKFLOW_INTEGRATION.md`, `COMPETITOR_*` (3 files), `CONFLICT_RESOLUTIONS.md`, `CTA-STYLE-GUIDE.md`, `DISCARDED_ITEMS_EVALUATION.md`, `DUPLICATE_ANALYSIS.md`, `EMOTIONAL_HOOK_TEST_PLAN.md`, `FIVE_ARTICLE_CATEGORIES.md`, `FOM_MERGE_PLAN.md`, `FOM_STANDARDS_ALIGNMENT.md`, `GRIEF_STORIES_LOGBOOK_INVENTORY.md`, `IMAGE_ATTRIBUTION_TRACKING.md`, `IMAGE_SOURCING_WORKFLOW.md`, `INTELLIGENT_BREADCRUMBS_README.md`, `NEW_RULES_EXTRACTION.md`, `PR_DESCRIPTION.md`, `QUICK_START_BREADCRUMBS.md`, `QUIZ_EXPANSION_GUIDE.md`, `RCL_FLEET_VENUE_RAW.md`, `SUGGESTED_ARTICLE_H1_DEK.md`, `VANILLA-STORIES.md`, plans subdir, reports subdir.

---

## Romans — Sermon Repository

### Branch state

```
claude/audit-unfinished-tasks-pXfBb  (current)
last: 8f87221 Merge PR #281 (claude/document-repo-souls-rb8LH)
ahead: sanitizer v1.2.0 audit (pin actions/checkout), Mother's Day, three-generation story
working tree: clean
```

### Primary source: `.claude/unfinished-work-tracker.md` (March 16, 2026)

**Summary table from tracker:**

| Category | Count |
|---|:--:|
| Unprocessed sermons in `memory2.md` | **0** (all 9 extracted) |
| Blocked sermons (source text missing) | 1 (Psalm 106; A Godly Home resolved) |
| Incomplete/truncated sermon manuscripts | 3 |
| Raw drafts needing polish and verification | 12 |
| Study papers incomplete | 2 |
| Book revision material not yet integrated | 1 |
| Sermon-map entries with verification flags (⚠️) | 46+ files |
| **Total distinct unfinished items** | **~67** |

### Incomplete manuscripts (truncated)

| File | Issue |
|---|---|
| `sermons/topical/Sermon - Thankfulness.md` | Cuts off mid-narrative at "Things kept deteriorating." No Scripture, no resolution. Need remainder from preacher. |
| `sermons/topical/Sermon - Sola Christus 2024.md` | Marked "INCOMPLETE DRAFT." Three roles (Prophet/Priest/King) never expounded. Scripture reference blank. Decide: complete or mark 2020 version authoritative. |
| `theology/Rapture - Study Paper (incomplete draft).md` | Introduction only. All Scripture analysis and position comparisons to come. |

### Raw drafts with verification flags (12 files)

Most have been substantially resolved through March 2026; remaining flags noted inline in the tracker. Highest-flag-count files (pre-resolution counts):

- `Philippians 4 (raw draft).md` — 16 flags → 11 resolved, 4 ⚠️ remain (Samuel Sey quote, Richard Baxter passage, Mo-Jer-Hai, pew Bible page)
- `Psalm 2 (raw draft).md` — 11 flags → all resolved; 2 dated-data ⚠️ remain ("53 countries", "Russia in Revelation")
- `Psalm 119 161-168 (raw draft).md` — 10 flags → all resolved; Florida stats need primary source before publication
- `Psalm 8 - Hebrews 2 (raw draft).md` — 4 flags → resolved; 3 ⚠️ remain (Platt cab driver, Edwards quote, MacArthur paraphrase)
- `Psalm 68 Part 2 (raw draft).md` — 7 flags → resolved; 1 standing (Elijah timeline phrasing)
- `1 Thess 5 - Rejoice Always (raw draft).md` — 7 flags → all resolved
- `Romans 1 - Psalm 22 (Prophecy raw draft).md` — 8 flags → resolved; Psalm 22 cross-reference table needs one correction
- `Romans 7.md` — 4 flags → 2 resolved; ⚠️ Tesla story disputed, "3 in 5 dieters" unverified
- `Romans 3 - antinomianism draft.md` — 3 flags → 2 resolved; ⚠️ John Brown quote in Pending Verification
- `Proverbs 13 (raw draft).md` — all resolved; ⬜ pew Bible page (pastor's task)
- `Deuteronomy 8 - Count Your Blessings (repaired draft).md` (added 2026-03-16 from main merge) — 3 pastoral flags: Oatman/Johnson hymn story may be embellished, Edwards "sinners in hands" wording, Col 3:6 application strained
- `Psalm 42 - As the Deer Pants.md` (added 2026-03-16 from main merge) — 2 flags: unnamed "PhD scholar" claim, "As the Deer" chorus attribution

### Blocked

| Sermon | Text | Issue |
|---|---|---|
| At the Altar of Our Convenience | Psalm 106 | No .docx or .md source in repo. Cataloged from earlier info dump. Source text must be re-provided. |

### Study papers / book project

| Item | File | Status |
|---|---|---|
| 2 Cor 5:15 Calvinism Rebuttal | `teaching/notes/Notes - 2 Corinthians 5-15 Rebuttal (Calvinism Objection).md` | First argument developed; additional arguments not written |
| Romans 6b boulder rewrite | `sermons/nt/romans/Romans_6b_boulder_rewrite.md` | ~10-line outline only. Companion `Romans_6b_with_boulder.md` more developed. Decide: complete or abandon |
| Missions bibliography | `teaching/notes/Notes - Missions Bibliography (25 Books for Local Church).md` | 5 verification flags on book descriptions |
| Empire and Suppression notes | `teaching/notes/Notes - Empire and Suppression (Romans 1 Book Revision).md` | Raw material for Romans 1 book revision; not integrated |
| Book title decision | — | Three options open: *The Night Is Far Gone*, *Waking Up*, *From Midnight to Morning* |
| Chapter polishing for print | All 16 chapters | Sermons exist; none revised from preached to read format |
| Inter-chapter transitions | — | None written |

### Sermon-map verification flags (46+ entries)

Resolution work in progress. Notable in-flight:

- `theology/Study - Joseph as a Type of Christ.md` — Gen 37:28 ESV ✓; Heb 7:26 ESV ✓; Phil 2:9 "new name" heading flagged inaccurate; **all quotes KJV — convert to ESV before preaching; source/attribution unknown**
- `Sermon - Faithful and God-Fearing.md` — major errors corrected; standing: Gospel presentation not developed; Pascal's Wager not developed; Dr. Alvin Reid quote unverified; Great Wall bribery number unverifiable
- `Sermon - Sola Scriptura 2021.md` — Integrity Log appended; Luther Quotes 1–2 verified; 3–4 editions identified but verbatim unconfirmed; **Trevor Noah attribution lead: Pastor Trevor Noah at City Centre Church (Whalley Presbyterian), Surrey BC; confirm 604-581-4833 / connect@citycentrechurch.org**

### Sermon-Infrastructure Plan (`.claude/sermon-infrastructure-plan.md`)

17 deliverables planned. Maps already in place (quote-map.md, illustration-map.md, etc. — per `.claude/` listing). Execution status of individual deliverables not tracked in audit-window files; cross-check needed against the plan's checklist.

### People Group repair pass

- ~517 sermon files; only ~69 have a named people group; ~12 have empty placeholders; ~448 are missing entirely
- Procedure documented in tracker Part VIII-B
- Priority: medium — fold into existing repair passes, not standalone sweep
- `people-group-map.md` registry currently 61 confirmed groups

### Preaching gaps (`.claude/preaching-gap-analysis.md`)

15 high-priority gaps, 24 books never primary preaching text (19 OT, 5 NT). Top 5:

1. Jeremiah 31:31–34 — New Covenant
2. 1 Corinthians 15 — Bodily resurrection
3. Revelation 4–5, 21–22 — Heavenly worship + new creation
4. Ruth — Kinsman-redeemer typology
5. Daniel 1–6 — Faithfulness under empire

Tracker explicitly notes these are **future planning**, not unfinished documentation.

### Action Items — Quick Wins (tracker Part IX)

| # | Item | Status |
|---|---|---|
| 1 | Extract remaining `memory2.md` sermons | ✅ Done |
| 2 | Resolve Sola Christus 2024 incomplete draft | Pending |
| 3 | Resolve Thankfulness sermon (request remainder from preacher) | Pending |
| 4 | Fix Romans 7 reference error | ✅ Done |
| 5 | Convert NIV/KJV → ESV in raw drafts (Psalm 2, Psalm 68 Part 2, 1 Thess 5) | ✅ Done |
| 6 | Josh 7 & 8 — Spurgeon/Edwards/MacArthur/Taylor quotes ⚠️ unverified | Pending |

---

## open-claw-stuff — Public-domain skill commons

### Branch state

```
claude/audit-unfinished-tasks-pXfBb  (current)
last: 3fa2034 Merge PR #2 (claude/document-repo-souls-rb8LH)
ahead: provenance record + baseline for P1#9 Slice 1, ai-regression-testing v1.0.0, context-budget v1.0.0, provenance schema v1.0.0
working tree: clean
```

### Published skills (10) — see `README.md#skills`

| Skill | Version | Activation |
|---|---|---|
| `careful-not-clever` | published | automatic + explicit |
| `verification-before-completion` | published | automatic + explicit |
| `external-content-wrapping` | published | automatic + explicit |
| `opensource-sanitizer` | v1.2.0 | explicit |
| `silent-failure-hunter` | published | automatic + explicit |
| `policy-as-markdown` | published | automatic + explicit |
| `harness-auditor` | v1.0.0 | explicit |
| `doc-updater` | v1.0.0 | explicit |
| `context-budget` | v1.0.0 | explicit |
| `ai-regression-testing` | v1.0.0 | explicit |

### No explicit HANDOFF/TODO files

Recent commits show forward motion (provenance schema, ai-regression-testing baseline). Quality bar per README: generic, self-contained, tool-scoped, verifiable. No tracked unfinished items.

### Implied pending (from sibling repos' new-skills-proposal.md)

Skills *not yet lifted* to the commons from the household — these would land here when mature, generic, and ready:

- `seo-schema-audit` — generic enough to land here once proven on InTheWake + flickersofmajesty
- `link-integrity` — generic enough
- `accessibility-audit` — generic enough
- `content-freshness` — generic enough
- `ebook-builder` — too recipe-specific; stays in household
- `breeding-advisor`, `port-content-builder`, `nutrition-estimator`, `sermon-cross-reference`, `collection-sync` — domain-locked, won't lift

No queue inside this repo for those; they originate elsewhere.

---

## Cross-cutting observations

### Staleness

- The most reliable inthewake backbone (`PROJECT_STATE_2026_02_14.md`) is **~12 weeks stale**. The April 9 port validation status and April 6 ship/fleet audits are the most current dev-side artifacts I can read.
- Romans `.claude/unfinished-work-tracker.md` was updated 2026-03-16 — **~8 weeks stale**.
- ken orchestrator docs (PLAN.md, ROLLOUT.md, CONTINUOUS_LEARNING_*) are active; commits to this branch are recent.
- open-claw-stuff is current — v1.0.0 skills landing within the last few branches.

### Documentation-vs-code drift risk

The `keeper-plan.md` has had 9 review rounds and exhaustive design without code. The ratio of design effort to implementation effort here is the household's largest single open commitment. The Stage 1 trim (5 commands, ~2 hrs) is the right cut — but stays unbuilt.

### Cognitive memory underuse

`/sheep` scope empty despite a month of decisions captured in commits. `/ken` and several other scopes likely the same. K4 of the Manatee Creek plan is the cheapest single-command fix to recover institutional knowledge — independent of K1–K3.

### "Done"-list discipline

Romans uses `~~strikethrough~~` for resolved items in the tracker — good signal, easy to scan. InTheWake's `PROJECT_STATE` uses ✅/🟡/🔴/⏳ status icons consistently. Neither convention is broken; both work.

### Validator deployment latency

The InTheWake port validator was consolidated **2026-04-09** (5 sub-validators into v2). The fleet-wide baseline run is **still pending**. Until that runs, no one knows the current pass-rate — every prior number is pre-consolidation. This is the single highest-leverage measurement to take in the next inthewake session.

---

## Recommended next-session ordering

Independent of which repo gets attention next:

1. **K4 of Manatee Creek** (ken) — 7 cognitive-memory `encode` commands, ~5 minutes. Preserves institutional knowledge before HANDOFF deletion.
2. **InTheWake fleet validator baseline** — `node scripts/batch-validate.js` against the consolidated v2. Single command; outputs the current state of the world.
3. **InTheWake cross-fleet dining hero swap** — 291 of 295 pages, bulk script. Highest-visibility credibility win.
4. **Historic ship batch (6 ships)** — 3–4.5 hours total, well-documented per-ship pattern in `SHIP_VALIDATION_COMPLETION_GUIDE.md`.
5. **Cruising After Loss HTML conversion** — 3–4 hours to publication, all content already written.
6. **Romans verification-flag sweep** — pick the file with the most remaining ⚠️ (Phil 4: 4 standing) and clear it.
7. **`keeper` Stage 1 MVP** — when design fatigue is acceptable, ship the 5-command scaffold; the plan is overspecified by design-round-9 standards.

---

*Audit produced by Claude (`claude-opus-4-7[1m]`) on 2026-05-12. Branch: `claude/audit-unfinished-tasks-pXfBb`. Sources: every dated plan/audit/status/HANDOFF/tracker file in `/home/user/ken/`, `/home/user/Romans/`, and `/home/user/open-claw-stuff/` reachable from the audit-window listing above.*

*Soli Deo Gloria.*
