# Ken — Personal Hub

Timezone utility, clock sync for Devuan/SysVinit, and home of the multi-LLM orchestrator.

---

## Multi-LLM Integration

This repository **hosts** the orchestrator at `orchestrator/`. It is the hub for all multi-LLM operations across all 9 repositories.

### Available Skills

| Skill | Usage | Purpose |
|-------|-------|---------|
| `/consult` | `/consult <model> <role> "<prompt>"` | Quick single-model second opinion |
| `/orchestrate` | `/orchestrate <mode> "<task>"` | Full multi-model linear pipeline |
| `/orchestra` | `/orchestra "<task>"` | Fan-out + deliberation debate |
| `/investigate` | `/investigate <mode> "<subject>"` | 4-phase deep research → content page |
| Cognitive Memory | Automatic on session start | Cross-session knowledge persistence |

### Mode: *(specify explicitly)*
This is the hub — no default mode. Specify `sermon`, `sheep`, `cruising`, `recipe`, or `family-history` when running `/orchestrate` or `/investigate`.

- **Memory scope:** `/ken`
- **Orchestrator:** `/home/user/ken/orchestrator/`

---

## Handoff Protocol

This project uses **handoff files** to survive session timeouts and rate limits. Every Claude Code session that does significant work must maintain a handoff file.

### How It Works

1. **At session start**: Check for `HANDOFF.md` in the relevant skill or project directory. Read it before doing anything else.
2. **During work**: After each logical milestone, update the handoff file with current state.
3. **On timeout/rate limit**: The handoff file already has the latest state. Next session reads it and continues.
4. **On completion**: Mark the handoff as complete with final status.

### Handoff File Format

Every `HANDOFF.md` must contain:
- **What Was Done** — completed steps, in order
- **What Still Needs Doing** — remaining work, prioritized
- **Key Decisions** — architecture choices that shouldn't be revisited
- **Files Created/Modified** — so the next session knows what exists
- **How to Resume** — exact first step for the next session

### Handoff Locations

| Scope | Location |
|-------|----------|
| Skill work | `.claude/skills/<skill-name>/HANDOFF.md` |
| Orchestrator work | `orchestrator/HANDOFF.md` |
| General repo work | `HANDOFF.md` (repo root) |

### Rules
- **Write the handoff BEFORE the work that might timeout** — not after
- Keep it under 100 lines — handoffs are for the next session, not documentation
- Include IDs, paths, and exact values — not vague descriptions
- Delete the handoff when the work is fully complete

---

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
