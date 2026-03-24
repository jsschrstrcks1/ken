---
name: orchestrate
description: "Full multi-LLM pipeline orchestration. This is the hub — no default mode. Specify sermon, sheep, cruising, or recipe explicitly."
---

# Orchestrate — Multi-LLM Pipeline (Hub)

*This repository hosts the orchestrator. Specify mode explicitly.*

## Usage

```
/orchestrate <mode> "task description"
/orchestrate sermon "Preach Romans 5:1-5 on suffering producing hope"
/orchestrate sheep "Plan spring breeding for the Katahdin ewes"
/orchestrate cruising "Build a new ship page for Norwegian Prima"
/orchestrate recipe "Generate a classic Southern cornbread recipe"
```

**No default mode.** This is the hub — you must specify `sermon`, `sheep`, `cruising`, or `recipe`.

---

## Available Modes

| Mode | Lead | Pipeline Steps |
|------|------|---------------|
| sermon | Claude | Draft → Challenge (Grok) → Expand (Gemini) → Structure (GPT) → Integrate → Evaluate → Voice Audit |
| sheep | GPT | Plan (GPT) → Expand (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT) |
| cruising | Claude | Read Standards → Generate → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate |
| recipe | GPT | Generate (GPT) → Expand (Gemini) → Safety (Claude) → Creative Variation (Grok) |

---

## Backend Invocation

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
python3 /home/user/ken/orchestrator/orchestrate.py <mode> "task description"
```

---

## Architecture

```
orchestrator/
├── orchestrate.py      ← Pipeline runner
├── consult.py          ← Quick consultation CLI
├── verify.py           ← Claim verification
├── adapters/           ← GPT, Gemini, Grok wrappers
├── modes/              ← sermon.yaml, sheep.yaml, cruising.yaml, recipe.yaml
├── state/              ← Runtime blackboard state
├── repo-modes.json     ← Repository-to-mode mapping
└── .env                ← API keys (gitignored)
```
