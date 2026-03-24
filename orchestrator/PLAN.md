# Multi-LLM Orchestration System — Master Plan

**Repository**: jsschrstrcks1/ken
**Status**: Planning → Phase 0 build
**Date**: March 23, 2026
**Contributors**: Human (architect), ChatGPT (planning), Grok (education/risk analysis), Gemini (context), Claude (evaluation/implementation)

---

## 0. What This Is

A lean, mode-driven consultation system that coordinates multiple AI models (GPT, Claude, Gemini, Grok) to enhance — not replace — existing workflows across four domains.

**One-sentence definition**: A disciplined consultation system that sharpens your work without corrupting it.

This is NOT:
- An autonomous agent system
- A framework-heavy architecture
- A replacement for Claude in sermon writing
- A chat relay or UI hack

---

## 1. Core Principles

1. **Human authority is primary.** You are the final arbiter at every stage.
2. **Claude remains lead in sermon and cruising workflows.** Claude has the voice profile, the reference maps, the evaluation rubrics, and file access.
3. **API-first only.** No browser automation, no UI scraping, no Discord/group chat hacks.
4. **Structured JSON communication.** All model responses are parseable, not prose.
5. **Synthesis over voting.** Never average outputs. Extract best elements and unify.
6. **Bounded loops.** Max 2 iterations. Stop if no meaningful change.
7. **Hallucination defense is mandatory.** Claims must be explicit and verifiable.
8. **Mode-specific pipelines.** Each domain has its own flow, not a global one.
9. **Start simple, expand only when needed.** No Redis, no vector DB, no frameworks until proven necessary.
10. **Privacy-aware.** Define what data is safe to send to each external provider.

---

## 2. System Architecture

```
orchestrator/
├── adapters/
│   ├── __init__.py
│   ├── gpt.py              # OpenAI API wrapper (~30 lines)
│   ├── gemini.py            # Google API wrapper (~30 lines)
│   └── grok.py              # xAI API wrapper (~30 lines)
├── modes/
│   ├── sermon.yaml          # Claude writes, others consult
│   ├── sheep.yaml           # GPT plans, Claude validates
│   ├── cruising.yaml        # Claude enforces + writes, others consult
│   └── recipe.yaml          # Single-pass, minimal pipeline
├── state/
│   └── current.json         # The blackboard (active task state)
├── consult.py               # CLI tool: quick second opinions
├── orchestrate.py           # Full pipeline runner (Phase 2)
├── .env                     # API keys (GITIGNORED)
├── env_seed.py              # Obfuscated .env seed (committed)
├── bootstrap-env.sh         # Auto-restores .env from seed
├── .gitignore
├── requirements.txt
└── PLAN.md                  # This file
```

### API Key Management

Keys live in `.env` (gitignored). An obfuscated copy is committed in `env_seed.py`
so that fresh clones in any container can auto-restore keys via `bootstrap-env.sh`.

#### Changing an existing API key

1. Edit `/home/user/ken/orchestrator/.env` with the new key value
2. Regenerate the seed:
   ```bash
   cd /home/user/ken/orchestrator
   python3 env_seed.py --encode
   ```
3. Copy the printed `_SEED = (...)` block and paste it into `env_seed.py`,
   replacing the existing `_SEED` variable
4. Commit and push `env_seed.py` — all containers will pick up the new key
   on their next clone or pull

#### Adding a new LLM provider

1. **Create the adapter** — add `orchestrator/adapters/<provider>.py`:
   ```python
   def query(prompt: str, system: str = "") -> dict:
       # Call the provider's API
       # Return {"text": "...", "model": "...", "usage": {...}}
   ```
   The adapter is auto-discovered by `adapters/__init__.py` (any `.py` in the
   directory with a `query()` function gets loaded).

2. **Add the API key** to `.env`:
   ```
   NEW_PROVIDER_API_KEY=your-key-here
   ```

3. **Read the key** in your adapter:
   ```python
   api_key = os.environ.get("NEW_PROVIDER_API_KEY", "")
   ```

4. **Regenerate the seed** (so other containers get the key):
   ```bash
   python3 env_seed.py --encode
   ```
   Then paste the new `_SEED` blob into `env_seed.py`.

5. **Update `.env.example`** with a placeholder for the new key.

6. **Add a mode step** (optional) — edit `modes/*.yaml` to include the new
   provider in pipeline steps.

7. Commit all changes: adapter, env_seed.py, .env.example, mode YAML.

#### Current keys

| Variable | Provider | Notes |
|----------|----------|-------|
| `OPENAI_API_KEY` | GPT (OpenAI) | Project-scoped key |
| `GOOGLE_API_KEY` | Gemini (AI Studio) | Free tier, used first |
| `GOOGLE_API_KEY_PAID` | Gemini (AI Studio) | Paid fallback |
| `VERTEX_API_KEY` | Gemini (Vertex AI) | Used when AI Studio is blocked |
| `GOOGLE_CLOUD_PROJECT` | Vertex AI | Project ID |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI | Region (us-central1) |
| `XAI_API_KEY` | Grok (xAI) | Not yet configured |

---

## 3. Shared State (JSON Blackboard)

Single source of truth for the active task. File-based (`state/current.json`), not Redis.

```json
{
  "mode": "",
  "goal": "",
  "constraints": [],
  "context": {},
  "candidates": {},
  "critiques": {},
  "current_best": "",
  "decisions": [],
  "risks": [],
  "open_questions": [],
  "cost_log": []
}
```

**Rules:**
- Only the orchestrator writes to state
- Models return proposals only (never mutate state directly)
- No raw transcripts stored
- State is per-task, not persistent (persistent knowledge lives in domain repos)

---

## 4. Communication Protocol

All model responses must conform to this JSON schema:

```json
{
  "analysis": "Free-text reasoning about the task",
  "claims": [
    {"type": "scripture", "claim": "Romans 5:3 says...", "source": "ESV"},
    {"type": "quote", "claim": "Spurgeon said...", "source": "Sermon #2234"},
    {"type": "factual", "claim": "Katahdin sheep are...", "source": "livestock data"}
  ],
  "proposed_update": "What should change in the current plan/output",
  "risks": ["Risk 1", "Risk 2"],
  "confidence": 0.85,
  "open_questions": ["Unresolved issue 1"]
}
```

The `claims` array is critical — it enables the hallucination defense layer to verify each factual assertion independently.

---

## 5. Model Roles

| Model | Provider | Primary Strengths | Context Window |
|-------|----------|-------------------|---------------|
| **Claude** | Anthropic | Writing, evaluation, standards enforcement, theological precision, voice fidelity | 200K |
| **GPT** | OpenAI | Planning, structure, synthesis, versatility | 128-200K |
| **Gemini** | Google | Research, cross-references, broad context, knowledge expansion | 1M+ |
| **Grok** | xAI | Adversarial thinking, challenging assumptions, unconventional ideas | Up to 2M |

**Role assignments vary by mode.** There is no global role assignment. See Section 7.

---

## 6. Hallucination Defense

The #1 risk in multi-LLM systems: one model fabricates a claim, the next treats it as fact, the synthesizer polishes it into confident nonsense.

### Claim-Type Routing

| Claim Type | Verification Method | Source |
|-----------|---------------------|--------|
| Scripture reference | Check exact ESV text | ESV API or local verification |
| Attributed quote | Lookup in `quote-map.md` | Romans repo `.claude/quote-map.md` |
| Theological claim | Check against theological map | Romans repo `.claude/theological-map.md` |
| Livestock/flock data | Check against flock database | Sheep records |
| Website standards | Check against standards docs | Cruising repo standards |
| Factual claim (other) | Flag for human review | Human judgment |

### Verification Flow

1. External model returns response with `claims` array
2. Orchestrator extracts claims by type
3. Each claim routed to appropriate verification backend
4. Verified claims → accepted into state
5. Unverified claims → flagged with `⚠️ UNVERIFIED` marker
6. Failed claims → discarded with log entry

**For Sermon Mode specifically**: Claude runs verification via the existing `careful-not-clever` guardrail. External model outputs pass through Claude before touching the blackboard.

---

## 7. Mode-Specific Pipelines

### 7A. Sermon Mode

**Lead**: Claude (author, evaluator, archivist)
**Others**: Consultants only — critique, expand, challenge

**Pipeline:**
1. Claude writes sermon draft (using full `.claude/` infrastructure: voice profile, theological maps, congregation profile, like-a-human, careful-not-clever)
2. **Optional consultation** (any or all):
   - Grok → challenge weak reasoning, surface bold illustrations
   - Gemini → expand cross-references, add historical/theological context
   - GPT → light structural suggestions only
3. Claude integrates feedback (discards what doesn't fit)
4. Claude evaluates via `thus-says-the-lord` rubric (100-point weighted scale)
5. Claude revises based on surgical fixes
6. `voice-audit` before committing

**Context boundary (what gets sent externally):**
- SEND: sermon outline, theological claims, cross-reference questions, illustration concepts
- KEEP LOCAL: congregation names, pastoral application details, personal illustrations with real people, voice profile internals

**What external models must NOT do:**
- Rewrite full sermon text
- Override theological commitments
- Introduce unverified quotes or references
- Alter voice or cadence

### 7B. Sheep Mode

**Lead**: GPT (planning, scheduling)
**Validator**: Claude (safety, inbreeding prevention, risk analysis)

**Pipeline:**
1. GPT → generate breeding plan from flock data + objectives
2. Gemini → add agricultural/veterinary context (Florida-specific: parasite pressure, humidity)
3. Grok → suggest unconventional pairings, challenge assumptions
4. Claude → validate safety (pedigree traversal for inbreeding, health risk correlation, breeding record checks) — this is substantive validation, not a rubber stamp
5. GPT → finalize plan incorporating all feedback

**Output schema:**
```json
{
  "breeding_plan": [],
  "pairings": [{"sire": "", "dam": "", "rationale": "", "risk_flags": []}],
  "culling_recommendations": [],
  "risk_flags": [],
  "expected_outcomes": [],
  "timeline": []
}
```

### 7C. Cruising Mode

**Lead**: Claude (standards enforcement + content generation)
**Others**: Consultants for content and UX ideas

**Pipeline:**
1. Claude reads standards from repo (hero, compass, right-side rail, a11y, canonical URLs, versioning)
2. Claude generates standards-compliant page content
3. GPT → suggests content additions or structural alternatives
4. Gemini → content completeness check
5. Grok → UX innovation challenges
6. Claude → integrates feedback, enforces compliance, produces final output

**Output schema:**
```json
{
  "page_type": "",
  "html": "",
  "seo": {},
  "a11y_checks": [],
  "compliance_report": []
}
```

### 7D. Recipe Mode

**Lead**: GPT (generation)
**Single-pass preferred.**

**Pipeline:**
1. GPT → generate recipe with structured format
2. Gemini → ingredient knowledge, substitutions, nutrition data
3. Claude → safety check (cooking temps, allergen warnings, clarity)
4. Optional: Grok → creative variations

**Output schema:**
```json
{
  "title": "",
  "ingredients": [],
  "instructions": [],
  "variations": [],
  "nutrition": {},
  "seo": {}
}
```

---

## 8. Loop Control

- **Max iterations**: 2
- **Stop conditions** (any triggers stop):
  - Convergence: minimal delta between iterations
  - Cost threshold reached (configurable per mode)
  - Human override
- **Sermon Mode exception**: Loops are managed by the existing `thus-says-the-lord` → revise → `voice-audit` cycle, not by the orchestrator

---

## 9. Cost Tracking

Built into the adapter layer from day one. Every API call returns:

```json
{
  "response": {},
  "usage": {
    "model": "gpt-4o",
    "input_tokens": 1234,
    "output_tokens": 567,
    "estimated_cost_usd": 0.04
  }
}
```

Accumulated in `state/current.json` under `cost_log`. Review after each run.

**Estimated costs per mode (single run):**

| Mode | Est. Cost | Notes |
|------|-----------|-------|
| Sermon (with 2 consultations) | $1-3 | Claude does heavy lifting locally via Claude Code |
| Sheep (full pipeline) | $2-4 | All 4 models active |
| Cruising (full pipeline) | $2-4 | All 4 models active |
| Recipe (single pass) | $0.50-1 | Minimal model usage |

---

## 10. Memory Strategy

### What exists now
- Romans repo: 26+ structured maps in `.claude/` (sermon-map, theological-map, quote-map, illustration-map, etc.)
- Cognitive-memory skill: designed but `~/.memory/` directory not yet built

### What to build
1. **Phase 0**: Build `~/.memory/` directory and `memory_ops.py` (the cognitive-memory skill already references these)
2. **Ongoing**: Claude encodes what's worth remembering from multi-model sessions. Other models remain stateless.
3. **Memory scoping**: `/romans`, `/sheep`, `/cruising`, `/recipes`, `/shared`

### What NOT to build
- No vector database (structured maps with exact lookup outperform fuzzy embeddings for your data)
- No shared memory between external models (they're stateless consultants)

---

## 11. Resilience

- If an external model's API is unavailable, skip that step and continue the pipeline
- Log the skip for review
- System must produce usable output with any single model missing
- Claude Code (the hub) is the only hard dependency

---

## 12. Privacy & Context Boundaries

Every prompt sent to an external API goes to a different company (OpenAI, Google, xAI). Mode configs must define what's safe to send.

**Global rules:**
- Never send API keys, credentials, or secrets
- Never send real names of congregation members
- Never send pastoral counseling details
- Never send PII (health records, financial data)
- Review ToS for each provider regarding data retention

**Per-mode boundaries are defined in mode config files** (see Section 7 for sermon-specific boundaries).

---

## 13. Phased Build Plan

### Phase 0: Consultation Tool (build first, use immediately)
- `consult.py` — CLI tool for quick second opinions
- `adapters/gpt.py`, `adapters/gemini.py`, `adapters/grok.py` — thin API wrappers
- `.env` — API keys
- `requirements.txt`
- Cost tracking in adapter layer

**Deliverable**: `echo "Review this outline for structural weaknesses: ..." | python3 consult.py gpt structure`

### Phase 1: Mode Configs
- `modes/sermon.yaml`, `modes/sheep.yaml`, `modes/cruising.yaml`, `modes/recipe.yaml`
- Define pipeline, roles, constraints, context boundaries, output schemas per mode

### Phase 2: Orchestration + State
- `orchestrate.py` — reads mode config, runs pipeline, manages blackboard state
- `state/current.json` — active task state
- Loop control with convergence detection

### Phase 3: Hallucination Defense
- Claim extraction from model responses
- Claim-type routing to verification backends
- Integration with `careful-not-clever` for sermon claims

### Phase 4: Memory Integration
- Build `~/.memory/` directory and `memory_ops.py`
- Connect to cognitive-memory skill
- Cross-domain memory scoping

---

## 14. What Was Evaluated and Rejected

Documenting these decisions so they don't get re-proposed:

| Proposal | Source | Why Rejected |
|----------|--------|-------------|
| Redis for state | GPT v2, v3 | Single-user CLI tool; JSON file handles this; Redis adds server dependency for no benefit |
| Vector DB (Qdrant/Pinecone) | GPT v2, v3; Grok | Structured markdown maps with exact lookup outperform fuzzy embeddings for this data scale |
| LangGraph / CrewAI / AutoGen | GPT v2; Grok | Premature abstraction; 4 API calls don't need a framework; adds lock-in and learning overhead |
| Consensus voting (3-of-4 agree) | Reddit; Grok | Models bias toward agreement; safe answers win; breakthrough ideas get discarded |
| Claude as "guardrail only" | GPT v1, v2 | Claude is lead author in Sermon Mode with 26 reference maps, voice profile, and evaluation rubric |
| GPT as sermon synthesizer | GPT v1, v2, v3 | GPT doesn't have the voice profile, theological maps, or congregation context |
| One global pipeline for all modes | GPT v1, v2 | Domains have fundamentally different needs; forced into one flow, recipes get over-engineered and sermons get under-specialized |
| multiple.chat / UI relay | Grok | No control, no structured output, no state management |
| Uncontrolled agent autonomy | Grok (AutoGen) | Unbounded agent-to-agent conversation burns tokens and produces drift |
| "DO NOT simplify architecture" | GPT v1, v2, v3 | Good architecture is minimum complexity that solves the problem |

---

## 15. Open Questions

1. **API key acquisition**: Which providers have free tiers? What are the rate limits?
2. **Flock data format**: What format are sheep/breeding records in? (Spreadsheet? Database? Flat files?)
3. **Cruising standards**: Are InTheWake standards documented in a machine-readable format?
4. **Recipe data**: What format does the recipe database use?
5. **Cost budget**: What monthly spend is acceptable across all modes?
6. **Grok SDK**: The `xai-sdk` package — verify current API and authentication method

---

## 16. Source Attribution

This plan was developed through iterative evaluation across multiple AI models:

- **ChatGPT (OpenAI)**: Initial architecture proposals (v1, v2, v3), mode definitions, core loop design
- **Grok (xAI)**: Educational framework (101-401 levels), hallucination propagation warning, context window mismatch awareness, privacy concerns, framework survey
- **Gemini (Google)**: Context expansion (integrated via GPT's synthesis)
- **Reddit**: Blackboard architecture pattern, shared state concept
- **Claude (Anthropic)**: Evaluation of all proposals against existing infrastructure, correction of role assignments, rejection of premature complexity, mode-specific pipeline design, hallucination defense routing, privacy/context boundary design, phased build plan

The final plan preserves the existing Claude Code infrastructure (26+ reference maps, 6 custom skills, hooks, voice profile, evaluation rubric) in the Romans repository while adding multi-model consultation as an enhancement layer.

---

> Start simple. Expand only when the simple version fails. The models are tools — you are the craftsman.
