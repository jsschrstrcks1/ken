---
name: consult
description: "Quick multi-LLM second opinion. Sends a single prompt to GPT, Gemini, Grok, You.com, or Perplexity with a role-based system prompt and returns structured feedback."
---

# Consult — Quick Second Opinion

*One model. One question. Structured feedback.*

## Usage

```
/consult <model> <role> "prompt text"
```

### Models
- **gpt** — OpenAI GPT (strong at structure, planning)
- **gemini** — Google Gemini (strong at expansion, cross-references)
- **grok** — xAI Grok (strong at challenge, adversarial thinking)
- **youdotcom** — You.com Search (strong at web search, sourced snippets)
- **perplexity** — Perplexity Sonar (strong at web-grounded research, cited answers)

### Roles
- **challenge** — Push back on assumptions, surface weak reasoning
- **expand** — Add context, cross-references, historical background
- **structure** — Review logical flow and organization
- **critique** — Evaluate accuracy, completeness, clarity
- **plan** — Produce structured plans with steps and risks
- **safety** — Flag risks, errors, unsafe recommendations
- **freestyle** — General-purpose response

---

## Backend Invocation

**IMPORTANT: Execute these commands directly using the Bash tool. Do NOT check if files exist first — just run them.**

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null; pip3 install -q -r /home/user/ken/orchestrator/requirements.txt 2>/dev/null && python3 /home/user/ken/orchestrator/consult.py <model> <role> "prompt text"
```

**Output:** JSON response to stdout with keys: `analysis`, `proposed_update`, `risks`, `confidence`
**Usage stats:** Printed to stderr (model, tokens, cost)
