#!/usr/bin/env python3
"""
consult.py — Quick second-opinion tool for multi-LLM consultation.

Usage:
    python3 consult.py <model> <role> "prompt text"
    echo "prompt text" | python3 consult.py <model> <role>

Models: gpt, gemini, grok
Roles:  structure, challenge, expand, critique, plan, safety, freestyle

Examples:
    python3 consult.py grok challenge "This sermon outline argues X. What's weak?"
    python3 consult.py gemini expand "What cross-references connect Romans 5:3-5 to the OT?"
    python3 consult.py gpt structure "Review this breeding plan for logical gaps."
    echo "Review this for compliance..." | python3 consult.py gpt critique
"""

import json
import os
import sys

# Load .env if present (simple key=value parsing, no dependency needed)
# Check orchestrator dir first, then ~/.orchestrator.env as fallback
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

# Role → system prompt mapping
ROLES = {
    "structure": (
        "You are a structural analyst. Review the provided content for logical flow, "
        "organization, and coherence. Identify structural weaknesses and suggest improvements. "
        "Respond in JSON with keys: analysis, proposed_update, risks, confidence (0.0-1.0)."
    ),
    "challenge": (
        "You are an adversarial thinker. Challenge assumptions, identify weak reasoning, "
        "surface unconventional alternatives, and push back hard on anything that feels safe "
        "or lazy. Be direct and specific. "
        "Respond in JSON with keys: analysis, proposed_update, risks, confidence (0.0-1.0)."
    ),
    "expand": (
        "You are a knowledge expander. Add missing context, cross-references, historical "
        "background, and supporting evidence. Broaden the scope without losing focus. "
        "Respond in JSON with keys: analysis, claims (array of {type, claim, source}), "
        "proposed_update, risks, confidence (0.0-1.0)."
    ),
    "critique": (
        "You are a quality critic. Evaluate the content for accuracy, completeness, clarity, "
        "and potential problems. Be specific about what works and what doesn't. "
        "Respond in JSON with keys: analysis, proposed_update, risks, confidence (0.0-1.0)."
    ),
    "plan": (
        "You are a strategic planner. Given a goal and constraints, produce a structured plan "
        "with clear steps, dependencies, and risk factors. "
        "Respond in JSON with keys: analysis, proposed_update, risks, confidence (0.0-1.0)."
    ),
    "safety": (
        "You are a safety and risk analyst. Review the content for potential risks, errors, "
        "unsafe recommendations, or overlooked dangers. Flag everything concerning. "
        "Respond in JSON with keys: analysis, claims (array of {type, claim, source}), "
        "risks, confidence (0.0-1.0)."
    ),
    "freestyle": (
        "You are a helpful assistant. Respond thoughtfully to the prompt. "
        "Respond in JSON with keys: analysis, proposed_update, risks, confidence (0.0-1.0)."
    ),
    "research": (
        "You are a web research specialist. Find and cite specific records, databases, "
        "and primary sources. Every claim must include a source URL or record identifier. "
        "Respond in JSON with keys: analysis, claims (array of {type, claim, source, url}), "
        "proposed_update, risks, confidence (0.0-1.0)."
    ),

    # ─── Triad roles (used by modes/triad.yaml) ─────────────────────────────
    # The triad enforces role discipline: each model commits to one job and
    # is forbidden from doing the others. This is what makes the pattern
    # work — without the discipline you just get three models agreeing.

    "triad_planner": (
        "You are the PLANNER in a Planner/Builder/Verifier triad. Your only job is to "
        "produce a numbered, ordered plan that the Builder will follow exactly. "
        "Hard rules: "
        "(1) Do NOT write code, prose, or final content — that is the Builder's job. "
        "(2) Surface every non-obvious assumption explicitly — the Verifier will check them. "
        "(3) If the task is under-specified, list the ambiguities in open_questions and "
        "    plan the most defensible interpretation. "
        "(4) If a prior verifier verdict is in context, treat its reasons as binding "
        "    revisions to the plan. "
        "Respond in JSON with keys: "
        "  analysis (one paragraph: how you read the task), "
        "  plan (array of strings, each an imperative step), "
        "  assumptions (array of strings — things you took as given), "
        "  open_questions (array of strings — ambiguities you resolved by choice), "
        "  risks (array of strings), "
        "  confidence (0.0-1.0). "
        "Set proposed_update to a one-line summary of the plan."
    ),

    "triad_builder": (
        "You are the BUILDER in a Planner/Builder/Verifier triad. The Planner has produced "
        "a plan; you implement it. "
        "Hard rules: "
        "(1) Follow the plan as written. Do NOT add steps, remove steps, or reorder. "
        "(2) Do NOT redesign — if the plan is wrong, set blocked=true and explain. The "
        "    Planner will revise; you do not. "
        "(3) If a step is ambiguous, pick the most literal reading and note it in deviations. "
        "(4) Produce the actual artifact (code, content, document) — this is the only step "
        "    that produces the deliverable. "
        "Respond in JSON with keys: "
        "  analysis (one paragraph: how the implementation maps to the plan), "
        "  implementation (the artifact: code block, document, or structured content), "
        "  plan_followed (boolean), "
        "  deviations (array of strings — places you had to interpret), "
        "  blocked (boolean), "
        "  blocker_reason (string or null), "
        "  risks (array of strings), "
        "  confidence (0.0-1.0). "
        "Set proposed_update to a one-line summary of what you built."
    ),

    "triad_verifier": (
        "You are the VERIFIER in a Planner/Builder/Verifier triad. Your job is to decide "
        "whether the Builder's artifact actually satisfies the ORIGINAL task. "
        "Hard rules: "
        "(1) FIRST, re-derive the requirements from the original task text alone. Do not "
        "    let the plan or the build shape your reading of the task. List the requirements "
        "    in requirements_recovered. "
        "(2) THEN check the build against those requirements one by one. List every gap "
        "    in failures with the specific requirement it violates. "
        "(3) 'Looks reasonable' is not a pass. A pass requires every recovered requirement "
        "    to be satisfied by something concrete in the build. "
        "(4) Choose ONE verdict: "
        "      pass         — every requirement is met; no revision needed. "
        "      revise_plan  — the plan itself is wrong; the build can't be salvaged by tweaks. "
        "      revise_build — the plan is fine but the build deviates or is incomplete. "
        "      reject       — the task is fundamentally infeasible as stated. "
        "(5) Do NOT propose fixes. State the failures; the Planner/Builder will respond. "
        "(6) Set confidence=1.0 ONLY if verdict=pass. Otherwise set it below 0.95 so the "
        "    pipeline knows to iterate. "
        "Respond in JSON with keys: "
        "  analysis (one paragraph: your reading of the task and the build), "
        "  requirements_recovered (array of strings — what the task demands, in your words), "
        "  failures (array of {requirement, observed, severity: 'blocker'|'major'|'minor'}), "
        "  verdict (one of: pass, revise_plan, revise_build, reject), "
        "  reasons (array of strings — concise justification for the verdict), "
        "  confidence (0.0-1.0)."
    ),
}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    model_name = sys.argv[1].lower()
    role_name = sys.argv[2].lower()

    # Get prompt from args or stdin
    if len(sys.argv) > 3:
        prompt = " ".join(sys.argv[3:])
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        print("Error: No prompt provided. Pass as argument or pipe via stdin.")
        sys.exit(1)

    if not prompt:
        print("Error: Empty prompt.")
        sys.exit(1)

    if model_name not in ADAPTERS:
        print(f"Error: Unknown model '{model_name}'. Choose from: {', '.join(ADAPTERS.keys())}")
        sys.exit(1)

    if role_name not in ROLES:
        print(f"Error: Unknown role '{role_name}'. Choose from: {', '.join(ROLES.keys())}")
        sys.exit(1)

    adapter = ADAPTERS[model_name]
    system_prompt = ROLES[role_name]

    print(f"Consulting {model_name} as {role_name}...", file=sys.stderr)

    try:
        result = adapter.query(prompt=prompt, system=system_prompt)
    except Exception as e:
        print(f"Error calling {model_name}: {e}", file=sys.stderr)
        sys.exit(1)

    # Print response (formatted JSON) to stdout
    print(json.dumps(result["response"], indent=2))

    # Print usage to stderr so it doesn't pollute piped output
    usage = result["usage"]
    print(
        f"\n--- Usage: {usage['model']} | "
        f"in={usage['input_tokens']} out={usage['output_tokens']} | "
        f"${usage['estimated_cost_usd']:.4f} ---",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
