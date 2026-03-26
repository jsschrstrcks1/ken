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
  1. RECALL    — Load relevant cognitive memories
  2. ORCHESTRA — Round-robin: GPT proposes → Gemini refines → Grok challenges
                 Each model sees full chain + wheat/chaff justifications
  3. BLIND SPOT — Final check: "what did we all miss?"
  4. SYNTHESIZE — Claude produces attributed plan from full debate
  5. REPORT    — Per-round costs, idea survival rate

The key difference from orchestrate.py: nothing is filtered between rounds.
Full context flows forward. What one model calls chaff, the next might rescue.
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

ROUND_1_TEMPLATE = """You are the FIRST model in a round-robin consultation. Two other AI models will review your work after you.

TASK: {task}

CONTEXT FROM MEMORY:
{memory_context}

YOUR ROLE: Propose structure, approach, and innovations for this task.

For each proposal, provide:
- PROPOSAL: [your idea]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why this matters — be specific]

Be thorough. The next model will build on your best ideas and challenge your weakest ones. Everything you write will be visible to all subsequent models.

ALSO: Identify any LOW-HANGING FRUIT — the easiest, highest-value wins that don't require complex implementation. Sometimes the best improvement is the simplest one.

Respond in JSON with a "proposals" array (each having: id, proposal, confidence, justification) and a "low_hanging_fruit" array (each having: idea, effort, impact)."""

ROUND_2_TEMPLATE = """You are the SECOND model in a round-robin consultation. You are reviewing the first model's work and adding your own.

TASK: {task}

ROUND 1 (from {round1_model}):
{round1_response}

YOUR ROLE: For EACH of {round1_model}'s proposals, provide a verdict. Then add your own original proposals.

For each prior proposal, respond with:
- PROPOSAL_ID: [reference the proposal]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT
- JUSTIFICATION: [why — be specific about your reasoning]
- REFINEMENT: [if WHEAT_WITH_REFINEMENT, what changes would make it better]

NOTE: What you call CHAFF might be rescued by the next model. Explain your reasoning clearly so they can evaluate whether you're right.

Then add YOUR OWN proposals with:
- PROPOSAL: [your idea — something the first model didn't think of]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why this matters]

ALSO: What LOW-HANGING FRUIT is everyone overcomplicating? What's the easiest win?

Respond in JSON with "verdicts" array, "proposals" array, and "low_hanging_fruit" array."""

ROUND_3_TEMPLATE = """You are the THIRD model in a round-robin consultation. You see the full debate chain. Your job is to challenge everything, rescue dismissed ideas, and add what everyone missed.

TASK: {task}

ROUND 1 (from {round1_model}):
{round1_response}

ROUND 2 (from {round2_model}) — their verdicts on Round 1 + their own proposals:
{round2_response}

YOUR ROLE:
1. For EACH proposal from BOTH prior rounds, provide a verdict
2. SPECIFICALLY look for ideas that Round 2 called CHAFF — are they really chaff, or do they become wheat with modification?
3. Add your own proposals that BOTH models missed
4. Identify the single biggest blind spot in the discussion so far

For each prior proposal, respond with:
- PROPOSAL_ID: [reference]
- ORIGINAL_MODEL: [who proposed it]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT | RESCUED (for ideas you're saving from the chaff pile)
- JUSTIFICATION: [why — be specific]
- REFINEMENT: [if applicable]

Then add YOUR OWN proposals, identify the BLIND_SPOT, and call out any LOW-HANGING FRUIT everyone is overcomplicating.

Respond in JSON with "verdicts" array, "proposals" array, "blind_spot" string, and "low_hanging_fruit" array."""

BLIND_SPOT_TEMPLATE = """You previously participated in a round-robin consultation. Here is the final synthesis that was produced.

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
        from memory_ops import recall as mem_recall, tree as mem_tree
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
    """Run the full round-robin orchestra."""
    mode_config = load_mode(mode_name)

    # Get orchestra config or use defaults
    orchestra_config = mode_config.get("orchestra", {})
    rounds = orchestra_config.get("rounds", [
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

    # ── Phase 2: ORCHESTRA (Round-Robin) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 2: ORCHESTRA — {len(rounds)} rounds", file=sys.stderr)

    round_responses = []

    for i, round_config in enumerate(rounds):
        model = round_config["model"]
        role = round_config.get("role", "freestyle")
        round_num = i + 1

        print(f"\n  Round {round_num}: {model} ({role})", file=sys.stderr)

        # Build prompt based on round number
        if round_num == 1:
            prompt = ROUND_1_TEMPLATE.format(
                task=task,
                memory_context=memory_context,
            )
        elif round_num == 2:
            prompt = ROUND_2_TEMPLATE.format(
                task=task,
                round1_model=rounds[0]["model"].upper(),
                round1_response=json.dumps(round_responses[0]["response"], indent=2)
                    if round_responses[0]["response"] else "(Round 1 failed)",
            )
        elif round_num >= 3:
            prompt = ROUND_3_TEMPLATE.format(
                task=task,
                round1_model=rounds[0]["model"].upper(),
                round1_response=json.dumps(round_responses[0]["response"], indent=2)
                    if round_responses[0]["response"] else "(Round 1 failed)",
                round2_model=rounds[1]["model"].upper(),
                round2_response=json.dumps(round_responses[1]["response"], indent=2)
                    if round_responses[1]["response"] else "(Round 2 failed)",
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
            # Count proposals
            proposals = response.get("proposals", [])
            verdicts = response.get("verdicts", [])
            print(f"  → {len(proposals)} new proposals, {len(verdicts)} verdicts on prior work", file=sys.stderr)
        else:
            print(f"  → Failed (pipeline continues)", file=sys.stderr)

    state["phases"].append({"phase": "orchestra", "rounds_completed": len(round_responses)})

    # ── Phase 3: BLIND SPOT CHECK ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 3: BLIND SPOT CHECK — {blind_spot_model}", file=sys.stderr)

    # Build a quick synthesis for the blind spot check
    synthesis_parts = [f"Task: {task}\n"]
    for r in round_responses:
        if r["response"]:
            synthesis_parts.append(f"Round {r['round']} ({r['model']}): {json.dumps(r['response'], indent=2)[:2000]}")

    blind_spot_prompt = BLIND_SPOT_TEMPLATE.format(
        task=task,
        synthesis="\n".join(synthesis_parts),
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

    # ── Phase 4: ENCODE ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 4: ENCODE — Saving key decisions to memory", file=sys.stderr)
    # Memory encoding happens in Claude Code after reviewing the output
    state["phases"].append({"phase": "encode", "note": "Claude encodes key decisions after review"})

    # ── Phase 5: COST REPORT ──
    state["status"] = "completed"
    state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Save state
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

    # Count wheat/chaff/rescued
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
                all_fruit.append({"model": r["model"], **lhf})
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
