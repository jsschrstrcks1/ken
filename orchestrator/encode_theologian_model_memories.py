#!/usr/bin/env python3
"""
Encode the theologian-model plan's durable design calls as protected
cognitive memories in open-claw-stuff/.memory/.

Per the canonical plan §11 (ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md),
these are the operator-approved design calls that should survive across
sessions as protected memories.

Provenance per memory_ops/7c1c1e38: source-tagged with the encode session.
Privacy posture per memory_ops/abb28ed6: open-claw-stuff is PRIVATE GitHub
repo; encoded memories committed there are private. No tokens or sensitive
prose in content.

Run from anywhere with PYTHONPATH including ken/orchestrator/, or invoke as:
  python3 ken/orchestrator/encode_theologian_model_memories.py
"""

import os
import sys

# Make memory_ops importable regardless of cwd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Tag this encode session per 7c1c1e38
os.environ["MEMORY_SESSION_ID"] = "theologian-model-planning-2026-05-21"

import memory_ops

SOURCE = "encoded-from-session:2026-05-21-theologian-model-planning"
SHARED_TAGS = ["operator-directive", "theologian-model"]

# Each memory: (domain, content, [extra_tags], confidence)
MEMORIES = [
    # 1. Scripture governs / 1689 is bumpers
    (
        "romans",
        "Authority order for the theologian-model build (operator verbatim 2026-05-21): "
        "Scripture governs doctrine. The 1689 LBCF is the bumpers — it keeps the ball out "
        "of the gutter, not the ball itself. Every doctrinal claim traces to a text. "
        "The confession is a confessional bumper, not the floor. This framing supersedes "
        "any earlier articulation that put the confession as primary. Refs: canonical plan "
        "ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md §1, §5; existing memory 1aa5a7b7.",
        ["scripture-governs", "1689-lbcf", "authority-order", "operator-verbatim"],
        0.99,
    ),
    # 2. Base model 14B Q4 + cluster deployment
    (
        "ken",
        "Theologian-model base-model decision: Llama 3.1 14B Q4 or Qwen 2.5 14B Q4 on "
        "the household Mac cluster. Cluster-aware deployment per canonical plan §3.2: "
        "m4mini (always-on, OpenClaw host) + m3pro (paired) carry inference; m4max (mobile, "
        "36 GB base-config) carries opportunistic training; m2mini handles batch overflow; "
        "RackNerd VPS is NATS broker + MinIO results-archive, NEVER a model host. "
        "8B is the fallback if 14B latency disappoints. Anchored on M4 Max 36 GB ceiling "
        "(memory 0a14e07b) and 32B Q4 local-LLM ceiling (memory 120e0c1b).",
        ["base-model", "14b-q4", "cluster-deployment", "hardware"],
        0.97,
    ),
    # 3. Full-roster Tier-1 theologian pool
    (
        "romans",
        "Theologian-model voice pool (operator correction 2026-05-21): the FULL handoff "
        "roster stays Tier 1; no demotion. 24 names: Spurgeon, Washer, Sproul, MacArthur, "
        "Platt, Davey, Chandler, Anyabwile, Begg, Ryle, M'Cheyne, Bunyan, Piper, Calvin, "
        "Edwards, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, "
        "Robinson, Keller. Plus Wright as single challenger. Heaviest USAGE concentrates "
        "on Spurgeon + Washer per quote-source hierarchy (71573d22), but no name gets a "
        "Tier-2 ghetto. Operator verbatim: 'the others should be included AND top tier.'",
        ["theologian-pool", "tier-1", "no-demotion", "operator-verbatim"],
        0.99,
    ),
    # 4. Voice-vs-corrector LoRA split (Extension #1)
    (
        "romans",
        "Theologian-model LoRA split (operator extension 2026-05-21 #1): the earlier "
        "'no biblical-author LoRAs' rule was too coarse. Splits into two artifacts: "
        "(a) biblical-author VOICE LoRAs — STILL NO (crosses 1689 LBCF + Berean Gate + "
        "Fatal-Flaw cap; impersonating Scripture). (b) biblical-author CORRECTOR LoRAs — "
        "YES, load-bearing. Three functions: factual correction (dates, geography, "
        "biography), doctrinal correction (claims contradicted by the corpus), and "
        "rhetorical-structural critique (sermon argument that violates the apostle's "
        "actual argument arc — diatribe, chiasm, kal vachomer, corporate-then-individual). "
        "Cheaper to train per LoRA; higher leverage for hallucination prevention.",
        ["lora-split", "biblical-authors", "corrector-loras", "extension-1"],
        0.99,
    ),
    # 5. Theologian-LoRAs-are-primarily-correctors (Extension #2)
    (
        "romans",
        "Theologian-LoRA training objective (operator extension 2026-05-21 #2): "
        "theologian LoRAs train PRIMARILY as corpus-scholars (detect + cite + correct "
        "against indexed corpus), with VOICE as a SECONDARY inference-time mode invoked "
        "on explicit request or by debate mode. Voice fidelity becomes a secondary "
        "evaluation metric, not the training gate. Author-by-mode matrix: biblical "
        "authors = corrective only (voice gateway-blocked); theologians = corrective "
        "primary + voice invokable; topic clusters = corrective only; Wright = corrective "
        "+ voice for challenger role only. Track C (voice-only LoRAs) collapsed into "
        "Track B. Operator framing: voice LoRAs should be 'in part corrector LoRAs too — "
        "maybe mostly.'",
        ["lora-objective", "corrector-primary", "voice-secondary", "extension-2", "operator-verbatim"],
        0.99,
    ),
    # 6. Pre-DRAFT human exegesis gate (orchestra blind-spot fix)
    (
        "romans",
        "Pre-DRAFT human exegesis gate (orchestra blind-spot fix 2026-05-21): the pastor "
        "produces and logs original passage work — Greek/Hebrew, FCF, Scopus, locus, "
        "congregation-burden mapping — BEFORE any LoRA or persona consultation fires. "
        "Step 7.5 is REFRAMED as post-exegesis critique (not generative input): theologian "
        "voices given draft + exegesis log produce wheat/chaff verdicts on pastor's "
        "argument, do NOT propose alternative arguments to be merged. Honors Scripture-"
        "governs ordering at the architecture level, not just rhetoric. Grok's blind-spot "
        "pass identified the original ordering as fatal-flaw class.",
        ["pre-draft-gate", "stage-0", "post-exegesis-critique", "orchestra-blind-spot"],
        0.99,
    ),
    # 7. RAG-as-citation-invariant rule
    (
        "shared",
        "Anti-hallucination architecture (theologian-model): cite-or-flag-or-fail is a "
        "SYSTEM INVARIANT, not a model behavior. Every attributed quotation in output "
        "must resolve to a retrieved chunk ID from the indexed corpus. Tool-call retrieval "
        "+ post-validator + cryptographic hash are layered enforcement. Models will be "
        "TRAINED to produce named-uncertainty when retrieval is empty, not fabricated "
        "confidence. This is non-negotiable and is the single most important architectural "
        "constraint on the entire build (operator: '100% super important').",
        ["anti-hallucination", "cite-or-flag", "system-invariant"],
        0.99,
    ),
    # 8. Substring-match post-validator + cryptographic chunk-hash
    (
        "ken",
        "Citation-enforcement implementation (theologian-model, research-grounded): "
        "tool_choice='required' is best-effort, NOT guaranteed (Promptfoo + Cao arXiv "
        "2412.04141 reliability-capability tradeoff). Wallat SIGIR 2025 (arXiv 2412.18004) "
        "documents 57% of RAG citations are unfaithful — model post-rationalizes citation "
        "from parametric knowledge. ACTUAL enforcement: (a) substring-match post-validator "
        "— every attributed quote string must be verbatim substring of retrieved chunk; "
        "(b) cryptographic SHA-256 chunk-hash verified on every emit. Tool gate is strong "
        "default, not the gate.",
        ["citation-enforcement", "substring-match", "chunk-hash", "research-grounded"],
        0.97,
    ),
    # 9. Two-path architecture
    (
        "ken",
        "Theologian-model two-path architecture (operator confirmation 2026-05-21): "
        "open-weight LoRA on 14B Q4 (cluster) + closed-weight persona on Claude/GPT/Grok/"
        "Gemini APIs. Both paths share the same indexed corpus, same cite-or-flag "
        "invariant, same gates. Path selection: open-weight when local LoRA exists and "
        "request fits 14B reasoning; closed-weight when LoRA missing or frontier-class "
        "reasoning needed. Debate mode mixes freely. Closed-weight ships fast (no "
        "training delay); LoRAs come online one at a time as Track B progresses. Each "
        "landing LoRA gets head-to-head voice-audit vs. its persona counterpart.",
        ["two-path", "open-weight", "closed-weight", "architecture"],
        0.97,
    ),
    # 10. retrieve_from_corpus tool gate
    (
        "ken",
        "retrieve_from_corpus tool spec (theologian-model closed-weight path): mandatory "
        "tool-call before any attributed quote on Claude/GPT/Grok/Gemini personas. Tool "
        "returns {author, chunk_id, text, citation_metadata, sha256}. Persona cannot emit "
        "an attributed quote without first calling the tool and including the returned "
        "chunk ID. Post-validator scans output for substring-match + hash equality. Tool "
        "is best-effort enforcement (per Cao 2412.04141); post-validator is the actual "
        "gate. Needs design before Track A week 4.",
        ["retrieve-from-corpus", "tool-spec", "closed-weight-path"],
        0.97,
    ),
    # 11. Claude-not-integrating-and-persona-in-same-run
    (
        "ken",
        "Theologian-model orchestra discipline: Claude does NOT wear a theologian persona "
        "in the same pipeline run that Claude is integrating. Conflict-of-interest in "
        "the wheat/chaff judgment. If Claude is called as a theologian voice at Stage 9, "
        "a different model carries integration for that run. Matches existing operator "
        "directive 0508b5e6 (Claude is participant with opinions, not neutral summarizer) "
        "extended with explicit role-separation rule.",
        ["orchestra-role-separation", "integration", "persona-conflict"],
        0.96,
    ),
    # 12. AlignGuard-LoRA + contrastive negative-corpus
    (
        "ken",
        "Theologian-model LoRA training discipline (research-grounded): every author LoRA "
        "uses AlignGuard-LoRA (Fisher Information Matrix regularization, arXiv 2508.02079) "
        "for documented drift reduction up to 50%. Mitigates catastrophic forgetting "
        "(arXiv 2402.15415, 2402.18865). Plus contrastive negative-corpus per author: "
        "when training Spurgeon, penalize MacArthur-distinctive / Owen-distinctive / "
        "Keller-distinctive terminology so LoRAs stay separable rather than merging into "
        "'Reformed-sounding soup.' OPLoRA orthogonal-projection (2510.13003) as fallback. "
        "Primary evaluation: corrective accuracy. Secondary: voice-fidelity via authorial-"
        "perplexity ALM (PMC12225838) + GRPO+sentence-transformer (arXiv 2512.05747).",
        ["lora-training", "alignguard", "contrastive-corpus", "research-grounded"],
        0.96,
    ),
    # 13. llama.cpp commitment
    (
        "ken",
        "Theologian-model runtime commitment: llama.cpp is the ONLY Apple Silicon multi-"
        "LoRA serving path that supports 24+ hot-swappable adapters (PR #7667, GGUF LoRA "
        "support). Ollama hot-swap NOT implemented (issues #5788, #9548 as of 2026-05); "
        "MLX multi-LoRA is alpha-only (MOLA); no Apple Silicon port of S-LoRA / Punica "
        "exists. Throughput baseline on M-series Q4_K_M: 38-58 tok/s. Commit explicitly; "
        "do not assume Ollama will catch up before the build needs it.",
        ["llama-cpp", "runtime", "apple-silicon", "lora-serving"],
        0.96,
    ),
    # 14. Debate-mode constraints
    (
        "ken",
        "Theologian-model debate-mode constraints (research-grounded): cap at 3 rounds "
        "(Du arXiv 2305.14325 + 2311.17371 sweet-spot; cost grows quadratically beyond). "
        "Persona re-anchoring each turn (Li arXiv 2402.10962: ~30%+ persona-drift past "
        "8-12 turns; split-softmax mitigation). Heterogeneity over homogeneity (literature "
        "settled: diversity helps; arXiv 2502.08788, 2509.05396, 2511.07784). Abstain-on-"
        "tie: if integration round can't produce wheat/chaff verdict with justification, "
        "abstain and surface disagreement to Integrity Log.",
        ["debate-mode", "three-rounds", "persona-anchoring", "heterogeneity"],
        0.96,
    ),
    # 15. InTheWake engineering-only
    (
        "cruising",
        "Theologian-model InTheWake application: ENGINEERING-ONLY, not voice. ITW takes "
        "the RAG-grounded citation invariant (applied to CruiseMapper / VesselFinder / "
        "official deck plans, two-source minimum per existing 4918b2a5), the orchestra "
        "gate (existing cruising mode ae168797), and voice-audit calibrated by voice-dna. "
        "Does NOT take theologian-voice generation (violates salt-not-billboard c6c6b22a, "
        "theology-implicit 6b63d32a, red-lane pastoral 23866c13, scripture-as-comment-side "
        "97abc51b). Spurgeon-voiced cruise content is forbidden.",
        ["inthewake", "engineering-only", "no-theologian-voice"],
        0.99,
    ),
    # 16. Wright-NPP integration-round reject
    (
        "romans",
        "Theologian-model Wright-challenger rule: Wright serves the structural challenger "
        "role (matches Grok-as-challenger pattern 2085caa2). Integration round runs a "
        "substitutionary-atonement VERIFIER PASS on every Wright-tagged contribution — "
        "rejects NPP-shaped framings that compromise the 1689 LBCF substitutionary-"
        "atonement bumper. Verifier is a CODED PASS, not a soft prompt. Applies on both "
        "open-weight (Wright LoRA) and closed-weight (Wright persona) paths. Higher risk "
        "on closed-weight because frontier models have more Wright training data.",
        ["wright", "npp-reject", "substitutionary-atonement", "challenger-role"],
        0.97,
    ),
    # 17. Pipeline restructure (12 stages, 3 new insertion points)
    (
        "romans",
        "Theologian-model sermon pipeline (12 stages, 3 new insertion points): Stage 0 "
        "pre-DRAFT human exegesis (hard gate with logged override; refuses on empty/stub "
        "log). Stage 1 DRAFT. Stage 2 post-DRAFT corrector pass (author-tagged content). "
        "Stages 3-7 existing orchestra consultation (Grok challenge → Gemini expand → "
        "GPT structure → Perplexity verify → You.com research). Stage 8 INTEGRATE. "
        "Stage 9 (formerly step 7.5) post-exegesis theologian critique — NON-GENERATIVE; "
        "≤3 rounds; persona re-anchored each turn. Stage 10 post-7.5 corrector pass. "
        "Stage 11 EVALUATE (thus-says-the-lord 105-pt rubric, all four diagnostic tests). "
        "Stage 12 VOICE_AUDIT + mandatory disclosure footer. Replaces the prior 9-step "
        "pipeline (memory 69213852).",
        ["pipeline", "12-stages", "stage-0", "stage-2", "stage-10"],
        0.97,
    ),
    # 18. NATS-on-m4mini for sermon traffic
    (
        "ken",
        "Theologian-model NATS routing: sermon-pipeline + theologian-model traffic stays "
        "on m4mini NATS (local-first, inside tailnet) for privacy. RackNerd VPS keeps "
        "NATS for non-sermon household traffic (family-history, photography ingest, "
        "cross-repo sync). Honors operator's one-user-trust posture (7c4c90e3) — sermon "
        "drafts, congregation-burden tags, pastoral concerns are sensitive content that "
        "doesn't leave the household tailnet on the open-weight path. rpi5 holds the "
        "NATS replica for failover. Closed-weight path inherits orchestra adapter "
        "privacy posture (external APIs).",
        ["nats", "m4mini", "cluster-topology", "sermon-privacy"],
        0.96,
    ),
    # 19. Disclosure footer (Decision 1 → D + A combined)
    (
        "romans",
        "Theologian-model disclosure posture (Decision 1 → D + A combined, operator "
        "2026-05-21): visible disclosure footer on every final sermon manuscript "
        "(canonical template at Romans/.claude/disclosure-footer.md, appended at Stage 12) "
        "PLUS one-time congregation-meeting / pastoral-letter methodology disclosure "
        "(draft template at Romans/.claude/methodology-disclosure-letter.md). REJECTED "
        "options: pure concealment (E — off-pattern with honesty discipline), top-of-"
        "manuscript header (B — hijacks sermon opening). Optional pulpit reference (C) "
        "is pastoral judgment, not architecturally required. Honors FTC AI-disclosure "
        "posture + Anthropic ToS sensitive-domain requirement.",
        ["disclosure-footer", "decision-1", "methodology-letter", "operator-decision"],
        0.99,
    ),
    # 20. Soft hard gate with logged override (Decision 2 → B)
    (
        "romans",
        "Theologian-model Stage 0 gate enforcement (Decision 2 → B, operator 2026-05-21): "
        "SOFT HARD GATE with logged override. Default refusal on empty/stub exegesis log "
        "(Stages 1+ technically refuse). Documented --override-exegesis-gate \"<reason>\" "
        "flag with MANDATORY one-line reason logged in Integrity Log + sermon-map "
        "⚠️ EXEGESIS-OVERRIDE flag. After N=3 un-backfilled overrides, system surfaces "
        "reminder at session start until backfill or operator dismisses. Override is for "
        "GENUINE emergencies (ER trip, family crisis, death) — not for last-minute prep. "
        "Conspicuous in audit log, never silent. Honors careful-not-clever discipline + "
        "action-over-deliberation 5855c0a4 simultaneously.",
        ["stage-0-enforcement", "decision-2", "soft-hard-gate", "override-mechanism", "operator-decision"],
        0.99,
    ),
]


def main():
    print(f"MEMORY_ROOT: {memory_ops.MEMORY_ROOT}")
    print(f"MEMORY_SESSION_ID: {os.environ.get('MEMORY_SESSION_ID')}")
    print(f"Encoding {len(MEMORIES)} protected memories...\n")

    encoded = []
    for i, (domain, content, extra_tags, confidence) in enumerate(MEMORIES, 1):
        tags = SHARED_TAGS + extra_tags
        try:
            result = memory_ops.encode(
                content=content,
                domain=domain,
                source=SOURCE,
                confidence=confidence,
                tags=tags,
                protected=True,
            )
            mem_id = result.get("id") if isinstance(result, dict) else result
            encoded.append((domain, mem_id, extra_tags[0] if extra_tags else "?"))
            print(f"  {i:2d}. [{domain:8s}] {mem_id}  c={confidence}  {extra_tags[0] if extra_tags else '?'}")
        except Exception as e:
            print(f"  {i:2d}. FAIL [{domain}] — {e}")

    print(f"\nEncoded {len(encoded)} of {len(MEMORIES)}.")
    by_domain = {}
    for d, mid, tag in encoded:
        by_domain.setdefault(d, 0)
        by_domain[d] += 1
    for d in sorted(by_domain):
        print(f"  {d}: {by_domain[d]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
