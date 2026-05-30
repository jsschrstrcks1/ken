# Multi-LLM Orchestrator — Rollout Plan

## Architecture Decision: Skill + Agent (Both)

After reviewing all 9 repositories, the recommendation is **both a skill and an agent-style pipeline** — each serves a different purpose.

### Why Both?

| | Skill (`/consult`) | Pipeline (`/orchestrate`) |
|---|---|---|
| **When** | Quick second opinion | Full multi-model workflow |
| **Steps** | 1 API call | 3-7 step pipeline |
| **Cost** | Pennies ($0.01-0.03) | Dimes ($0.03-0.20) |
| **Speed** | Seconds | Minutes |
| **Example** | "Does this illustration land?" | "Draft a full sermon on Romans 5" |

---

## What Was Deployed

### 1. Global Skills (available in all repos)

**Location:** `~/.claude/skills/`

| Skill | File | Purpose |
|-------|------|---------|
| `/consult` | `~/.claude/skills/consult/SKILL.md` | Quick single-model consultation with role-based prompts |
| `/orchestrate` | `~/.claude/skills/orchestrate/SKILL.md` | Full multi-model pipeline with mode auto-detection |
| Cognitive Memory | `~/.claude/skills/cognitive-memory/SKILL.md` | Cross-session knowledge persistence with auto-scoping |

### 2. Repository-to-Mode Mapping

**Location:** `/home/user/ken/orchestrator/repo-modes.json`

| Repository | Mode | Lead | Memory Scope |
|---|---|---|---|
| Romans | `sermon` | Claude | `/romans` |
| manateecreeksheep | `sheep` | GPT + Claude (safety) | `/sheep` |
| InTheWake | `cruising` | Claude | `/inthewake` |
| flickersofmajesty | `cruising` | Claude | `/flickersofmajesty` |
| Allrecipes | `recipe` | GPT | `/recipes/allrecipes` |
| Grandmasrecipes | `recipe` | GPT | `/recipes/grandmasrecipes` |
| Grannysrecipes | `recipe` | GPT | `/recipes/grannysrecipes` |
| MomsRecipes | `recipe` | GPT | `/recipes/momsrecipes` |
| ken | *(specify)* | *(varies)* | `/ken` |

### 3. CLAUDE.md Updates

Every repository now has a Multi-LLM Integration section in its CLAUDE.md documenting:
- Available skills and usage examples
- Assigned mode and pipeline
- Memory scope
- Context boundaries (what to send / what to keep private)

### 4. Gemini API Keys

Stored in `/home/user/ken/orchestrator/.env`:
- `GOOGLE_API_KEY` — Free tier (use first)
- `GOOGLE_API_KEY_PAID` — Paid fallback (auto-switches on quota exhaustion)

Gemini adapter updated with automatic key fallback logic.

---

## Usage Examples

### Quick Consultation (any repo)
```
/consult grok challenge "Is this Romans 5 outline airtight?"
/consult gemini expand "Southern buttermilk biscuit history and science"
/consult gpt structure "product page layout for landscape prints"
```

### Full Pipeline (auto-detects mode from repo)
```
# In Romans repo:
/orchestrate "preach Romans 5:1-5 on suffering"

# In manateecreeksheep repo:
/orchestrate "evaluate fall breeding pairs for parasite resistance"

# In Grandmasrecipes repo:
/orchestrate "generate a banana pudding recipe with variations"
```

### Cognitive Memory (automatic)
```
# Session start: auto-recalls relevant memories
# During work: encode important decisions
# End of session: consolidate and decay unused memories
```

---

## What's NOT Deployed Yet (Future Phases)

| Phase | Feature | Status |
|-------|---------|--------|
| 2 | Per-mode cost budgets | Planned |
| 2 | Grok API key integration | Needs key |
| 3 | Custom `photography` mode for flickersofmajesty | Planned |
| 3 | Livestock data integration for verify.py | Planned |
| 4 | Memory consolidation automation | Planned |
| 4 | Cross-repo memory queries | Planned |

---

## Verification Checklist

- [x] Global skills created in `~/.claude/skills/`
- [x] All 9 CLAUDE.md files updated with Multi-LLM Integration section
- [x] Repo-to-mode mapping created
- [x] Gemini API keys configured with free-tier-first fallback
- [x] Gemini adapter updated with auto-fallback logic
- [x] Cognitive memory skill globalized with auto-scoping
- [ ] Commits pushed to all 9 repos
- [ ] Live test: `/consult` from a recipe repo
- [ ] Live test: `/orchestrate` from Romans
- [ ] Grok API key added when available
