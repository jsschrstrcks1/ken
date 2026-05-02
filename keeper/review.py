"""`keeper review` — multi-persona Claude-checks-Claude verification.

Two modes:
  - DRY RUN (default): builds prompts but does not invoke any model.
    Use `keeper review` to inspect the roster and prompt shape.
  - LIVE: invokes one model call per persona in parallel. Use
    `keeper review --live` (requires the orchestrator/adapters to be
    importable; errors cleanly if they aren't).
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from keeper import checkpoint as kc
from keeper.personas import (
    Persona,
    filter_roster,
    load_all_personas,
    roster_for_repo,
)


# Estimate per persona call (rough: ~1.5K input + ~200 output tokens at
# typical model rates). Used for the cost-confirmation prompt.
ESTIMATED_COST_PER_PERSONA_USD = 0.012


def detect_repo_name(root: Path | None = None) -> str:
    return (root or kc.repo_root()).name


def build_persona_messages(
    p: Persona,
    state: dict,
    journal: list[dict],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for an adapter.query call.

    The system prompt is everything that defines the persona — body,
    criteria, penalty list, protocol, and the JSON output requirement.
    The user prompt is just the data: family state + journal.
    """
    state_payload = {
        k: v for k, v in state.items()
        if not k.startswith("_") and k not in ("instance_token",)
    }
    journal_payload = [
        {k: v for k, v in entry.items() if k != "instance_token"}
        for entry in journal
    ]

    crits = ", ".join(p.criteria) if p.criteria else "(none defined)"
    pens = "; ".join(repr(x) for x in p.penalty_phrases) if p.penalty_phrases else "(none)"

    system_prompt = (
        f"[PERSONA — {p.name}]\n\n"
        f"{p.body}\n\n"
        f"---\n\n"
        f"Follow this protocol exactly:\n"
        f"1. Generate 10 candidate critiques in your voice.\n"
        f"2. Rate each on the 3 criteria (10-point scale): {crits}\n"
        f"3. Apply -1 penalty for any critique containing: {pens}\n"
        f"4. Aggregate by MIN of the 3 scores.\n"
        f"5. Select the highest aggregate. If aggregate < 4, set comment to:\n"
        f"   'no critique cleared threshold for {p.name}'\n"
        f"6. The comment must be a single 1-3 sentence critique in your voice — "
        f"no preamble, no list, no scoring, no quotation marks.\n\n"
        f'Respond in JSON with keys: comment (string), '
        f'aggregate_score (integer 1-10), confidence (0.0-1.0).'
    )
    user_prompt = (
        f"CURRENT FAMILY STATE:\n"
        f"{json.dumps(state_payload, indent=2, ensure_ascii=False, sort_keys=True)}\n\n"
        f"RECENT JOURNAL EVENTS (last {len(journal_payload)}):\n"
        f"{json.dumps(journal_payload, indent=2, ensure_ascii=False) if journal_payload else '(none)'}"
    )
    return system_prompt, user_prompt


def build_persona_prompt(p: Persona, state: dict, journal: list[dict]) -> str:
    """Combined system+user prompt for human display in dry-run mode."""
    system, user = build_persona_messages(p, state, journal)
    return f"{system}\n\n---\n\n{user}\n"


def build_review(
    family: str,
    *,
    repo_name: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    root: Path | None = None,
) -> dict:
    """Assemble the review plan: state, roster, prompts. No model calls."""
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
        roster_view.append({
            "name": p.name,
            "repo": p.repo or ("baseline" if p.baseline else None),
            "baseline": p.baseline,
            "criticality": p.criticality,
            "needs_domain_expert_review": p.needs_domain_expert_review,
            "criteria": p.criteria,
            "prompt_chars": len(prompt),
        })
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


# ─── Live mode ──────────────────────────────────────────────────────────

class LiveReviewError(RuntimeError):
    """Raised when --live is requested but adapters aren't available."""


def _import_adapters():
    """Try to import the orchestrator's adapter dict. The orchestrator's
    adapters/__init__.py uses bare `import adapters.X` imports, which
    means we need orchestrator/ on sys.path directly (not orchestrator's
    parent)."""
    ken_root = Path(__file__).resolve().parent.parent
    orch_dir = ken_root / "orchestrator"
    if not orch_dir.exists():
        raise LiveReviewError(
            f"--live requires {orch_dir} to exist (where the orchestrator's "
            f"adapter package lives)."
        )
    # Load orchestrator/.env so adapters find their API keys.
    env_path = orch_dir / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
    if str(orch_dir) not in sys.path:
        sys.path.insert(0, str(orch_dir))
    try:
        from adapters import ADAPTERS  # type: ignore
    except Exception as e:
        raise LiveReviewError(f"could not import adapters: {e}")
    if not ADAPTERS:
        raise LiveReviewError(
            "no adapters loaded — install the SDKs the orchestrator needs "
            "(see orchestrator/requirements.txt)."
        )
    return ADAPTERS


def run_review_live(
    family: str,
    *,
    repo_name: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    model: str = "gpt",
    timeout_per_persona: int = 120,
    max_parallel: int = 5,
    root: Path | None = None,
) -> dict:
    """Build the review THEN actually invoke one model call per persona,
    in parallel. Returns the dry-run dict augmented with `results` and
    `live: true`."""
    review = build_review(
        family,
        repo_name=repo_name,
        include=include,
        exclude=exclude,
        root=root,
    )
    if not review["state_present"]:
        return review

    adapters = _import_adapters()
    if model not in adapters:
        raise LiveReviewError(
            f"unknown model {model!r}; available: {', '.join(adapters)}"
        )
    adapter = adapters[model]

    state = kc.read_state(family, root or kc.repo_root())
    journal = kc.journal_tail(family, n=10, root=root or kc.repo_root())

    all_personas = load_all_personas()
    repo = repo_name or detect_repo_name(root or kc.repo_root())
    roster = roster_for_repo(all_personas, repo)
    roster = filter_roster(
        roster, include=include, exclude=exclude, all_personas=all_personas,
    )

    results: dict[str, dict] = {}
    n = max(1, min(max_parallel, len(roster)))
    with ThreadPoolExecutor(max_workers=n) as ex:
        futures = {}
        for p in roster:
            sys_prompt, user_prompt = build_persona_messages(p, state, journal)
            fut = ex.submit(adapter.query, prompt=user_prompt, system=sys_prompt)
            futures[fut] = p.name
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                r = fut.result(timeout=timeout_per_persona)
                resp = r.get("response", {})
                comment = (
                    resp.get("comment")
                    if isinstance(resp, dict)
                    else None
                ) or _fallback_comment(resp)
                results[name] = {
                    "comment": comment,
                    "aggregate_score": resp.get("aggregate_score") if isinstance(resp, dict) else None,
                    "confidence": resp.get("confidence") if isinstance(resp, dict) else None,
                    "usage": r.get("usage", {}),
                }
            except Exception as e:
                results[name] = {"error": str(e)}

    review["live"] = True
    review["results"] = results
    review["actual_cost_usd"] = sum(
        (r.get("usage", {}) or {}).get("estimated_cost_usd", 0.0)
        for r in results.values()
    )
    return review


def _fallback_comment(resp) -> str:
    """If the model didn't return JSON-with-comment, salvage what we can."""
    if isinstance(resp, dict):
        # Try common keys
        for k in ("analysis", "proposed_update", "raw_text", "text"):
            v = resp.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip().splitlines()[0][:500]
    if isinstance(resp, str):
        return resp.strip().splitlines()[0][:500] if resp.strip() else "(no comment returned)"
    return "(no comment returned)"


# ─── Rendering ──────────────────────────────────────────────────────────

def render_review_text(review: dict, *, show_prompts: bool = False) -> str:
    """Format the review for human reading. Handles both dry-run and live."""
    if not review["state_present"]:
        return f"=== keeper review — family '{review['family']}' ===\n" + (
            "\n".join(review["notes"]) if review["notes"] else "no state"
        )

    L = []
    L.append(f"=== keeper review — family '{review['family']}' (repo: {review['repo']}) ===")
    L.append("")
    L.append(f"Roster: {len(review['roster'])} personas")
    if review.get("live"):
        L.append(f"Actual cost: ${review.get('actual_cost_usd', 0):.4f}")
    else:
        L.append(f"Estimated cost: ~${review['cost_estimate_usd']:.2f}")
    L.append("")

    if review.get("results"):
        L.append("Comments:")
        for r in review["roster"]:
            name = r["name"]
            entry = review["results"].get(name, {})
            if "error" in entry:
                L.append(f"  ✗ {name}: error — {entry['error'][:120]}")
                continue
            score = entry.get("aggregate_score")
            score_str = f" [{score}/10]" if score is not None else ""
            comment = entry.get("comment", "(no comment)")
            L.append(f"  • {name}{score_str}")
            for line in str(comment).splitlines() or [""]:
                L.append(f"      {line}")
        L.append("")
    else:
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
    if review.get("live"):
        L.append(f"--- LIVE — {len(review.get('results', {}))} personas invoked ---")
    else:
        L.append("--- DRY RUN — no Claude calls made ---")
    return "\n".join(L)

