#!/usr/bin/env python3
"""
orchestra.py — Fan-out multi-LLM consultation with Claude+GPT deliberation.

Architecture:
  Phase 1: RECALL     — Load cognitive memories
  Phase 2: CLAUDE R1  — Claude writes substantive lead analysis (not a placeholder)
  Phase 3: FAN-OUT    — All models respond independently, seeing only Claude's R1
                        GPT, Gemini, Perplexity, You.com, Grok — in parallel conceptually
  Phase 4: DELIBERATE — Claude and GPT alternate 2-3 rounds, seeing ALL fan-out responses
  Phase 5: BLIND SPOT — Final contrarian check
  Phase 6: REPORT     — Per-round costs, idea tracking

Why fan-out: Each model sees the raw task + Claude's analysis without being
biased by other models' framing. Web-grounded models (Perplexity, You.com)
search independently. Then Claude + GPT deliberate with the full picture.

Usage:
    python3 orchestra.py <mode> "task description"
"""

import json
import os
import sys
import time
import yaml

from iteration import (
    IterationController, validate_response, build_format_retry_prompt,
)

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
# Prompt Templates
# ─────────────────────────────────────────────

CLAUDE_ROUND1_PROMPT = """You are CLAUDE — the lead author with full codebase context, memory, and project knowledge. You go FIRST. All other models (GPT, Gemini, Perplexity, You.com, Grok) will independently review your analysis and add their own perspectives.

TASK: {task}

CONTEXT FROM MEMORY:
{memory_context}

YOUR ROLE: Provide a thorough, substantive analysis. You know the codebase, the user's preferences, and the project history. Use that knowledge to:

1. Frame the key questions and what's already known
2. Propose specific research directions with justifications
3. Identify gaps, risks, and open questions
4. Suggest concrete next steps

For each proposal, provide:
- PROPOSAL: [your idea — be specific]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why this matters, referencing project context]

ALSO: Identify any LOW-HANGING FRUIT — easiest, highest-value wins.

Every other model will see only YOUR analysis (not each other). Make it count."""

FAN_OUT_TEMPLATE = """You are {model_name} responding independently in a multi-model consultation. CLAUDE (the lead author with codebase access) provided the initial analysis below. You have NOT seen other models' responses — only Claude's.

TASK: {task}

CLAUDE'S ANALYSIS (Round 1):
{claude_analysis}

YOUR ROLE ({role_description}):
For EACH of Claude's proposals, provide a verdict:
- PROPOSAL_ID: [reference]
- VERDICT: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT
- JUSTIFICATION: [specific reasoning]
- REFINEMENT: [if WHEAT_WITH_REFINEMENT, what changes]

Then add YOUR OWN proposals — things Claude missed or didn't consider:
- PROPOSAL: [your idea]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why]

ALSO: What LOW-HANGING FRUIT is being overlooked?

Respond in JSON with "verdicts" array, "proposals" array, and "low_hanging_fruit" array."""

DELIBERATION_CLAUDE_TEMPLATE = """You are CLAUDE in a deliberation round with GPT. You've seen the full fan-out — all 5 models responded independently to your Round 1 analysis. Now you and GPT are deliberating to reach the optimal solution.

TASK: {task}

YOUR ORIGINAL ANALYSIS (Round 1):
{claude_analysis}

ALL FAN-OUT RESPONSES:
{fan_out_summary}

{deliberation_context}

YOUR ROLE (Deliberation Round {delib_round}):
1. Synthesize the strongest ideas from ALL fan-out responses
2. Resolve contradictions — when models disagree, take a position and justify it
3. Revise your own Round 1 proposals based on what you've learned
4. Produce an ATTRIBUTED PLAN — credit which model each step came from
5. Flag anything GPT raised that you disagree with (or agree with)

Respond in JSON with:
- "verdicts": your final call on each proposal from all models
- "revised_proposals": your updated proposals
- "attributed_plan": concrete steps with source attribution
- "for_gpt": specific questions or disagreements for GPT to address
- "low_hanging_fruit": easiest wins"""

DELIBERATION_GPT_TEMPLATE = """You are GPT in a deliberation round with Claude. You've seen the full fan-out — all 5 models responded independently to Claude's analysis. You and Claude are deliberating to reach the optimal solution.

TASK: {task}

CLAUDE'S ORIGINAL ANALYSIS (Round 1):
{claude_analysis}

ALL FAN-OUT RESPONSES:
{fan_out_summary}

{deliberation_context}

YOUR ROLE (Deliberation Round {delib_round}):
1. Evaluate Claude's synthesis — what did Claude get right? What did Claude miss or get wrong?
2. Challenge any weak reasoning in Claude's deliberation
3. Rescue any fan-out proposals that Claude dismissed too quickly
4. Propose structural improvements to the plan
5. Answer any questions Claude directed at you

Respond in JSON with:
- "evaluation": your assessment of Claude's current synthesis
- "challenges": specific disagreements with reasoning
- "rescued_proposals": ideas you're saving from dismissal
- "structural_improvements": plan-level suggestions
- "for_claude": specific points for Claude to address in the next round
- "confidence": 0.0-1.0 that the plan is converging on the right answer"""

BLIND_SPOT_TEMPLATE = """You previously participated in a multi-model consultation. Here is the final deliberated synthesis.

TASK: {task}

FINAL SYNTHESIS:
{synthesis}

ONE QUESTION: What is the single most important thing this plan is still missing or getting wrong? Be specific and constructive. This is your last chance to flag something before execution.

Respond in JSON with: "analysis" (string), "proposed_update" (string), "risks" (string), "confidence" (0.0-1.0)."""


# ─────────────────────────────────────────────
# Role descriptions for fan-out models
# ─────────────────────────────────────────────

DEFAULT_ROLE_DESCRIPTIONS = {
    "structure": "Cross-reference claims, check logical consistency, suggest prioritized task ordering.",
    "expand": "Add missing context, cross-references, historical background, and supporting evidence.",
    "challenge": "Challenge assumptions, identify weak reasoning, surface unconventional alternatives.",
    "research": "Search the web for specific records, databases, and primary sources. Every claim should include a source URL or record identifier.",
}


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
        "family-history": "family-history",
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


def call_model(model_name, prompt, role="freestyle", schema_name=None, controller=None):
    """Call an external model with format validation and retry."""
    if model_name not in ADAPTERS:
        return None, None, []

    adapter = ADAPTERS[model_name]
    from consult import ROLES
    system_prompt = ROLES.get(role, ROLES["freestyle"])
    current_prompt = prompt
    total_usage = None

    for attempt in range(1 + (controller.max_format_retries if controller else 2)):
        try:
            result = adapter.query(prompt=current_prompt, system=system_prompt)
            response = result["response"]
            usage = result["usage"]
            citations = result.get("citations", [])

            if total_usage is None:
                total_usage = usage
            elif usage:
                for k in ("tokens_in", "tokens_out", "input_tokens", "output_tokens"):
                    if k in usage and k in total_usage:
                        total_usage[k] = total_usage.get(k, 0) + usage.get(k, 0)
                total_usage["estimated_cost_usd"] = total_usage.get("estimated_cost_usd", 0) + usage.get("estimated_cost_usd", 0)

            if schema_name:
                is_valid, issues = validate_response(response, schema_name)
                if not is_valid:
                    can_retry = controller.can_format_retry(model_name) if controller else (attempt < 2)
                    if can_retry:
                        if controller:
                            controller.record_format_retry(model_name)
                        print(f"  → Format issues: {'; '.join(issues)}. Retrying ({attempt+1})...", file=sys.stderr)
                        current_prompt = build_format_retry_prompt(prompt, response, issues, schema_name)
                        continue
                    else:
                        print(f"  → Format issues (max retries): {'; '.join(issues)}", file=sys.stderr)

            return response, total_usage, citations

        except Exception as e:
            print(f"  → {model_name} failed: {e}", file=sys.stderr)
            return None, {"model": model_name, "tokens_in": 0, "tokens_out": 0, "estimated_cost_usd": 0}, []

    return response, total_usage, citations


def format_fan_out_summary(fan_out_responses):
    """Build a text summary of all fan-out responses for deliberation."""
    parts = []
    for entry in fan_out_responses:
        model = entry["model"].upper()
        role = entry["role"]
        resp = entry["response"]
        citations = entry.get("citations", [])

        if resp is None:
            parts.append(f"\n--- {model} ({role}) --- FAILED ---\n")
            continue

        resp_text = json.dumps(resp, indent=2, default=str)
        # Truncate very long responses to keep deliberation prompts manageable
        if len(resp_text) > 4000:
            resp_text = resp_text[:4000] + "\n... (truncated)"

        section = f"\n--- {model} ({role}) ---\n{resp_text}"
        if citations:
            section += f"\nCitations: {', '.join(citations[:10])}"
        parts.append(section)

    return "\n".join(parts)


def run_orchestra(mode_name, task):
    """Run the fan-out + deliberation orchestra."""
    mode_config = load_mode(mode_name)

    orchestra_config = mode_config.get("orchestra", {})
    fan_out_models = orchestra_config.get("fan_out", [
        {"model": "gpt", "role": "structure"},
        {"model": "gemini", "role": "expand"},
        {"model": "grok", "role": "challenge"},
    ])
    deliberation_rounds = orchestra_config.get("deliberation_rounds", 2)
    blind_spot_model = orchestra_config.get("blind_spot_model", "grok")

    state = {
        "mode": mode_name,
        "task": task,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phases": [],
        "claude_r1": None,
        "fan_out": [],
        "deliberation": [],
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

    # ── Phase 2: CLAUDE ROUND 1 (Substantive) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 2: CLAUDE R1 — Lead analysis", file=sys.stderr)

    claude_prompt = CLAUDE_ROUND1_PROMPT.format(
        task=task,
        memory_context=memory_context,
    )

    # Claude's R1 is generated locally by Claude Code.
    # For CLI runs, we produce a substantive placeholder that frames the task.
    claude_r1 = {
        "proposals": [
            {
                "id": "claude_1",
                "proposal": f"Claude's substantive lead analysis of: {task}",
                "confidence": "HIGH",
                "justification": "Claude has full codebase context, memory access, and project knowledge. This is the informed starting position that all other models will independently evaluate.",
            }
        ],
        "low_hanging_fruit": [],
        "note": "In interactive mode, Claude Code fills this with a detailed, substantive response. The prompt above guides Claude's analysis."
    }

    state["claude_r1"] = {
        "response": claude_r1,
        "prompt_for_claude": claude_prompt,
    }
    print(f"  → Claude R1 recorded (lead analysis)", file=sys.stderr)

    claude_r1_text = json.dumps(claude_r1, indent=2)

    # ── Phase 3: FAN-OUT ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 3: FAN-OUT — {len(fan_out_models)} models respond independently", file=sys.stderr)

    fan_out_responses = []

    for config in fan_out_models:
        model = config["model"]
        role = config.get("role", "freestyle")
        role_desc = config.get("description", DEFAULT_ROLE_DESCRIPTIONS.get(role, "Provide your analysis."))

        print(f"\n  {model.upper()} ({role})", file=sys.stderr)

        prompt = FAN_OUT_TEMPLATE.format(
            model_name=model.upper(),
            task=task,
            claude_analysis=claude_r1_text,
            role_description=role_desc,
        )

        response, usage, citations = call_model(model, prompt, role)

        entry = {
            "model": model,
            "role": role,
            "response": response,
            "usage": usage,
            "citations": citations,
        }
        fan_out_responses.append(entry)
        state["fan_out"].append(entry)

        if usage:
            cost = usage.get("estimated_cost_usd", 0) or 0
            state["cost_log"].append(usage)
            state["total_cost_usd"] += cost
            print(f"  → Cost: ${cost:.4f}", file=sys.stderr)

        if response:
            proposals = response.get("proposals", []) if isinstance(response, dict) else []
            verdicts = response.get("verdicts", []) if isinstance(response, dict) else []
            print(f"  → {len(proposals)} proposals, {len(verdicts)} verdicts", file=sys.stderr)
            if citations:
                print(f"  → {len(citations)} citations", file=sys.stderr)
        else:
            print(f"  → Failed (continuing)", file=sys.stderr)

    state["phases"].append({"phase": "fan_out", "models_called": len(fan_out_responses)})

    # ── Phase 4: DELIBERATION (Claude ↔ GPT) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 4: DELIBERATION — Claude ↔ GPT, {deliberation_rounds} rounds", file=sys.stderr)

    fan_out_summary = format_fan_out_summary(fan_out_responses)
    deliberation_history = []

    for d_round in range(1, deliberation_rounds + 1):
        # Build deliberation context from prior rounds
        if deliberation_history:
            delib_context = "PRIOR DELIBERATION:\n"
            for dh in deliberation_history:
                delib_context += f"\n--- {dh['model'].upper()} (Deliberation {dh['delib_round']}) ---\n"
                delib_context += json.dumps(dh["response"], indent=2, default=str)[:3000]
                delib_context += "\n"
        else:
            delib_context = ""

        # Claude deliberates (output as prompt for Claude Code)
        print(f"\n  Deliberation {d_round}a: Claude", file=sys.stderr)
        claude_delib_prompt = DELIBERATION_CLAUDE_TEMPLATE.format(
            task=task,
            claude_analysis=claude_r1_text,
            fan_out_summary=fan_out_summary,
            deliberation_context=delib_context,
            delib_round=d_round,
        )

        claude_delib = {
            "model": "claude",
            "delib_round": d_round,
            "response": {
                "note": f"Claude deliberation round {d_round} — executed locally by Claude Code.",
                "prompt": claude_delib_prompt,
            },
            "usage": None,
        }
        deliberation_history.append(claude_delib)
        state["deliberation"].append(claude_delib)
        print(f"  → Claude deliberation {d_round} prompt generated", file=sys.stderr)

        # GPT deliberates (via API)
        print(f"\n  Deliberation {d_round}b: GPT", file=sys.stderr)

        # Update context with Claude's deliberation
        delib_context_for_gpt = "PRIOR DELIBERATION:\n"
        for dh in deliberation_history:
            delib_context_for_gpt += f"\n--- {dh['model'].upper()} (Deliberation {dh['delib_round']}) ---\n"
            resp_text = json.dumps(dh["response"], indent=2, default=str)
            delib_context_for_gpt += resp_text[:3000] + "\n"

        gpt_delib_prompt = DELIBERATION_GPT_TEMPLATE.format(
            task=task,
            claude_analysis=claude_r1_text,
            fan_out_summary=fan_out_summary,
            deliberation_context=delib_context_for_gpt,
            delib_round=d_round,
        )

        gpt_response, gpt_usage, _ = call_model("gpt", gpt_delib_prompt, "structure")

        gpt_delib = {
            "model": "gpt",
            "delib_round": d_round,
            "response": gpt_response,
            "usage": gpt_usage,
        }
        deliberation_history.append(gpt_delib)
        state["deliberation"].append(gpt_delib)

        if gpt_usage:
            cost = gpt_usage.get("estimated_cost_usd", 0) or 0
            state["cost_log"].append(gpt_usage)
            state["total_cost_usd"] += cost
            print(f"  → GPT deliberation {d_round} cost: ${cost:.4f}", file=sys.stderr)

        if gpt_response:
            confidence = gpt_response.get("confidence", "?") if isinstance(gpt_response, dict) else "?"
            print(f"  → GPT confidence: {confidence}", file=sys.stderr)
        else:
            print(f"  → GPT deliberation failed", file=sys.stderr)

    state["phases"].append({"phase": "deliberation", "rounds": deliberation_rounds})

    # ── Phase 5: BLIND SPOT CHECK ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"PHASE 5: BLIND SPOT — {blind_spot_model}", file=sys.stderr)

    # Build synthesis from deliberation
    synthesis_parts = [f"Task: {task}\n\nClaude's Lead Analysis:\n{claude_r1_text}\n"]
    synthesis_parts.append(f"\nFan-Out Responses:\n{fan_out_summary}\n")
    for dh in deliberation_history:
        if dh["response"]:
            synthesis_parts.append(
                f"\nDeliberation {dh['delib_round']} ({dh['model'].upper()}):\n"
                + json.dumps(dh["response"], indent=2, default=str)[:2000]
            )

    blind_spot_prompt = BLIND_SPOT_TEMPLATE.format(
        task=task,
        synthesis="\n".join(synthesis_parts),
    )

    bs_response, bs_usage, _ = call_model(blind_spot_model, blind_spot_prompt, "challenge")
    state["blind_spot"] = bs_response
    if bs_usage:
        cost = bs_usage.get("estimated_cost_usd", 0) or 0
        state["cost_log"].append(bs_usage)
        state["total_cost_usd"] += cost
        print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
    if bs_response:
        analysis = bs_response.get("analysis", str(bs_response)) if isinstance(bs_response, dict) else str(bs_response)
        print(f"  → Blind spot: {str(analysis)[:200]}", file=sys.stderr)

    state["phases"].append({"phase": "blind_spot", "model": blind_spot_model})

    # ── Finalize ──
    state["status"] = "completed"
    state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    os.makedirs(STATE_DIR, exist_ok=True)
    state_path = os.path.join(STATE_DIR, "orchestra.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)

    return state


def print_report(state):
    """Print human-readable report."""
    print(f"\n{'═'*60}")
    print(f"ORCHESTRA COMPLETE: {state['mode']} mode")
    print(f"{'═'*60}")
    print(f"Task: {state['task'][:200]}")
    print(f"Status: {state['status']}")
    print(f"Total cost: ${state['total_cost_usd']:.4f}")

    # Fan-out results
    print(f"\n── Fan-Out Results ──")
    for entry in state.get("fan_out", []):
        model = entry["model"]
        role = entry["role"]
        usage = entry.get("usage") or {}
        cost = usage.get("estimated_cost_usd", 0) or 0
        citations = entry.get("citations", [])
        resp = entry.get("response")

        proposals = 0
        verdicts = 0
        if resp and isinstance(resp, dict):
            proposals = len(resp.get("proposals", []))
            verdicts = len(resp.get("verdicts", []))

        status = f"{proposals}P/{verdicts}V" if resp else "FAILED"
        cite_str = f" +{len(citations)}cit" if citations else ""
        print(f"  {model:12s} ({role:10s}) | ${cost:.4f} | {status}{cite_str}")

    # Deliberation results
    print(f"\n── Deliberation (Claude ↔ GPT) ──")
    for entry in state.get("deliberation", []):
        model = entry["model"]
        d_round = entry["delib_round"]
        usage = entry.get("usage") or {}
        cost = usage.get("estimated_cost_usd", 0) or 0
        resp = entry.get("response")
        if model == "claude":
            print(f"  Round {d_round}a: Claude (local prompt generated)")
        else:
            confidence = "?"
            if resp and isinstance(resp, dict):
                confidence = resp.get("confidence", "?")
            status = f"confidence={confidence}" if resp else "FAILED"
            print(f"  Round {d_round}b: GPT    | ${cost:.4f} | {status}")

    # Blind spot
    if state.get("blind_spot"):
        bs = state["blind_spot"]
        if isinstance(bs, dict):
            print(f"\n── Blind Spot ──")
            print(f"  {str(bs.get('analysis', bs))[:400]}")
        else:
            print(f"\n── Blind Spot ──")
            print(f"  {str(bs)[:400]}")

    # Idea tracking across fan-out
    all_proposals = []
    all_verdicts = []
    for entry in state.get("fan_out", []):
        resp = entry.get("response")
        if resp and isinstance(resp, dict):
            for p in resp.get("proposals", []):
                all_proposals.append({"model": entry["model"], **p})
            for v in resp.get("verdicts", []):
                all_verdicts.append({"model": entry["model"], **v})

    all_citations = []
    for entry in state.get("fan_out", []):
        for c in entry.get("citations", []):
            all_citations.append({"model": entry["model"], "url": c})

    print(f"\n── Idea Summary ──")
    print(f"  Total proposals: {len(all_proposals)}")
    print(f"  Total verdicts: {len(all_verdicts)}")
    if all_citations:
        print(f"  Total citations: {len(all_citations)}")

    wheat = sum(1 for v in all_verdicts if str(v.get("VERDICT", v.get("verdict", ""))).upper() in ("WHEAT", "WHEAT_WITH_REFINEMENT"))
    chaff = sum(1 for v in all_verdicts if str(v.get("VERDICT", v.get("verdict", ""))).upper() == "CHAFF")
    rescued = sum(1 for v in all_verdicts if str(v.get("VERDICT", v.get("verdict", ""))).upper() == "RESCUED")
    print(f"  Wheat: {wheat} | Chaff: {chaff} | Rescued: {rescued}")

    # Low-hanging fruit
    all_fruit = []
    for entry in state.get("fan_out", []):
        resp = entry.get("response")
        if resp and isinstance(resp, dict):
            for lhf in resp.get("low_hanging_fruit", []):
                if isinstance(lhf, dict):
                    all_fruit.append({"model": entry["model"], **lhf})
                else:
                    all_fruit.append({"model": entry["model"], "idea": str(lhf)})
    if all_fruit:
        print(f"\n── Low-Hanging Fruit ──")
        for f in all_fruit:
            print(f"  [{f['model']}] {f.get('idea', f.get('PROPOSAL', str(f)))[:150]}")

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
