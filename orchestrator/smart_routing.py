"""
smart_routing.py — Intelligent trigger detection, disagreement scoring,
weighted voting, and routing for orchestra pipelines.

Features:
  1. Conditional round-robin triggers (6 conditions)
  2. Disagreement detection via keyword/structural overlap
  3. Weighted voting with model performance tracking
  4. Intelligent routing (skip expensive models for simple tasks)
  5. Feedback loop for refining triggers over time

Used by both orchestra.py and research_orchestra.py.
"""

import json
import os
import re
import hashlib
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PERF_LOG_PATH = os.path.join(SCRIPT_DIR, "state", "model_performance.json")

# ─────────────────────────────────────────────
# 1. Round-Robin Trigger Detection
# ─────────────────────────────────────────────

# High-stakes keywords by domain
HIGH_STAKES_KEYWORDS = {
    "family-history": [
        "royal", "king", "queen", "plantagenet", "charlemagne", "land grant",
        "tribal", "seminole", "cherokee", "native american", "nobility",
        "hidalgo", "hidalguía", "descendant of", "direct line", "confirmed ancestor",
        "dna", "identity", "maiden name", "biological parent",
    ],
    "default": [
        "legal", "medical", "financial", "safety", "security", "compliance",
    ],
}


def detect_triggers(fan_out_responses, mode="family-history"):
    """
    Analyze fan-out responses and return which triggers fired.

    Returns:
        {
            "should_trigger": bool,
            "triggers_fired": [{"id": str, "reason": str, "score": float}],
            "summary": str,
        }
    """
    triggers = []
    valid_responses = [r for r in fan_out_responses
                       if r.get("response") and isinstance(r.get("response"), dict)]

    if len(valid_responses) < 2:
        return {"should_trigger": False, "triggers_fired": [], "summary": "Too few valid responses"}

    # ── Trigger 1: Semantic Disagreement ──
    disagreement = measure_disagreement(valid_responses)
    if disagreement["score"] > 0.4:  # High disagreement
        triggers.append({
            "id": "disagreement",
            "reason": f"High disagreement score: {disagreement['score']:.2f} — {disagreement['detail']}",
            "score": disagreement["score"],
        })

    # ── Trigger 2: Low Confidence ──
    confidence_issue = check_low_confidence(valid_responses)
    if confidence_issue["triggered"]:
        triggers.append({
            "id": "low_confidence",
            "reason": confidence_issue["reason"],
            "score": confidence_issue["avg_confidence"],
        })

    # ── Trigger 3: Citation Conflict ──
    citation_conflict = check_citation_conflict(valid_responses)
    if citation_conflict["triggered"]:
        triggers.append({
            "id": "citation_conflict",
            "reason": citation_conflict["reason"],
            "score": citation_conflict["overlap"],
        })

    # ── Trigger 4: High-Stakes Claims ──
    stakes = check_high_stakes(valid_responses, mode)
    if stakes["triggered"]:
        triggers.append({
            "id": "high_stakes",
            "reason": stakes["reason"],
            "score": stakes["keyword_density"],
        })

    # ── Trigger 5: Partial Gap Coverage ──
    gaps = check_partial_gaps(valid_responses)
    if gaps["triggered"]:
        triggers.append({
            "id": "partial_gaps",
            "reason": gaps["reason"],
            "score": gaps["coverage_score"],
        })

    # ── Trigger 6: Format Degradation ──
    format_issues = check_format_degradation(fan_out_responses)
    if format_issues["triggered"]:
        triggers.append({
            "id": "format_degradation",
            "reason": format_issues["reason"],
            "score": format_issues["failure_rate"],
        })

    should_trigger = len(triggers) >= 2 or any(t["id"] == "high_stakes" for t in triggers)

    summary_parts = [t["reason"] for t in triggers]
    summary = f"{len(triggers)} triggers fired: {'; '.join(summary_parts)}" if triggers else "No triggers fired"

    return {
        "should_trigger": should_trigger,
        "triggers_fired": triggers,
        "summary": summary,
    }


# ─────────────────────────────────────────────
# Trigger Implementation Functions
# ─────────────────────────────────────────────

def measure_disagreement(responses):
    """
    Measure structural disagreement between responses.
    Uses verdict agreement, proposal overlap, and key assertion comparison.
    """
    # Compare verdicts across models
    verdict_sets = {}
    for r in responses:
        model = r["model"]
        verdicts = r["response"].get("verdicts", [])
        for v in verdicts:
            pid = v.get("PROPOSAL_ID", v.get("proposal_id", v.get("proposal_ref", "?")))
            verdict_val = str(v.get("VERDICT", v.get("verdict", "?"))).upper()
            if pid not in verdict_sets:
                verdict_sets[pid] = {}
            verdict_sets[pid][model] = verdict_val

    # Calculate agreement rate
    if verdict_sets:
        agreements = 0
        total = 0
        for pid, model_verdicts in verdict_sets.items():
            vals = list(model_verdicts.values())
            if len(vals) >= 2:
                total += 1
                if len(set(vals)) == 1:
                    agreements += 1
        agreement_rate = agreements / total if total > 0 else 1.0
        disagreement_score = 1.0 - agreement_rate
    else:
        # No shared verdicts — compare proposal themes via keyword overlap
        all_proposals = []
        for r in responses:
            props = r["response"].get("proposals", [])
            text = " ".join(str(p.get("PROPOSAL", p.get("proposal", ""))) for p in props).lower()
            all_proposals.append(set(text.split()))

        if len(all_proposals) >= 2:
            overlaps = []
            for i in range(len(all_proposals)):
                for j in range(i + 1, len(all_proposals)):
                    if all_proposals[i] and all_proposals[j]:
                        overlap = len(all_proposals[i] & all_proposals[j]) / max(
                            len(all_proposals[i] | all_proposals[j]), 1)
                        overlaps.append(overlap)
            avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.5
            disagreement_score = 1.0 - avg_overlap
        else:
            disagreement_score = 0.0

    detail = f"{len(verdict_sets)} shared proposals evaluated" if verdict_sets else "keyword overlap comparison"
    return {"score": round(disagreement_score, 2), "detail": detail}


def check_low_confidence(responses):
    """Check if any model reports low confidence."""
    confidences = []
    low_models = []

    for r in responses:
        resp = r["response"]
        # Check explicit confidence field
        conf = resp.get("confidence")
        if isinstance(conf, (int, float)):
            confidences.append(conf)
            if conf < 0.5:
                low_models.append(r["model"])

        # Check proposal-level confidence
        for p in resp.get("proposals", resp.get("findings", [])):
            if isinstance(p, dict):
                c = str(p.get("CONFIDENCE", p.get("confidence", ""))).upper()
                if c == "LOW":
                    low_models.append(r["model"])
                    confidences.append(0.3)
                elif c == "MEDIUM":
                    confidences.append(0.6)
                elif c == "HIGH":
                    confidences.append(0.8)

    avg = sum(confidences) / len(confidences) if confidences else 0.7

    triggered = avg < 0.65 or len(set(low_models)) >= 1
    reason = f"Avg confidence {avg:.2f}"
    if low_models:
        reason += f", low-confidence models: {', '.join(set(low_models))}"

    return {"triggered": triggered, "avg_confidence": round(avg, 2), "reason": reason}


def check_citation_conflict(responses):
    """Check for contradictory or non-overlapping citations."""
    all_citations = {}
    for r in responses:
        model = r["model"]
        cites = r.get("citations", [])
        # Also extract from findings
        resp = r["response"]
        for finding in resp.get("findings", resp.get("claims", [])):
            if isinstance(finding, dict):
                url = finding.get("url", finding.get("SOURCE", finding.get("source", "")))
                if url and url.startswith("http"):
                    cites.append(url)

        # Normalize URLs (strip trailing slashes, fragments)
        normalized = set()
        for c in cites:
            c = c.split("#")[0].rstrip("/").lower()
            normalized.add(c)

        all_citations[model] = normalized

    if len(all_citations) < 2:
        return {"triggered": False, "overlap": 1.0, "reason": "Not enough models with citations"}

    # Pairwise overlap
    models = list(all_citations.keys())
    overlaps = []
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            s1 = all_citations[models[i]]
            s2 = all_citations[models[j]]
            if s1 and s2:
                overlap = len(s1 & s2) / max(len(s1 | s2), 1)
                overlaps.append(overlap)

    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 1.0
    triggered = avg_overlap < 0.3  # Less than 30% citation overlap

    return {
        "triggered": triggered,
        "overlap": round(avg_overlap, 2),
        "reason": f"Citation overlap: {avg_overlap:.0%} across {len(models)} models",
    }


def check_high_stakes(responses, mode="family-history"):
    """Check if responses contain high-stakes claims."""
    keywords = HIGH_STAKES_KEYWORDS.get(mode, HIGH_STAKES_KEYWORDS["default"])

    all_text = ""
    for r in responses:
        resp = r["response"]
        all_text += json.dumps(resp, default=str).lower()

    hits = sum(1 for kw in keywords if kw.lower() in all_text)
    density = hits / max(len(keywords), 1)

    triggered = density > 0.15  # More than 15% of keywords present

    matching = [kw for kw in keywords if kw.lower() in all_text]
    reason = f"{hits}/{len(keywords)} high-stakes keywords found"
    if matching:
        reason += f": {', '.join(matching[:5])}"

    return {"triggered": triggered, "keyword_density": round(density, 2), "reason": reason}


def check_partial_gaps(responses):
    """Check if models each address different aspects of the same gap."""
    # Extract unique topics/keywords per model
    model_topics = {}
    for r in responses:
        model = r["model"]
        resp = r["response"]
        text = json.dumps(resp, default=str).lower()
        # Extract key nouns (simple heuristic)
        words = set(re.findall(r'\b[a-z]{5,}\b', text))
        model_topics[model] = words

    if len(model_topics) < 2:
        return {"triggered": False, "coverage_score": 0, "reason": "Not enough models"}

    # Check if models cover different ground
    all_topics = set()
    for topics in model_topics.values():
        all_topics |= topics

    # Calculate per-model unique contribution
    unique_contributions = {}
    for model, topics in model_topics.items():
        other_topics = set()
        for m, t in model_topics.items():
            if m != model:
                other_topics |= t
        unique = topics - other_topics
        unique_contributions[model] = len(unique) / max(len(topics), 1)

    avg_uniqueness = sum(unique_contributions.values()) / len(unique_contributions)

    # High uniqueness = each model covering different ground = potential for round-robin value
    triggered = avg_uniqueness > 0.3

    return {
        "triggered": triggered,
        "coverage_score": round(avg_uniqueness, 2),
        "reason": f"Avg per-model unique coverage: {avg_uniqueness:.0%}",
    }


def check_format_degradation(responses):
    """Check how many models returned invalid or degraded responses."""
    total = len(responses)
    failures = sum(1 for r in responses if r.get("response") is None)
    raw_text = sum(1 for r in responses if r.get("response") and
                   isinstance(r.get("response"), dict) and "raw_text" in r["response"])

    bad = failures + raw_text
    rate = bad / max(total, 1)

    return {
        "triggered": bad >= 2,
        "failure_rate": round(rate, 2),
        "reason": f"{bad}/{total} models returned invalid/degraded responses",
    }


# ─────────────────────────────────────────────
# 2. Weighted Voting
# ─────────────────────────────────────────────

def load_performance_log():
    """Load model performance history."""
    if os.path.exists(PERF_LOG_PATH):
        with open(PERF_LOG_PATH) as f:
            return json.load(f)
    return {"models": {}, "runs": 0}


def save_performance_log(log):
    """Save model performance history."""
    os.makedirs(os.path.dirname(PERF_LOG_PATH), exist_ok=True)
    with open(PERF_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_model_weights(mode="default"):
    """
    Get model weights based on historical performance.
    Returns dict of model_name -> weight (0.0-1.0).
    Defaults to equal weights if no history.
    """
    log = load_performance_log()
    weights = {}

    for model, data in log.get("models", {}).items():
        mode_data = data.get(mode, data.get("default", {}))
        # Weight = (successful_responses / total_calls) * avg_quality
        total = mode_data.get("total_calls", 0)
        successes = mode_data.get("successful_responses", 0)
        avg_quality = mode_data.get("avg_quality", 0.5)

        if total > 0:
            reliability = successes / total
            weights[model] = round(reliability * avg_quality, 2)
        else:
            weights[model] = 0.5  # Default weight

    return weights


def record_model_performance(model_name, mode, success, quality_score=None,
                              cost=0, response_valid=True):
    """Record a model's performance for future weighting."""
    log = load_performance_log()
    log["runs"] = log.get("runs", 0) + 1

    if model_name not in log["models"]:
        log["models"][model_name] = {}

    if mode not in log["models"][model_name]:
        log["models"][model_name][mode] = {
            "total_calls": 0,
            "successful_responses": 0,
            "format_failures": 0,
            "total_cost": 0,
            "avg_quality": 0.5,
            "quality_samples": [],
        }

    data = log["models"][model_name][mode]
    data["total_calls"] += 1
    if success:
        data["successful_responses"] += 1
    if not response_valid:
        data["format_failures"] += 1
    data["total_cost"] = round(data["total_cost"] + cost, 4)

    if quality_score is not None:
        samples = data.get("quality_samples", [])
        samples.append(quality_score)
        # Keep last 20 samples
        if len(samples) > 20:
            samples = samples[-20:]
        data["quality_samples"] = samples
        data["avg_quality"] = round(sum(samples) / len(samples), 2)

    save_performance_log(log)


def weighted_synthesis(responses, mode="default"):
    """
    Produce a weighted summary of model responses.
    Higher-weighted models' proposals get priority.
    """
    weights = get_model_weights(mode)

    weighted_proposals = []
    for r in responses:
        model = r["model"]
        weight = weights.get(model, 0.5)
        resp = r.get("response")
        if not resp or not isinstance(resp, dict):
            continue

        for p in resp.get("proposals", resp.get("findings", [])):
            if isinstance(p, dict):
                weighted_proposals.append({
                    "model": model,
                    "weight": weight,
                    "proposal": p,
                })

    # Sort by weight descending
    weighted_proposals.sort(key=lambda x: x["weight"], reverse=True)
    return weighted_proposals


# ─────────────────────────────────────────────
# 3. Intelligent Routing
# ─────────────────────────────────────────────

# Model cost tiers (approximate $/1K tokens)
MODEL_COST_TIERS = {
    "perplexity": {"tier": "cheap", "cost_per_call": 0.006},
    "youdotcom": {"tier": "cheap", "cost_per_call": 0.006},
    "gpt": {"tier": "medium", "cost_per_call": 0.010},
    "gemini": {"tier": "medium", "cost_per_call": 0.005},
    "grok": {"tier": "expensive", "cost_per_call": 0.025},
}

# Task complexity signals
COMPLEXITY_KEYWORDS = {
    "simple": ["verify", "check", "confirm", "look up", "find", "search for"],
    "moderate": ["compare", "analyze", "evaluate", "research", "investigate"],
    "complex": ["synthesize", "trace lineage", "prove connection", "deep dive",
                "reconstruct", "resolve contradiction", "challenge"],
}


def assess_task_complexity(task):
    """
    Assess task complexity to determine routing strategy.
    Returns: "simple" | "moderate" | "complex"
    """
    task_lower = task.lower()

    complex_hits = sum(1 for kw in COMPLEXITY_KEYWORDS["complex"] if kw in task_lower)
    moderate_hits = sum(1 for kw in COMPLEXITY_KEYWORDS["moderate"] if kw in task_lower)
    simple_hits = sum(1 for kw in COMPLEXITY_KEYWORDS["simple"] if kw in task_lower)

    # Also check length — longer tasks tend to be more complex
    word_count = len(task.split())

    if complex_hits >= 2 or word_count > 100:
        return "complex"
    elif moderate_hits >= 2 or word_count > 50:
        return "moderate"
    elif simple_hits >= 1 and word_count < 30:
        return "simple"
    else:
        return "moderate"  # Default to moderate


def route_models(task, available_models, mode="default"):
    """
    Select which models to use based on task complexity and model performance.

    Returns:
        list of model configs to use (subset of available_models)
    """
    complexity = assess_task_complexity(task)
    weights = get_model_weights(mode)

    if complexity == "simple":
        # Use only cheap/fast models
        selected = [m for m in available_models
                    if MODEL_COST_TIERS.get(m["model"], {}).get("tier") in ("cheap", "medium")]
        # Ensure at least 2 models
        if len(selected) < 2:
            selected = available_models[:2]
        return selected

    elif complexity == "moderate":
        # Use all except the most expensive if it has low weight
        selected = []
        for m in available_models:
            model_name = m["model"]
            tier = MODEL_COST_TIERS.get(model_name, {}).get("tier", "medium")
            weight = weights.get(model_name, 0.5)

            if tier == "expensive" and weight < 0.4:
                continue  # Skip expensive low-performers
            selected.append(m)

        return selected if selected else available_models

    else:  # complex
        # Use all models — the task warrants full coverage
        return available_models


# ─────────────────────────────────────────────
# 4. Feedback Loop
# ─────────────────────────────────────────────

def record_trigger_outcome(trigger_id, was_useful, mode="default"):
    """
    Record whether a round-robin trigger led to useful outcomes.
    Used to refine trigger thresholds over time.
    """
    log = load_performance_log()

    if "trigger_outcomes" not in log:
        log["trigger_outcomes"] = {}

    key = f"{mode}:{trigger_id}"
    if key not in log["trigger_outcomes"]:
        log["trigger_outcomes"][key] = {"useful": 0, "not_useful": 0}

    if was_useful:
        log["trigger_outcomes"][key]["useful"] += 1
    else:
        log["trigger_outcomes"][key]["not_useful"] += 1

    save_performance_log(log)


def get_trigger_effectiveness(mode="default"):
    """Get effectiveness rates for each trigger."""
    log = load_performance_log()
    outcomes = log.get("trigger_outcomes", {})

    effectiveness = {}
    for key, counts in outcomes.items():
        if key.startswith(f"{mode}:"):
            trigger_id = key.split(":", 1)[1]
            total = counts["useful"] + counts["not_useful"]
            if total > 0:
                effectiveness[trigger_id] = {
                    "rate": round(counts["useful"] / total, 2),
                    "samples": total,
                }

    return effectiveness
