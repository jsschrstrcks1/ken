# Investigate — Multi-LLM Research Pipeline

> Research first. Build from evidence. Every fact traceable.

Adapted from jsschrstrcks1/ken `.claude/skills/investigate/SKILL.md` for OpenClaw/Skynet.

---

## What This Is

A 4-phase chained investigation pipeline for deep research. Used when you need 
thorough, multi-source, traceable findings — not a quick answer.

---

## The 4 Phases

| Phase | What Happens |
|-------|-------------|
| **1. RECON** | Fan-out: 5 models research independently (GPT, Gemini, Perplexity, You.com, Grok). Claude leads deliberation + blind spot check. |
| **2. TRIAGE** | Composite scoring — confidence (40%) + citation density (30%) + multi-model agreement (30%). Drop below threshold. |
| **3. DEEP RESEARCH** | Staged pipeline on top N threads. Each thread: research models verify → Claude synthesizes → analysts evaluate. |
| **4. SYNTHESIS** | Cross-thread conflict analysis. All citations collected. Provenance report. |

---

## Modes

| Mode | Domain | Source Hierarchy |
|------|--------|-----------------|
| `family-history` | Genealogy | Family Bible > cathedral records > census > secondary > unverified trees |
| `cruising` | InTheWake ship/port research | Official cruise line data > industry DBs > review sites > user content |
| `sermon` | Biblical/theological research | Scripture > theological maps > attributed sources > general |
| `sheep` | Agricultural/flock research | Flock records > veterinary sources > agricultural extension data |
| `recipe` | Recipe research | Primary recipe documents > tested sources > general |

**Source hierarchy rule:** Lower-tier never overrides higher-tier without flagging.
Conflicts documented, not silently resolved.

---

## Merge-Not-Replace Rule (CRITICAL)

Before generating any content page, check if it already exists.

```
File exists? → YES: MERGE MODE — enrich, do not replace
              → NO:  NEW PAGE — build from template + investigation output
```

### In Merge Mode, ALWAYS preserve:
- User-curated images (carousel photos, hero images)
- Authentic narrative entries (real voices, real names)
- Internal links already wired to other pages
- Sister/sibling lists the existing page maintains
- Attribution sections (legal obligations)
- Author-curated ordering (pill order, section arrangement)

### Update only where investigation found fresher/better data:
- Stats (corrected specs, counts, dates)
- FAQ answers (stale info, missing context)
- Metadata (ai-summary, description)

**Flag conflicts** — "Existing says X, investigation found Y" — don't silently overwrite.

---

## Verification Path

```
UNVERIFIED → PARTIALLY CORROBORATED → CONFIRMED
```

Every fact tagged with provenance. Multiple independent sources upgrade confidence.

---

## Adapter Failure Policy (MANDATORY)

If any model adapter fails for any reason, I:
1. Automatically fill that model's role in the synthesis
2. Label the fill-in "Claude-as-<model>" explicitly
3. Report the failure to you every time — no exceptions

**What counts as a failure:** HTTP errors, rate limits, auth failures, timeouts, 
billing exhaustion, parse errors, empty responses.

**Final synthesis MUST include if any adapter failed:**
```
## Adapter Failures This Run
| Model | Role | Failure | How I Filled In |
```

Silence is not an option.

---

## When to Use

**Use investigate when:**
- Deep family history research (tracing a person, verifying a lineage)
- Building a new InTheWake ship or port page from scratch
- Researching a sermon topic thoroughly before writing
- Verifying complex sheep breeding or health decisions
- Any time "every fact traceable" matters more than speed

**Cost:** Typical $1–3. Exhaustive mode $3–5.

---

## How to Request

Say something like:
- "Investigate the Baker line from William H. Baker to colonial Virginia"
- "Investigate Norwegian Prima for an InTheWake ship page"
- "Deep research on Romans 5:3-5 for historical/theological background"
- "Investigate FAMACHA and parasite resistance in Florida sheep breeds"

---

*Skynet note: This is the heavy artillery. Use it when you need real depth, 
not when you need a quick answer. Every finding comes with a provenance trail.*
