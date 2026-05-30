# DEBATE Skill — Adversarial Multi-Model Synthesis

## Description
Run an adversarial multi-model debate where Grok, GPT, Gemini, and local Ollama models challenge each other's answers. Claude synthesizes the winner. Use when: "debate this", "have Grok try to out-code you", "adversarial analysis", "get multiple models arguing", "challenge this", "think this through with multiple models", or any hard problem with real stakes.

## Location
See DEBATE.md in this directory for full protocol.

## Quick Start

1. Read `DEBATE.md` in this skill directory for the full architecture
2. Decompose the problem into sub-problems (Phase 0)
3. Farm to independent models without cross-contamination (Phase 1)
4. Run cross-examination — each model evaluates others (Phase 2)
5. Defense round for anything labeled CHAFF (Phase 3)
6. Claude synthesizes — wheat selected, chaff rejected, final output (Phase 4)

## Triggers (autofire on these phrases)
- "debate this"
- "have Grok / GPT / Gemini try to [do X]"
- "adversarial analysis"
- "out-code you" / "beat you" / "challenge you"
- "get multiple models arguing"
- "think this through" (when the problem is genuinely hard)
- "multiple opinions" / "second opinion from [specific model]"

## For Code Challenges (Grok vs Claude)

**Default adversarial code team:**
- **Grok-3** (`xai/grok-3`) — adversarial challenger, unconventional angles
- **Claude-Sonnet** (me) — lead implementation + final synthesis
- **o3 or qwen3:32b** — logic/correctness verification

**Pattern:**
1. I propose a solution
2. Grok critiques it + proposes its own
3. Cross-examine: which is actually better?
4. I synthesize the winner (could be Grok's, could be mine, could be a hybrid)

## Privacy
- Code problems: cloud models OK
- Congregation/counseling/sobriety data: local Ollama ONLY
- See DEBATE.md Privacy Boundaries table
