# Ken — Personal Hub

Timezone utility, clock sync for Devuan/SysVinit, and home of the multi-LLM orchestrator.

---

## Multi-LLM Integration

This repository **hosts** the orchestrator at `orchestrator/`. It is the hub for all multi-LLM operations across all 9 repositories.

### Available Skills

| Skill | Usage | Purpose |
|-------|-------|---------|
| `/consult` | `/consult <model> <role> "<prompt>"` | Quick single-model second opinion |
| `/orchestrate` | `/orchestrate <mode> "<task>"` | Full multi-model pipeline |
| Cognitive Memory | Automatic on session start | Cross-session knowledge persistence |

### Mode: *(specify explicitly)*
This is the hub — no default mode. Specify `sermon`, `sheep`, `cruising`, or `recipe` when running `/orchestrate`.

- **Memory scope:** `/ken`
- **Orchestrator:** `/home/user/ken/orchestrator/`

### Orchestrator Architecture

```
orchestrator/
├── orchestrate.py      ← Pipeline runner
├── consult.py          ← Quick consultation CLI
├── verify.py           ← Claim verification
├── memory_ops.py       ← Cognitive memory system
├── adapters/           ← GPT, Gemini, Grok wrappers
├── modes/              ← sermon.yaml, sheep.yaml, cruising.yaml, recipe.yaml
├── state/              ← Runtime blackboard state
├── repo-modes.json     ← Repository-to-mode mapping
└── .env                ← API keys (gitignored)
```
