"""
iteration.py — Shared iteration, recursion, and response validation for orchestra pipelines.

Three retry triggers:
  1. FORMAT MISMATCH — model returned unexpected/malformed response
  2. EVIDENCE GAP   — Claude or analyst flags a testable gap
  3. NEW THREAD     — finding opens a sub-investigation

Termination conditions:
  - Max 2 research iterations per run
  - Max 1 recursion depth (sub-orchestras don't spawn sub-sub-orchestras)
  - Cost ceiling ($0.50 default) — hard stop
  - Convergence check — if retry returns same results, stop
  - Format retries: max 2 per model per call
"""

import json
import hashlib


# ─────────────────────────────────────────────
# Response Format Validation
# ─────────────────────────────────────────────

# Expected keys per response type
EXPECTED_SCHEMAS = {
    "research": {
        "required": [],  # At least one of these groups must be present
        "any_of": [["verdicts"], ["findings"], ["rescued_ideas"]],
        "description": "Research model response (verdicts, findings, rescued_ideas)",
    },
    "analytical": {
        "required": [],
        "any_of": [["verdicts"], ["assessments"], ["biggest_risk"], ["evaluation"]],
        "description": "Analytical model response (verdicts, assessments, biggest_risk)",
    },
    "fan_out": {
        "required": [],
        "any_of": [["verdicts"], ["proposals"], ["low_hanging_fruit"]],
        "description": "Fan-out model response (verdicts, proposals, low_hanging_fruit)",
    },
    "deliberation_gpt": {
        "required": [],
        "any_of": [["evaluation"], ["challenges"], ["for_claude"], ["structural_improvements"]],
        "description": "GPT deliberation response",
    },
    "synthesis": {
        "required": [],
        "any_of": [["attributed_plan"], ["revised_proposals"], ["verdicts"], ["final_verdicts"]],
        "description": "Synthesis response (attributed_plan, verdicts)",
    },
}


def validate_response(response, schema_name):
    """
    Validate a model response against expected schema.

    Returns:
        (is_valid: bool, issues: list[str])
    """
    if response is None:
        return False, ["Response is None (model failed)"]

    if isinstance(response, str):
        return False, ["Response is raw string, not parsed JSON"]

    if not isinstance(response, dict):
        return False, [f"Response is {type(response).__name__}, expected dict"]

    # Check for raw_text wrapper (adapter couldn't parse JSON)
    if "raw_text" in response and len(response) == 1:
        return False, ["Response is unparsed raw_text — model didn't return valid JSON"]

    schema = EXPECTED_SCHEMAS.get(schema_name)
    if not schema:
        return True, []  # No schema to check against

    issues = []

    # Check required keys
    for key in schema.get("required", []):
        if key not in response:
            issues.append(f"Missing required key: {key}")

    # Check any_of groups — at least one group must have all keys present
    any_of = schema.get("any_of", [])
    if any_of:
        found_any = False
        for group in any_of:
            if any(k in response for k in group):
                found_any = True
                break
        if not found_any:
            expected = " OR ".join([str(g) for g in any_of])
            issues.append(f"None of the expected key groups found. Expected at least one of: {expected}")

    return len(issues) == 0, issues


def build_format_retry_prompt(original_prompt, response, issues, schema_name):
    """Build a retry prompt that tells the model what went wrong with its response format."""
    schema = EXPECTED_SCHEMAS.get(schema_name, {})
    desc = schema.get("description", schema_name)

    resp_preview = str(response)[:500] if response else "None"

    return f"""{original_prompt}

IMPORTANT — YOUR PREVIOUS RESPONSE HAD FORMAT ISSUES:
{chr(10).join(f'  - {issue}' for issue in issues)}

Your response was: {resp_preview}

PLEASE RETRY with valid JSON containing the expected structure: {desc}
Remember: Respond in JSON with the keys described in the instructions above."""


# ─────────────────────────────────────────────
# Iteration Control
# ─────────────────────────────────────────────

class IterationController:
    """Manages iteration budgets, cost ceilings, and convergence detection."""

    def __init__(self, max_research_iterations=2, max_recursion_depth=1,
                 cost_ceiling=0.50, max_format_retries=2):
        self.max_research_iterations = max_research_iterations
        self.max_recursion_depth = max_recursion_depth
        self.cost_ceiling = cost_ceiling
        self.max_format_retries = max_format_retries

        self.research_iterations = 0
        self.recursion_depth = 0
        self.total_cost = 0.0
        self.format_retries = {}  # model_name -> count
        self._response_hashes = []  # For convergence detection

    def can_iterate_research(self):
        """Can we do another research iteration?"""
        return (self.research_iterations < self.max_research_iterations
                and self.total_cost < self.cost_ceiling)

    def can_recurse(self):
        """Can we spawn a sub-orchestra?"""
        return (self.recursion_depth < self.max_recursion_depth
                and self.total_cost < self.cost_ceiling)

    def can_format_retry(self, model_name):
        """Can we retry this model for format issues?"""
        retries = self.format_retries.get(model_name, 0)
        return retries < self.max_format_retries

    def record_research_iteration(self):
        self.research_iterations += 1

    def record_recursion(self):
        self.recursion_depth += 1

    def record_format_retry(self, model_name):
        self.format_retries[model_name] = self.format_retries.get(model_name, 0) + 1

    def record_cost(self, cost):
        self.total_cost += cost

    def is_over_budget(self):
        return self.total_cost >= self.cost_ceiling

    def check_convergence(self, responses):
        """
        Check if research responses are substantially the same as last iteration.
        Uses content hashing to detect when retrying isn't producing new information.
        """
        # Hash the response content
        content = json.dumps(responses, sort_keys=True, default=str)
        h = hashlib.md5(content.encode()).hexdigest()

        if h in self._response_hashes:
            return True  # Converged — same results as before

        self._response_hashes.append(h)
        return False

    def status(self):
        return {
            "research_iterations": self.research_iterations,
            "max_research_iterations": self.max_research_iterations,
            "recursion_depth": self.recursion_depth,
            "max_recursion_depth": self.max_recursion_depth,
            "total_cost": round(self.total_cost, 4),
            "cost_ceiling": self.cost_ceiling,
            "format_retries": dict(self.format_retries),
            "over_budget": self.is_over_budget(),
        }


# ─────────────────────────────────────────────
# Gap Detection
# ─────────────────────────────────────────────

def extract_gaps(response):
    """
    Extract testable gaps from a model response.
    Returns list of gap descriptions that could trigger research iteration.
    """
    if not response or not isinstance(response, dict):
        return []

    gaps = []

    # Look for explicit gap fields
    for key in ("gaps_for_analysts", "gaps_identified", "remaining_uncertainties",
                "evidence_gaps", "unverifiable_claims"):
        items = response.get(key, [])
        if isinstance(items, list):
            gaps.extend([str(item) for item in items])
        elif isinstance(items, str) and items:
            gaps.append(items)

    # Look for UNVERIFIABLE verdicts
    for verdict in response.get("verdicts", []):
        if isinstance(verdict, dict):
            v = str(verdict.get("VERDICT", verdict.get("verdict", ""))).upper()
            if v in ("UNVERIFIABLE", "CONTRADICTED", "WEAK"):
                justification = verdict.get("JUSTIFICATION", verdict.get("justification", ""))
                if justification:
                    gaps.append(f"[{v}] {justification}")

    # Look for biggest_risk
    risk = response.get("biggest_risk", "")
    if risk and isinstance(risk, str) and len(risk) > 20:
        gaps.append(f"[RISK] {risk}")

    return gaps


def extract_new_threads(response):
    """
    Extract new research threads that warrant sub-investigation.
    Returns list of thread descriptions.
    """
    if not response or not isinstance(response, dict):
        return []

    threads = []

    # Look for explicit thread/follow-up fields
    for key in ("new_threads", "sub_investigations", "follow_up_research",
                "suggested_next_steps", "spawn_investigation"):
        items = response.get(key, [])
        if isinstance(items, list):
            threads.extend([str(item) for item in items])

    # Look for findings with HIGH confidence that open new directions
    for finding in response.get("findings", []):
        if isinstance(finding, dict):
            relevance = str(finding.get("RELEVANCE", finding.get("relevance", "")))
            if "new" in relevance.lower() or "branch" in relevance.lower() or "sub-" in relevance.lower():
                threads.append(str(finding.get("FINDING", finding.get("finding", ""))))

    return threads


def build_refined_query(original_task, gaps, iteration_num):
    """Build a refined research query targeting specific gaps."""
    gap_list = "\n".join(f"  {i+1}. {g}" for i, g in enumerate(gaps[:5]))

    return f"""REFINED RESEARCH QUERY (Iteration {iteration_num}):

Original task: {original_task}

Previous research left these SPECIFIC GAPS that need evidence:
{gap_list}

Focus ONLY on these gaps. Do not repeat previously found information.
For each gap, either:
  - FIND evidence (with source URL/citation)
  - CONFIRM it's unfindable (explain why and suggest alternative approaches)

Respond in JSON with "verdicts" array and "findings" array."""
