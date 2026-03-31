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


def call_model(model_name, prompt, role="freestyle"):
    if model_name not in ADAPTERS:
        return None, None, []
    adapter = ADAPTERS[model_name]
    from consult import ROLES
    system_prompt = ROLES.get(role, ROLES["freestyle"])
    try:
        result = adapter.query(prompt=prompt, system=system_prompt)
        return result["response"], result["usage"], result.get("citations", [])
    except Exception as e:
        print(f"  → {model_name} failed: {e}", file=sys.stderr)
        return None, {"model": model_name, "tokens_in": 0, "tokens_out": 0, "estimated_cost_usd": 0}, []


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


def run_staged_orchestra(mode_name, task):
    mode_config = load_mode(mode_name)
    orchestra_config = mode_config.get("orchestra", {})

    # Separate research and analytical models from fan_out config
    fan_out = orchestra_config.get("fan_out", [
        {"model": "gpt", "role": "structure"},
        {"model": "gemini", "role": "expand"},
        {"model": "perplexity", "role": "research"},
        {"model": "youdotcom", "role": "research"},
        {"model": "grok", "role": "challenge"},
    ])

    research_models = [m for m in fan_out if m.get("role") in ("research", "expand")]
    analytical_models = [m for m in fan_out if m.get("role") in ("structure", "challenge")]
    blind_spot_model = orchestra_config.get("blind_spot_model", "grok")

    state = {
        "mode": mode_name,
        "task": task,
        "architecture": "staged",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stages": [],
        "cost_log": [],
        "total_cost_usd": 0.0,
        "status": "running",
    }

    def track_cost(usage):
        if usage:
            cost = usage.get("estimated_cost_usd", 0) or 0
            state["cost_log"].append(usage)
            state["total_cost_usd"] += cost
            return cost
        return 0

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

    stage1 = {
        "stage": 1, "name": "claude_lead",
        "prompt_for_claude": claude_r1_prompt,
        "response": claude_r1,
    }
    state["stages"].append(stage1)
    claude_r1_text = json.dumps(claude_r1, indent=2)
    print(f"  → Claude R1 recorded", file=sys.stderr)

    # ── Stage 2: Research Models ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 2: RESEARCH — {len(research_models)} models verify and expand", file=sys.stderr)

    research_responses = []
    for config in research_models:
        model = config["model"]
        role = config.get("role", "research")
        role_desc = config.get("description", "Search for evidence, cite sources, verify claims.")

        print(f"\n  {model.upper()} ({role})", file=sys.stderr)
        prompt = RESEARCH_MODEL_PROMPT.format(
            model_name=model.upper(), task=task,
            claude_analysis=claude_r1_text, role_description=role_desc,
        )
        response, usage, citations = call_model(model, prompt, role)
        entry = {"model": model, "role": role, "response": response, "usage": usage, "citations": citations}
        research_responses.append(entry)

        cost = track_cost(usage)
        print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
        if response:
            findings = response.get("findings", []) if isinstance(response, dict) else []
            verdicts = response.get("verdicts", []) if isinstance(response, dict) else []
            print(f"  → {len(findings)} findings, {len(verdicts)} verdicts", file=sys.stderr)
            if citations:
                print(f"  → {len(citations)} citations", file=sys.stderr)
        else:
            print(f"  → Failed (continuing)", file=sys.stderr)

    state["stages"].append({
        "stage": 2, "name": "research",
        "models": [r["model"] for r in research_responses],
        "responses": research_responses,
    })

    # ── Stage 3: Claude Synthesizes Research ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 3: CLAUDE — Synthesize research, prepare for analysts", file=sys.stderr)

    research_reports_text = format_reports(research_responses)
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
        "prompt_for_claude": claude_s2_prompt,
        "response": claude_synthesis,
    })
    claude_synthesis_text = json.dumps(claude_synthesis, indent=2, default=str)
    print(f"  → Claude synthesis prompt generated", file=sys.stderr)

    # ── Stage 4: Analytical Models ──
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"STAGE 4: ANALYTICAL — {len(analytical_models)} models evaluate", file=sys.stderr)

    analytical_responses = []
    for config in analytical_models:
        model = config["model"]
        role = config.get("role", "structure")
        role_desc = config.get("description", "Evaluate reasoning, challenge assumptions.")

        print(f"\n  {model.upper()} ({role})", file=sys.stderr)
        prompt = ANALYTICAL_MODEL_PROMPT.format(
            model_name=model.upper(), task=task,
            claude_synthesis=claude_synthesis_text,
            research_reports=research_reports_text,
            role_description=role_desc,
        )
        response, usage, citations = call_model(model, prompt, role)
        entry = {"model": model, "role": role, "response": response, "usage": usage, "citations": citations}
        analytical_responses.append(entry)

        cost = track_cost(usage)
        print(f"  → Cost: ${cost:.4f}", file=sys.stderr)
        if response:
            verdicts = response.get("verdicts", []) if isinstance(response, dict) else []
            risk = response.get("biggest_risk", "?") if isinstance(response, dict) else "?"
            print(f"  → {len(verdicts)} verdicts, biggest risk: {str(risk)[:100]}", file=sys.stderr)
        else:
            print(f"  → Failed (continuing)", file=sys.stderr)

    state["stages"].append({
        "stage": 4, "name": "analytical",
        "models": [r["model"] for r in analytical_responses],
        "responses": analytical_responses,
    })

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

    mode_name = sys.argv[1].lower()
    task = " ".join(sys.argv[2:])

    print(f"Research Orchestra: {mode_name} mode (staged)", file=sys.stderr)
    print(f"Task: {task}", file=sys.stderr)

    state = run_staged_orchestra(mode_name, task)
    print_report(state)


if __name__ == "__main__":
    main()
