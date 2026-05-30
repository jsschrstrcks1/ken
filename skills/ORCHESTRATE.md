# Orchestrate — Multi-LLM Pipeline

*Multi-model linear pipeline. Each domain has its own flow.*

Adapted from jsschrstrcks1/ken `.claude/skills/orchestrate/SKILL.md` for OpenClaw/Skynet.

---

## What This Is

A structured multi-model pipeline where different AI models play specific roles
depending on the domain. Not a free-for-all — disciplined pipelines, mode-specific.

**Core principle from Ken's architecture:**
> Claude leads. All other models consult.
> Synthesis over voting. Human authority is primary.

---

## Full Model Roster

### ✅ Frontier / Cloud (API keys confirmed active)

| Model | Role in Pipeline | Strength | Weakness |
|-------|-----------------|----------|----------|
| `claude-sonnet-4-6` | **Me — lead, synthesizer, judge** | Judgment, nuance, integration, writing quality | Occasionally hedges |
| `claude-opus-4-6` | Heavy lifting, hardest sub-problems | Deepest reasoning, theological depth | Slow, expensive |
| `claude-haiku-4-5` | Fast/cheap Claude for light passes | Quick and cheap | Less depth |
| `openai/gpt-4o` | Breadth, structure, instruction-following | Broad knowledge, reliable, strong benchmarks | Agreeable — may validate bad drafts; verbose |
| `openai/gpt-4.1` | General workhorse, code | Fast, reliable for GPT tier | Less depth than o3 |
| `openai/o3` | Logic, math, multi-step proofs | Proof-level reasoning, hard chains | Expensive, slow |
| `google/gemini-2.5-pro` | Web research, long context, real-time info | Grounded research, document synthesis | Overconfident on niche facts |
| `google/gemini-2.0-flash` | Fast web research sweep | Quick, cheap | Lower ceiling |
| `xai/grok-3` | Adversarial challenge, unconventional angles | Real-time X/web, less constrained, direct | Can go off-piste; verify claims |
| `xai/grok-3-fast` | Speed-sensitive adversarial passes | Faster than grok-3 | Slightly less thorough |
| `openrouter/auto` | Budget buffer, fallback, exotic models | 275+ models, cost arbitrage | Adds latency |

### ✅ Local Ollama Cluster (Ken's hardware — zero cost, zero privacy risk)

| Model | Role | Best Domain | Host |
|-------|------|-------------|------|
| `qwen3:32b` | Deep reasoning, analysis | Theology, breeding plans, family history, hard analysis | m4max |
| `qwen2.5:32b-instruct-q4_K_M` | Broad general, content gen | Cross-checking, content generation, structure | m4max |
| `qwen3:14b` | Fast + adversarial | Challenge rounds, code, quick tasks | m3pro |
| `deepseek-coder-v2:16b` | Code precision | Implementation, architecture, debugging | m3pro |
| `qwen2.5-coder:7b` | Fast code | Small patches, fast iteration | m4mini |
| `llava:13b` | Vision | Images, diagrams, visual content | m4max |

### 🔍 Search / Research Tools (active)

| Tool | Use | Key |
|------|-----|-----|
| Perplexity | Cited web research | `PERPLEXITY_API_KEY` ✅ |
| Grok search | Real-time X/web | `XAI_API_KEY` ✅ |
| Gemini search | Google web-grounded | `GEMINI_API_KEY` ✅ |
| DuckDuckGo | Private web search | — ✅ |

### ❌ Not Yet Configured

| Provider | Models | What They'd Add |
|----------|--------|-----------------|
| `groq` | qwen-3-235b, deepseek-r1 | Ultra-fast inference on large models |
| `mistral` | devstral-medium, codestral | Code + European perspective |
| `you.com` | You.com hybrid | Web + AI hybrid |

---

## Graceful Failure Protocol

API failures, budget exhaustion, and model timeouts are expected. Handle gracefully:

| Failure | Action |
|---------|--------|
| Model times out | `⚠️ [model] timed out` — substitute from fallback chain, keep pipeline moving |
| API key missing | `⚠️ [provider] not configured` — route to local equivalent |
| Budget exhausted | `⚠️ [provider] quota exceeded` — route to OpenRouter first, then local |
| Model returns garbage | Discard, note, move on — don't polish garbage into the pipeline |
| Multiple failures (≥2 stages) | Report degradation to Ken before delivering output |
| Full frontier outage | Run local-only pipeline with explicit notice |

### Provider-Specific Fallback Chain

| Unavailable | First Fallback | Second Fallback | Note |
|-------------|---------------|-----------------|------|
| `openai/gpt-4o` | `openrouter/openai/gpt-4o` | `qwen2.5:32b` | Flag if local |
| `openai/o3` | `openai/gpt-4o` | `qwen3:32b` | Note reasoning depth reduced |
| `google/gemini-2.5-pro` | `google/gemini-2.0-flash` | `qwen3:32b` + web_search | Web-grounding degraded; flag |
| `xai/grok-3` | `xai/grok-3-fast` | `qwen3:14b` | Real-time data lost; flag |
| `claude-opus-4-6` | `claude-sonnet-4-6` (elevated effort) | — | Flag reduced depth |
| `qwen3:32b` | `qwen2.5:32b` | `qwen3:14b` | Near-equivalent |
| `openrouter/auto` | Local Ollama cluster | — | Flag budget issue |

**Fund exhaustion / API billing:**
- 429/quota → OpenRouter (budget buffer across providers)
- OpenRouter also exhausted → local Ollama (no cost)
- Never fabricate what a failed model "would have said"
- Always name the substitution and the reason

---

## Modes

### Sermon Mode (lead: me/Claude)

```
Draft (Claude) → Challenge (Grok-3 | qwen3:14b) → Expand (qwen3:32b)
→ Structure (GPT-4o | qwen2.5:32b) → Integrate (Claude) → Evaluate (Claude) → Voice Audit
```

- Claude writes, evaluates, integrates
- Grok provides adversarial challenge; `qwen3:14b` if Grok unavailable
- GPT reviews structure and flow; `qwen2.5:32b` if GPT unavailable
- Local models for congregation privacy — never send member names externally
- Context boundary: send outlines, claims, cross-references — NOT pastoral application specifics

### Sheep Mode (lead: qwen3:32b — local-only)

```
Plan (qwen3:32b) → Context (qwen2.5:32b) → Challenge (qwen3:14b) → Validate (Claude) → Finalize (Claude)
```

- All local — privacy irrelevant, faster, free
- qwen3:32b plans; Claude validates against flock records, pedigree, health data
- Claude's validation is substantive, not a rubber stamp

### Cruising / InTheWake Mode (lead: me/Claude)

```
Read Standards (Claude) → Generate (Claude) → Content (qwen2.5:32b | GPT-4o)
→ Web-Ground (Gemini 2.5 Pro | web_search) → Completeness (qwen3:32b)
→ UX/Web (qwen3:14b) → Integrate (Claude)
```

- Claude enforces ICP-2 — the standard is non-negotiable
- Gemini valuable for grounding cruise/port facts in real-world data
- GPT substitutes for `qwen2.5:32b` on content generation when useful

### Recipe Mode (lead: qwen2.5:32b)

```
Generate (qwen2.5:32b | GPT-4o) → Expand/Nutrition (qwen3:32b) → Safety (Claude) → Creative Variation (qwen3:14b)
```

- Single-pass preferred; full pipeline for complex tasks
- Claude handles safety (temps, allergens, cross-contamination) — non-negotiable
- GPT-4o can lead if the recipe category is broad/complex

### Family History Mode (lead: me/Claude)

```
Load Context (Claude) → Extract/Draft (Claude) → Verify (qwen3:32b)
→ Web Research (Gemini 2.5 Pro | Perplexity | web_search) → Expand (qwen2.5:32b)
→ Challenge (qwen3:14b) → Synthesize (Claude)
```

- Source hierarchy is absolute: Family Bible > Cathedral records > secondary sources
- Conflicts flagged, never silently resolved
- Gemini's web-grounding valuable; Perplexity for cited sources; fall back to web_search
- Living family members — never send externally

### Triad Mode (general-purpose three-model review)

```
Plan (qwen3:32b) → Build (qwen2.5:32b) → Verify (qwen3:14b) — verdict-driven, max 1 revision
```

- Use for: ambiguous specs, large decisions, "did we solve the right problem"
- Skip for: simple one-shot tasks
- If frontier models are available and stakes are high → escalate to DEBATE mode

### Code Mode (lead: deepseek-coder-v2:16b)

```
Draft (deepseek-coder-v2:16b) → Review (qwen2.5-coder:7b) → Logic/Security (Claude) → Finalize (Claude)
```

- DeepSeek leads on implementation; Claude judges correctness and safety
- Never deploy without Claude's review
- o3 for logic-heavy code problems (proofs, algorithms, correctness)
- GPT-4.1 as general code fallback

### Research Mode (lead: Gemini + Perplexity)

```
Web-Ground (Gemini 2.5 Pro + Perplexity) → Structure (GPT-4o | qwen3:32b)
→ Challenge claims (Grok-3) → Synthesize (Claude)
```

- Use when current events, real-time data, or web-grounded facts are needed
- Perplexity provides cited sources; Gemini provides synthesis
- Grok challenges conventional takes and adds X/social signal
- Claude synthesizes and flags any unverified claims

---

## Hallucination Defense

Multi-model pipelines amplify hallucinations if unchecked: one model fabricates,
the next treats it as fact, I polish it into confident nonsense.
Frontier models — GPT, Gemini, Grok — are NOT immune.

| Claim Type | Verification |
|-----------|-------------|
| Scripture reference | Check exact ESV text |
| Attributed quote | Check against known sources |
| Theological claim | Flag for human review |
| Livestock/flock data | Check against flock records |
| Website standards | Check against ICP-2 / InTheWake HANDOFF.md |
| Family history fact | Source hierarchy applies |
| Current events | Gemini/Grok/Perplexity web-grounded data preferred |
| Any unverifiable claim | `⚠️ UNVERIFIED — requires confirmation` |

Two models agreeing ≠ truth. Consensus doesn't clear the flag.

---

## Privacy Boundaries

**Never send externally (to any cloud model):**
- API keys or credentials
- Congregation member names
- Pastoral counseling details
- Sobriety companion client details
- PII (health records, financial data)
- Living family member sensitive info

**Safe to send:**
- Sermon outlines, theological claims, cross-references
- Flock data (sheep names, breeding records — public livestock)
- Recipe content
- Family history at public record level
- InTheWake / cruising content

---

## Loop Control

- **Max iterations: 2**
- Stop conditions: convergence (minimal delta), cost threshold, human override
- Synthesis over voting — extract best elements; never average outputs
- Human authority primary at every stage

---

## Model Configuration Status

| Provider | Status | Auth |
|----------|--------|------|
| Anthropic (Claude Sonnet, Opus, Haiku) | ✅ Active | `ANTHROPIC_API_KEY` in env |
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

## How to Request

Say something like:
- "Run the sermon pipeline on Romans 8:28-30"
- "Orchestrate a sheep breeding plan for fall"
- "Use the cruising pipeline to generate content for Norwegian Prima"
- "Triad review on this InTheWave redesign plan"
- "Code mode: build a FAMACHA tracking script"
- "Research mode: current FAMACHA protocols"

---

*Skynet note: I am the lead, not the committee. I take what's useful from consultants
and discard what doesn't fit. Human authority remains primary at every stage.*
