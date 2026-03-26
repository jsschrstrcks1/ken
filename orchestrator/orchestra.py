#!/usr/bin/env python3
"""
orchestra.py — Round-robin multi-LLM consultation with full-context debate.

Unlike orchestrate.py (linear pipeline), orchestra.py runs a round-robin
where each model sees ALL prior proposals + judgments + justifications,
and is asked to add, refine, rescue, and challenge.

Usage:
    python3 orchestra.py <mode> "task description"
    python3 orchestra.py cruising "build a new port page for Santorini"

Phases:
  1. RECALL      — Load relevant cognitive memories
  2. ORCHESTRA   — Round-robin: Claude proposes → GPT refines → Gemini expands → Grok challenges
                   Each model sees full chain + wheat/chaff justifications
  3. SYNTHESIZE  — Claude reviews full debate, gives own verdicts, produces attributed plan
  4. BLIND SPOT  — Final check: "what did we all miss?"
  5. REPORT      — Per-round costs, idea survival rate

Claude goes FIRST (has codebase + memory context), then external models
refine, expand, and challenge from their strengths. Claude returns at the
end to synthesize with its own verdicts and justifications.

Nothing is filtered between rounds. Full context flows forward.
What one model calls chaff, the next might rescue.
"""

import json
import os
import sys
import time
import yaml

# Load .env
_env_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    os.path.expanduser("~/.orchestrator.env"),
]
for _env_path in _env_candidates:
    if os.path.exists(_env_path):
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
        break

from adapters import ADAPTERS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "state")
MODES_DIR = os.path.join(SCRIPT_DIR, "modes")

# ─────────────────────────────────────────────
# Round-Robin Prompt Templates
# ─────────────────────────────────────────────

# Round 1 is Claude — handled locally in Claude Code, not via API.
# The orchestrator outputs a prompt for Claude to answer, then the user/Claude
# provides the Round 1 response which gets fed to the external models.

CLAUDE_ROUND1_PROMPT = """You are CLAUDE — the lead author and the model with the most context. You go FIRST in a round-robin consultation. Three other AI models (GPT, Gemini, Grok) will review your work, refine it, and challenge it.

TASK: {task}

CONTEXT FROM MEMORY:
{memory_context}

YOUR ROLE: Propose structure, approach, and innovations. You know the codebase, the user's preferences, and the project history. Use that knowledge.

For each proposal, provide:
- PROPOSAL: [your idea]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why this matters — be specific, reference what you know about the project]

ALSO: Identify any LOW-HANGING FRUIT — the easiest, highest-value wins.

The next three models will see everything you write. They will verdict each proposal as WHEAT, CHAFF, or WHEAT_WITH_REFINEMENT — with their justifications. Be thorough so they have something real to work with."""

ROUND_2_TEMPLATE = """You are the SECOND model in a round-robin consultation. CLAUDE (the lead author with codebase access) went first. You are reviewing Claude's work and adding your own.

TASK: {task}

ROUND 1 (from CLAUDE — the lead author):
{round1_response}

YOUR ROLE: For EACH of Claude's proposals, provide a verdict. Then add your own original proposals.

For each prior proposal, respond with:
- PROPOSAL_ID: [reference the proposal]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT
- JUSTIFICATION: [why — be specific about your reasoning]
- REFINEMENT: [if WHEAT_WITH_REFINEMENT, what changes would make it better]

NOTE: What you call CHAFF might be rescued by the next model. Explain your reasoning clearly so they can evaluate whether you're right.

Then add YOUR OWN proposals with:
- PROPOSAL: [your idea — something Claude didn't think of]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why this matters]

ALSO: What LOW-HANGING FRUIT is everyone overcomplicating? What's the easiest win?

Respond in JSON with "verdicts" array, "proposals" array, and "low_hanging_fruit" array."""

ROUND_3_TEMPLATE = """You are the THIRD model in a round-robin consultation. CLAUDE went first, then {round2_model} refined. You see both.

TASK: {task}

ROUND 1 (from CLAUDE — the lead author):
{round1_response}

ROUND 2 (from {round2_model}) — their verdicts on Claude's work + their own proposals:
{round2_response}

YOUR ROLE: For EACH proposal from BOTH prior rounds, provide a verdict. Then add your own.

For each prior proposal, respond with:
- PROPOSAL_ID: [reference]
- ORIGINAL_MODEL: [who proposed it]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT | RESCUED
- JUSTIFICATION: [why — be specific]
- REFINEMENT: [if applicable]

ALSO: What LOW-HANGING FRUIT is everyone overcomplicating?

Respond in JSON with "verdicts" array, "proposals" array, and "low_hanging_fruit" array."""

ROUND_4_TEMPLATE = """You are the FOURTH and final external model in a round-robin consultation. You see the FULL debate chain. Your job is to challenge everything, rescue dismissed ideas, and add what everyone missed.

TASK: {task}

ROUND 1 (from CLAUDE — the lead author):
{round1_response}

ROUND 2 (from {round2_model}) — their verdicts on Round 1 + their own proposals:
{round2_response}

ROUND 3 (from {round3_model}) — their verdicts on Rounds 1-2 + their own proposals:
{round3_response}

YOUR ROLE:
1. For EACH proposal from ALL prior rounds, provide a verdict
2. SPECIFICALLY look for ideas called CHAFF — are they really chaff, or wheat with modification?
3. Add your own proposals that ALL models missed
4. Identify the single biggest blind spot in the discussion

For each prior proposal, respond with:
- PROPOSAL_ID: [reference]
- ORIGINAL_MODEL: [who proposed it]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT | RESCUED (for ideas you're saving from the chaff pile)
- JUSTIFICATION: [why — be specific]
- REFINEMENT: [if applicable]

Then add YOUR OWN proposals, identify the BLIND_SPOT, and call out any LOW-HANGING FRUIT everyone is overcomplicating.

Respond in JSON with "verdicts" array, "proposals" array, "blind_spot" string, and "low_hanging_fruit" array."""

CLAUDE_SYNTHESIS_TEMPLATE = """You are CLAUDE returning for the FINAL SYNTHESIS. You proposed in Round 1. Three external models have now debated your proposals and added their own. You've seen the full chain.

TASK: {task}

YOUR ROUND 1 PROPOSALS:
{round1_response}

ROUND 2 ({round2_model}):
{round2_response}

ROUND 3 ({round3_model}):
{round3_response}

ROUND 4 ({round4_model}):
{round4_response}

YOUR ROLE: You are NOT a neutral summarizer. You are a participant with opinions. For EVERY proposal from ALL four rounds (including your own from Round 1):

1. Give your FINAL verdict: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT | RESCUED
2. Justify WHY — you may disagree with any model's reasoning, including revising your own Round 1 positions
3. If you rescue something, explain what the other models got wrong

Then produce an ATTRIBUTED PLAN — concrete next steps, crediting which model each step came from.

Respond with:
- "verdicts": array of proposals with your final call
- "revised_own_proposals": any of YOUR Round 1 proposals you'd now change based on the debate
- "attributed_plan": array of steps with source attribution
- "low_hanging_fruit": easiest wins from the whole debate"""

BLIND_SPOT_TEMPLATE = """You previously participated in a round-robin consultation. Here is the final synthesis.

TASK: {task}

FINAL SYNTHESIS:
{synthesis}

ONE QUESTION: What is the single most important thing this plan is still missing or getting wrong? Be specific and constructive. This is your last chance to flag something before execution.

Respond in JSON with: "blind_spot" (string), "severity" (HIGH|MEDIUM|LOW), "suggestion" (string)."""


# ─────────────────────────────────────────────
# Core Engine
# ─────────────────────────────────────────────

def load_mode(mode_name):
    path = os.path.join(MODES_DIR, f"{mode_name}.yaml")
    if not os.path.exists(path):
        available = [f.replace(".yaml", "") for f in os.listdir(MODES_DIR) if f.endswith(".yaml")]
        print(f"Error: Unknown mode '{mode_name}'. Available: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def recall_memories(mode_name):
    """Load relevant memories for context."""
    domain_map = {
        "sermon": "romans", "sheep": "sheep",
        "cruising": "cruising", "recipe": "recipes",
    }
    domain = domain_map.get(mode_name, "shared")
    try:
        from memory_ops import recall as mem_recall
        memories = mem_recall("", domain=domain, limit=5)
        if memories:
            return "\n".join(
                f"- [{m.get('type','?')}] {m.get('content','')[:200]}"
                for m in memories
            )
    except Exception:
        pass
    return "(no relevant memories found)"


def call_model(model_name, prompt, role="freestyle"):
    """Call an external model and return the response + usage."""
    if model_name not in ADAPTERS:
        return None, None

    adapter = ADAPTERS[model_name]
    from consult import ROLES
    system_prompt = ROLES.get(role, ROLES["freestyle"])

    try:
        result = adapter.query(prompt=prompt, system=system_prompt)
        return result["response"], result["usage"]
    except Exception as e:
        print(f"  → {model_name} failed: {e}", file=sys.stderr)
        return None, {"model": model_name, "tokens_in": 0, "tokens_out": 0, "estimated_cost_usd": 0}


def run_orchestra(mode_name, task):
    """Run the full round-robin orchestra with Claude as Round 1."""
    mode_config = load_mode(mode_name)

    orchestra_config = mode_config.get("orchestra", {})
    external_rounds = orchestra_config.get("rounds", [
        {"model": "gpt", "role": "structure"},
        {"model": "gemini", "role": "expand"},
        {"model": "grok", "role": "challenge"},
    ])
    blind_spot_model = orchestra_config.get("blind_spot_model", "grok")

    state = {
        "mode": mode_name,
        "task": task,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phases": [],
        "rounds": [],
        "claude_synthesis": None,
        "blind_spot": None,
        "cost_log": [],
        "total_cost_usd": 0.0,
        "status": "running",
    }

    # ── Phase 1: RECALL ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 1: RECALL — Loading memories for {mode_name}", file=sys.stderr)
    memory_context = recall_memories(mode_name)
    state["phases"].append({"phase": "recall", "memory_context": memory_context})
    print(f"  → {memory_context[:100]}...", file=sys.stderr)

    # ── Phase 2: CLAUDE ROUND 1 (Local) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 2: ROUND 1 — Claude (lead author, local)", file=sys.stderr)

    claude_prompt = CLAUDE_ROUND1_PROMPT.format(
        task=task,
        memory_context=memory_context,
    )

    # Claude's Round 1 is generated locally by Claude Code — we output the prompt
    # and capture Claude's response. For automated runs, we use a placeholder
    # that describes Claude's position as lead author.
    claude_r1_response = {
        "proposals": [
            {
                "id": "claude_1",
                "proposal": f"Claude's analysis of: {task}",
                "confidence": "HIGH",
                "justification": "Claude has full codebase context, memory access, and understands the user's project constraints. This proposal represents the lead author's informed starting position.",
            }
        ],
        "low_hanging_fruit": [],
        "note": "This is Claude's Round 1 position. In interactive mode, Claude Code fills this with a detailed response based on codebase knowledge."
    }

    # Store Claude's round
    state["rounds"].append({
        "round": 1,
        "model": "claude",
        "role": "lead",
        "response": claude_r1_response,
        "usage": {"model": "claude", "tokens_in": 0, "tokens_out": 0, "estimated_cost_usd": 0},
        "prompt_for_claude": claude_prompt,
    })
    print(f"  → Claude Round 1 recorded (lead position)", file=sys.stderr)

    # ── Phase 3: EXTERNAL ROUNDS ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 3: ORCHESTRA — {len(external_rounds)} external rounds", file=sys.stderr)

    round_responses = [state["rounds"][0]]  # Start with Claude's Round 1

    for i, round_config in enumerate(external_rounds):
        model = round_config["model"]
        role = round_config.get("role", "freestyle")
        round_num = i + 2  # Claude was Round 1

        print(f"\n  Round {round_num}: {model} ({role})", file=sys.stderr)

        r1_text = json.dumps(round_responses[0]["response"], indent=2)

        if round_num == 2:
            prompt = ROUND_2_TEMPLATE.format(
                task=task,
                round1_response=r1_text,
            )
        elif round_num == 3:
            prompt = ROUND_3_TEMPLATE.format(
                task=task,
                round1_response=r1_text,
                round2_model=external_rounds[0]["model"].upper(),
                round2_response=json.dumps(round_responses[1]["response"], indent=2)
                    if len(round_responses) > 1 and round_responses[1]["response"] else "(Round 2 failed)",
            )
        elif round_num >= 4:
            prompt = ROUND_4_TEMPLATE.format(
                task=task,
                round1_response=r1_text,
                round2_model=external_rounds[0]["model"].upper(),
                round2_response=json.dumps(round_responses[1]["response"], indent=2)
                    if len(round_responses) > 1 and round_responses[1]["response"] else "(Round 2 failed)",
                round3_model=external_rounds[1]["model"].upper(),
                round3_response=json.dumps(round_responses[2]["response"], indent=2)
                    if len(round_responses) > 2 and round_responses[2]["response"] else "(Round 3 failed)",
            )

        response, usage = call_model(model, prompt, role)

        round_entry = {
            "round": round_num,
            "model": model,
            "role": role,
            "response": response,
            "usage": usage,
        }
        round_responses.append(round_entry)
        state["rounds"].append(round_entry)

        if usage:
            state["cost_log"].append(usage)
            state["total_cost_usd"] += usage.get("estimated_cost_usd", 0)
            print(f"  → Cost: ${usage.get('estimated_cost_usd', 0):.4f}", file=sys.stderr)
        if response:
            proposals = response.get("proposals", [])
            verdicts = response.get("verdicts", [])
            print(f"  → {len(proposals)} new proposals, {len(verdicts)} verdicts on prior work", file=sys.stderr)
        else:
            print(f"  → Failed (pipeline continues)", file=sys.stderr)

    state["phases"].append({"phase": "orchestra", "rounds_completed": len(round_responses)})

    # ── Phase 4: CLAUDE SYNTHESIS ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 4: CLAUDE SYNTHESIS — Final verdicts + attributed plan", file=sys.stderr)

    # Build synthesis prompt with all rounds
    synth_parts = {
        "round1_response": json.dumps(round_responses[0]["response"], indent=2),
        "round2_model": round_responses[1]["model"].upper() if len(round_responses) > 1 else "?",
        "round2_response": json.dumps(round_responses[1]["response"], indent=2) if len(round_responses) > 1 and round_responses[1]["response"] else "N/A",
        "round3_model": round_responses[2]["model"].upper() if len(round_responses) > 2 else "?",
        "round3_response": json.dumps(round_responses[2]["response"], indent=2) if len(round_responses) > 2 and round_responses[2]["response"] else "N/A",
        "round4_model": round_responses[3]["model"].upper() if len(round_responses) > 3 else "?",
        "round4_response": json.dumps(round_responses[3]["response"], indent=2) if len(round_responses) > 3 and round_responses[3]["response"] else "N/A",
    }

    synthesis_prompt = CLAUDE_SYNTHESIS_TEMPLATE.format(task=task, **synth_parts)
    state["claude_synthesis"] = {
        "prompt": synthesis_prompt,
        "note": "Claude Code performs the synthesis locally with full codebase context. The prompt above guides Claude's final verdicts and attributed plan."
    }
    state["phases"].append({"phase": "claude_synthesis"})
    print(f"  → Synthesis prompt generated for Claude Code", file=sys.stderr)

    # ── Phase 5: BLIND SPOT CHECK ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 5: BLIND SPOT CHECK — {blind_spot_model}", file=sys.stderr)

    synthesis_summary = [f"Task: {task}\n"]
    for r in round_responses:
        if r["response"]:
            synthesis_summary.append(f"Round {r['round']} ({r['model']}): {json.dumps(r['response'], indent=2)[:2000]}")

    blind_spot_prompt = BLIND_SPOT_TEMPLATE.format(
        task=task,
        synthesis="\n".join(synthesis_summary),
    )

    bs_response, bs_usage = call_model(blind_spot_model, blind_spot_prompt, "challenge")
    state["blind_spot"] = bs_response
    if bs_usage:
        state["cost_log"].append(bs_usage)
        state["total_cost_usd"] += bs_usage.get("estimated_cost_usd", 0)
        print(f"  → Cost: ${bs_usage.get('estimated_cost_usd', 0):.4f}", file=sys.stderr)
    if bs_response:
        bs_text = bs_response.get("blind_spot", str(bs_response))
        severity = bs_response.get("severity", "?")
        print(f"  → Blind spot ({severity}): {str(bs_text)[:200]}", file=sys.stderr)

    state["phases"].append({"phase": "blind_spot", "model": blind_spot_model})

    # ── Phase 6: ENCODE ──
    state["phases"].append({"phase": "encode", "note": "Claude encodes key decisions after review"})

    # ── Finalize ──
    state["status"] = "completed"
    state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    os.makedirs(STATE_DIR, exist_ok=True)
    state_path = os.path.join(STATE_DIR, "orchestra.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)

    return state


def print_report(state):
    """Print human-readable cost and idea report."""
    print(f"\n{'═'*60}")
    print(f"ORCHESTRA COMPLETE: {state['mode']} mode")
    print(f"{'═'*60}")
    print(f"Task: {state['task']}")
    print(f"Status: {state['status']}")
    print(f"Total cost: ${state['total_cost_usd']:.4f}")

    print(f"\n── Cost Per Round ──")
    for r in state["rounds"]:
        usage = r.get("usage", {})
        cost = usage.get("estimated_cost_usd", 0)
        tokens_in = usage.get("tokens_in", 0)
        tokens_out = usage.get("tokens_out", 0)
        proposals = len(r.get("response", {}).get("proposals", [])) if r.get("response") else 0
        verdicts = len(r.get("response", {}).get("verdicts", [])) if r.get("response") else 0
        print(f"  Round {r['round']}: {r['model']:8s} | ${cost:.4f} | {tokens_in}→{tokens_out} tok | {proposals} proposals, {verdicts} verdicts")

    if state.get("blind_spot"):
        bs = state["blind_spot"]
        print(f"\n── Blind Spot ({bs.get('severity', '?')}) ──")
        print(f"  {bs.get('blind_spot', str(bs))[:300]}")

    # Idea tracking
    all_proposals = []
    for r in state["rounds"]:
        resp = r.get("response")
        if resp and "proposals" in resp:
            for p in resp["proposals"]:
                all_proposals.append({"model": r["model"], "round": r["round"], **p})

    all_verdicts = []
    for r in state["rounds"]:
        resp = r.get("response")
        if resp and "verdicts" in resp:
            for v in resp["verdicts"]:
                all_verdicts.append({"model": r["model"], "round": r["round"], **v})

    print(f"\n── Idea Summary ──")
    print(f"  Total proposals: {len(all_proposals)}")
    print(f"  Total verdicts: {len(all_verdicts)}")

    wheat = sum(1 for v in all_verdicts if v.get("verdict", "").upper() in ("WHEAT", "WHEAT_WITH_REFINEMENT"))
    chaff = sum(1 for v in all_verdicts if v.get("verdict", "").upper() == "CHAFF")
    rescued = sum(1 for v in all_verdicts if v.get("verdict", "").upper() == "RESCUED")
    print(f"  Wheat: {wheat} | Chaff: {chaff} | Rescued: {rescued}")

    # Low-hanging fruit
    all_fruit = []
    for r in state["rounds"]:
        resp = r.get("response")
        if resp and "low_hanging_fruit" in resp:
            for lhf in resp["low_hanging_fruit"]:
                if isinstance(lhf, dict):
                    all_fruit.append({"model": r["model"], **lhf})
                else:
                    all_fruit.append({"model": r["model"], "idea": str(lhf)})
    if all_fruit:
        print(f"\n── Low-Hanging Fruit ──")
        for f in all_fruit:
            print(f"  [{f['model']}] {f.get('idea', str(f))[:150]}")

    print(f"\nFull state: state/orchestra.json")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mode_name = sys.argv[1].lower()
    task = " ".join(sys.argv[2:])

    print(f"Orchestra: {mode_name} mode", file=sys.stderr)
    print(f"Task: {task}", file=sys.stderr)

    state = run_orchestra(mode_name, task)
    print_report(state)

    # Output full state as JSON to stdout
    print(json.dumps(state, indent=2, default=str))


if __name__ == "__main__":
    main()
