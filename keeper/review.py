"""`keeper review` — multi-persona Claude-checks-Claude verification.

This module is wired in DRY-RUN MODE only. It builds the prompts that
would be sent to Claude per persona but does not invoke any model calls.
Live invocation is a separate commit pending user review of the
dry-run output shape.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from keeper import checkpoint as kc
from keeper.personas import (
    Persona,
    filter_roster,
    load_all_personas,
    roster_for_repo,
)


# Per-persona estimated cost. Used only for the --dry-run summary;
# real cost depends on model + actual token usage at invocation time.
ESTIMATED_COST_PER_PERSONA_USD = 0.05


def detect_repo_name(root: Path | None = None) -> str:
    """Use the repo root's directory name as the repo identifier."""
    return (root or kc.repo_root()).name


def build_persona_prompt(p: Persona, state: dict, journal: list[dict]) -> str:
    """Compose the full prompt that will be sent to a Claude call when
    we run this persona. Includes:
      - the persona's body (system-prompt-style)
      - current family state (operator metadata stripped)
      - last 10 journal events
      - the explicit protocol footer instructing the 4-step chain
    """
    state_payload = {
        k: v for k, v in state.items()
        if not k.startswith("_") and k not in ("instance_token",)
    }
    # Strip instance_token from journal entries too — operator metadata,
    # not relevant to the persona's critique.
    journal_payload = [
        {k: v for k, v in entry.items() if k != "instance_token"}
        for entry in journal
    ]
    crits_block = ", ".join(p.criteria) if p.criteria else "(none defined)"
    pen_block = (
        "; ".join(repr(x) for x in p.penalty_phrases)
        if p.penalty_phrases
        else "(none)"
    )
    return (
        f"[PERSONA — {p.name}]\n\n"
        f"{p.body}\n\n"
        f"---\n\n"
        f"CURRENT FAMILY STATE:\n"
        f"{json.dumps(state_payload, indent=2, ensure_ascii=False, sort_keys=True)}\n\n"
        f"RECENT JOURNAL EVENTS (last {len(journal_payload)}):\n"
        f"{json.dumps(journal_payload, indent=2, ensure_ascii=False) if journal_payload else '(none)'}\n\n"
        f"---\n\n"
        f"Follow this protocol exactly:\n"
        f"1. Generate 10 candidate critiques in your voice.\n"
        f"2. Rate each on the 3 criteria (10-point scale): {crits_block}\n"
        f"3. Apply -1 penalty for any critique containing: {pen_block}\n"
        f"4. Aggregate by MIN of the 3 scores.\n"
        f"5. Select the highest aggregate. If aggregate < 4, output exactly:\n"
        f"   'no critique cleared threshold for {p.name}'\n"
        f"6. Format the winner as a single 1-3 sentence comment in your voice.\n\n"
        f"Return ONLY the final comment (no preamble, no list, no scores).\n"
    )


def build_review(
    family: str,
    *,
    repo_name: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    root: Path | None = None,
) -> dict:
    """Assemble the review plan: state, roster, prompts. No model calls.

    Returns:
        {
          family: str,
          repo: str,
          state_present: bool,
          roster: [{name, repo, baseline, criticality,
                    needs_domain_expert_review, criteria, prompt_chars}],
          prompts: {persona_name: prompt_text, ...},
          cost_estimate_usd: float,
          notes: [str, ...],
        }
    """
    root = root or kc.repo_root()
    state = kc.read_state(family, root)
    if state is None:
        return {
            "family": family,
            "repo": repo_name or detect_repo_name(root),
            "state_present": False,
            "roster": [],
            "prompts": {},
            "cost_estimate_usd": 0.0,
            "notes": [f"no family '{family}' in {root}"],
        }

    repo = repo_name or detect_repo_name(root)
    journal = kc.journal_tail(family, n=10, root=root)

    all_personas = load_all_personas()
    roster = roster_for_repo(all_personas, repo)
    roster = filter_roster(
        roster, include=include, exclude=exclude, all_personas=all_personas
    )

    prompts: dict[str, str] = {}
    notes: list[str] = []
    roster_view = []
    for p in roster:
        prompt = build_persona_prompt(p, state, journal)
        prompts[p.name] = prompt
        roster_view.append(
            {
                "name": p.name,
                "repo": p.repo or ("baseline" if p.baseline else None),
                "baseline": p.baseline,
                "criticality": p.criticality,
                "needs_domain_expert_review": p.needs_domain_expert_review,
                "criteria": p.criteria,
                "prompt_chars": len(prompt),
            }
        )
        if p.needs_domain_expert_review:
            notes.append(
                f"persona '{p.name}' carries domain-expert-review caveat — "
                f"specific thresholds in the prompt may need calibration"
            )

    return {
        "family": family,
        "repo": repo,
        "state_present": True,
        "roster": roster_view,
        "prompts": prompts,
        "cost_estimate_usd": ESTIMATED_COST_PER_PERSONA_USD * len(roster),
        "notes": notes,
    }


def render_review_text(review: dict, *, show_prompts: bool = False) -> str:
    """Format the dry-run review for human reading."""
    if not review["state_present"]:
        return f"=== keeper review — family '{review['family']}' ===\n" + (
            "\n".join(review["notes"]) if review["notes"] else "no state"
        )

    L = []
    L.append(f"=== keeper review — family '{review['family']}' (repo: {review['repo']}) ===")
    L.append("")
    L.append(f"Roster: {len(review['roster'])} personas")
    L.append(f"Estimated cost: ~${review['cost_estimate_usd']:.2f}")
    L.append("")
    L.append("Personas:")
    for r in review["roster"]:
        scope = "baseline" if r["baseline"] else (r["repo"] or "?")
        flag = "  ⚠ domain-expert" if r["needs_domain_expert_review"] else ""
        crit = f"  rank={r['criticality']}" if r.get("criticality") else ""
        L.append(
            f"  • {r['name']:<28} ({scope}){crit}  "
            f"{r['prompt_chars']}ch{flag}"
        )
    if review["notes"]:
        L.append("")
        L.append("Notes:")
        for n in review["notes"]:
            L.append(f"  - {n}")

    if show_prompts:
        L.append("")
        L.append("=" * 60)
        L.append("PROMPTS")
        L.append("=" * 60)
        for name, prompt in review["prompts"].items():
            L.append("")
            L.append(f"--- {name} " + "-" * (60 - len(name) - 5))
            L.append(prompt)

    L.append("")
    L.append("--- DRY RUN — no Claude calls made ---")
    return "\n".join(L)
