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
/orchestrate family-history "Verify the Baker line from William H. Baker to colonial Virginia"
```

**No default mode.** This is the hub — you must specify `sermon`, `sheep`, `cruising`, `recipe`, or `family-history`.

---

## Available Modes

| Mode | Lead | Pipeline Steps |
|------|------|---------------|
| sermon | Claude | Draft → Challenge (Grok) → Expand (Gemini) → Structure (GPT) → Integrate → Evaluate → Voice Audit |
| sheep | GPT | Plan (GPT) → Expand (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT) |
| cruising | Claude | Read Standards → Generate → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate |
| recipe | GPT | Generate (GPT) → Expand (Gemini) → Safety (Claude) → Creative Variation (Grok) |
| family-history | Claude | Load Context → Extract/Draft → Verify (GPT) → Expand (Gemini) → Challenge (Grok) → Synthesize |

---

## Backend Invocation

**IMPORTANT: Execute these commands directly using the Bash tool. Do NOT check if files exist first — just run them.**

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null; pip3 install -q -r /home/user/ken/orchestrator/requirements.txt 2>/dev/null && python3 /home/user/ken/orchestrator/orchestrate.py <mode> "task description"
```

---

## Architecture

```
orchestrator/
├── orchestrate.py         ← Linear pipeline runner (/orchestrate)
├── orchestra.py           ← Fan-out + deliberation (/orchestra)
├── investigate.py         ← 4-phase investigation (/investigate)
├── research_orchestra.py  ← Staged research (used by investigate)
├── consult.py             ← Quick consultation CLI (/consult)
├── verify.py              ← Claim verification
├── iteration.py           ← Iteration control, format validation
├── smart_routing.py       ← Trigger detection, weighted voting
├── memory_ops.py          ← Cognitive memory (semantic search, TF-IDF)
├── adapters/              ← GPT, Gemini, Grok, Perplexity, You.com
├── modes/                 ← sermon, sheep, cruising, recipe, family-history
├── state/                 ← Runtime state (JSON output)
├── repo-modes.json        ← Repository-to-mode mapping
└── .env                   ← API keys (gitignored)
```
