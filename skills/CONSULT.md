# Consult — Quick Second Opinion

*One model. One question. Structured feedback.*

Adapted from jsschrstrcks1/ken `.claude/skills/consult/SKILL.md` for OpenClaw/Skynet.

---

## What This Is

A quick way to get a second opinion from a specific model on a targeted question,
without running a full orchestration pipeline. Fast, targeted, purposeful.

## When to Use

- You want to pressure-test an idea before committing
- You want a different model's perspective on a specific claim
- You need web-grounded research (Gemini, Perplexity)
- You want adversarial challenge (Grok)
- You want structure and breadth (GPT)
- You need deep local reasoning without privacy cost (Qwen)
- Full debate is overkill — just get one good second opinion

---

## Full Model Roster & Capability Profiles

### ✅ Frontier / Cloud Models (API keys confirmed active)

| Model | Best For | Weakness to Watch | Key |
|-------|----------|-------------------|-----|
| `openai/gpt-4o` | Structure, instruction-following, factual breadth, cross-checking, code | Agreeableness — validates bad ideas; verbose | `OPENAI_API_KEY` ✅ |
| `openai/gpt-4.1` | Fast reliable general-purpose, strong on code | Less reasoning depth than o3 | `OPENAI_API_KEY` ✅ |
| `openai/o3` | Proof-level logic, math, multi-step reasoning chains | Expensive, slow, over-explains | `OPENAI_API_KEY` ✅ |
| `google/gemini-2.5-pro` | Web-grounded research, real-time info, very long context, document synthesis | Overconfident on obscure or niche facts | `GEMINI_API_KEY` ✅ |
| `google/gemini-2.0-flash` | Fast cheap research pass, quick web queries | Lower ceiling on hard reasoning | `GEMINI_API_KEY` ✅ |
| `xai/grok-3` | Adversarial challenge, unconventional angles, real-time X/web, less constrained | Can go off-piste; verify claims | `XAI_API_KEY` ✅ |
| `xai/grok-3-fast` | Same as grok-3, faster, slightly less thorough | Less depth than grok-3 | `XAI_API_KEY` ✅ |
| `claude-opus-4-6` | Hardest sub-problems, theological depth, complex multi-step reasoning | Slow + expensive — reserve for high stakes | `ANTHROPIC_API_KEY` ✅ |
| `claude-sonnet-4-6` | Me — default lead for everything | — | `ANTHROPIC_API_KEY` ✅ |
| `claude-haiku-4-5` | Fast lightweight Claude for quick checks | Less depth | `ANTHROPIC_API_KEY` ✅ |
| `openrouter/auto` | Unified access to 275+ models, cost arbitrage | Router adds latency; model varies | `OPENROUTER_API_KEY` ✅ |

### ✅ Local Ollama Cluster (Ken's hardware — zero cost, zero privacy risk)

| Model | Best For | Host |
|-------|----------|------|
| `qwen3:32b` | Deep reasoning, structured analysis, theology, flock decisions | m4max |
| `qwen2.5:32b-instruct-q4_K_M` | Broad knowledge, general-purpose, reliable output | m4max |
| `qwen3:14b` | Fast general + adversarial challenge, code | m3pro |
| `deepseek-coder-v2:16b` | Code-specialized, technical precision, architecture | m3pro |
| `qwen2.5-coder:7b` | Fast code, iterative edits | m4mini |
| `llava:13b` | Vision — images, diagrams, visual content | m4max |

### ❌ Not Yet Configured (would need additional setup)

| Provider | Models | What They'd Add |
|----------|--------|-----------------|
| `groq` | qwen-3-235b, deepseek-r1 | Ultra-fast inference on large models |
| `mistral` | devstral-medium, codestral | Code + European perspective |
| `you.com` | You.com hybrid | Web search + AI hybrid; real-time |

---

## Roles

| Role | What It Does | Best Model |
|------|-------------|------------|
| **challenge** | Push back on assumptions, surface weak reasoning | Grok, `qwen3:14b` |
| **expand** | Add context, cross-references, historical background | GPT, `qwen2.5:32b` |
| **structure** | Review logical flow and organization | GPT, `qwen3:32b` |
| **critique** | Evaluate accuracy, completeness, clarity | `qwen3:32b`, Opus |
| **research** | Web-grounded current information | Gemini, Perplexity |
| **plan** | Structured plans with steps and risks | GPT, `qwen3:32b` |
| **safety** | Flag risks, errors, unsafe recommendations | Claude (me) |
| **code** | Implementation, review, debugging | DeepSeek, `qwen2.5-coder`, o3 |
| **logic** | Proof, math, multi-step reasoning | o3, `qwen3:32b` |
| **adversarial** | Devil's advocate, assumption stress-test | Grok, `qwen3:14b` |
| **vision** | Image/diagram analysis | `llava:13b` |
| **freestyle** | General-purpose response | Varies |

---

## Graceful Failure Protocol

If the requested model is unavailable:

| Unavailable | First Fallback | Second Fallback | Flag |
|-------------|---------------|-----------------|------|
| `openai/gpt-4o` | `openrouter/openai/gpt-4o` | `qwen2.5:32b` | If local: note depth loss |
| `openai/o3` | `openai/gpt-4o` | `qwen3:32b` | Note reasoning depth reduced |
| `google/gemini-2.5-pro` | `google/gemini-2.0-flash` | `qwen3:32b` + web_search | Web-grounding lost; flag |
| `xai/grok-3` | `xai/grok-3-fast` | `qwen3:14b` | Real-time X/web data lost; flag |
| `claude-opus-4-6` | `claude-sonnet-4-6` (elevated effort) | — | Flag reduced depth |
| `openrouter/auto` | Local Ollama cluster | — | Flag if budget issue |
| `qwen3:32b` | `qwen2.5:32b` | `qwen3:14b` | Near-equivalent |

**Fund exhaustion handling:**
- If an API returns 429/quota exceeded: route to OpenRouter first (budget buffer)
- If OpenRouter also exhausted: fall back to local Ollama
- Never hallucinate what a failed model "would have said"
- Always name the gap: `⚠️ [provider] quota exceeded — using [fallback] instead`

---

## Strength/Weakness Matrix

| Task | Best Choice | Watch Out For |
|------|-------------|---------------|
| Factual breadth + accuracy | GPT-4o | Over-agreeing with my draft |
| Heavy logic / proofs | o3 | Slow; may over-explain |
| Real-time web research | Gemini 2.5 Pro + Perplexity | Overconfidence on obscure facts |
| Adversarial challenge | Grok-3 | Going off-piste; verify claims |
| Deep analysis / theology | Opus or `qwen3:32b` | Slow; expensive for Opus |
| Code (architecture) | DeepSeek-Coder or o3 | Code tunnel vision |
| Code (fast iteration) | `qwen2.5-coder:7b` | Limited depth |
| Privacy-sensitive content | Local Ollama only | — |
| Cost-sensitive task | `qwen3:14b` or Haiku | Reduced depth vs 32b |
| Vision / images | `llava:13b` | Weaker text reasoning |

---

## Usage

Say something like:
- "Consult GPT on the structure of this sermon outline"
- "Get Grok to challenge this breeding plan"
- "Ask Gemini to research current FAMACHA scoring protocols"
- "Consult qwen3:32b to analyze this family history source conflict"
- "Get DeepSeek to review this code"
- "Use o3 to check the logic in this argument"

---

## Ken's Projects — Default Consult Patterns

| Project | Quick Consult |
|---------|---------------|
| Romans sermons | `qwen3:32b` (depth) / Grok (challenge) / GPT (structure) |
| InTheWake content | GPT (breadth) / Gemini (web research) / `qwen2.5:32b` (structure) |
| Sheep / flock decisions | `qwen3:32b` (reasoning) / `qwen3:14b` (challenge) — local preferred |
| Family History | Gemini (web research) / `qwen3:32b` (deep analysis) |
| Recipe work | GPT (generation) / `qwen3:14b` (safety challenge) |
| Code / technical | `deepseek-coder-v2:16b` (precision) / `qwen2.5-coder:7b` (fast) / o3 (logic) |
| Real-time info | Gemini (web-grounded) / Grok (live data) / Perplexity (citations) |
| Logic / math | o3 / `qwen3:32b` |

---

## Privacy Note

Before sending to any frontier model (GPT, Gemini, Grok), apply the privacy filter:

| Data | Frontier OK? |
|------|-------------|
| Congregation member names | ❌ Local only |
| Pastoral counseling details | ❌ Local only |
| Sobriety companion client details | ❌ Local only |
| Living family members' sensitive info | ❌ Local only |
| Sermon theology, outlines, arguments | ✅ |
| Sheep names and flock data | ✅ |
| InTheWake content (public site) | ✅ |
| Family history at public record level | ✅ |
| API keys / credentials | ❌ Never anywhere |

---

## Model Configuration Status

| Provider | Status | Auth |
|----------|--------|------|
| Anthropic (Claude) | ✅ Active | `ANTHROPIC_API_KEY` in env |
| Ollama (local cluster) | ✅ Active | No key needed |
| OpenAI (GPT-4o, gpt-4.1, o3) | ✅ Active | `OPENAI_API_KEY` in env |
| Google (Gemini 2.5 Pro, 2.0 Flash) | ✅ Active | `GEMINI_API_KEY` in env |
| xAI (Grok-3, Grok-3-fast) | ✅ Active | `XAI_API_KEY` in env |
| OpenRouter (275+ models) | ✅ Active | `OPENROUTER_API_KEY` in env |
| Perplexity (search tool) | ✅ Active | `PERPLEXITY_API_KEY` in env |
| Groq | ❌ Not configured | Add `GROQ_API_KEY` |
| Mistral | ❌ Not configured | Add `MISTRAL_API_KEY` |
| You.com | ❌ Not configured | Add key |

---

*Skynet note: This is a consultation layer, not a replacement for my judgment.
I integrate what's useful and discard what doesn't fit.*
