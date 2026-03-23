#!/usr/bin/env python3
"""
orchestrate.py — Reads a mode config, runs the pipeline, manages blackboard state.

Usage:
    python3 orchestrate.py <mode> "task description"
    python3 orchestrate.py sermon "Preach Romans 5:1-5 on suffering producing hope"
    python3 orchestrate.py sheep "Plan spring breeding for the Katahdin ewes"

Modes are defined in modes/*.yaml. The orchestrator:
  1. Loads the mode config
  2. Initializes a blackboard (shared state)
  3. Runs each pipeline step in order
  4. Tracks costs, skips failed external calls gracefully
  5. Writes final state to state/current.json
"""

import json
import os
import sys
import time
import yaml

# Load .env if present
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

from adapters import ADAPTERS
from verify import verify_claims

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
MODES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modes")


def load_mode(mode_name):
    """Load a mode config from modes/<name>.yaml."""
    path = os.path.join(MODES_DIR, f"{mode_name}.yaml")
    if not os.path.exists(path):
        available = [f.replace(".yaml", "") for f in os.listdir(MODES_DIR) if f.endswith(".yaml")]
        print(f"Error: Unknown mode '{mode_name}'. Available: {', '.join(available)}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def init_blackboard(mode_config, task):
    """Initialize the shared blackboard state."""
    return {
        "mode": mode_config["name"],
        "task": task,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline": [],
        "current_draft": None,
        "consultations": [],
        "claims": [],
        "verified_claims": [],
        "unverified_claims": [],
        "failed_claims": [],
        "cost_log": [],
        "total_cost_usd": 0.0,
        "iterations": 0,
        "max_iterations": mode_config.get("max_loops", 1),
        "status": "running",
    }


def run_step(step, blackboard):
    """Execute a single pipeline step. Returns True if step ran, False if skipped."""
    model_name = step.get("model", "claude")
    role = step.get("role", "freestyle")
    step_name = step.get("step", "unnamed")
    optional = step.get("optional", False)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Step: {step_name} | Model: {model_name} | Role: {role}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Claude steps are handled locally (by Claude Code itself)
    if model_name == "claude":
        print(f"  → Claude step (local). Skipping adapter call.", file=sys.stderr)
        print(f"  → Description: {step.get('description', 'N/A')}", file=sys.stderr)
        blackboard["pipeline"].append({
            "step": step_name,
            "model": "claude",
            "status": "local",
            "description": step.get("description", ""),
            "notes": step.get("notes", "Claude handles this step locally in Claude Code."),
        })
        return True

    # External model call
    if model_name not in ADAPTERS:
        print(f"  → Unknown model '{model_name}'. Skipping.", file=sys.stderr)
        blackboard["pipeline"].append({
            "step": step_name, "model": model_name, "status": "skipped",
            "reason": f"Unknown model: {model_name}",
        })
        return False

    adapter = ADAPTERS[model_name]

    # Build prompt from blackboard context
    prompt = build_prompt(step, blackboard)

    # Import role system prompts from consult.py
    from consult import ROLES
    system_prompt = ROLES.get(role, ROLES["freestyle"])

    try:
        result = adapter.query(prompt=prompt, system=system_prompt)
    except Exception as e:
        msg = f"API call failed: {e}"
        print(f"  → {msg}", file=sys.stderr)
        if optional:
            print(f"  → Step is optional. Continuing.", file=sys.stderr)
        blackboard["pipeline"].append({
            "step": step_name, "model": model_name, "status": "failed",
            "error": str(e), "optional": optional,
        })
        return False

    # Record result
    usage = result["usage"]
    blackboard["cost_log"].append(usage)
    blackboard["total_cost_usd"] += usage["estimated_cost_usd"]
    blackboard["consultations"].append({
        "step": step_name,
        "model": model_name,
        "role": role,
        "response": result["response"],
    })

    # Extract and verify claims
    claims = result["response"].get("claims", [])
    if claims:
        verification = verify_claims(claims, blackboard["mode"])
        blackboard["claims"].extend(claims)
        blackboard["verified_claims"].extend(verification["verified"])
        blackboard["unverified_claims"].extend(verification["unverified"])
        blackboard["failed_claims"].extend(verification["failed"])

    blackboard["pipeline"].append({
        "step": step_name,
        "model": model_name,
        "status": "completed",
        "usage": usage,
        "claims_found": len(claims),
    })

    print(f"  → Completed. Cost: ${usage['estimated_cost_usd']:.4f}", file=sys.stderr)
    return True


def build_prompt(step, blackboard):
    """Build a prompt for an external model from blackboard state."""
    parts = [f"Task: {blackboard['task']}"]

    if blackboard["current_draft"]:
        parts.append(f"\nCurrent draft/plan:\n{blackboard['current_draft']}")

    # Include prior consultation summaries (not full responses)
    if blackboard["consultations"]:
        parts.append("\nPrior feedback from other models:")
        for c in blackboard["consultations"][-3:]:  # Last 3 to stay within context
            summary = c["response"].get("analysis", str(c["response"]))[:500]
            parts.append(f"  [{c['model']} as {c['role']}]: {summary}")

    if step.get("description"):
        parts.append(f"\nYour specific assignment: {step['description']}")

    parts.append("\nRespond in JSON format.")
    return "\n".join(parts)


def check_convergence(blackboard):
    """Check if the pipeline has converged (minimal delta between iterations)."""
    consultations = blackboard["consultations"]
    if len(consultations) < 2:
        return False

    last = consultations[-1]["response"]
    prev = consultations[-2]["response"]

    # Simple convergence: if confidence is high and analysis is short
    last_conf = last.get("confidence", 0)
    if last_conf >= 0.95:
        print("  → Convergence detected (confidence >= 0.95).", file=sys.stderr)
        return True

    return False


def save_state(blackboard):
    """Write blackboard to state/current.json."""
    os.makedirs(STATE_DIR, exist_ok=True)
    path = os.path.join(STATE_DIR, "current.json")
    with open(path, "w") as f:
        json.dump(blackboard, f, indent=2, default=str)
    print(f"\nState saved to {path}", file=sys.stderr)


def print_summary(blackboard):
    """Print a human-readable summary."""
    print(f"\n{'='*60}")
    print(f"ORCHESTRATION COMPLETE: {blackboard['mode']} mode")
    print(f"{'='*60}")
    print(f"Task: {blackboard['task']}")
    print(f"Status: {blackboard['status']}")
    print(f"Steps run: {len(blackboard['pipeline'])}")
    print(f"Total cost: ${blackboard['total_cost_usd']:.4f}")

    if blackboard["consultations"]:
        print(f"\nConsultations:")
        for c in blackboard["consultations"]:
            print(f"  • {c['model']} ({c['role']})")

    if blackboard["unverified_claims"]:
        print(f"\n⚠️  UNVERIFIED CLAIMS ({len(blackboard['unverified_claims'])}):")
        for claim in blackboard["unverified_claims"]:
            print(f"  • [{claim.get('type', '?')}] {claim.get('claim', '?')}")

    if blackboard["failed_claims"]:
        print(f"\n✗ FAILED CLAIMS ({len(blackboard['failed_claims'])}):")
        for claim in blackboard["failed_claims"]:
            print(f"  • [{claim.get('type', '?')}] {claim.get('claim', '?')}")

    verified = len(blackboard["verified_claims"])
    if verified:
        print(f"\n✓ Verified claims: {verified}")

    print(f"\nFull state: state/current.json")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mode_name = sys.argv[1].lower()
    task = " ".join(sys.argv[2:])

    mode_config = load_mode(mode_name)
    blackboard = init_blackboard(mode_config, task)
    pipeline = mode_config.get("pipeline", [])

    print(f"Orchestrating: {mode_name} mode", file=sys.stderr)
    print(f"Pipeline: {len(pipeline)} steps", file=sys.stderr)
    print(f"Max loops: {blackboard['max_iterations']}", file=sys.stderr)

    iteration = 0
    max_iter = blackboard["max_iterations"]

    while iteration <= max_iter:
        blackboard["iterations"] = iteration

        for step in pipeline:
            run_step(step, blackboard)

        if check_convergence(blackboard):
            break

        iteration += 1
        if iteration <= max_iter:
            print(f"\n--- Loop {iteration}/{max_iter} ---", file=sys.stderr)

    blackboard["status"] = "completed"
    blackboard["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_state(blackboard)
    print_summary(blackboard)

    # Output final consultations as JSON to stdout for piping
    output = {
        "mode": blackboard["mode"],
        "task": blackboard["task"],
        "consultations": blackboard["consultations"],
        "unverified_claims": blackboard["unverified_claims"],
        "failed_claims": blackboard["failed_claims"],
        "total_cost_usd": blackboard["total_cost_usd"],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
