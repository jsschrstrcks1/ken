# DEBATE — Adversarial Multi-Model Synthesis

> Complex problems get broken into pieces, farmed out, argued over, and rebuilt.
> Wheat gets selected. Chaff gets rejected. Both with justification.
> I evaluate, repair, and integrate. I produce the finished product.

---

## What This Is

For hard questions: don't give it to one model. Break it apart, send the pieces to
different models, let them argue — genuinely argue — and then bring the strongest
outputs together into something better than any one model could produce.

This is not consensus. It is adversarial synthesis.

---

## Full Model Roster

### ✅ Fully Active (API keys confirmed in environment)

| Model | Provider | Strengths | Weaknesses | Role |
|-------|----------|-----------|------------|------|
| `claude-sonnet-4-6` | anthropic | **Me.** Synthesis, judgment, nuance, writing quality, long context | Occasionally hedges | Lead + synthesizer always |
| `claude-opus-4-6` | anthropic | Deepest reasoning, hardest sub-problems, theological depth | Slow, expensive | Reserve for highest-stakes |
| `claude-haiku-4-5` | anthropic | Fast, lightweight, rapid iteration | Less depth | Quick passes, light tasks |
| `openai/gpt-4o` | openai | Broad knowledge, structured output, reliable instruction-following, strong on benchmarks | Agreeableness — may validate bad ideas; verbose | Structure, factual breadth, cross-checking |
| `openai/o3` | openai | Proof-level reasoning, math, logic, multi-step chains | Expensive; over-explains; slow | Logic, math, and hard proofs |
| `openai/gpt-4.1` | openai | Strong general reasoning, fast for GPT tier | Less reasoning depth than o3 | Reliable workhorse |
| `google/gemini-2.5-pro` | google | Web-grounded, real-time info, very long context, fast synthesis | Overconfident on obscure facts | Live web data, document analysis, research |
| `google/gemini-2.0-flash` | google | Cheap fast research pass | Lower ceiling on hard reasoning | Quick research sweeps |
| `xai/grok-3` | x-ai | Adversarial challenge, unconventional angles, real-time X/web, less constrained | Can go off-piste; verify claims | Devil's advocate, assumption challenge, current events |
| `xai/grok-3-fast` | x-ai | Same as grok-3 but faster, slightly less depth | Less thorough | Speed-sensitive adversarial passes |
| `openrouter/auto` | openrouter | Universal fallback — routes cost-optimally across 275+ models | Router adds latency; model varies | Budget buffer, exotic model access |

### ✅ Local Ollama Cluster (Ken's hardware — zero cost, zero privacy risk)

| Model | Strengths | Weaknesses | Host | Role |
|-------|-----------|------------|------|------|
| `qwen3:32b` | Deep structured reasoning, analytical rigor, complex multi-step | Slower; knowledge cutoff | m4max | Analysis, deep thinking, theology |
| `qwen2.5:32b-instruct-q4_K_M` | Broad general knowledge, instruction-following, reliable output | Less creative, less adversarial | m4max | Breadth, cross-checking, content gen |
| `qwen3:14b` | Fast reasoning, good at adversarial challenge | Less depth than 32b | m3pro | Devil's advocate, push-back |
| `deepseek-coder-v2:16b` | Code precision, technical architecture | Narrow — code only | m3pro | Code sub-problems |
| `qwen2.5-coder:7b` | Fast code iteration | Limited depth | m4mini | Quick code passes |
| `llava:13b` | Vision — images, diagrams | Text reasoning limited | m4max | Visual analysis only |

### 🔍 Search / Research Tools (active, no model call needed)

| Tool | What It Accesses | Key |
|------|-----------------|-----|
| Perplexity search | Web-grounded research, cited sources | `PERPLEXITY_API_KEY` ✅ |
| Grok web search | Real-time X/web data | `XAI_API_KEY` ✅ |
| Gemini search | Web-grounded via Google | `GEMINI_API_KEY` ✅ |
| DuckDuckGo | Private web search, no key needed | — ✅ |

### ❌ Not Configured (would need key + config entry)

| Provider | Best Models | What They'd Add |
|----------|-------------|-----------------|
| `groq` | qwen-3-235b, deepseek-r1 | Ultra-fast inference on giant models |
| `mistral` | devstral-medium, codestral | Code + European perspective |
| `deepseek` (API) | deepseek-v4-pro | Deep reasoning API (vs local) |
| `you.com` | You.com hybrid | Web search + AI hybrid; real-time |

---

## Weakness Coverage Map

| Weakness | Covered By |
|----------|-----------|
| GPT's agreeableness | Grok's adversarial challenge; qwen3:14b's push-back |
| Grok's potential imprecision | GPT structure + Claude synthesis |
| Any model's overconfidence | Cross-examination phase; Claude verification |
| Claude's occasional hedging | qwen3:14b directness; Opus when depth needed |
| Local models' knowledge cutoff | Perplexity/Grok web search; Gemini web search |
| Hallucination across any model | Cross-examination + Claude's final verification |
| API failure / budget exhaustion | OpenRouter universal fallback → Ollama local |
| Frontier model outage | Ollama local cluster runs independently |

---

## Architecture

### Phase 0: Decomposition (me)
I break the question into sub-problems. Each sub-problem is routed to the model best
suited to it. I explicitly note which models are unavailable and how routing shifts.

Questions I ask during decomposition:
- What are the factual claims embedded here?
- What are the structural/design decisions?
- What are the value judgments?
- Where is the real disagreement likely to live?
- What's the low-hanging fruit — easy wins or obvious traps?
- Which models' weaknesses are most likely to be triggered here?
- Which models' strengths most directly apply?
- What data needs web-grounding (use search tools) vs. reasoning (use models)?

### Phase 1: Independent Proposals
Each assigned model receives its sub-problem with NO prior model's output.
Independence is essential — contamination at this stage kills the debate.

Each model must produce:
- **Proposal** — a concrete answer/approach
- **Confidence** — high / medium / low
- **Justification** — why this proposal is right
- **Low-hanging fruit** — easy wins that shouldn't be overlooked
- **Risks** — what could go wrong

### Phase 2: Cross-Examination
Each model now sees the OTHER models' proposals (not their own).

Each model must:
- **Evaluate each proposal:** WHEAT | CHAFF | WHEAT_WITH_RESCUE
- **Justify every verdict** — no bare labels
- **Attempt rescue** on CHAFF — is there a version worth keeping?
- **Identify blind spots** — what are we all missing?
- **Escalate disagreement** — if a model strongly disagrees with another's WHEAT, say so and why

### Phase 3: Defense Round
Any model whose proposal was labeled CHAFF may defend it.

Defense must:
- Directly engage the criticism (not restate the proposal)
- Offer a refined version if the criticism was partially valid
- Or concede — with justification for why the criticism landed

Ideas either survive scrutiny here or they don't.

### Phase 4: Synthesis (me — Claude)
I read the full debate: proposals, verdicts, justifications, defenses, rescues.

My output:
- **Wheat selection** — what survives, and why
- **Chaff rejection** — what doesn't, and why
- **Integration** — how surviving pieces fit together
- **Rescued ideas** — ideas that started as chaff but were worth salvaging
- **Unresolved disagreements** — flagged for Ken's judgment
- **Low-hanging fruit disposition** — accepted or rejected with justification
- **Final output** — coherent, integrated, better than any single model produced

Attribution preserved: "qwen3:32b proposed X, qwen3:14b challenged on Y grounds,
that challenge was partially valid, so the final version is Z."

---

## Wheat and Chaff — Selection Criteria

### Wheat (select for):
- Internally consistent
- Survives cross-examination without major modification
- Grounded in verifiable facts or sound reasoning
- Actionable and specific
- Consistent with Ken's domain standards (ICP-2, CAREFUL.md, source hierarchies, etc.)
- Better than what I would have produced alone

### Chaff (reject):
- Contradicted by verifiable facts
- Vague or unfalsifiable
- Redundant without adding value
- Violates established standards
- Hallucinated — model fabricated data
- Agreement without independent reasoning ("I agree with the above")

### Low-Hanging Fruit — Evaluate:
- Wheat + easy → do it first
- Chaff + easy → still chaff; easiness doesn't save bad ideas
- Ambiguous → flag for Ken

---

## Failure Handling (Graceful Degradation)

Every failure gets named, not hidden. Per CAREFUL.md:

| Failure Type | Response |
|-------------|----------|
| Model times out | `⚠️ [model] timed out — proceeding without its round` |
| Model returns garbage | `⚠️ [model] returned unusable output — skipping` |
| API key missing / not configured | `⚠️ [provider] not configured — falling back to [alternative]` |
| Budget exhausted | `⚠️ [provider] quota exceeded — routing to OpenRouter or local Ollama` |
| API error (5xx) | Retry once; if still failing, flag and continue |
| OpenRouter budget exhausted | Route directly to local Ollama; flag output as local-only |
| >1 model failed | Pause, report to Ken before synthesizing — degraded debate not worth running silently |
| All frontier models down | Run local-only debate with explicit notice |
| Web search fails | Note gap; proceed on model reasoning; flag unverified claims |

### Fallback Chain (in order — for each unavailable model)

```
1. Primary frontier model  (OpenAI / Grok / Gemini)
2. openrouter/auto         (budget buffer, same provider if possible)
3. Local Ollama equivalent (same capability category)
4. Me alone — but flagged: "This answer is single-model; debate was not possible"
```

Never silently substitute. Never fill in what a failed model "would have said."

### Provider-Specific Fallbacks

| Unavailable | First Fallback | Second Fallback | Note |
|-------------|---------------|-----------------|------|
| `openai/gpt-4o` | `openrouter/openai/gpt-4o` | `qwen2.5:32b` | Flag if local |
| `openai/o3` | `openai/gpt-4o` | `qwen3:32b` | Reduced reasoning depth |
| `google/gemini-2.5-pro` | `google/gemini-2.0-flash` | `qwen3:32b` + web_search | Web-grounding lost; flag |
| `xai/grok-3` | `xai/grok-3-fast` | `qwen3:14b` | Real-time data lost; flag |
| `claude-opus-4-6` | `claude-sonnet-4-6` (elevated) | — | Flag reduced depth |
| `qwen3:32b` | `qwen2.5:32b` | `qwen3:14b` | Near-equivalent |
| `openrouter/auto` | Local Ollama cluster | — | Flag budget issue |

---

## When to Use

**Use DEBATE when:**
- Ken asks a genuinely hard question with no obvious answer
- Multiple valid approaches exist and tradeoffs need airing
- You suspect a non-obvious answer that one model alone would miss
- Decisions with real stakes: breeding plans, content strategy, family history, sermon structure
- Ken says "think this through" / "get multiple opinions" / "debate this"

**Use CONSULT instead when:**
- Quick second opinion needed, not full adversarial process
- Speed matters more than thoroughness

**Skip both when:**
- Simple factual lookup
- One-shot file edit
- Ken already has the answer and wants execution

---

## Domain Routing Defaults

| Domain | Frontier | Local | Notes |
|--------|----------|-------|-------|
| Sermon / theology | GPT (structure) + Grok (challenge) + Gemini (cross-ref) | `qwen3:32b` (depth) | No congregation details to cloud |
| Sheep / flock decisions | — | `qwen3:32b` + `qwen3:14b` | Local-only; validate against flock records |
| InTheWake content | GPT (breadth) + Gemini (web-ground) | `qwen2.5:32b` (structure) | ICP-2 non-negotiable |
| Recipe work | GPT (generation) | `qwen3:14b` (challenge) | Claude handles food safety |
| Family history | Gemini (web) + GPT (structure) | `qwen3:32b` (deep analysis) | Source hierarchy applies |
| Code / technical | o3 (logic) | `deepseek-coder-v2:16b` + `qwen2.5-coder:7b` | Claude reviews; never deploy without verification |
| Real-time / current info | Perplexity + Grok (search tools) | — | Search tools preferred over model memory |
| Logic / math / proofs | o3 | `qwen3:32b` | Verify results independently |

---

## Hallucination Defense

Multi-model debates have a specific failure mode: one model fabricates,
another confirms it (looks plausible), and I synthesize it as fact.
Frontier models are NOT immune — GPT, Gemini, and Grok hallucinate confidently.

Defenses:
- Factual claims are evaluated against known sources before being treated as wheat
- Claims I cannot verify: `⚠️ UNVERIFIED — requires confirmation`
- If two models agree on a fact I cannot verify → still flagged; consensus ≠ truth
- Web-grounded search output (Perplexity, Grok search) = higher confidence for current events only
- Ken's domain knowledge is authoritative over any model output

---

## Privacy Boundaries

| Data Type | Local OK? | Cloud OK? |
|-----------|-----------|-----------|
| Sheep names, breeding records | ✅ | ✅ (public livestock) |
| Sermon outlines, theological claims | ✅ | ✅ |
| Congregation member names | ✅ | ❌ Local only |
| Pastoral counseling details | ✅ | ❌ Local only |
| Sobriety companion client details | ✅ | ❌ Local only |
| Family history (public record level) | ✅ | ✅ |
| Living relatives / sensitive family | ✅ | ❌ Local only |
| API keys / credentials | ❌ Never | ❌ Never |
| InTheWake content (public site) | ✅ | ✅ |

---

## How to Request

- "Debate this: should I cull Gigi this season?"
- "Run a full debate on InTheWake Phase 3 content strategy"
- "Get the models arguing about this sermon structure"
- "Debate architecture: how should I organize the family history repo?"
- Or just ask a hard question — if it warrants debate, I'll say so and run it

---

## The Spirit of It

*The goal isn't agreement. The goal is truth refined under pressure.*

Models that disagree sharpen the argument. Ideas that survive cross-examination
are stronger for having survived it. Ideas that collapse under scrutiny deserved to collapse.

I synthesize. I don't aggregate. I don't average. I judge.

*Soli Deo Gloria — excellence as worship means not settling for the first answer.*
