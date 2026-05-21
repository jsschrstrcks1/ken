# Theologian Model Library — Plan

Branch: `claude/theological-model-planning-VU2zD`
Primary repo: `Romans` (sermons). Secondary application: `InTheWake` (engineering pattern only — see §6).
Status: planning. No training has begun. Spurgeon corpus scraper is at 5/3,561 sermons.

This plan integrates the multi-LLM-integration handoff (theologian LoRA pool, Open Claw routing, debate mode, Wright-as-challenger) with the protected-memory directives the household already operates under. Where the handoff and memory conflict, memory wins and the wheat/chaff call is named.

## 1. Anchor directives (protected-memory citations)

- **Authority order**: **Scripture governs doctrine.** The 1689 LBCF is the bumpers on the bowling lane — it keeps the ball out of the gutter, but it is not the ball, and it is not the lane. ESV-only for English quotation, including conversational paraphrase. Substitutionary atonement foregrounded; credo-baptism; Calvinistic soteriology within a Baptist covenant frame; FCF design. Refs: `romans/1aa5a7b7`, `romans/a8e030ac`. *Operator framing (2026-05-21): "First of all, the Bible governs doctrine. The 1689 is like bumpers in bowling."*
- **Evaluation gate**: thus-says-the-lord 105-pt rubric with Berean Gate + Fatal-Flaw cap. Berean Gate checks whether the sermon actually opens, quotes, and exegetes its named text — failure here is fatal before the rest of the rubric applies. Refs: `romans/32bacde3`, `romans/6debe5a2`.
- **Anti-hallucination posture (load-bearing)**: "no halucinations, no lies. id rather you be honest and ahve some integrity." Named-uncertainty over fabricated confidence; two-source minimum on factual claims; if it can't be verified, mark UNSURE rather than publish. This is **non-negotiable** and is the single most important architectural constraint on the entire build. Refs: `ken/39de9e17`, `ken/2085caa2`, `cruising/4918b2a5`. See §3.1 for how this becomes a system invariant.
- **Quote-source pool** (operator's actual usage — the handoff's full roster, all kept as Tier 1; the operator's correction 2026-05-21 was "the others should be included AND top tier"): Spurgeon, Washer, Sproul, MacArthur, Platt, Davey, Chandler, Anyabwile, Begg, Ryle, M'Cheyne, Bunyan, Piper, Calvin, Edwards, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, Robinson, Keller. Heaviest use within Tier 1 still concentrates on Spurgeon + Washer per `romans/71573d22`, but no member of the roster gets demoted.
- **Orchestra discipline**: Claude R1 → external models → Claude integration; full-context round-passing; wheat/chaff with justifications; nothing filtered between rounds. Refs: `ken/0508b5e6`, `ken/04c5571e`, `ken/1811ac0e`, `ken/43d5ce6a`.
- **Hardware**: the operator's cluster, not a single node. m4mini (Mac mini M4, always-on, OpenClaw host) is the steady inference target. m3pro (MacBook Pro M3 Pro, home LAN, code-specialized inference + Whisper) is the second always-available LLM node. m4max (MacBook Pro M4 Max, mobile, 36 GB) is the opportunistic heavy-compute / training node. m2mini (Mac mini M2, remote) is batch-overflow. RackNerd VPS is coordinator/NATS/MinIO — never a model host. Three Pis handle ingest + scheduled jobs + hot spare. Refs: `ken/de9c5aa2`, `ken/f98289ea`, `ken/0a14e07b`, `ken/120e0c1b`. See §3.2 for how training and inference map onto this cluster.
- **Voice separation**: sermon voice ≠ cruise voice; skill content is per-repo. Ref: `shared/e291a2c0`.
- **InTheWake voice posture**: SDG immutable but theology implicit; Scripture as salt in prose with refs in HTML comments; pastoral content red lane (human writes). Refs: `cruising/c6c6b22a`, `cruising/97abc51b`, `cruising/23866c13`, `shared/6b63d32a`.

## 2. What the handoff proposes — wheat and chaff

| Handoff proposal | Verdict | Why |
|---|---|---|
| Llama 8B base (16 GB) + per-theologian LoRA (~300 MB) | **Chaff (size)** — keep the LoRA idea, raise the base. | The decision isn't bound to one node. m4max headroom alone is 32B Q4; with the cluster (m4mini steady, m3pro paired, m4max opportunistic) the real ceiling is bigger than 36 GB. Inference target is 14B base on the always-on nodes; m4max trains the LoRAs opportunistically. 8B leaves theology-reasoning capacity on the table. |
| Per-theologian LoRA adapters, swap in ~2 s | **Wheat.** | Matches the per-repo voice-tuning discipline (`shared/e291a2c0`) and the operator's quote-source roster. Adapter swap is what makes the cluster-distributed routing fast — the NATS-coordinated request lands on the node holding the right adapter, or any node can hot-load it. |
| Theologian pool: Spurgeon, Piper, Sproul, Calvin, Edwards, Owen, Lloyd-Jones, MacArthur, Platt, Chandler, Davey, Anyabwile, Baucham, Begg, Keller, Carson, Schreiner, Hamilton, Washer, Chapell, Robinson | **Wheat — keep all of them at Tier 1.** Add Ryle, M'Cheyne, Bunyan from the operator's heavy-use list. | Per operator correction 2026-05-21: the handoff's roster stays top-tier; do not demote. Heaviest *usage* still concentrates on Spurgeon + Washer per `romans/71573d22`, but no name gets a Tier-2 ghetto. |
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
                                     │ retrieved chunks (with chunk-IDs)
                                     ▼
   ┌────────────┐   ┌─────────────────────────────┐   ┌────────────────────┐
   │  Router    │──▶│  Base model (14B Q4)        │──▶│  Output + cite-IDs │
   │  (passage  │   │  + 1–3 theologian LoRAs     │   │  Cite-or-flag-or-  │
   │  + locus   │   │  + (debate mode: 2 LoRAs)   │   │  fail invariant    │
   │  + burden) │   │  + Wright-as-challenger     │   │  (see §3.1)        │
   └────────────┘   │  Distributed on cluster     │   └────────────────────┘
                    │  via NATS (see §3.2)        │
                    └─────────────────────────────┘
```

### 3.1 Anti-hallucination as system invariant (load-bearing)

The operator's anti-hallucination directive is non-negotiable. The plan refuses to lean on "the model will be careful." Instead:

- **Cite-or-flag-or-fail**. Every attributed quotation in output must resolve to a retrieved chunk ID from the indexed corpus. No retrieval ID, no quote — the system flags or refuses, the model never invents.
- **Named-uncertainty in prose** is allowed and preferred over fabricated confidence: "I'm not sure where I first heard this — whoever said it…" (`ken/14bea502`, `ken/39de9e17`). The LoRA-augmented model is *trained* to produce this disposition when retrieval is empty.
- **Two-source minimum** on factual claims that aren't direct quotation (dates, numbers, historical events).
- **Cross-check against the source-of-truth files**: ESV verses against the canonical ESV index; Spurgeon attributions against `quotes-and-references/spurgeon/`; modern attributions against their respective corpus directories.
- **Hallucination audit** runs as a post-step on every generated sermon section: scan attributed claims, verify each has a chunk-ID, surface any without to the Integrity Log per `romans/eac4d8bd`.

This is not a feature. It is the architecture. If the cite-or-flag invariant fails, the whole build fails its purpose.

### 3.2 Cluster-aware deployment (not single-node)

The operator's cluster is documented at `ken/de9c5aa2` + `ken/f98289ea`. Mapping work onto nodes:

- **m4mini** (Mac mini M4, always-on, OpenClaw host): **primary inference node** for production sermon-pipeline requests. Hosts the base model + frequently-used LoRAs. NATS subscriber for sermon-pipeline tool requests.
- **m3pro** (MBP M3 Pro, home LAN, code-specialized): **secondary inference node** + Whisper. Pairs with m4mini for parallel debate-mode (each node holds one LoRA, full-context round-passing rides NATS between them).
- **m4max** (MBP M4 Max, mobile, 36 GB — **base-config M4 Max**, not the 48 GB upgrade; confirmed operator 2026-05-21): **opportunistic training node**. Trains LoRAs serially (per `ken/4a66badc` one-at-a-time). When mobile, it falls off the tailnet and training pauses; when home, it resumes. m4max also handles SDXL — keep training scheduled around photography work.
- **m2mini** (Mac mini M2, remote network): **batch overflow** + NATS replica. Picks up sermon-pipeline jobs that queue up when m4mini is busy.
- **RackNerd VPS**: NATS broker + MinIO results-archive. **Not a model host.**
- **rpi5/4a/4b**: NATS replica, scheduled-job runner, photo ingest. No LLM role.

This means base-model size is not bound to any single node's RAM. Inference target is **14B Q4** on m4mini and m3pro (each well under their unified-memory budgets); m4max could in principle run larger (up to 32B Q4 per `ken/120e0c1b`) but the always-on inference path stays portable across nodes by anchoring on 14B.

Adapter swap (~2 s claimed in the handoff) is exactly what makes this cluster-distributed routing work: the right adapter is hot-loaded onto whichever node serves the request, or, more efficiently, the router targets the node that already has it resident.

**Bearer-token auth on every OpenClaw endpoint (`ken/f1f9ab67`)** is preserved. Tailscale gates devices; bearer auth gates processes.

### 3.3 Models, roster, gates

**Base model**: Llama 3.1 14B or Qwen 2.5 14B Q4 on m4mini + m3pro, ~9–10 GB resident. 8B kept as fallback if 14B inference latency disappoints in practice on either node.

**Theologian LoRAs — all Tier 1, published corpora only**:
- Spurgeon, Washer, Sproul, MacArthur, Platt, Davey, Chandler, Anyabwile, Begg, Ryle, M'Cheyne, Bunyan, Piper, Calvin, Edwards, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, Robinson, Keller (24 total).
- Heaviest usage routing concentrates on Spurgeon + Washer per `romans/71573d22`. No demotion of the rest.
- Single challenger: **Wright**. Structural role; integration must reject NPP-shaped challenges.
- **No biblical-author LoRAs.** Scripture is retrieved and exegeted, never impersonated.

**Greek scholars** (Robertson, Wallace, Campbell, Harris, Hays, Mounce): RAG-indexed, not voiced. Consulted as exegesis aides during step 7.5.

**Routing logic**: passage book/genre + doctrinal locus + congregation-burden tag → theologian set.
- Romans 9 / hard sovereignty texts → Calvin, Edwards, Schreiner, Sproul, Piper + Wright (challenger).
- Psalms / lament / praise → Spurgeon, M'Cheyne, Ryle, Bunyan.
- Pastoral burden (grief, identity, exhausted load-bearers) → Lloyd-Jones, Keller, Anyabwile, Chapell, Robinson.
- Gospel-call passages → Washer, Platt, Spurgeon, Baucham.
- NT exposition + epistles → Carson, Schreiner, Hamilton, Lloyd-Jones, MacArthur.
- OT narrative / covenant → Hamilton, Schreiner, Calvin, Owen.
- Reformed-resister teaching contexts (per `romans/91b2b27c`) → MacArthur, Sproul, Begg, Ryle (clear-bridge teachers).
- Topical-with-anchor (per `romans/d7a7be68`) → topic-led set; passage-led RAG.

**Debate mode**: two voices argue with full-context round-passing (`ken/04c5571e`); Claude integrates with its own wheat/chaff verdict and justification (`ken/0508b5e6`, `ken/1811ac0e`). Voices can be any mix of local-LoRA or closed-weight-persona (see §3.4).

### 3.4 Cross-model theologian adapters (open-weight + closed-weight paths)

Operator confirmation 2026-05-21: theologian adapters span multiple base models, including frontier APIs (Claude, GPT, Grok, Gemini, Perplexity, You.com).

LoRAs are weight-bound to their base; you can't attach a Llama-14B LoRA to Claude. So the theologian pool runs as **two parallel paths sharing the same corpus and the same cite-or-flag invariant**:

| Path | Voice mechanism | Base model | Voice fidelity | Reasoning depth | Cost | Latency |
|---|---|---|---|---|---|---|
| **Open-weight** | LoRA adapter (~300 MB) on 14B Q4 | Llama 3.1 14B or Qwen 2.5 14B on m4mini/m3pro/m4max | High (trained on author corpus) | 14B-class | $0 marginal (local) | Local-LLM latency |
| **Closed-weight** | Retrieval-grounded **persona system prompt** | Claude / GPT / Grok / Gemini / Perplexity / You.com via orchestra adapters | Lower (prompted, not trained) | Frontier-class | API cost per call (`ken/47dd2ce1`) | API latency |

**Shared invariants across both paths:**
- Same indexed corpus at `Romans/quotes-and-references/<author>/`.
- Same cite-or-flag-or-fail rule (§3.1). On the closed-weight path, this is enforced via mandatory tool-call to a `retrieve_from_corpus(author, query)` tool — the model cannot emit an attributed quote without first calling the tool and receiving a chunk ID.
- Same Scripture-governs / Berean-Gate / substitutionary-atonement / ESV-only gates (§5).
- Same routing logic by passage + locus + burden (§3.3).
- Same voice-audit after step 7.5 — output must still sound like the pastor.

**Path selection (router logic):**
- If the local LoRA exists and the request fits a reasoning-budget the 14B can handle → open-weight path.
- If the local LoRA doesn't exist yet, or the passage demands frontier-class reasoning (Romans 9 hard sovereignty, long-range epistolary argument) → closed-weight persona on the strongest available frontier model.
- For debate mode, mix freely: two LoRAs, two personas, or one of each. The router picks based on which voices are available and the cost budget.

**Closed-weight persona structure** (per theologian, anchored on the indexed corpus):
- Author background, sermon era, doctrinal commitments, characteristic moves (Spurgeon's plain Saxon + Puritan density; Washer's appeal-and-warn; Sproul's clarity-of-distinction).
- Vocabulary and rhythm patterns drawn from corpus analysis (voice-dna style measurement).
- Explicit interdiction: "Do not invent quotations. Do not invent dates, sermon titles, or pastoral anecdotes attributed to this author. If you would say 'as X once said,' you must call `retrieve_from_corpus` first."
- Substitutionary-atonement bumper baked into the persona for Wright specifically; integration round still runs the verifier pass.

**Special role of Claude in the orchestra**: Claude remains the **integrator** (`ken/0508b5e6`) — proposing in R1, synthesizing at the end. Claude does **not** wear a theologian persona in the same run that it's integrating; that's a conflict-of-interest in the wheat/chaff judgment. If Claude is called as a theologian voice in step 7.5, a different model carries the integration role for that pipeline run.

**Phasing benefit**: the closed-weight path is **available now** — no training delay. The 24 personas can be drafted and shipped before any LoRA is trained. LoRAs come online one at a time on m4max; each landing LoRA gets head-to-head voice-audit comparison against its closed-weight persona counterpart on a benchmark passage, and the winning voice per author becomes the default for that name.

## 4. Integration with the existing sermon pipeline

Existing 9-step pipeline (`ken/69213852`): DRAFT → consult_challenge (Grok) → consult_expand (Gemini) → consult_structure (GPT) → consult_verify (Perplexity) → consult_research (You.com) → INTEGRATE (Claude) → EVALUATE (thus-says-the-lord) → VOICE_AUDIT.

Insert a new step **7.5 — theological-corpus consultation** between INTEGRATE and EVALUATE:

1. Router selects 2–3 theologian voices + Wright-challenger based on passage/locus/burden. Each voice is served by **either** its local LoRA (if trained) **or** its closed-weight persona on a frontier API (§3.4).
2. Each voice produces commentary with RAG-cited quotes. Closed-weight path enforces citation via mandatory `retrieve_from_corpus` tool-call; open-weight path enforces it via the cite-or-flag invariant post-validator.
3. Full-context round-passing: each voice sees prior commentary (matches `ken/04c5571e`). On the cluster, open-weight voices exchange via NATS; closed-weight voices pass context through the orchestra adapter chain.
4. Claude integrates with wheat/chaff verdict per voice contribution; rejects NPP-shaped challenges from Wright via the substitutionary-atonement verifier pass. Claude does not also wear a theologian persona in this same run.
5. Output feeds into step 8 (thus-says-the-lord scoring) with all four required diagnostic tests intact (Scopus, Berean Gate, Fallen-Condition-Focus, Gospel-presence).

Step 7.5 is `optional: true` (graceful degradation, matches `ken/69213852`). On the closed-weight path, step 7.5 inherits the orchestra's existing cost-management posture (`ken/6bc81f3a`).

## 5. Non-negotiable gates (LoRA output gets no pass)

- **Scripture governs**: the Bible is the authority. Every doctrinal claim traces to a text. The 1689 LBCF is the bumpers — out of the gutter, not the ball.
- **Berean Gate**: if the sermon doesn't open/quote/exegete its named text, Fatal-Flaw cap at 60/105 regardless of LoRA quality (`romans/32bacde3`).
- **Substitutionary atonement** as gospel-call shape — confessional bumper (`romans/1aa5a7b7`).
- **ESV-only** for quotation, including conversational paraphrase (`romans/a8e030ac`).
- **Cite-or-flag-or-fail** on every attributed quote: retrieved chunk ID or hard flag. See §3.1.
- **No fabricated quotes, ever.** Named-uncertainty in prose is the disposition when retrieval is empty.
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

- **Frontier-model quote fabrication (HIGH RISK)**: Claude / GPT / Grok / Gemini all have Spurgeon, Calvin, Edwards, Piper, etc. in their training data. A persona-prompted "Spurgeon" can confidently emit a plausible-sounding Spurgeon quote that does not exist. Mitigation is **mandatory tool-call retrieval**: the closed-weight persona cannot emit an attributed quote without first calling `retrieve_from_corpus(author, query)` and including the returned chunk ID. Post-validator scans output for any attributed quote without a chunk ID and flags or rejects. This is the single biggest failure mode of the cross-model approach; the cite-or-flag invariant is what holds against it.
- **Wright NPP-leak from frontier training data**: same problem at the doctrinal level. Frontier models have Wright in training; a Wright persona will tend to import NPP. The substitutionary-atonement bumper runs as a verifier pass on every Wright-tagged contribution at integration — not a soft prompt.
- **LoRA confabulation under RAG**: open-weight path; default-flag any attributed claim without retrieval ID. Sample audit after every LoRA release.
- **Training-data gating**: Spurgeon = 5/3,561; Washer/Sproul/MacArthur/etc. = 0 scraped. No LoRA is real until its corpus is real. Closed-weight personas can ship sooner but only if the indexed corpus exists for retrieval to anchor against.
- **Cost escalation on the full pipeline**: orchestra runs are $0.03–0.08 per pass today (`ken/47dd2ce1`). Adding 2–3 theologian-persona calls per step-7.5 run multiplies that. Cost-reporting per round (`ken/47dd2ce1`) must include theologian-voice cost as a separate line; cost-management posture (`ken/6bc81f3a`) calibrates which sermons warrant the full panel vs. a single voice.
- **Cluster training cadence**: m4max is the mobile training node; m4mini and m3pro are the always-on inference nodes. Train serially on m4max, one author at a time, careful-not-clever per the `one-at-a-time` directive (`ken/4a66badc`). 24 LoRAs is a multi-month effort even with serial discipline. Don't queue eight LoRAs and walk away.
- **Cluster failure modes**: m4mini offline drops the always-on inference path → m3pro is the fallback. NATS broker on the VPS is single-point-of-failure for routing → rpi5 holds the NATS replica. m2mini is batch overflow only — don't promote it to primary inference because it's on a remote network. Closed-weight path is unaffected by cluster failures (rides existing orchestra adapters).
- **Path-selection drift**: if every request defaults to "frontier API is easier" the local LoRA investment never pays back. Router must prefer the open-weight path when both paths are available and the request fits; closed-weight is the bridge until LoRAs land and the depth-needed exception thereafter.
- **Voice-bleed into the pastor's own voice**: voice-audit must run *after* step 7.5 to confirm the manuscript still reads as the preacher, not the panel.

## 8. Sequencing (estimates; will drift)

Two tracks running in parallel: **A (closed-weight, ships fast)** and **B (open-weight, depth)**. Track A unblocks step 7.5 in weeks 3–4; track B replaces or supplements voices as LoRAs land.

**Track A — closed-weight personas (immediate)**

| Week | Work |
|---|---|
| 1 | Complete Spurgeon scrape (3,556 remaining). Begin Washer + Sproul + MacArthur + Platt corpus acquisition. The corpora are needed first because they anchor RAG, which anchors both paths. |
| 2 | RAG layer over indexed corpora at `Romans/quotes-and-references/`. Chunk-ID format. `retrieve_from_corpus` tool spec. Cite-or-flag enforcement scaffold. |
| 3 | Draft 24 closed-weight personas (voice/era/doctrinal-commitments/characteristic-moves per theologian, anchored on corpus chunks). Substitutionary-atonement bumper baked into Wright persona. |
| 4 | Wire personas into orchestra adapters (GPT, Grok, Gemini, Claude-when-not-integrating). Pipeline step 7.5 ships with closed-weight path. |
| 5 | Score against Romans 1a/1b benchmarks (88/105, 91/105 per `romans/50b2c027`). Hallucination audit: every attributed quote must have a chunk ID. |
| 6 | Cost calibration: measure $/sermon for the full step-7.5 panel; tune voice count per pipeline run based on `ken/6bc81f3a`. |

**Track B — LoRA training (parallel; serial within itself)**

| Week | Work |
|---|---|
| 3 | Base-model decision via 3-pass orchestra design review (`ken/05261df2`): PASS 1 design proposal, PASS 2 stress with Romans 9 + Psalm 23 + a wounded-congregation pastoral text, PASS 3 refine. |
| 5–28 | LoRA training on m4max, one author at a time (serial; `4a66badc`). Recommended order: Spurgeon → Washer → Sproul → MacArthur → Platt → Piper → Calvin → Edwards → Davey → Chandler → Anyabwile → Begg → Ryle → M'Cheyne → Bunyan → Lloyd-Jones → Carson → Schreiner → Baucham → Hamilton → Owen → Chapell → Robinson → Keller. Each landing LoRA gets a head-to-head voice-audit vs. its closed-weight persona on a benchmark passage; the winning voice becomes the default for that author. |
| 29 | Wright LoRA last. Adversarial review (`ken/07bb1504`) on Wright outputs against the substitutionary-atonement bumper. |
| 30 | Voice-audit recalibration after all LoRAs land. Post-deploy monitoring of cite-or-flag rate + named-uncertainty disposition + path-selection mix. |

## 9. What does NOT get built

- No biblical-author LoRAs and no biblical-author personas.
- No Greek-scholar voice LoRAs or personas (those become RAG-indexed exegesis aides).
- No theologian-voice deployment to InTheWake content.
- No "model decides its own boundary fencing" — the boundary is the retrieval-grounded citation invariant, enforced at the system level on both paths.
- No batch parallel LoRA training on m4max — serial, one at a time, per `one-at-a-time`.
- No Claude-as-theologian-persona in the same pipeline run that Claude is integrating. Conflict-of-interest in the wheat/chaff judgment.
- No closed-weight persona that omits the `retrieve_from_corpus` tool-call requirement. Persona without the tool gate is just decoration over fabrication.

## 10. Open dependencies / blockers

- Spurgeon scrape completion. Without it, the indexed corpus is hypothetical and **both paths are blocked** (closed-weight personas need RAG-grounding too).
- Washer + Sproul + MacArthur + Platt + Piper + Calvin + Edwards (etc.) corpora — need acquisition decision per author (which sources, IP/copyright posture). Spurgeon is public domain; many of the modern Tier 1 are not. **Until copyright posture is clarified per author, neither LoRA training nor closed-weight persona retrieval can run for that author.** Personas can be drafted in parallel but cannot ship without an indexed corpus to anchor cite-or-flag against.
- Grok API key refresh (per session handoff — 400 errors). Wright challenger role is harder to validate without Grok available as the structural-role parallel.
- Perplexity adapter for orchestra (per handoff). Step 5 of the existing sermon pipeline degrades gracefully without it.
- `retrieve_from_corpus` tool spec — needs design before track A week 4. Tool returns `{author, chunk_id, text, citation_metadata}`; closed-weight personas must call it before any attributed quote.

## 11. Memory encodings to write after operator approval

The handoff names "Theologian Model Library Plan (in protected memory)" but no discrete protected memory captures the plan. After operator approval of this doc, encode:

- The Scripture-governs / 1689-is-bumpers framing (operator's verbatim 2026-05-21).
- The base-model decision (14B Q4) and its cluster-distributed deployment.
- The full-roster Tier-1 theologian pool (24 names; no demotion).
- The no-biblical-author-LoRA rule and its Scripture-governs + Berean-Gate grounding.
- The RAG-as-citation-invariant rule (anti-hallucination as system invariant, not model behavior).
- **The two-path architecture** (open-weight LoRA + closed-weight persona, sharing corpus and cite-or-flag invariant) per operator confirmation 2026-05-21.
- **The `retrieve_from_corpus` tool gate** as the citation enforcement mechanism on the closed-weight path.
- **The Claude-not-integrating-and-persona-in-same-run rule**.
- The InTheWake engineering-only application.
- The Wright-NPP integration-round reject rule (verifier pass, both paths).
- Pipeline step 7.5 insertion into the existing 9-step sermon pipeline.
- The cluster topology mapping for inference vs. training (m4mini/m3pro inference, m4max training, m2mini overflow, VPS coordinator).

Each encoded as a protected memory in `romans/` or `shared/` domain with `operator-directive` tag once approved.

---

Soli Deo Gloria.
