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

### First-Time Setup (Per Session)

Before first use of `/consult` or `/orchestrate` in a session, install dependencies:

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

This is silent when already installed. If `/consult` or `/orchestrate` fails with `ModuleNotFoundError`, run this command first.

### Adapter Troubleshooting

**Gemini (`google-genai` import error):**
The Gemini adapter uses `from google import genai` which requires the `google-genai` package (NOT `google-generativeai`). If you see `cannot import name 'genai' from 'google'`:
```bash
pip install google-genai
```
If that fails with `_cffi_backend` / `cryptography` errors (common in containerized environments where system cryptography is outdated):
```bash
pip install cffi cryptography --force-reinstall --ignore-installed
```

**Grok (xAI authentication error):**
If Grok returns `401 / no-credentials`, the XAI_API_KEY is missing from `.env`. Fix:
```bash
rm /home/user/ken/orchestrator/.env
python3 /home/user/ken/orchestrator/env_seed.py --decode
```
This re-decodes the `.env` from the committed seed. The seed must contain the XAI key — if it's blank, the seed needs to be re-encoded with a valid key (`python3 env_seed.py --encode` after editing `.env`).

**GPT:** Usually works out of the box after `pip install openai`. Key is in `.env` as `OPENAI_API_KEY`.

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
