#!/usr/bin/env python3
"""
investigate.py — Chained multi-LLM investigation pipeline.

Combines fan-out reconnaissance (orchestra.py) with staged deep research
(research_orchestra.py) via a structured triage bridge.

Architecture:
  Phase 1: RECONNAISSANCE — Fan-out orchestra (Claude R1 + 5 models + deliberation)
            Outputs structured JSON threads with hypothesis, evidence, confidence.
  Phase 2: TRIAGE         — Schema-based thread scoring + merge + threshold filter.
            NOT free-form Claude — constrained operations on structured outputs.
  Phase 3: DEEP RESEARCH  — Staged research pipeline on top N threads (parallel).
            Each thread: research models verify → Claude synthesizes → analysts evaluate.
  Phase 4: SYNTHESIS      — Cross-thread conflict analysis + provenance report.

Design informed by orchestra consensus (GPT, Perplexity, You.com — April 2026):
  - Structured handoffs between pipelines (not free-form LLM triage)
  - Auto-ranking by composite score (confidence + citation density + primary sources)
  - Parallel deep dives with per-thread cost budgets
  - Citation density thresholds before deep dives
  - Cross-thread conflict reporting in final synthesis

Usage:
    python3 investigate.py <mode> "research question"
    python3 investigate.py --threads 5 <mode> "research question"
    python3 investigate.py --parallel <mode> "research question"
    python3 investigate.py --budget 2.00 <mode> "research question"
"""

import json
import os
import sys
import time
import concurrent.futures

# Load .env before importing adapters
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

from orchestra import run_orchestra, load_mode
from research_orchestra import run_staged_orchestra
from iteration import IterationController

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "state")

# ─────────────────────────────────────────────
# Thread Extraction — Structured, not free-form
# ─────────────────────────────────────────────

def extract_threads_from_fanout(state):
    """
    Extract structured research threads from fan-out state.

    Pulls hypotheses from fan-out proposals, verdicts, and low-hanging fruit.
    Each thread gets a composite score based on confidence, citation density,
    and whether multiple models raised it.
    """
    threads = []
    model_proposals = {}  # track which models raised which ideas

    for entry in state.get("fan_out", []):
        model = entry.get("model", "?")
        resp = entry.get("response")
        citations = entry.get("citations", [])
        if not resp or not isinstance(resp, dict):
            continue

        # Extract proposals
        for p in resp.get("proposals", []):
            text = p.get("PROPOSAL", p.get("proposal", str(p)))
            conf = p.get("CONFIDENCE", p.get("confidence", "MEDIUM"))
            justification = p.get("JUSTIFICATION", p.get("justification", ""))

            thread = {
                "hypothesis": str(text)[:500],
                "justification": str(justification)[:500],
                "source_models": [model],
                "evidence_cited": citations[:10],
                "confidence_raw": conf,
                "confidence_score": _parse_confidence(conf),
                "citation_count": len(citations),
                "type": "EXPLORE",
            }

            # Deduplicate: merge with existing if similar
            merged = False
            for existing in threads:
                if _threads_similar(existing["hypothesis"], thread["hypothesis"]):
                    existing["source_models"].append(model)
                    existing["evidence_cited"].extend(thread["evidence_cited"])
                    existing["confidence_score"] = max(
                        existing["confidence_score"], thread["confidence_score"]
                    )
                    existing["citation_count"] += thread["citation_count"]
                    merged = True
                    break
            if not merged:
                threads.append(thread)

        # Extract verdicts that suggest investigation
        for v in resp.get("verdicts", []):
            verdict = str(v.get("VERDICT", v.get("verdict", ""))).upper()
            if verdict in ("WHEAT_WITH_REFINEMENT", "CONTRADICTED", "PARTIALLY_VERIFIED"):
                refinement = v.get("REFINEMENT", v.get("refinement",
                                v.get("JUSTIFICATION", v.get("justification", ""))))
                if refinement and len(str(refinement)) > 30:
                    thread = {
                        "hypothesis": f"[{verdict}] {str(refinement)[:400]}",
                        "justification": f"Raised by {model} as {verdict}",
                        "source_models": [model],
                        "evidence_cited": citations[:5],
                        "confidence_raw": "MEDIUM",
                        "confidence_score": 0.6 if verdict == "WHEAT_WITH_REFINEMENT" else 0.4,
                        "citation_count": len(citations),
                        "type": "VERIFY",
                    }
                    threads.append(thread)

        # Extract low-hanging fruit as TRACE threads
        for lhf in resp.get("low_hanging_fruit", []):
            text = lhf.get("description", lhf.get("item", str(lhf))) if isinstance(lhf, dict) else str(lhf)
            if len(str(text)) > 20:
                thread = {
                    "hypothesis": str(text)[:400],
                    "justification": f"Low-hanging fruit from {model}",
                    "source_models": [model],
                    "evidence_cited": [],
                    "confidence_raw": "HIGH",
                    "confidence_score": 0.7,
                    "citation_count": 0,
                    "type": "TRACE",
                }
                threads.append(thread)

    # Score and rank
    for t in threads:
        t["composite_score"] = _compute_composite_score(t)

    threads.sort(key=lambda t: t["composite_score"], reverse=True)
    return threads


def _parse_confidence(conf):
    """Convert confidence label to float."""
    if isinstance(conf, (int, float)):
        return float(conf)
    conf_str = str(conf).upper().strip()
    return {"HIGH": 0.85, "MEDIUM": 0.55, "LOW": 0.25}.get(conf_str, 0.5)


def _threads_similar(a, b):
    """Rough dedup: check if two hypothesis strings are substantially the same."""
    a_words = set(str(a).lower().split())
    b_words = set(str(b).lower().split())
    if not a_words or not b_words:
        return False
    overlap = len(a_words & b_words)
    return overlap / min(len(a_words), len(b_words)) > 0.6


def _compute_composite_score(thread):
    """
    Composite score combining:
    - Confidence (0-1, weight 0.4)
    - Citation density (0-1 normalized, weight 0.3)
    - Multi-model agreement (0-1, weight 0.3)
    """
    conf = thread.get("confidence_score", 0.5)
    citations = min(thread.get("citation_count", 0) / 5, 1.0)  # 5+ citations = max
    models = min(len(set(thread.get("source_models", []))) / 3, 1.0)  # 3+ models = max

    return conf * 0.4 + citations * 0.3 + models * 0.3


# ─────────────────────────────────────────────
# Triage — Constrained schema-based filtering
# ─────────────────────────────────────────────

def triage_threads(threads, max_threads=3, min_score=0.3):
    """
    Filter and select threads for deep research.

    This is NOT a free-form LLM call — it's deterministic logic:
    1. Drop threads below minimum composite score
    2. Merge near-duplicates (already done in extraction)
    3. Select top N by composite score
    4. Log justification for each keep/drop decision
    """
    decisions = []

    for t in threads:
        if t["composite_score"] < min_score:
            decisions.append({
                "hypothesis": t["hypothesis"][:100],
                "action": "DROP",
                "reason": f"Score {t['composite_score']:.2f} below threshold {min_score}",
            })
        else:
            decisions.append({
                "hypothesis": t["hypothesis"][:100],
                "action": "KEEP",
                "score": t["composite_score"],
                "type": t["type"],
                "source_models": t["source_models"],
            })

    kept = [t for t in threads if t["composite_score"] >= min_score]
    selected = kept[:max_threads]

    return selected, decisions


# ─────────────────────────────────────────────
# Deep Research — Run staged pipeline per thread
# ─────────────────────────────────────────────

def run_deep_dive(thread, mode_name, thread_budget, thread_idx):
    """Run research_orchestra on a single thread."""
    task = f"""DEEP INVESTIGATION (Thread {thread_idx + 1}):

HYPOTHESIS: {thread['hypothesis']}

JUSTIFICATION: {thread['justification']}

TYPE: {thread['type']} — {"Verify a specific claim with citations" if thread['type'] == 'VERIFY'
    else "Explore a new research direction" if thread['type'] == 'EXPLORE'
    else "Trace a specific record or chain"}

PRIOR EVIDENCE: {', '.join(thread['evidence_cited'][:5]) or 'None yet'}

RAISED BY: {', '.join(thread['source_models'])}

Your task: Investigate this hypothesis thoroughly. Find primary sources, verify claims,
cite everything. If the hypothesis is wrong, say so with evidence."""

    print(f"\n{'━'*60}", file=sys.stderr)
    print(f"DEEP DIVE {thread_idx + 1}: {thread['hypothesis'][:80]}...", file=sys.stderr)
    print(f"  Type: {thread['type']} | Score: {thread['composite_score']:.2f} | Budget: ${thread_budget:.2f}", file=sys.stderr)

    controller = IterationController(
        max_research_iterations=1,
        max_recursion_depth=0,
        cost_ceiling=thread_budget,
        max_format_retries=2,
    )

    state = run_staged_orchestra(
        mode_name, task,
        deep=True,
        parent_controller=controller,
    )

    return {
        "thread_idx": thread_idx,
        "thread": thread,
        "research_state": state,
        "cost": state.get("total_cost_usd", 0),
    }


# ─────────────────────────────────────────────
# Final Synthesis — Cross-thread integration
# ─────────────────────────────────────────────

def synthesize_results(deep_dive_results, recon_state, triage_decisions):
    """Build final cross-thread synthesis."""
    synthesis = {
        "investigation_summary": {
            "threads_explored": len(deep_dive_results),
            "total_cost": sum(r["cost"] for r in deep_dive_results) + recon_state.get("total_cost_usd", 0),
        },
        "threads": [],
        "cross_thread_conflicts": [],
        "all_citations": [],
        "triage_log": triage_decisions,
    }

    all_findings = []

    for result in deep_dive_results:
        thread = result["thread"]
        state = result["research_state"]

        # Collect citations from all stages
        thread_citations = []
        for stage in state.get("stages", []):
            for entry in stage.get("responses", []):
                thread_citations.extend(entry.get("citations", []))

        # Collect findings
        thread_findings = []
        for stage in state.get("stages", []):
            for entry in stage.get("responses", []):
                resp = entry.get("response")
                if resp and isinstance(resp, dict):
                    for f in resp.get("findings", []):
                        finding_text = f.get("FINDING", f.get("finding", str(f)))
                        thread_findings.append({
                            "finding": str(finding_text)[:500],
                            "model": entry.get("model", "?"),
                            "source_thread": result["thread_idx"],
                        })
                    for v in resp.get("verdicts", []):
                        verdict_text = v.get("VERDICT", v.get("verdict", ""))
                        evidence = v.get("EVIDENCE", v.get("evidence", ""))
                        if evidence:
                            thread_findings.append({
                                "finding": f"[{verdict_text}] {str(evidence)[:400]}",
                                "model": entry.get("model", "?"),
                                "source_thread": result["thread_idx"],
                            })

        all_findings.extend(thread_findings)

        synthesis["threads"].append({
            "idx": result["thread_idx"],
            "hypothesis": thread["hypothesis"][:200],
            "type": thread["type"],
            "composite_score": thread["composite_score"],
            "source_models": thread["source_models"],
            "findings_count": len(thread_findings),
            "citations_count": len(thread_citations),
            "cost": result["cost"],
        })
        synthesis["all_citations"].extend(thread_citations)

    # Deduplicate citations
    synthesis["all_citations"] = list(set(synthesis["all_citations"]))

    return synthesis


# ─────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────

def run_investigation(mode_name, task, max_threads=3, parallel=False,
                      budget=1.50, min_score=0.3):
    """Run the full investigation pipeline."""

    state = {
        "pipeline": "investigate",
        "mode": mode_name,
        "task": task,
        "config": {
            "max_threads": max_threads,
            "parallel": parallel,
            "budget": budget,
            "min_score": min_score,
        },
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phases": {},
        "status": "running",
    }

    try:
        return _run_investigation_inner(state, mode_name, task, max_threads, parallel, budget, min_score)
    except Exception as e:
        print(f"\n{'!'*60}", file=sys.stderr)
        print(f"PIPELINE CRASHED: {e}", file=sys.stderr)
        print(f"{'!'*60}", file=sys.stderr)
        state["status"] = f"crashed: {str(e)[:200]}"
        state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _save_state(state)
        print(f"  → Partial state saved to state/investigate.json", file=sys.stderr)
        return state


def _run_investigation_inner(state, mode_name, task, max_threads, parallel, budget, min_score):
    """Inner pipeline logic — wrapped by run_investigation for crash recovery."""

    per_thread_budget = budget / (max_threads + 1)  # +1 for recon phase

    # ══════════════════════════════════════════
    # PHASE 1: RECONNAISSANCE (fan-out orchestra)
    # ══════════════════════════════════════════
    print(f"\n{'═'*60}", file=sys.stderr)
    print(f"PHASE 1: RECONNAISSANCE — Fan-out orchestra", file=sys.stderr)
    print(f"{'═'*60}", file=sys.stderr)

    recon_state = run_orchestra(mode_name, task)
    recon_cost = recon_state.get("total_cost_usd", 0)
    state["phases"]["reconnaissance"] = {
        "cost": recon_cost,
        "models_responded": sum(1 for e in recon_state.get("fan_out", []) if e.get("response")),
        "models_total": len(recon_state.get("fan_out", [])),
    }

    print(f"\n  Recon cost: ${recon_cost:.4f}", file=sys.stderr)
    remaining_budget = budget - recon_cost

    # ══════════════════════════════════════════
    # PHASE 2: TRIAGE — Structured thread extraction + filtering
    # ══════════════════════════════════════════
    print(f"\n{'═'*60}", file=sys.stderr)
    print(f"PHASE 2: TRIAGE — Extract and rank research threads", file=sys.stderr)
    print(f"{'═'*60}", file=sys.stderr)

    threads = extract_threads_from_fanout(recon_state)
    print(f"\n  Extracted {len(threads)} candidate threads", file=sys.stderr)

    selected, decisions = triage_threads(threads, max_threads=max_threads, min_score=min_score)
    print(f"  Selected {len(selected)} for deep research", file=sys.stderr)

    for i, t in enumerate(selected):
        print(f"  [{i+1}] {t['type']:7s} | score={t['composite_score']:.2f} | "
              f"models={','.join(t['source_models'])} | {t['hypothesis'][:80]}", file=sys.stderr)

    kept_count = sum(1 for d in decisions if d["action"] == "KEEP")
    dropped_count = sum(1 for d in decisions if d["action"] == "DROP")
    print(f"  Kept: {kept_count} | Dropped: {dropped_count}", file=sys.stderr)

    state["phases"]["triage"] = {
        "candidates": len(threads),
        "selected": len(selected),
        "dropped": dropped_count,
        "decisions": decisions,
        "threads": [
            {
                "hypothesis": t["hypothesis"][:200],
                "type": t["type"],
                "composite_score": t["composite_score"],
                "source_models": t["source_models"],
                "citation_count": t["citation_count"],
            }
            for t in selected
        ],
    }

    if not selected:
        print(f"\n  No threads above threshold. Investigation complete.", file=sys.stderr)
        state["status"] = "completed_no_threads"
        _save_state(state)
        return state

    # ══════════════════════════════════════════
    # PHASE 3: DEEP RESEARCH — Staged pipeline per thread
    # ══════════════════════════════════════════
    print(f"\n{'═'*60}", file=sys.stderr)
    exec_mode = "PARALLEL" if parallel else "SEQUENTIAL"
    print(f"PHASE 3: DEEP RESEARCH — {len(selected)} threads, {exec_mode}", file=sys.stderr)
    print(f"  Remaining budget: ${remaining_budget:.2f} (${remaining_budget/len(selected):.2f}/thread)", file=sys.stderr)
    print(f"{'═'*60}", file=sys.stderr)

    thread_budget = remaining_budget / len(selected)
    deep_dive_results = []

    if parallel and len(selected) > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as executor:
            futures = {
                executor.submit(run_deep_dive, t, mode_name, thread_budget, i): i
                for i, t in enumerate(selected)
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    deep_dive_results.append(result)
                    print(f"\n  Thread {result['thread_idx']+1} complete | cost: ${result['cost']:.4f}", file=sys.stderr)
                except Exception as e:
                    idx = futures[future]
                    print(f"\n  Thread {idx+1} FAILED: {e}", file=sys.stderr)
                    deep_dive_results.append({
                        "thread_idx": idx,
                        "thread": selected[idx],
                        "research_state": {"error": str(e), "total_cost_usd": 0},
                        "cost": 0,
                    })
    else:
        for i, thread in enumerate(selected):
            result = run_deep_dive(thread, mode_name, thread_budget, i)
            deep_dive_results.append(result)

    # Sort by thread index for consistent output
    deep_dive_results.sort(key=lambda r: r["thread_idx"])

    total_deep_cost = sum(r["cost"] for r in deep_dive_results)
    state["phases"]["deep_research"] = {
        "threads_run": len(deep_dive_results),
        "execution_mode": exec_mode.lower(),
        "total_cost": total_deep_cost,
        "per_thread": [
            {
                "idx": r["thread_idx"],
                "hypothesis": r["thread"]["hypothesis"][:100],
                "cost": r["cost"],
            }
            for r in deep_dive_results
        ],
    }

    # ══════════════════════════════════════════
    # PHASE 4: CROSS-THREAD SYNTHESIS
    # ══════════════════════════════════════════
    print(f"\n{'═'*60}", file=sys.stderr)
    print(f"PHASE 4: SYNTHESIS — Cross-thread integration", file=sys.stderr)
    print(f"{'═'*60}", file=sys.stderr)

    synthesis = synthesize_results(deep_dive_results, recon_state, decisions)
    state["phases"]["synthesis"] = synthesis

    # ── Finalize ──
    state["total_cost_usd"] = recon_cost + total_deep_cost
    state["status"] = "completed"
    state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    _save_state(state)
    return state


def _save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = os.path.join(STATE_DIR, "investigate.json")
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ─────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────

def print_report(state):
    print(f"\n{'═'*60}")
    print(f"INVESTIGATION COMPLETE: {state['mode']} mode")
    print(f"{'═'*60}")
    print(f"Task: {state['task'][:200]}")
    print(f"Status: {state['status']}")
    print(f"Total cost: ${state.get('total_cost_usd', 0):.4f}")

    # Phase 1
    recon = state.get("phases", {}).get("reconnaissance", {})
    print(f"\n── Phase 1: Reconnaissance ──")
    print(f"  Models: {recon.get('models_responded', '?')}/{recon.get('models_total', '?')} responded | Cost: ${recon.get('cost', 0):.4f}")

    # Phase 2
    triage = state.get("phases", {}).get("triage", {})
    print(f"\n── Phase 2: Triage ──")
    print(f"  Candidates: {triage.get('candidates', '?')} → Selected: {triage.get('selected', '?')} | Dropped: {triage.get('dropped', '?')}")
    for t in triage.get("threads", []):
        print(f"  [{t.get('type', '?'):7s}] score={t.get('composite_score', 0):.2f} | {t.get('hypothesis', '?')[:80]}")

    # Phase 3
    deep = state.get("phases", {}).get("deep_research", {})
    print(f"\n── Phase 3: Deep Research ({deep.get('execution_mode', '?')}) ──")
    print(f"  Threads: {deep.get('threads_run', '?')} | Cost: ${deep.get('total_cost', 0):.4f}")
    for pt in deep.get("per_thread", []):
        print(f"  [Thread {pt.get('idx', '?')+1}] ${pt.get('cost', 0):.4f} | {pt.get('hypothesis', '?')[:80]}")

    # Phase 4
    synthesis = state.get("phases", {}).get("synthesis", {})
    citations = synthesis.get("all_citations", [])
    print(f"\n── Phase 4: Synthesis ──")
    print(f"  Citations: {len(citations)}")
    for c in citations[:10]:
        print(f"  {c}")
    if len(citations) > 10:
        print(f"  ... and {len(citations) - 10} more")

    print(f"\n── Total Cost: ${state.get('total_cost_usd', 0):.4f} ──")
    print(f"\nFull state: state/investigate.json")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    args = sys.argv[1:]

    # Parse flags
    parallel = "--parallel" in args
    if parallel:
        args.remove("--parallel")

    max_threads = 3
    if "--threads" in args:
        idx = args.index("--threads")
        max_threads = int(args[idx + 1])
        args.pop(idx + 1)
        args.pop(idx)

    budget = 1.50
    if "--budget" in args:
        idx = args.index("--budget")
        budget = float(args[idx + 1])
        args.pop(idx + 1)
        args.pop(idx)

    exhaustive = "--exhaustive" in args
    if exhaustive:
        args.remove("--exhaustive")
        max_threads = 10  # effectively unlimited
        budget = max(budget, 5.00)

    mode_name = args[0].lower()
    task = " ".join(args[1:])

    print(f"Investigation: {mode_name} mode", file=sys.stderr)
    print(f"Task: {task}", file=sys.stderr)
    print(f"Config: threads={max_threads}, parallel={parallel}, budget=${budget:.2f}", file=sys.stderr)

    state = run_investigation(
        mode_name, task,
        max_threads=max_threads,
        parallel=parallel,
        budget=budget,
    )
    print_report(state)
    print(json.dumps(state, indent=2, default=str))


if __name__ == "__main__":
    main()
