# Orchestra — Round-Robin Multi-LLM Debate

> Ask the orchestra. Let them debate. Take what survives.

Adapted from jsschrstrcks1/ken `.claude/skills/orchestra/SKILL.md` for OpenClaw/Skynet.

---

## What This Is

Unlike the linear pipeline (`ORCHESTRATE.md`), orchestra runs a round-robin debate 
where each model sees EVERYTHING from prior rounds — proposals, verdicts, justifications, 
and rejections. Nothing is filtered between rounds.

**The key difference:** What one model calls chaff, the next might rescue.

---

## How It Works

### Round 1: GPT Proposes
- Receives: task + relevant context/memories
- Produces: proposals (with confidence + justification), low-hanging fruit

### Round 2: Gemini Refines
- Receives: task + GPT's FULL response
- For each GPT proposal: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT (with justification)
- Adds own proposals
- May rescue ideas GPT undervalued

### Round 3: Grok Challenges
- Receives: task + GPT's FULL response + Gemini's FULL response (including verdicts)
- For EVERY prior proposal: verdict + justification
- Specifically looks for dismissed ideas worth rescuing
- Identifies blind spots

### Blind Spot Check
- Grok (most contrarian model): "What is the single most important thing we're all still missing?"

### Synthesis (me/Claude)
- Sees the full debate chain: every proposal, every verdict, every justification
- Produces attributed plan: "GPT proposed X, Gemini refined to Y, Grok challenged Z"
- I do not filter between rounds — the whole debate informs the synthesis

---

## Why Full Context Matters

If I filter between rounds, rejected ideas die silently. With full context:
- Gemini can disagree with GPT's *reasoning*, not just its conclusions
- Grok can rescue an idea Gemini dismissed, explaining WHY Gemini was wrong
- The final synthesis is informed by the **debate**, not just the survivors

---

## When to Use

**Use orchestra when:**
- A single linear pipeline is too narrow
- You want models to genuinely argue
- The question is genuinely hard and benefits from adversarial pressure
- You suspect there's a non-obvious answer that consensus would kill

**Skip orchestra when:**
- One-shot simple edits — overhead isn't worth it
- You just need a quick second opinion (use `/consult` instead)
- Speed matters more than thoroughness

---

## Cost

Typical: $0.03–$0.08 per full orchestra run (all 3 external models + synthesis).
More expensive than `/consult`, less than `/orchestrate` full pipeline.

---

## How to Request

Say something like:
- "Run an orchestra on the InTheWake content strategy"
- "Orchestra: should we cull or keep Gigi this season?"
- "Get the full orchestra debate on this sermon structure"
- "Orchestra: design the breeding pen layout for parasite-resistance selection"

---

*Soli Deo Gloria — Let the orchestra play. Take what survives.*

*Skynet note: I synthesize, I don't aggregate. The models debate; I decide what's worth keeping.*
