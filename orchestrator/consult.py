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
