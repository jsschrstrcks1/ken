# Ken — Personal Hub

Timezone utility, clock sync for Devuan/SysVinit, and home of the multi-LLM orchestrator.

---

## Skills

The full skill catalog (30 skills) is documented in [`SKILLS.md`](SKILLS.md) — human-facing index with activation modes, trigger keywords, slash commands, and example prompts.

**Read it at session start** when work involves the multi-LLM orchestrator (`/consult`, `/orchestrate`, `/orchestra`, `/investigate`), cross-repo health checks, or any of the household-wide skills (`like-a-human`, `voice-audit`, `verification-before-completion`, etc.).

The Multi-LLM Integration section below gives the orchestrator quick reference; SKILLS.md gives the full picture.

---

## Multi-LLM Integration

This repository **hosts** the orchestrator at `orchestrator/`. It is the hub for all multi-LLM operations across all 11 repositories in the household.

### Available Skills

| Skill | Usage | Purpose |
|-------|-------|---------|
| `/consult` | `/consult <model> <role> "<prompt>"` | Quick single-model second opinion |
| `/orchestrate` | `/orchestrate <mode> "<task>"` | Full multi-model linear pipeline |
| `/orchestra` | `/orchestra "<task>"` | Fan-out + deliberation debate |
| `/investigate` | `/investigate <mode> "<subject>"` | 4-phase deep research → content page |
| Cognitive Memory | Automatic on session start | Cross-session knowledge persistence |

### Mode: *(specify explicitly)*
This is the hub — no default mode. Specify one of `sermon`, `sheep`, `cruising`, `recipe`, `family-history`, `triad`, `adversarial-review`, or `strategy` when running `/orchestrate` or `/investigate`. The last three are hub-only modes (red-team review, planner/builder/verifier triad, non-page document synthesis).

- **Memory scope:** `/ken`
- **Orchestrator:** `/home/user/ken/orchestrator/`

---

## OpenClaw Integration — Anthropic ToS Hard Requirements

This repo hosts skills that load into the OpenClaw runtime (`github.com/openclaw/openclaw`). Architecture spec: `openclaw/ARCHITECTURE_v1.md`. The following requirements are **non-negotiable** and derive from Anthropic's Usage Policy, Commercial Terms of Service, and Consumer Terms of Service. They override convenience. If a planned skill, configuration, or integration would violate any of them, **halt and flag before continuing** — do not work around them.

### Authentication

- **Use a dedicated API key** (`ANTHROPIC_API_KEY=sk-ant-...`) issued from a `console.anthropic.com` billing account. This is the only compliant Anthropic auth path for OpenClaw.
- **Never wire OpenClaw to Claude.ai subscription auth.** OAuth tokens from Free/Pro/Max accounts in any third-party tool violate the Consumer Terms and are actively detected and blocked by Anthropic.
- **Keep this API key separate from Claude Code's auth.** A revocation on one billing relationship must not take down the other.

### Tenancy

- **Single user only.** Bearer-token auth on every OpenClaw endpoint per `openclaw/ARCHITECTURE_v1.md` Section 8. Tokens issue to the owner's own devices (phone, laptops, Mac minis); never to other natural persons.
- **No multi-tenant gateway.** Letting another household member, friend, or collaborator use Claude through this API key is the "funnel" / "redistribution" pattern explicitly prohibited by Anthropic's Commercial Terms.
- **No public-facing endpoint.** OpenClaw stays inside the tailnet. No port forwards, no Tailscale Funnel, no public reverse proxy in front of OpenClaw's gateway.

### Agentic skills

- Any skill that takes external action — `coding-agent`, browser control, file modification outside `/tmp`, voice-call, screen capture, message-channel posting — declares `requires_human_confirmation: true` in its manifest entry. Anthropic's agentic-use guidelines require clear consent and documented user control.
- **No skill auto-publishes pastoral, Scripture, or family-history content.** Manifest-loader enforcement of `publish_*` names and the `external_endpoints` allowlist is documented in architecture Section 9. The doctrinal constraint from architecture Section 8 is mechanically enforced, not policy-only.

### Universal usage standards

- No use of OpenClaw for any prohibited category under Anthropic's Universal Usage Standards (CSAM, attacks on critical infrastructure, election manipulation, deception of democratic processes, etc.). Project intent is far from these; restated for completeness because the constraint is absolute.
- Sensitive-domain output (pastoral, mental-health-adjacent, legal-adjacent, etc.) carries forward the disclaimers and accessibility commitments already in place for `cruisinginthewake.com` and sibling sites. Any skill contributing to such output must preserve those disclaimers in its return value.

### Naming and trademark

- Don't label any local skill, channel, or user-facing surface as "Claude" or use the Claude trademark as a product name. Factual references in logs and metadata (e.g., `model: claude-opus-4-7`) are fine; product-style use ("Claude in your menu bar," "Claude said:" as a brand) is not.
- "OpenClaw" is the runtime name and is settled (Anthropic-trademark concerns over the original "Clawdbot" / "Moltbot" names were resolved by the rename in Jan 2026). Don't revert to or reference the older names in any user-facing surface.

### Audit posture

- Every Anthropic API call made through an OpenClaw skill in this repo must produce a `tool.audit` record per architecture Section 9. The `tool.audit` subject is the source of truth for compliance review; if it can't be reconstructed, the call shouldn't happen.

### Enforcement

These are hard requirements, not best practices. Anthropic's Safeguards Team can throttle, suspend, or terminate access for violations. A revoked API key blocks every other workflow that depends on it (consult, orchestrate, orchestra, investigate, plus any future skill).

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

### Keeper — automated half of continuity

`keeper/` is the machine-readable companion to `HANDOFF.md`. It writes session state under `.keeper/<family>/` so the next session can resume without re-discovery.

```
python -m keeper checkpoint <family> ...   # write a checkpoint
python -m keeper status <family>           # show session state
python -m keeper snapshot <family>         # capture full snapshot
python -m keeper validate <family>         # quality rubric + lint checks
python -m keeper recover <family>          # produce recovery brief
python -m keeper complete <family>         # mark session done
python -m keeper install-hooks             # SessionStart / PreCompact / SessionEnd
```

Run `keeper install-hooks` once per repo to wire keeper into the harness lifecycle. See `keeper/README.md` for the full review-and-checkpoint workflow.

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
├── modes/                 ← sermon, sheep, cruising, recipe, family-history, triad, adversarial-review, strategy
├── state/                 ← Runtime state (JSON output)
├── repo-modes.json        ← Repository-to-mode mapping
└── .env                   ← API keys (gitignored)
```

---

## Cognitive Memory — Slice 6 Observation Capture (ACTIVE in this repo)

This repo hosts the canonical hook + writer pair that other household repos reference. The wiring is already enabled in `.claude/settings.json` (commit `ca78cad`):

```json
"env": {
  "MEMORY_OBSERVATIONS_ENABLED": "true",
  "MEMORY_AUTO_OBSERVE_ENABLED": "true"
},
"hooks": {
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {"type": "command",
         "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/observe-tool-use.sh"}
      ]
    }
  ]
}
```

Per-call flow: bash wrapper reads stdin → gates on env flag → spawns detached Python writer (`orchestrator/hook_observe.py`) → wrapper exits 0. Writer hashes args via `_compute_args_hash`, classifies response, calls `record_observation`. Fail-closed: any error → exit 0, never blocks the tool call. Args SHA256-hashed before disk; raw values never persisted. Errors → `/tmp/observe-hook.err`.

Sibling repos enable by registering with the absolute path `/home/user/ken/.claude/hooks/observe-tool-use.sh` instead of `$CLAUDE_PROJECT_DIR/...` (the hook lives only here; siblings reference it).

Surface candidates after a session: `python3 orchestrator/memory_ops.py` then `import memory_ops; memory_ops.extract_candidates_from_observations(session_id)`. Measured cost: 1.86 ms/call direct, 14.97 ms/call wrapper (detached writer keeps work off the critical path) — `python3 orchestrator/bench_hook.py` to re-measure.

Setup memory: id `5a9c8ae1`.
