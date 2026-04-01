#!/usr/bin/env python3
"""
research_orchestra.py — Staged multi-LLM consultation for research-heavy tasks.

Unlike orchestra.py (fan-out), this uses a staged pipeline where
fact-finding precedes judgment:

  Stage 1: Claude sends substantive analysis to RESEARCH models
           (Perplexity, You.com, Gemini). They verify, innovate,
           cite sources, and report back.

  Stage 2: Claude reviews research feedback, forms assessment,
           justifies conclusions, rescues declined plans, then
           sends synthesis to ANALYTICAL models (GPT, Grok).

  Stage 3: GPT and Grok evaluate Claude's research-informed
           synthesis (seeing BOTH raw research + Claude's take),
           challenge, rescue, report back.

  Stage 4: Claude produces final synthesis.

Why staged: Genealogy and research tasks need evidence before
argument. Web-grounded models search independently, then
analytical models evaluate with full evidence in hand.

Usage:
    python3 research_orchestra.py <mode> "task description"
"""

import json
import os
import sys
import time
import yaml

from iteration import (
    IterationController, validate_response, build_format_retry_prompt,
    extract_gaps, extract_new_threads, build_refined_query,
)
from smart_routing import (
    detect_triggers, route_models, assess_task_complexity,
    record_model_performance, weighted_synthesis, get_model_weights,
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

CLAUDE_R1_PROMPT = """You are CLAUDE — the lead researcher with full project context and memory. You are initiating a staged research consultation.

TASK: {task}

CONTEXT FROM MEMORY:
{memory_context}

YOUR ROLE: Provide a thorough, substantive analysis that research models will verify and expand. You know the project, the sources, and the gaps. Be specific about:

1. What is already known and documented
2. What specific claims need verification
3. What gaps exist in the evidence
4. What archives, databases, or sources should be searched
5. Concrete research questions for the web-grounded models

For each proposal:
- PROPOSAL: [specific research direction]
- CONFIDENCE: HIGH | MEDIUM | LOW
- JUSTIFICATION: [why, referencing project knowledge]
- VERIFICATION_NEEDED: [what the research models should check]

Also identify LOW-HANGING FRUIT — easiest wins.

Research models (Perplexity, You.com, Gemini) will independently verify your claims, search for evidence, and report back with citations. Make your analysis specific enough that they know exactly what to look for."""

RESEARCH_MODEL_PROMPT = """You are {model_name}, a web-grounded research model. CLAUDE (the lead researcher with project context) has provided an analysis below. Your job is to:

1. VERIFY Claude's claims — search for supporting or contradicting evidence
2. FORM YOUR OWN OPINIONS — where Claude is wrong or incomplete, say so
3. INNOVATE — suggest research avenues Claude didn't consider
4. RESCUE — if Claude declined any direction, evaluate whether it deserves another look
5. CITE EVERYTHING — every claim needs a source URL or record identifier

TASK: {task}

CLAUDE'S ANALYSIS:
{claude_analysis}

YOUR ROLE ({role_description}):
For each of Claude's proposals, provide a verdict with evidence:
- PROPOSAL_ID: [reference]
- VERDICT: VERIFIED | CONTRADICTED | PARTIALLY_VERIFIED | UNVERIFIABLE
- EVIDENCE: [what you found, with sources]
- JUSTIFICATION: [your reasoning]

Then add YOUR OWN findings — things Claude didn't know or got wrong:
- FINDING: [what you discovered]
- SOURCE: [URL or record identifier]
- CONFIDENCE: HIGH | MEDIUM | LOW
- RELEVANCE: [how this connects to the task]

Respond in JSON with "verdicts" array, "findings" array, and "rescued_ideas" array."""

CLAUDE_STAGE2_PROMPT = """You are CLAUDE reviewing research feedback. Three research models independently verified your analysis and searched for evidence. Now synthesize their findings.

TASK: {task}

YOUR ORIGINAL ANALYSIS:
{claude_analysis}

RESEARCH MODEL REPORTS:
{research_reports}

YOUR ROLE (Stage 2 — Research Synthesis):
1. Assess each research model's findings — what's reliable, what's speculative
2. Revise your original proposals based on new evidence
3. Resolve contradictions between models (cite which evidence is stronger)
4. Rescue any of your declined ideas that research models supported
5. Identify remaining gaps that analytical models should scrutinize
6. Produce an evidence-grounded synthesis for GPT and Grok to evaluate

Respond in JSON with:
- "evidence_assessment": evaluation of each model's findings
- "revised_proposals": your updated proposals with evidence
- "contradictions_resolved": where models disagreed and your ruling
- "rescued_ideas": ideas you're bringing back based on evidence
- "gaps_for_analysts": specific questions for GPT and Grok
- "for_analysts": your synthesis for analytical models to evaluate"""

ANALYTICAL_MODEL_PROMPT = """You are {model_name}, an analytical model. Claude has synthesized findings from three research models (Perplexity, You.com, Gemini). You have access to BOTH the raw research AND Claude's synthesis.

TASK: {task}

CLAUDE'S SYNTHESIS (informed by research):
{claude_synthesis}

RAW RESEARCH REPORTS (so you can independently verify Claude's interpretation):
{research_reports}

YOUR ROLE ({role_description}):
1. Evaluate Claude's synthesis — did Claude correctly interpret the research?
2. Challenge weak reasoning or unsupported conclusions
3. Rescue any research findings Claude dismissed or downweighted
4. Check for logical consistency, temporal plausibility, source reliability
5. Identify the biggest remaining risk in the plan

For each of Claude's revised proposals:
- PROPOSAL_ID: [reference]
- VERDICT: SOUND | WEAK | NEEDS_REVISION | RESCUED
- JUSTIFICATION: [specific reasoning, referencing the evidence]
- SUGGESTED_FIX: [if WEAK or NEEDS_REVISION]

Then add your own assessments:
- ASSESSMENT: [your evaluation]
- CONFIDENCE: HIGH | MEDIUM | LOW
- BIGGEST_RISK: [single most important concern]

Respond in JSON with "verdicts" array, "assessments" array, "rescued" array, and "biggest_risk" string."""

ROUND_ROBIN_PROMPT = """You are {model_name} in a CROSS-EXAMINATION round. You've already given your independent response. Now you can see what the OTHER models said. Challenge their findings, verify their citations, rescue ideas you agree with, and revise your own position if warranted.

TASK: {task}

YOUR ORIGINAL RESPONSE:
{own_response}

OTHER MODELS' RESPONSES (summaries):
{other_summaries}

TRIGGERS THAT ACTIVATED THIS ROUND:
{trigger_reasons}

YOUR ROLE: Focus on the trigger reasons above. Specifically:
1. CHALLENGE — Point out errors, unsupported claims, or weak citations from other models
2. VERIFY — Confirm or contradict specific claims with your own evidence
3. RESCUE — Bring back good ideas that others dismissed
4. REVISE — Update your own position based on what you've learned

Respond in JSON with:
- "challenges": array of {{model, claim, challenge, evidence}}
- "verifications": array of {{model, claim, status: CONFIRMED|CONTRADICTED|UNCERTAIN, evidence}}
- "rescued": array of {{model, idea, justification}}
- "revised_position": your updated findings/proposals
- "confidence": 0.0-1.0"""

CLAUDE_FINAL_PROMPT = """You are CLAUDE producing the FINAL SYNTHESIS. You've been through the full staged pipeline:
- Stage 1: Your initial analysis
- Stage 2: Research models verified and expanded
- Stage 3: You synthesized the research
- Stage 4: Analytical models (GPT, Grok) evaluated your synthesis

TASK: {task}

YOUR STAGE 2 SYNTHESIS:
{claude_synthesis}

ANALYTICAL MODEL EVALUATIONS:
{analytical_reports}

YOUR ROLE (Final Synthesis):
1. Accept or rebut each analytical challenge — justify your position
2. Incorporate valid critiques into the final plan
3. Rescue anything the analysts dismissed that the research supports
4. Produce the ATTRIBUTED PLAN — credit which model/source each step came from
5. List concrete, prioritized next steps

Respond in JSON with:
- "final_verdicts": your response to each analytical challenge
- "attributed_plan": steps with source attribution
- "prioritized_next_steps": ordered by impact and feasibility
- "confidence": overall confidence in the plan (0.0-1.0)
- "remaining_uncertainties": what we still don't know"""


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
    """Call a model with optional format validation and retry."""
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

            # Accumulate usage across retries
            if total_usage is None:
                total_usage = usage
            elif usage:
                for k in ("tokens_in", "tokens_out", "input_tokens", "output_tokens"):
                    if k in usage and k in total_usage:
                        total_usage[k] = total_usage.get(k, 0) + usage.get(k, 0)
                total_usage["estimated_cost_usd"] = total_usage.get("estimated_cost_usd", 0) + usage.get("estimated_cost_usd", 0)

            # Validate response format if schema provided
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

    # Exhausted retries — return last response anyway
    return response, total_usage, citations


def format_reports(entries, max_per_entry=4000):
    parts = []
    for entry in entries:
        model = entry["model"].upper()
        resp = entry["response"]
        citations = entry.get("citations", [])
        if resp is None:
            parts.append(f"\n--- {model} --- FAILED ---\n")
            continue
        resp_text = json.dumps(resp, indent=2, default=str)
        if len(resp_text) > max_per_entry:
            resp_text = resp_text[:max_per_entry] + "\n... (truncated)"
        section = f"\n--- {model} ---\n{resp_text}"
        if citations:
            section += f"\nCitations: {', '.join(citations[:15])}"
        parts.append(section)
    return "\n".join(parts)


def run_staged_orchestra(mode_name, task, deep=False, parent_controller=None):
    mode_config = load_mode(mode_name)
    orchestra_config = mode_config.get("orchestra", {})

    fan_out = orchestra_config.get("fan_out", [
        {"model": "gpt", "role": "structure"},
        {"model": "gemini", "role": "expand"},
        {"model": "perplexity", "role": "research"},
        {"model": "youdotcom", "role": "research"},
        {"model": "grok", "role": "challenge"},
    ])

    research_models = [m for m in fan_out if m.get("role") in ("research", "expand")]
    analytical_models = [m for m in fan_out if m.get("role") in ("structure", "challenge")]

    # Initialize iteration controller
    if parent_controller:
        controller = parent_controller
        controller.record_recursion()
    else:
        controller = IterationController(
            max_research_iterations=2 if deep else 0,
            max_recursion_depth=1 if deep else 0,
            cost_ceiling=0.50,
            max_format_retries=2,
        )

    state = {
        "mode": mode_name,
        "task": task,
        "architecture": "staged",
        "deep": deep,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stages": [],
        "iterations": [],
        "sub_orchestras": [],
        "cost_log": [],
        "total_cost_usd": 0.0,
        "iteration_control": controller.status(),
        "status": "running",
    }

    def track_cost(usage):
        if usage:
            cost = usage.get("estimated_cost_usd", 0) or 0
            state["cost_log"].append(usage)
            state["total_cost_usd"] += cost
            controller.record_cost(cost)
            return cost
        return 0

    def run_research_stage(research_query, iteration_num=0):
        """Run research models (reusable for iterations)."""
        responses = []
        for config in research_models:
            model = config["model"]
            role = config.get("role", "research")
            role_desc = config.get("description", "Search for evidence, cite sources, verify claims.")

            if controller.is_over_budget():
                print(f"  → COST CEILING reached (${controller.total_cost:.2f}), skipping {model}", file=sys.stderr)
                break

            print(f"\n  {model.upper()} ({role})", file=sys.stderr)
            prompt = RESEARCH_MODEL_PROMPT.format(
                model_name=model.upper(), task=task,
                claude_analysis=research_query, role_description=role_desc,
            )
            response, usage, citations = call_model(model, prompt, role,
                                                     schema_name="research", controller=controller)
            entry = {"model": model, "role": role, "response": response,
                     "usage": usage, "citations": citations, "iteration": iteration_num}
            responses.append(entry)

            cost = track_cost(usage)
            print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
            if response and isinstance(response, dict):
                findings = len(response.get("findings", []))
                verdicts = len(response.get("verdicts", []))
                print(f"  → {findings} findings, {verdicts} verdicts", file=sys.stderr)
                if citations:
                    print(f"  → {len(citations)} citations", file=sys.stderr)
            else:
                print(f"  → Failed or invalid format (continuing)", file=sys.stderr)

        return responses

    # ── Stage 1: Claude R1 ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 1: CLAUDE — Lead analysis", file=sys.stderr)

    memory_context = recall_memories(mode_name)
    claude_r1_prompt = CLAUDE_R1_PROMPT.format(task=task, memory_context=memory_context)

    claude_r1 = {
        "proposals": [{
            "id": "claude_1",
            "proposal": f"Claude's substantive lead analysis of: {task}",
            "confidence": "HIGH",
            "justification": "Claude has full project context. In interactive mode, Claude Code fills this with detailed analysis.",
        }],
        "low_hanging_fruit": [],
        "note": "Claude Code fills this locally. The prompt above guides the analysis."
    }

    state["stages"].append({
        "stage": 1, "name": "claude_lead",
        "prompt_for_claude": claude_r1_prompt, "response": claude_r1,
    })
    claude_r1_text = json.dumps(claude_r1, indent=2)
    print(f"  → Claude R1 recorded", file=sys.stderr)

    # ── Intelligent Routing ──
    complexity = assess_task_complexity(task)
    research_models = route_models(task, research_models, mode=mode_name)
    analytical_models = route_models(task, analytical_models, mode=mode_name)

    state["routing"] = {
        "complexity": complexity,
        "research_models_selected": [m["model"] for m in research_models],
        "analytical_models_selected": [m["model"] for m in analytical_models],
    }
    print(f"  → Task complexity: {complexity} — routing {len(research_models)}R + {len(analytical_models)}A models", file=sys.stderr)

    # ── Stage 2: Research Models (with iteration) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 2: RESEARCH — {len(research_models)} models{' (deep mode: iteration enabled)' if deep else ''}", file=sys.stderr)

    all_research_responses = []
    research_responses = run_research_stage(claude_r1_text, iteration_num=0)
    all_research_responses.extend(research_responses)

    state["stages"].append({
        "stage": 2, "name": "research", "iteration": 0,
        "models": [r["model"] for r in research_responses],
        "responses": research_responses,
    })

    # ── Research Iteration Loop (deep mode only) ──
    if deep:
        for iteration in range(1, controller.max_research_iterations + 1):
            # Extract gaps from ALL research responses so far
            all_gaps = []
            for entry in all_research_responses:
                if entry.get("response"):
                    all_gaps.extend(extract_gaps(entry["response"]))

            # Check convergence
            if controller.check_convergence([r.get("response") for r in research_responses]):
                print(f"\n  ⟳ CONVERGED — research iteration {iteration} would repeat. Stopping.", file=sys.stderr)
                break

            if not all_gaps:
                print(f"\n  ⟳ No testable gaps found. Skipping iteration {iteration}.", file=sys.stderr)
                break

            if not controller.can_iterate_research():
                print(f"\n  ⟳ Iteration budget exhausted or cost ceiling reached.", file=sys.stderr)
                break

            controller.record_research_iteration()
            print(f"\n{'─'*60}", file=sys.stderr)
            print(f"STAGE 2.{iteration}: RESEARCH ITERATION — {len(all_gaps)} gaps to investigate", file=sys.stderr)
            for g in all_gaps[:3]:
                print(f"  → Gap: {str(g)[:100]}", file=sys.stderr)

            refined_query = build_refined_query(task, all_gaps, iteration)
            research_responses = run_research_stage(refined_query, iteration_num=iteration)
            all_research_responses.extend(research_responses)

            state["iterations"].append({
                "iteration": iteration, "gaps_targeted": all_gaps[:5],
                "responses": research_responses,
            })

    # ── Conditional Round-Robin (between research and synthesis) ──
    trigger_result = detect_triggers(all_research_responses, mode=mode_name)
    state["trigger_detection"] = trigger_result

    if trigger_result["should_trigger"] and not controller.is_over_budget():
        print(f"\n{'─'*60}", file=sys.stderr)
        print(f"ROUND-ROBIN TRIGGERED — {len(trigger_result['triggers_fired'])} conditions met", file=sys.stderr)
        for t in trigger_result["triggers_fired"]:
            print(f"  → [{t['id']}] {t['reason']}", file=sys.stderr)

        trigger_reasons = "\n".join(f"- [{t['id']}] {t['reason']}" for t in trigger_result["triggers_fired"])
        round_robin_responses = []

        for entry in all_research_responses:
            model = entry["model"]
            if entry["response"] is None:
                continue

            if controller.is_over_budget():
                print(f"  → Cost ceiling reached, stopping round-robin", file=sys.stderr)
                break

            # Build summaries of OTHER models' responses (not full text — sparse topology)
            other_summaries = []
            for other in all_research_responses:
                if other["model"] != model and other["response"]:
                    summary = json.dumps(other["response"], default=str)[:1500]
                    other_summaries.append(f"--- {other['model'].upper()} ---\n{summary}")

            print(f"\n  Round-robin: {model.upper()}", file=sys.stderr)
            rr_prompt = ROUND_ROBIN_PROMPT.format(
                model_name=model.upper(),
                task=task,
                own_response=json.dumps(entry["response"], indent=2, default=str)[:2000],
                other_summaries="\n".join(other_summaries),
                trigger_reasons=trigger_reasons,
            )

            rr_response, rr_usage, rr_citations = call_model(
                model, rr_prompt, entry.get("role", "research"),
                controller=controller)

            rr_entry = {
                "model": model, "phase": "round_robin",
                "response": rr_response, "usage": rr_usage, "citations": rr_citations,
            }
            round_robin_responses.append(rr_entry)

            cost = track_cost(rr_usage)
            print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
            if rr_response and isinstance(rr_response, dict):
                challenges = len(rr_response.get("challenges", []))
                verifications = len(rr_response.get("verifications", []))
                print(f"  → {challenges} challenges, {verifications} verifications", file=sys.stderr)

            # Record performance
            record_model_performance(
                model, mode_name,
                success=rr_response is not None,
                cost=cost,
                response_valid=rr_response is not None and isinstance(rr_response, dict),
            )

        state["round_robin"] = {
            "triggered": True,
            "triggers": trigger_result["triggers_fired"],
            "responses": round_robin_responses,
        }

        # Append round-robin findings to research pool for synthesis
        all_research_responses.extend(round_robin_responses)
    else:
        reason = "no triggers fired" if not trigger_result["should_trigger"] else "cost ceiling"
        print(f"\n  Round-robin: NOT triggered ({reason})", file=sys.stderr)
        state["round_robin"] = {"triggered": False, "reason": reason}

    # ── Stage 3: Claude Synthesizes Research ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 3: CLAUDE — Synthesize research, prepare for analysts", file=sys.stderr)

    research_reports_text = format_reports(all_research_responses)
    claude_s2_prompt = CLAUDE_STAGE2_PROMPT.format(
        task=task, claude_analysis=claude_r1_text,
        research_reports=research_reports_text,
    )

    claude_synthesis = {
        "note": "Claude Code performs synthesis locally with full project context.",
        "prompt": claude_s2_prompt,
    }
    state["stages"].append({
        "stage": 3, "name": "claude_synthesis",
        "prompt_for_claude": claude_s2_prompt, "response": claude_synthesis,
    })
    claude_synthesis_text = json.dumps(claude_synthesis, indent=2, default=str)
    print(f"  → Claude synthesis prompt generated", file=sys.stderr)

    # ── Check for new threads → spawn sub-orchestra (deep mode only) ──
    if deep and controller.can_recurse():
        all_threads = []
        for entry in all_research_responses:
            if entry.get("response"):
                all_threads.extend(extract_new_threads(entry["response"]))

        if all_threads:
            print(f"\n{'─'*60}", file=sys.stderr)
            print(f"SUB-ORCHESTRA — {len(all_threads)} new threads discovered", file=sys.stderr)
            # Spawn ONE sub-orchestra for the highest-priority thread
            thread = all_threads[0]
            print(f"  → Investigating: {str(thread)[:200]}", file=sys.stderr)

            sub_state = run_staged_orchestra(
                mode_name, f"Sub-investigation: {thread}",
                deep=False,  # Sub-orchestras don't go deep
                parent_controller=controller,
            )
            state["sub_orchestras"].append({
                "thread": thread,
                "state": sub_state,
            })

    # ── Stage 4: Analytical Models (with format validation) ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 4: ANALYTICAL — {len(analytical_models)} models evaluate", file=sys.stderr)

    analytical_responses = []
    for config in analytical_models:
        model = config["model"]
        role = config.get("role", "structure")
        role_desc = config.get("description", "Evaluate reasoning, challenge assumptions.")

        if controller.is_over_budget():
            print(f"  → COST CEILING reached, skipping {model}", file=sys.stderr)
            break

        print(f"\n  {model.upper()} ({role})", file=sys.stderr)
        prompt = ANALYTICAL_MODEL_PROMPT.format(
            model_name=model.upper(), task=task,
            claude_synthesis=claude_synthesis_text,
            research_reports=research_reports_text,
            role_description=role_desc,
        )
        response, usage, citations = call_model(model, prompt, role,
                                                 schema_name="analytical", controller=controller)
        entry = {"model": model, "role": role, "response": response, "usage": usage, "citations": citations}
        analytical_responses.append(entry)

        cost = track_cost(usage)
        print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
        if response and isinstance(response, dict):
            verdicts = len(response.get("verdicts", []))
            risk = response.get("biggest_risk", "?")
            print(f"  → {verdicts} verdicts, biggest risk: {str(risk)[:100]}", file=sys.stderr)
        else:
            print(f"  → Failed (continuing)", file=sys.stderr)

    state["stages"].append({
        "stage": 4, "name": "analytical",
        "models": [r["model"] for r in analytical_responses],
        "responses": analytical_responses,
    })

    # ── Analyst-triggered research iteration (deep mode) ──
    if deep and controller.can_iterate_research():
        analyst_gaps = []
        for entry in analytical_responses:
            if entry.get("response"):
                analyst_gaps.extend(extract_gaps(entry["response"]))

        if analyst_gaps:
            controller.record_research_iteration()
            print(f"\n{'─'*60}", file=sys.stderr)
            print(f"STAGE 4→2: ANALYST-TRIGGERED RESEARCH — {len(analyst_gaps)} gaps", file=sys.stderr)

            refined_query = build_refined_query(task, analyst_gaps, controller.research_iterations)
            extra_research = run_research_stage(refined_query, iteration_num=controller.research_iterations)
            all_research_responses.extend(extra_research)

            state["iterations"].append({
                "iteration": controller.research_iterations,
                "triggered_by": "analysts",
                "gaps_targeted": analyst_gaps[:5],
                "responses": extra_research,
            })

            # Update research reports for final synthesis
            research_reports_text = format_reports(all_research_responses)

    # ── Stage 5: Claude Final Synthesis ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 5: CLAUDE — Final synthesis", file=sys.stderr)

    analytical_reports_text = format_reports(analytical_responses)
    claude_final_prompt = CLAUDE_FINAL_PROMPT.format(
        task=task, claude_synthesis=claude_synthesis_text,
        analytical_reports=analytical_reports_text,
    )
    state["stages"].append({
        "stage": 5, "name": "claude_final",
        "prompt_for_claude": claude_final_prompt,
        "response": {"note": "Claude Code performs final synthesis locally.", "prompt": claude_final_prompt},
    })
    print(f"  → Final synthesis prompt generated", file=sys.stderr)

    # ── Finalize ──
    state["iteration_control"] = controller.status()
    state["status"] = "completed"
    state["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    os.makedirs(STATE_DIR, exist_ok=True)
    state_path = os.path.join(STATE_DIR, "research_orchestra.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)

    return state


def print_report(state):
    print(f"\n{'═'*60}")
    print(f"RESEARCH ORCHESTRA COMPLETE: {state['mode']} mode")
    print(f"{'═'*60}")
    print(f"Task: {state['task'][:200]}")
    print(f"Status: {state['status']}")
    print(f"Total cost: ${state['total_cost_usd']:.4f}")

    for stage in state.get("stages", []):
        name = stage.get("name", "?")
        stage_num = stage.get("stage", "?")

        if name in ("claude_lead", "claude_synthesis", "claude_final"):
            print(f"\n── Stage {stage_num}: {name} (local) ──")
            continue

        responses = stage.get("responses", [])
        print(f"\n── Stage {stage_num}: {name} ({len(responses)} models) ──")
        for entry in responses:
            model = entry["model"]
            usage = entry.get("usage") or {}
            cost = usage.get("estimated_cost_usd", 0) or 0
            citations = entry.get("citations", [])
            resp = entry.get("response")

            if resp and isinstance(resp, dict):
                findings = len(resp.get("findings", []))
                verdicts = len(resp.get("verdicts", []))
                assessments = len(resp.get("assessments", []))
                items = f"{findings}F/{verdicts}V/{assessments}A"
            elif resp:
                items = "response"
            else:
                items = "FAILED"

            cite_str = f" +{len(citations)}cit" if citations else ""
            print(f"  {model:12s} | ${cost:.4f} | {items}{cite_str}")

    # Total citations
    all_citations = []
    for stage in state.get("stages", []):
        for entry in stage.get("responses", []):
            all_citations.extend(entry.get("citations", []))

    if all_citations:
        print(f"\n── Citations ({len(all_citations)} total) ──")
        for url in all_citations[:20]:
            print(f"  {url}")
        if len(all_citations) > 20:
            print(f"  ... and {len(all_citations) - 20} more")

    print(f"\n── Final Cost: ${state['total_cost_usd']:.4f} ──")
    print(f"\nFull state: state/research_orchestra.json")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # Parse --deep flag
    args = sys.argv[1:]
    deep = "--deep" in args
    if deep:
        args.remove("--deep")

    mode_name = args[0].lower()
    task = " ".join(args[1:])

    depth_label = "staged+deep" if deep else "staged"
    print(f"Research Orchestra: {mode_name} mode ({depth_label})", file=sys.stderr)
    print(f"Task: {task}", file=sys.stderr)
    if deep:
        print(f"  Deep mode: iteration (max 2), recursion (max depth 1), cost ceiling $0.50", file=sys.stderr)

    state = run_staged_orchestra(mode_name, task, deep=deep)
    print_report(state)


if __name__ == "__main__":
    main()
