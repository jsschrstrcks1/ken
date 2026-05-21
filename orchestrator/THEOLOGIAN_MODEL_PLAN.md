# Theologian Model Library — Plan

Branch: `claude/theological-model-planning-VU2zD`
Primary repo: `Romans` (sermons). Secondary application: `InTheWake` (engineering pattern only — see §6).
Status: planning. No training has begun. Spurgeon corpus scraper is at 5/3,561 sermons.

This plan integrates the multi-LLM-integration handoff (theologian LoRA pool, Open Claw routing, debate mode, Wright-as-challenger) with the protected-memory directives the household already operates under. Where the handoff and memory conflict, memory wins and the wheat/chaff call is named.

## 1. Anchor directives (protected-memory citations)

- **Theology baseline**: 1689 LBCF; ESV-only; substitutionary atonement; credo-baptism; FCF design. Refs: `romans/1aa5a7b7`, `romans/a8e030ac`.
- **Evaluation gate**: thus-says-the-lord 105-pt rubric with Berean Gate + Fatal-Flaw cap. Refs: `romans/32bacde3`, `romans/6debe5a2`.
- **Quote-source hierarchy** (operator's actual usage, not invented): Tier 1 heavy = Spurgeon, Washer; also Sproul, MacArthur, Platt, Anyabwile, Davey, Chandler, Ryle, M'Cheyne, Bunyan. Ref: `romans/71573d22`.
- **Anti-hallucination posture**: "no halucinations, no lies"; named-uncertainty over fabricated confidence; two-source minimum on factual claims. Refs: `ken/39de9e17`, `ken/2085caa2`.
- **Orchestra discipline**: Claude R1 → external models → Claude integration; full-context round-passing; wheat/chaff with justifications; nothing filtered between rounds. Refs: `ken/0508b5e6`, `ken/04c5571e`, `ken/1811ac0e`, `ken/43d5ce6a`.
- **Hardware ceiling**: M4 Max = 36 GB unified; practical local ceiling ~32B dense Q4 at ~20 GB resident; MoE does not save RAM. Refs: `ken/0a14e07b`, `ken/120e0c1b`.
- **Voice separation**: sermon voice ≠ cruise voice; skill content is per-repo. Ref: `shared/e291a2c0`.
- **InTheWake voice posture**: SDG immutable but theology implicit; Scripture as salt in prose with refs in HTML comments; pastoral content red lane (human writes). Refs: `cruising/c6c6b22a`, `cruising/97abc51b`, `cruising/23866c13`, `shared/6b63d32a`.

## 2. What the handoff proposes — wheat and chaff

| Handoff proposal | Verdict | Why |
|---|---|---|
| Llama 8B base (16 GB) + per-theologian LoRA (~300 MB) | **Chaff (size)** — keep the LoRA idea, raise the base. | M4 Max headroom is 32B Q4. 8B leaves ~25 GB on the table and weakens theological reasoning unnecessarily. |
| Per-theologian LoRA adapters, swap in ~2 s | **Wheat.** | Matches the per-repo voice-tuning discipline (`shared/e291a2c0`) and the operator's quote-source tier. |
| Theologian pool: Spurgeon, Piper, Sproul, Calvin, Edwards, Owen, Lloyd-Jones, MacArthur, Platt, Chandler, Davey, Anyabwile, Baucham, Begg, Keller, Carson, Schreiner, Hamilton, Washer, Chapell, Robinson | **Wheat with Tier-1 weighting.** Add Ryle, M'Cheyne, Bunyan from the operator's actual heavy list. | Memory `romans/71573d22` is the source of truth for whose voice gets heaviest use. |
| Greek scholars: Robertson, Wallace, Campbell, Harris, Hays, Mounce | **Wheat — but reframed as exegesis aides, not voices.** | These are consulted for parsing/syntax, not voiced. Train a single "Greek-grammar consult" LoRA or, more honestly, just RAG-index their published works. |
| Biblical-author LoRAs (Paul, John, Peter, David, Isaiah) | **Chaff.** Cut. | Scripture is read, not impersonated. Producing "Paul-style" new prose collides with 1689 LBCF, Berean Gate, and the Fatal-Flaw cap on fabricated claims. |
| Wright as dedicated challenger | **Wheat structurally — caveat doctrinally.** | Role matches Grok's challenger pattern (`ken/2085caa2`). But Wright's NPP deviates from LBCF substitutionary atonement; the integration round must reject NPP-shaped challenges, not merge them. |
| Anti-hallucination via "cite-or-flag, boundary fencing" inside the model | **Chaff as model-property; wheat as architectural property.** | Move citation from "model behavior" to "system invariant": every attributed quote in output must resolve to a retrieved chunk ID from the indexed corpus. The LoRA shapes voice; RAG provides the citation. |
| Open Claw dynamic routing on passage + doctrine + pastoral need | **Wheat.** | Honors `romans/f5f00d5f` (congregation profile) and `romans/91b2b27c` (doctrinal-resisters audience). |
| Debate mode (two theologians argue from their works) | **Wheat.** | Direct match to orchestra full-context round-passing (`ken/04c5571e`). |
| Plan applies to "primarily sermons but also InTheWake" | **Chaff at the voice layer; wheat at the engineering layer.** | See §6 — InTheWake takes the RAG + orchestra + voice-audit pattern, not the theologian voice. |

## 3. Architecture

```
                      ┌────────────────────────────────────┐
                      │  Indexed corpora (RAG)             │
                      │  /Romans/quotes-and-references/    │
                      │   spurgeon/  washer/  sproul/ ...  │
                      └──────────────┬─────────────────────┘
                                     │ retrieved chunks
                                     ▼
   ┌────────────┐   ┌─────────────────────────────┐   ┌────────────┐
   │  Router    │──▶│  Base model (Llama 3.1 14B  │──▶│  Output    │
   │  (passage  │   │  or Qwen 2.5 14B Q4)        │   │  + cite-IDs│
   │  + locus   │   │  + 1–3 theologian LoRAs     │   └────────────┘
   │  + burden) │   │  + (debate mode: 2 LoRAs)   │
   └────────────┘   │  + Wright-as-challenger     │
                   └─────────────────────────────┘
```

**Base model**: Llama 3.1 14B or Qwen 2.5 14B Q4, ~9–10 GB resident. Headroom for two adapters resident + KV cache during debate mode. 8B kept as fallback if 14B latency disappoints in practice.

**Theologian LoRAs (published corpora only)**:
- Tier 1 (heavy use): Spurgeon, Washer, Sproul, MacArthur, Platt, Davey, Chandler, Anyabwile, Begg, Ryle, M'Cheyne, Bunyan.
- Tier 2 (depth): Calvin, Edwards, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, Robinson, Keller.
- Single challenger: Wright. Structural role; integration must reject NPP-shaped challenges.
- **No biblical-author LoRAs.** Scripture is retrieved and exegeted, never impersonated.

**Greek scholars** (Robertson, Wallace, Campbell, Harris, Hays, Mounce): RAG-indexed, not voiced. Consulted as exegesis aides during the orchestra step (§5).

**RAG layer above LoRAs**: every attributed quotation in output must trace to a retrieved chunk ID. Hard-fail flag on any attribution without a backing ID. Cite-or-flag becomes a system invariant, not a model behavior.

**Routing logic**: passage book/genre + doctrinal locus + congregation-burden tag → theologian set.
- Romans 9 → Calvin, Edwards, Schreiner, Sproul + Wright (challenger).
- Psalms → Spurgeon, M'Cheyne, Ryle, Bunyan.
- Pastoral burden (grief, identity, exhausted load-bearers) → Lloyd-Jones, Keller, Anyabwile, Chapell.
- Gospel-call passages → Washer, Platt, Spurgeon (heavy Tier-1).
- Topical-with-anchor (per `romans/d7a7be68`) → topic-led set; passage-led RAG.

**Debate mode**: two LoRAs argue with full-context round-passing (`ken/04c5571e`); Claude integrates with its own wheat/chaff verdict and justification (`ken/0508b5e6`, `ken/1811ac0e`).

## 4. Integration with the existing sermon pipeline

Existing 9-step pipeline (`ken/69213852`): DRAFT → consult_challenge (Grok) → consult_expand (Gemini) → consult_structure (GPT) → consult_verify (Perplexity) → consult_research (You.com) → INTEGRATE (Claude) → EVALUATE (thus-says-the-lord) → VOICE_AUDIT.

Insert a new step **7.5 — theological-corpus consultation** between INTEGRATE and EVALUATE:

1. Router selects 2–3 theologian LoRAs + Wright-challenger based on passage/locus/burden.
2. Each LoRA produces its commentary with RAG-cited quotes.
3. Full-context round-passing: each LoRA sees prior commentary (matches `ken/04c5571e`).
4. Claude integrates with wheat/chaff verdict per LoRA contribution; rejects NPP-shaped challenges from Wright.
5. Output feeds into step 8 (thus-says-the-lord scoring) with all four required diagnostic tests intact (Scopus, Berean Gate, Fallen-Condition-Focus, Gospel-presence).

Step 7.5 is `optional: true` (graceful degradation, matches `ken/69213852`).

## 5. Non-negotiable gates (LoRA output gets no pass)

- **Berean Gate**: if the sermon doesn't open/quote/exegete its named text, Fatal-Flaw cap at 60/105 regardless of LoRA quality (`romans/32bacde3`).
- **LBCF substitutionary atonement** as gospel-call shape (`romans/1aa5a7b7`).
- **ESV-only** for quotation, including conversational paraphrase (`romans/a8e030ac`).
- **Cite-or-flag-or-fail** on every attributed quote: retrieved chunk ID or hard flag.
- **Political-neutrality** rule preserved (`romans/0c10d211`) — LoRA voices that drift political get the integration round's chop.
- **Voice-audit** post-LoRA: the manuscript must still sound like the pastor, not Spurgeon. LoRA enriches argument; voice belongs to the preacher.

## 6. InTheWake — what it actually gets

InTheWake's protected memory is unambiguous: theology is **implicit, salt-not-billboard**, pastoral content is **red lane** (notes only, human writes), Scripture refs live in HTML comments not visible prose. Spurgeon-voiced cruise content would violate the immutable posture.

InTheWake gets the **engineering**, not the **voice**:

- **RAG-grounded citation discipline** applied to cruise sources: CruiseMapper (primary for deployment data per `cruising/2dd627ed`), VesselFinder/MarineTraffic (IMO/AIS per `cruising/9f819c5e`), official deck-plan URLs (`cruising/f621ebcd`). Every price/menu/IMO/itinerary claim resolves to a retrieved-source ID before publish — same architectural invariant, different sources.
- **Orchestra-as-pre-execution-gate** already running in `cruising` mode (`ken/ae168797`); no change.
- **Voice-audit calibrated by voice-dna** against the cruise corpus (already deployed); the theological-model build informs the *technique* but does not transfer the *voice*.
- **Hallucination-elimination preference** (`cruising/4918b2a5`): the cite-or-flag invariant directly addresses the "AI-generated content with specific-sounding details" failure mode already named in memory.

Engineering shared, theology not. The InTheWake LoRAs are zero.

## 7. Risk register

- **Wright leaking NPP into integration**: encode LBCF substitutionary-atonement check as a hard reject in the integration round. Not a soft prompt — a verifier pass.
- **LoRA confabulation under RAG**: default-flag any attributed claim without retrieval ID. Run a sample audit after every LoRA-trained-author release.
- **Training-data gating**: Spurgeon = 5/3,561; Washer/Sproul/MacArthur/etc. = 0 scraped. No Tier-1 LoRA is real until its corpus is real.
- **M4 Max is opportunistic**: m4mini is always-on (`ken/de9c5aa2`); m4max is mobile. Train serially, one author at a time, careful-not-clever per the `one-at-a-time` directive (`ken/4a66badc`). Don't queue eight LoRAs and walk away.
- **Voice-bleed into the pastor's own voice**: voice-audit must run *after* step 7.5 to confirm the manuscript still reads as the preacher, not the LoRA panel.
- **Cost / latency on the full pipeline**: orchestra runs already $0.03–0.08 per pass (`ken/47dd2ce1`). Step 7.5 is local-LLM, so $0 marginal but adds wall-clock. Budget against the cost-management posture (`ken/6bc81f3a`).

## 8. Sequencing (estimates; will drift)

| Week | Work |
|---|---|
| 1–2 | Complete Spurgeon scrape (3,556 remaining). Begin Washer, Sproul, MacArthur, Platt corpus collection. Dedup + quality pass. |
| 3 | RAG layer over indexed corpora at `Romans/quotes-and-references/`. Retrieval-ID format. Cite-or-flag enforcement scaffold. |
| 4 | Base-model decision via 3-pass orchestra design review (`ken/05261df2`): PASS 1 design proposal, PASS 2 stress with Romans 9 + Psalm 23 + a wounded-congregation pastoral text, PASS 3 refine. |
| 5–8 | Tier-1 LoRA training, one author at a time. Order: Spurgeon → Washer → Sproul → MacArthur → Platt → Davey → Chandler → Anyabwile → Begg → Ryle → M'Cheyne → Bunyan. |
| 9 | Pipeline step 7.5 integration. Routing logic. Debate mode wired. |
| 10 | Score against Romans 1a/1b benchmarks (88/105, 91/105 per `romans/50b2c027`). Compare with-LoRA vs. without on the same passage. Hallucination audit. |
| 11 | Wright LoRA + LBCF substitutionary-atonement gate. Adversarial review (`ken/07bb1504`) on Wright outputs. |
| 12 | Voice-audit recalibration. Post-deploy monitoring of cite-or-flag rate. |

## 9. What does NOT get built

- No biblical-author LoRAs.
- No Greek-scholar voice LoRAs (those become RAG-indexed exegesis aides).
- No theologian-voice deployment to InTheWake content.
- No "model decides its own boundary fencing" — the boundary is the retrieval-grounded citation invariant, enforced at the system level.
- No batch parallel LoRA training on m4max — serial, one at a time, per `one-at-a-time`.

## 10. Open dependencies / blockers

- Spurgeon scrape completion. Without it, Tier-1 anchor is hypothetical.
- Washer + Sproul + MacArthur + Platt corpora — need acquisition decision (which sources, with what IP/copyright posture). The Spurgeon corpus is public domain; the moderns are not. **Until copyright posture is clarified, Tier-1 LoRA training cannot proceed.**
- Grok API key refresh (per session handoff — 400 errors). Wright challenger role is harder to validate without Grok available as the structural-role parallel.
- Perplexity adapter for orchestra (per handoff). Step 5 of the existing sermon pipeline degrades gracefully without it.

## 11. Memory encodings to write after operator approval

The handoff names "Theologian Model Library Plan (in protected memory)" but no discrete protected memory captures the plan. After operator approval of this doc, encode:

- The base-model decision (14B Q4) and its hardware-ceiling justification.
- The no-biblical-author-LoRA rule and its LBCF/Berean-Gate grounding.
- The RAG-as-citation-invariant rule.
- The InTheWake engineering-only application.
- The Wright-NPP integration-round reject rule.
- Pipeline step 7.5 insertion into the existing 9-step sermon pipeline.

Each encoded as a protected memory in `romans/` or `shared/` domain with `operator-directive` tag once approved.

---

Soli Deo Gloria.
