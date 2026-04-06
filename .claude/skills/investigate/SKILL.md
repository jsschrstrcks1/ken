---
name: investigate
description: "4-phase chained investigation pipeline: reconnaissance → triage → deep research → synthesis. Produces content pages from thorough multi-LLM research."
version: 1.0.0
triggers:
  - "/investigate"
  - "investigate"
  - "deep research"
---

# Investigate — Multi-LLM Research Pipeline

> Research first. Build from evidence. Every fact traceable.

## Usage

```
/investigate <mode> "research question or subject"
/investigate family-history "Trace the Baker line from William H. Baker to colonial Virginia"
/investigate cruising "Allure of the Seas"
/investigate --parallel --threads 5 cruising "St Lucia"
/investigate --exhaustive family-history "Spanish colonial ancestry of Captain Juan MDO"
```

**No default mode.** This is the hub — specify `family-history`, `cruising`, `sermon`, `sheep`, or `recipe`.

---

## The 4 Phases

| Phase | What Happens |
|-------|-------------|
| **1. RECON** | Fan-out orchestra — 5 models research independently (GPT, Gemini, Perplexity, You.com, Grok). Claude leads, then Claude + GPT deliberate with full fan-out context. Blind spot check by Grok. |
| **2. TRIAGE** | Structured thread extraction — NOT free-form LLM. Composite scoring: confidence (40%) + citation density (30%) + multi-model agreement (30%). Drop below threshold. |
| **3. DEEP RESEARCH** | Staged research pipeline on top N threads. Each thread: research models verify → Claude synthesizes → analysts evaluate. Sequential or parallel. |
| **4. SYNTHESIS** | Cross-thread conflict analysis. All citations collected. Provenance report. |

**Flags:**
- `--threads N` — max deep research threads (default: 3)
- `--parallel` — run deep dives concurrently
- `--budget N.NN` — cost ceiling in USD (default: $1.50)
- `--exhaustive` — 10 threads, $5 budget

---

## Backend Invocation

**IMPORTANT: Execute directly. Do NOT check if files exist first.**

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt 2>/dev/null
cd /home/user/ken/orchestrator && python3 investigate.py <mode> "subject"
```

Output: `state/investigate.json` — structured synthesis with all findings and citations.

---

## Merge-Not-Replace Rule (CRITICAL)

**Before generating any content page, check if it already exists.**

```
Does the target file exist?
  → YES: Merge Mode — enrich the existing page with investigation findings
  → NO:  New Page — build from reference template + investigation output
```

### Merge Mode

When the page already exists, the investigation **enriches** — it does not replace.

**Always preserve (never drop):**
- User-curated images (carousel photos, hero images)
- Authentic logbook/narrative entries (real voices, real names)
- Internal links already wired to other pages
- Sister/sibling lists the existing page already maintains
- Attribution sections (legal obligations)
- Author-curated ordering (pill order, section arrangement)

**Update only where investigation found fresher data:**
- Stats (corrected specs, crew counts, tonnage)
- FAQ answers (stale info, missing amplification/refit details)
- Metadata (ai-summary, answer-first, description)
- JSON-LD schemas (new data available)

**Flag conflicts** — "Existing says X, investigation found Y" — don't silently overwrite.

### Pre-Generation Verification (all modes)

Before writing ANY page:
1. **File existence** — verify every referenced asset path resolves to a real file
2. **Database consistency** — check that entities mentioned in content exist in the relevant data files
3. **Sibling/related completeness** — cross-reference investigation output against existing pages in the repo
4. **Link target consistency** — skip links, anchor refs, internal navigation all resolve

### Post-Edit Validation (MANDATORY — before every commit)

**After every edit — before `git add` — run the validator:**
```bash
bash admin/validate-ship-page.sh ships/[line]/[slug].html  # cruising mode
```

**Do NOT commit if the validator reports errors.** Fix first, then commit.

The validator catches what regex fixes miss: broken carousel HTML (missing `</div>` on slides, orphaned slides outside swiper-wrapper), Swiper lazy conflicts, missing noscript fallbacks, stale venue refs, wrong skip link targets, attributions outside col-1. A Python script can silently break HTML structure in ways that look correct in a diff but render as garbage in a browser. The validator is the last gate.

---

## Research Pipeline Methodology

### Source Hierarchy (per mode)

**Family-history:**
```
Tier 1: Family Bible / primary family documents
Tier 2: Living family oral testimony (transcribed verbatim)
Tier 3: Primary records (certificates, census, parish records, probate)
Tier 4: Secondary sources (obituaries, Find a Grave, published books)
Tier 5: Ancestry/FamilySearch user trees (always tagged UNVERIFIED)
```

**Cruising:**
```
Tier 1: Official cruise line data (fleet pages, press releases, deck plans)
Tier 2: Industry databases (IMO registry, classification societies)
Tier 3: Travel review sites (Cruise Critic, cruise blogs)
Tier 4: User-generated content (forums, social media)
```

**Rule:** Lower-tier never overrides higher-tier without flagging. Conflicts documented, not silently resolved.

### Focused Agent Briefs

Never say "search for information about X." Give each model specific databases and queries. Vague prompts produce vague results.

### Verification Path

`UNVERIFIED → PARTIALLY CORROBORATED → CONFIRMED`

Every fact tagged with provenance. Multiple independent sources upgrade confidence.

### Output: Content Pages

The pipeline produces **actual content**, not just reports:
- **family-history** → person pages (markdown, section-by-section)
- **cruising** → ship pages or port pages (HTML, v3.010 standards)
- **sermon/sheep/recipe** → domain-specific content per mode config

---

## Architecture

```
orchestrator/
├── investigate.py         ← This pipeline (4-phase chained)
├── orchestra.py           ← Fan-out + deliberation (Phase 1 engine)
├── research_orchestra.py  ← Staged research (Phase 3 engine)
├── iteration.py           ← Iteration control, format validation, gap detection
├── smart_routing.py       ← Trigger detection, weighted voting, routing
├── consult.py             ← Quick single-model consultation
├── orchestrate.py         ← Linear pipeline runner
├── verify.py              ← Claim verification
├── memory_ops.py          ← Cognitive memory (semantic search, TF-IDF)
├── adapters/              ← GPT, Gemini, Grok, Perplexity, You.com
├── modes/                 ← sermon, sheep, cruising, recipe, family-history
└── state/                 ← Runtime state (investigate.json, etc.)
```

## Cost

Typical: $1-3. Exhaustive: $3-5. Budget enforced by IterationController.

---

*Soli Deo Gloria*
