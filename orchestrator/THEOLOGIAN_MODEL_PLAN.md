# Theologian Model Library — Plan

Branch: `claude/theological-model-planning-VU2zD`
Primary repo: `Romans` (sermons). Secondary application: `InTheWake` (engineering pattern only — see §6).
Status: planning. No training has begun. Spurgeon corpus scraper is at 5/3,561 sermons.

This plan integrates the multi-LLM-integration handoff (theologian LoRA pool, Open Claw routing, debate mode, Wright-as-challenger) with the protected-memory directives the household already operates under. Where the handoff and memory conflict, memory wins and the wheat/chaff call is named. The plan was design-reviewed by the household orchestra (strategy mode, $0.20, 2026-05-21) and stress-tested against four parallel research agents covering Magisterium AI prior art, LoRA voice-transfer literature, multi-agent debate frameworks, and RAG citation-enforcement research; provenance is logged in §12.

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

The operator's anti-hallucination directive is non-negotiable. The plan refuses to lean on "the model will be careful." Instead, four layered enforcement mechanisms, none optional:

- **Cite-or-flag-or-fail**. Every attributed quotation in output must resolve to a retrieved chunk ID from the indexed corpus. No retrieval ID, no quote — the system flags or refuses, the model never invents.
- **Substring-match post-validator** (research-grounded; Wallat et al. SIGIR 2025, arXiv 2412.18004): the literature documents *57% of RAG citations are unfaithful* — the model generates from parametric knowledge then post-rationalizes the citation. Mitigation: every attributed quote string must be a verbatim substring of its retrieved chunk text. Citation-presence without substring-match is the documented failure mode; the validator catches it.
- **Cryptographic chunk-ID hashing** (Perplexity refinement from orchestra): each retrieved chunk carries a SHA-256 hash computed at index time; the system verifies hash-equality on every quote emission. Detects corpus tampering, stale-chunk reuse, and mid-pipeline chunk substitution.
- **Forced-tool-use is best-effort, not guaranteed** (research-grounded; Promptfoo + Cao et al. arXiv 2412.04141). `tool_choice: "required"` increases compliance but does not guarantee it; stronger reasoning models hallucinate tool calls *more*, not less, under enforcement pressure (the reliability-capability tradeoff). The post-validator is therefore the actual enforcement; tool-call routing is a strong default, not the gate.
- **Named-uncertainty in prose** is allowed and preferred over fabricated confidence: "I'm not sure where I first heard this — whoever said it…" (`ken/14bea502`, `ken/39de9e17`). The LoRA-augmented model is *trained* to produce this disposition when retrieval is empty.
- **Two-source minimum** on factual claims that aren't direct quotation (dates, numbers, historical events).
- **Hallucination audit** runs as a post-step on every generated sermon section: scan attributed claims, verify each has a chunk-ID + substring-match + hash-verification, surface any failures to the Integrity Log per `romans/eac4d8bd`.

This is not a feature. It is the architecture. If the cite-or-flag invariant fails, the whole build fails its purpose. The research literature is explicit that persona prompts *amplify* parametric-knowledge leakage (RoleBreak arXiv 2409.16727; SHARP arXiv 2411.07965); the persona-Spurgeon framing is the documented worst case, so the gates above carry more weight than they would on neutral output.

### 3.2 Cluster-aware deployment (not single-node)

The operator's cluster is documented at `ken/de9c5aa2` + `ken/f98289ea`. Mapping work onto nodes:

- **m4mini** (Mac mini M4, always-on, OpenClaw host): **primary inference node** for production sermon-pipeline requests. Hosts the base model + frequently-used LoRAs. NATS subscriber for sermon-pipeline tool requests.
- **m3pro** (MBP M3 Pro, home LAN, code-specialized): **secondary inference node** + Whisper. Pairs with m4mini for parallel debate-mode (each node holds one LoRA, full-context round-passing rides NATS between them).
- **m4max** (MBP M4 Max, mobile, 36 GB — **base-config M4 Max**, not the 48 GB upgrade; confirmed operator 2026-05-21): **opportunistic training node**. Trains LoRAs serially (per `ken/4a66badc` one-at-a-time). When mobile, it falls off the tailnet and training pauses; when home, it resumes. m4max also handles SDXL — keep training scheduled around photography work.
- **m2mini** (Mac mini M2, remote network): **batch overflow** + NATS replica. Picks up sermon-pipeline jobs that queue up when m4mini is busy.
- **m4mini hosts the NATS broker** for theologian-model traffic (orchestra refinement 2026-05-21). The RackNerd VPS keeps NATS for the rest of the household (family-history, photography ingest, cross-repo sync) but theologian-model + sermon-pipeline traffic stays inside the tailnet on m4mini. Rationale: sermon drafts, congregation-burden tags, and pastoral concerns are sensitive content; local-first NATS for that traffic honors the one-user-trust posture (`ken/7c4c90e3`) without compromising other household services.
- **RackNerd VPS**: NATS broker for non-sermon household traffic + MinIO results-archive. **Not a model host. Not the sermon-pipeline broker.**
- **rpi5/4a/4b**: rpi5 holds the m4mini NATS replica (failover), scheduled-job runner, photo ingest. No LLM role.

**Inference runtime commitment**: **llama.cpp** is the only Apple Silicon path that supports the 24+ hot-swappable LoRAs this plan requires (PR #7667, GGUF LoRA support). Ollama hot-swap is not implemented (issues #5788, #9548 as of 2026-05); MLX multi-LoRA serving is alpha-only (MOLA). Throughput baseline on M-series Q4_K_M: 38–58 tok/s. No Apple Silicon port of S-LoRA / Punica exists, so multi-tenant adapter serving at scale stays out of reach until that lands.

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

**Debate-mode constraints (research-grounded refinements)**:
- **Cap at 3 rounds** (Du et al. arXiv 2305.14325 + arXiv 2311.17371 sweet-spot finding). Cost grows quadratically; marginal value drops sharply past round 3.
- **Persona re-anchoring each turn**: Li et al. arXiv 2402.10962 documented ~30%+ persona-drift past 8–12 turns; mitigation is split-softmax re-weighting + re-anchoring the persona prompt in each turn rather than relying on initial-context persistence. Apply uniformly on both paths.
- **Heterogeneity over homogeneity**: the literature is settled that diversity helps and contested that debate-beats-CoT+SC at matched compute (arXiv 2502.08788, 2509.05396, 2511.07784). Routing should select voices that represent different theological emphases on the same passage, not three similar voices.
- **Abstain-on-tie**: if the integration round can't produce a wheat/chaff verdict with justification, abstain rather than synthesize; surface the disagreement to the pastor as an Integrity Log entry.

**Theologian LoRAs — primarily correctors, voice as secondary mode** (operator extension 2026-05-21 #2):

Each theologian LoRA is trained as a **corpus-scholar first**, with voice as a secondary inference-time mode invoked on explicit request. This is the cleaner architectural fit: the primary disposition is "what did this author actually say?" not "speak as this author." Voice fidelity becomes a secondary evaluation metric, not the gate. Reasons:

- **Aligns training with cite-or-flag**: a LoRA whose default disposition is corrective grounds in the corpus reflexively. Voice-first training grounds in stylistic mimicry, which makes parametric-knowledge leakage easier (per RoleBreak / SHARP findings in §3.1).
- **Resolves voice-audit tension**: the pastor's voice must dominate final manuscripts (per `voice-audit` + `like-a-human` calibrated to his voice). Theologian voice as a primary mode actively competes with that; theologian voice as explicit-invocation does not.
- **Tighter training objective**: corrective-LoRA training (detect + cite + correct against indexed corpus) is better-published than voice-transfer training (AuthorMix arXiv 2603.23069, ASTRAPOP arXiv 2403.08043 — both contested on corpus-size thresholds for reliable voice transfer).

Voice-mode invocation pattern: the pastor explicitly requests "give me this in [author]'s voice" at inference time, or debate mode (Stage 9) calls for voice as part of the wheat/chaff critique. Default output mode otherwise is corrective scholarship.

**Author-by-mode matrix** (the operative rule):

| Author class | Corrective mode | Voice mode |
|---|---|---|
| **Biblical authors** (Paul, John, Peter, David, Isaiah, etc.) | YES — primary, only | **NO — never available**. Scripture is uniquely inspired; impersonation crosses 1689 LBCF + Berean Gate + Fatal-Flaw cap. |
| **Theologians** (Spurgeon, Calvin, Edwards, Sproul, MacArthur, Platt, Davey, Chandler, Anyabwile, Begg, Ryle, M'Cheyne, Bunyan, Piper, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, Robinson, Keller, Washer — 24 total) | YES — primary, default | YES — secondary, invoked on explicit request |
| **Topic clusters** (ANE, Second Temple Judaism, Greco-Roman, Greek grammar, Hebrew grammar, biblical-theology themes) | YES — only mode | N/A |
| **Wright (challenger)** | YES — corrective on claims about Wright | YES — secondary, specifically for the challenger role at Stage 9, gated by the substitutionary-atonement verifier pass on every emit |

**LoRA training discipline (research-grounded; applies to corrective objective primarily)**:
- **AlignGuard-LoRA (Fisher Information Matrix regularization, arXiv 2508.02079)** applied on every LoRA. Preserves alignment-critical directions; documented drift reduction up to 50%. This is the documented mitigation for catastrophic-forgetting risk (arXiv 2402.15415, 2402.18865).
- **Contrastive negative-corpus** per author: when training Spurgeon, penalize MacArthur-distinctive / Owen-distinctive / Keller-distinctive terminology so the LoRAs stay separable rather than merging into "Reformed-sounding soup." This matters even for the corrective objective — keeps authors distinguishable in retrieval-grounded output, and prevents the voice-mode (when invoked) from drifting to generic-Reformed.
- **Stylometric evaluation harness as secondary check**: authorial-perplexity ALM (PMC12225838) + GRPO + sentence-transformer reward (arXiv 2512.05747) for voice-fidelity scoring when voice mode is invoked. Primary evaluation is corrective accuracy (catches attested errors? verifies quotes against the corpus? surfaces relevant material for a passage?).
- **OPLoRA orthogonal-projection** (arXiv 2510.13003) considered as fallback if AlignGuard alone proves insufficient.

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

### 3.5 Corrector LoRAs (operator extensions 2026-05-21 #1 and #2)

The earlier "no biblical-author LoRAs" rule was too coarse. It conflated two distinct artifacts (extension #1):

| LoRA type | What it does | Theological posture | Verdict |
|---|---|---|---|
| **Voice LoRA on a biblical author** | Produces new prose styled as Paul / John / Peter / etc. | Crosses into impersonating Scripture | **No — rule stands** |
| **Corrector LoRA on a biblical author** | Catches errors in claims *about* that author (dates, geography, doctrine, context, argument structure) and drives back to the text | Guardrail; serves Scripture-governs | **Yes — and load-bearing** |

Then extension #2 (operator 2026-05-21): **theologian LoRAs are primarily correctors too — maybe mostly.** This unifies the architecture: most LoRAs in the build are correctors with optional secondary voice mode. See §3.3 for the author-by-mode matrix.

The corrector LoRAs are *not* primarily voice impersonators. They are domain scholars whose default output mode is detect-and-correct against the indexed corpus + reputable scholarship. They serve the cite-or-flag invariant rather than violating it. Voice output is a *secondary inference-time mode* available only for theologians and Wright (never for biblical authors).

**The three functions of a corrector LoRA** (operator extension 2026-05-21):

1. **Factual correction** — dates, geography, historical context, biographical claims. Examples for Paul: "Paul lived in the 2600s AD" → corrects to c. AD 5–67 with citation chain; "Paul wrote Romans from Ephesus around AD 40" → corrects to Corinth, AD 56–57, citing Rom 15:25–26 + Acts 20:2–3, notes AD 40 predates Paul's conversion (c. AD 33–35); "Paul traveled through Mesopotamia" → flags; documented routes were Asia Minor / Macedonia / Achaia / Rome via Crete and Malta.

2. **Doctrinal correction** — claims about the author's positions that the corpus contradicts. "Paul taught justification by faith and works" → flags as contradicting Rom 3:28, 4:5, Gal 2:16; names the Reformed harmonization with James 2 (faith-genre vs. forensic-justification).

3. **Rhetorical-structural critique** — catches sermon argument that violates the apostle's actual argument arc. This is the highest-leverage of the three functions. Paul's argumentation is genuinely different from modern Western homiletic structure:
   - Diatribe form with hypothetical interlocutors ("what shall we say then," "is the law sin," "by no means")
   - Rabbinic argumentation patterns (kal vachomer / lesser-to-greater; gezerah shavah on shared vocabulary)
   - OT citations as midrashic anchors, not just proof-texts
   - Chiastic structures (Rom 5:12–21, Phil 2:6–11) where the central B carries the weight, not the A/A'
   - Corporate-then-individual movement (Romans 1–3 builds corporate condemnation precisely to set up the universal need for imputed righteousness in 3:21–26)
   - Situational polemic disguised as systematic (Galatians)
   - Periodic sentences with subordinated argument-chains

   Worked failure modes the corrector catches:
   - Sermon excerpts Romans 3:23 ("all have sinned") and pivots straight to individual conviction, skipping the corporate argument arc that gives v.23 its actual force.
   - Sermon treats Romans 7's "I" as Paul's autobiographical struggle without naming which exegetical option is being taken (Paul-believer / Paul-pre-conversion / Adam-typology / rhetorical-persona-of-Israel-under-Law).
   - Sermon uses Galatians 3:28 toward modern social conclusions while skipping the covenantal Abrahamic-inheritance argument the verse actually serves.
   - Sermon imposes a three-point Western homiletic frame on a chiastic Pauline passage where the chiasm's B is the load-bearing claim.

This function is essentially an **automated Scopus test** for Pauline material (per `romans/32bacde3`'s four diagnostic tests). It also feeds the thus-says-the-lord rubric (`romans/6debe5a2`) categories Exposition & Hermeneutics (25 pts), Structure & Logical Flow (9 pts), and Sermonic Force (5 pts).

**The category this opens** — three sub-categories of corrector LoRAs sharing the same architecture, differing in whether voice mode is available:

- **Biblical-author correctors** (no voice mode, ever): Paul, Peter, John, James, Jude, Hebrews-author, Luke, Mark, Matthew, the Twelve, David, Isaiah, Jeremiah, Ezekiel, Daniel, Moses, Solomon, Joshua, Samuel-author, Kings-author, Chronicles-author.
- **Theologian-author correctors** (voice mode invokable on explicit request): the full 24-name Tier-1 roster from §3.3. Each LoRA is primarily a corpus-scholar; voice output is available when the pastor explicitly requests it or when debate mode (Stage 9) calls for it.
- **Topic-cluster correctors** (no voice mode applicable): ANE backgrounds, Second Temple Judaism, Greco-Roman world, NT Greek grammar, Hebrew grammar, biblical-theology themes (covenant, kingdom, sacrifice, exile).
- **Per-book correctors** (optional sub-layer): Romans-specific historical-context corrector, Genesis-specific framework corrector, etc.

All four sub-categories train against the same primary objective (corpus-scholar; detect + cite + correct). The voice-mode availability is an *inference-time flag*, not a training-time difference. Biblical-author voice-mode is hard-disabled at the system level (the LoRA may have the capacity but the gateway refuses the invocation); theologian voice-mode is enabled but secondary; topic-cluster voice-mode is N/A.

Corrector LoRAs are *cheaper to train per LoRA* than pure voice-LoRAs — smaller corpora, narrower objective, no voice-fidelity benchmark gate to clear. They are also *higher-leverage* for hallucination prevention because the corrections are reflexive rather than prompted. The collapsing of theologian-voice training into theologian-corrector training (extension #2) shortens the overall sequencing materially — Track C no longer needs to run as a separate stretch.

**Training corpus per corrector**:
- The biblical text itself (ESV; the author's books).
- Conservative Reformed scholarship on that author — Schreiner, Moo, Murray, Carson, Fee, Bruce, Murray Harris, Bock, conservative Witherington on Pauline rhetoric, Aletti / Stowers / Stuhlmacher on rhetorical-criticism diversity.
- First-century reference works — Hengel, Schürer, conservative archaeology, ANE-background standards.
- Greek lexical material (BDAG, NIDNTTE) for vocabulary work.

**Framework-agnostic training posture on contested scholarship**: Pauline rhetoric scholarship is *not monolithic* — Witherington (Greco-Roman primary), Stendahl / Stuhlmacher (Jewish midrashic primary), Stowers (diatribe specifically), Aletti (literary rhetoric) read the same passage differently. The corrector is trained on multiple frameworks and surfaces *which framework reads which way* with named-uncertainty rather than pretending one framework is settled.

**Pipeline integration** (see §4):
- **Post-DRAFT, pre-INTEGRATE (Stage 2)**: correctors fire on author-tagged material in the pastor's draft. Both biblical-author correctors and theologian correctors fire here.
- **Post-step-7.5, pre-EVALUATE (Stage 10)**: correctors fire again to catch errors smuggled in by Stage-9 critique (whether the voices spoke in correction-mode or, with explicit invocation, in voice-mode).
- **Stage 9 itself** uses theologian correctors in their *primary* corrective mode by default — they critique the pastor's argument and his claims about them, surfacing what the author actually said. Voice mode at Stage 9 is invoked only when the pastor explicitly requests "give me this in Spurgeon's own voice" or when debate-mode framing calls for it (e.g., Wright's challenger role).
- **PostToolUse hook** on Edit/Write of author-tagged sermons (extends the existing advisory hook pattern at `romans/44566500`).

**Where this beats closed-weight personas**: the closed-weight path can simulate "Pauline scholar persona" or "Spurgeon scholar persona" via prompt + RAG, but a trained LoRA is meaningfully more reliable for systematic fact-correction because the corrections become reflexive rather than prompted. Worth doing the LoRA on the open-weight path even when the persona exists on the closed-weight side.

### 3.6 Pre-DRAFT human exegesis gate (orchestra blind-spot fix; operator decisions 2026-05-21)

Grok's blind-spot pass on the orchestra design-review (2026-05-21) identified a fatal-flaw-class concern: as originally drafted, step 7.5 inserted theologian consultation *between INTEGRATE and EVALUATE*, which by ordering means machine-generated commentary precedes the pastor's own original exegesis. That inverts the Scripture-governs priority. "Reformed-sounding" language can mask non-authoritative synthesis when the pastor receives generated theologian commentary before producing his own argument.

The fix has three components — pastor-first ordering, override mechanism, and disclosure posture. All three decided by the operator 2026-05-21.

**Component 1 — Mandatory pre-DRAFT human exegesis stage.** The pastor produces and logs original passage work — Greek/Hebrew, structure, FCF (Fallen Condition Focus), Scopus proposition, theological locus, congregation-burden mapping — before any LoRA or persona consultation fires. The output is a structured exegesis log appended to the sermon file.

**Component 2 — Soft hard gate with logged override (Decision 2 → B).** Default is hard refusal on empty/stub exegesis log:

- Stages 1+ technically refuse to fire when the sermon file's exegesis-log section is empty or stub-only ("INCOMPLETE:" markers + nothing else, or fewer than a documented minimum-content threshold).
- A documented override flag exists: `--override-exegesis-gate "<one-line reason>"` (or equivalent flag on the sermon-pipeline runner).
- The override **requires** a one-line reason logged in the sermon's Integrity Log (per `romans/eac4d8bd` + `romans/9601fa7e` HTML-comment integrity-flag conventions). No silent overrides — the audit trail is conspicuous.
- Sermons that used the override carry a flag in `sermon-map.md` (per `romans/13109dae` sermon-map maintenance rule) — a new column or status marker like `⚠️ EXEGESIS-OVERRIDE`.
- After N un-backfilled overrides (default N=3), the system surfaces a reminder at session start: *"you have N sermons with overridden exegesis gates — schedule time to backfill before the next series."* The reminder fires until backfill is complete or the operator explicitly acknowledges/dismisses it.
- **Override is for genuine emergencies** (death in the family, ER trip, hospital emergency, family crisis). It is not for last-minute prep that could have been done earlier. The careful-not-clever spot-audit ("were you careful or clever on this one?") applies to override-flagged sermons specifically.
- **Backfill mechanism**: when an override is invoked, the sermon-map flag persists until the pastor retroactively completes the exegesis log. The flag clears when the log meets the minimum-content threshold.

This honors both patterns simultaneously: careful-not-clever discipline holds by default with conspicuous override-audit, and action-over-deliberation works at the moment of real need.

**Component 3 — Disclosure posture (Decision 1 → D + A combined).**

- **A: Manuscript footer.** Every final sermon manuscript ends with the visible disclosure footer. Canonical template lives at `Romans/.claude/disclosure-footer.md` (see template in next paragraph). Stage 12 (Voice-audit + disclosure) appends it during pipeline.
- **D: Congregation-meeting / pastoral-letter methodology disclosure.** A one-time pastoral letter or congregation meeting explains the methodology: that AI tools assist with research, language-checking, and theologian-corpus consultation; that the exegesis, conviction, and pastoral application are the pastor's; that the methodology is recorded in each manuscript's footer for the long tail of readers. Canonical draft template lives at `Romans/.claude/methodology-disclosure-letter.md`. One-time deliverable; not pipelined.
- **What's NOT adopted**: pure E (no disclosure) is concealment, off-pattern with the household's honesty discipline. Pure B (top-of-manuscript header) hijacks the sermon opening. F (per-artifact tiering) is honest but operationally complex; deferred unless needed.
- **Optional C (occasional pulpit reference)**: pastoral judgment; not architecturally required. The pastor may verbally acknowledge AI tool use from the pulpit at series introductions or once a year as he sees fit. Not pipelined.

**Canonical footer template** (lives at `Romans/.claude/disclosure-footer.md`; appended at Stage 12):

> *Methodology note: This manuscript incorporates AI-retrieved historical voices and corrector-LoRA review under 1689 LBCF discipline. The exegesis, conviction, and pastoral application are the pastor's; the AI tools assist with research, source verification, and language-checking. See the congregational methodology letter (date) for details.*
>
> *Soli Deo Gloria.*

**No AI-on-empty-draft**. If the pastor's exegesis log is empty or stub-only and the override is not invoked, Stages 1+ refuse to fire. The system enforces the order: pastor first, AI second, with the override as the named emergency exit.

This is a posture change, not just a code change. It honors what the household's existing memory already encodes: the sermon belongs to the pastor (`romans/454c8aaa` pastoral-voice rule, "real life goes into the teaching, not around it"; `romans/0c10d211` political-neutrality rule; the entire careful-not-clever discipline). The corrector LoRAs and theologian voices sharpen; they do not replace exegetical labor. The disclosure footer + methodology letter honor transparency without making the AI the headline.

## 4. Integration with the existing sermon pipeline

Existing 9-step pipeline (`ken/69213852`): DRAFT → consult_challenge (Grok) → consult_expand (Gemini) → consult_structure (GPT) → consult_verify (Perplexity) → consult_research (You.com) → INTEGRATE (Claude) → EVALUATE (thus-says-the-lord) → VOICE_AUDIT.

The pipeline is restructured to honor the pre-DRAFT exegesis gate (§3.6) and the corrector LoRAs (§3.5):

**Revised pipeline (12 stages, three new insertion points marked ★)**:

| # | Stage | Owner | Notes |
|---|---|---|---|
| 0 | ★ **Pre-DRAFT human exegesis** | Pastor | Greek/Hebrew, FCF, Scopus, locus, burden map. No AI consults. Log appended to sermon file. Gate: subsequent stages refuse to fire on empty/stub log. |
| 1 | DRAFT | Claude | First manuscript pass with codebase + memory context. |
| 2 | ★ **Post-DRAFT corrector** | Corrector LoRAs | Author-tagged material gets fact-checked + doctrinal-checked + rhetorical-structurally critiqued. Output to Integrity Log. |
| 3 | consult_challenge | Grok | Existing orchestra step. |
| 4 | consult_expand | Gemini | Existing. |
| 5 | consult_structure | GPT | Existing. |
| 6 | consult_verify | Perplexity | Existing. |
| 7 | consult_research | You.com | Existing (last word). |
| 8 | INTEGRATE | Claude | Synthesizes the consultation chain. |
| 9 | **Step 7.5 — post-exegesis theologian critique** | LoRAs + personas | NOT generative. Voices given the pastor's draft + exegesis log; produce wheat/chaff verdicts on his argument with cited support. Debate mode (≤3 rounds, persona re-anchored each turn). Claude integrates wheat/chaff with own justification. Wright runs through the substitutionary-atonement verifier. `optional: true`. |
| 10 | ★ **Post-7.5 corrector** | Corrector LoRAs | Catches errors smuggled in by theologian voices. |
| 11 | EVALUATE | thus-says-the-lord rubric | All four diagnostic tests (Scopus, Berean Gate, FCF, Gospel-presence) + 105-pt scoring. Corrector output feeds Exposition + Structure + Sermonic Force categories. |
| 12 | VOICE_AUDIT | Voice-audit + voice-dna | Confirms manuscript still sounds like the pastor, not the LoRA panel. Mandatory visible-disclosure footer added. |

**Notes**:
- Stage 0 is **mandatory**, not optional. The whole architecture's posture-correctness rests on it (per §3.6).
- Stages 2 and 10 are corrector-LoRA passes; same LoRA, different content target. They are **non-generative**: their only output mode is detect + correct + cite.
- Stage 9 ("step 7.5") is `optional: true` for graceful degradation if voices are unavailable or under-trained, but it has been **reframed**: voices critique the pastor's argument, they do not propose alternative arguments to be merged. This is the orchestra blind-spot fix applied.
- Persona re-anchoring fires at the start of every turn within Stage 9's debate rounds.
- Cost-management posture (`ken/6bc81f3a`): Stage 9 inherits the cost calibration. Single-voice consultation for routine weekly sermons; full debate panel for series-anchor sermons (e.g., Romans 9, key holiday preaches, doctrinal-watershed passages).

## 5. Non-negotiable gates (LoRA output gets no pass)

- **Scripture governs**: the Bible is the authority. Every doctrinal claim traces to a text. The 1689 LBCF is the bumpers — out of the gutter, not the ball.
- **Pastor-first ordering** (§3.6): the pastor's exegesis precedes any AI consultation. AI never produces an alternative argument to be merged with the pastor's — AI critiques his argument.
- **Berean Gate**: if the sermon doesn't open/quote/exegete its named text, Fatal-Flaw cap at 60/105 regardless of LoRA quality (`romans/32bacde3`).
- **Substitutionary atonement** as gospel-call shape — confessional bumper (`romans/1aa5a7b7`). Verifier pass on every Wright-tagged contribution.
- **ESV-only** for quotation, including conversational paraphrase (`romans/a8e030ac`).
- **Cite-or-flag-or-fail** on every attributed quote: retrieved chunk ID + substring-match + hash-equality, or hard flag. See §3.1.
- **No fabricated quotes, ever.** Named-uncertainty in prose is the disposition when retrieval is empty.
- **Corrector LoRAs run on author-tagged content** at stages 2 and 10. Detected drift (factual, doctrinal, rhetorical-structural) is surfaced to the Integrity Log; the pastor decides whether to honor or override.
- **Political-neutrality** rule preserved (`romans/0c10d211`) — LoRA voices that drift political get the integration round's chop.
- **Voice-audit** post-LoRA: the manuscript must still sound like the pastor, not Spurgeon. LoRA enriches argument; voice belongs to the preacher.
- **Visible disclosure footer** on every final manuscript (per §3.6 Component 3 / Decision 1). Canonical template at `Romans/.claude/disclosure-footer.md`. Appended at Stage 12.
- **Pre-DRAFT exegesis gate is a soft hard gate** (per §3.6 Component 2 / Decision 2) — default refusal on empty/stub log; `--override-exegesis-gate "<reason>"` flag exists; override is logged in Integrity Log + sermon-map flag; backfill reminder after N=3 un-backfilled overrides. The override exists for genuine emergencies; the discipline is conspicuous, not silent.

## 6. InTheWake — what it actually gets

InTheWake's protected memory is unambiguous: theology is **implicit, salt-not-billboard**, pastoral content is **red lane** (notes only, human writes), Scripture refs live in HTML comments not visible prose. Spurgeon-voiced cruise content would violate the immutable posture.

InTheWake gets the **engineering**, not the **voice**:

- **RAG-grounded citation discipline** applied to cruise sources: CruiseMapper (primary for deployment data per `cruising/2dd627ed`), VesselFinder/MarineTraffic (IMO/AIS per `cruising/9f819c5e`), official deck-plan URLs (`cruising/f621ebcd`). Every price/menu/IMO/itinerary claim resolves to a retrieved-source ID before publish — same architectural invariant, different sources.
- **Orchestra-as-pre-execution-gate** already running in `cruising` mode (`ken/ae168797`); no change.
- **Voice-audit calibrated by voice-dna** against the cruise corpus (already deployed); the theological-model build informs the *technique* but does not transfer the *voice*.
- **Hallucination-elimination preference** (`cruising/4918b2a5`): the cite-or-flag invariant directly addresses the "AI-generated content with specific-sounding details" failure mode already named in memory.

Engineering shared, theology not. The InTheWake LoRAs are zero.

## 7. Risk register

- **Frontier-model quote fabrication (HIGH RISK; research-documented)**: Claude / GPT / Grok / Gemini all have Spurgeon, Calvin, Edwards, Piper, etc. in their training data. A persona-prompted "Spurgeon" can confidently emit a plausible-sounding Spurgeon quote that does not exist. *Wallat et al. SIGIR 2025 (arXiv 2412.18004) documents 57% of RAG citations are unfaithful — the cited document exists and is topical but did not drive the generation.* RoleBreak (arXiv 2409.16727) and SHARP (arXiv 2411.07965) show persona prompts measurably *amplify* parametric-knowledge leakage. The cite-or-flag invariant + substring-match validator + cryptographic chunk-hash (§3.1) are layered specifically against this failure mode. Tool-call enforcement alone (`tool_choice: "required"`) is best-effort, not guaranteed (Promptfoo + Cao arXiv 2412.04141).
- **Wright NPP-leak from frontier training data**: same problem at the doctrinal level. Frontier models have Wright in training; a Wright persona will tend to import NPP. The substitutionary-atonement bumper runs as a verifier pass on every Wright-tagged contribution at integration — not a soft prompt.
- **LoRA confabulation under RAG**: open-weight path; default-flag any attributed claim without retrieval ID. Sample audit after every LoRA release.
- **Training-data gating**: Spurgeon = 5/3,561; Washer/Sproul/MacArthur/etc. = 0 scraped. No LoRA is real until its corpus is real. Closed-weight personas can ship sooner but only if the indexed corpus exists for retrieval to anchor against.
- **Cost escalation on the full pipeline**: orchestra runs are $0.03–0.08 per pass today (`ken/47dd2ce1`). Adding 2–3 theologian-persona calls per step-7.5 run multiplies that. Cost-reporting per round (`ken/47dd2ce1`) must include theologian-voice cost as a separate line; cost-management posture (`ken/6bc81f3a`) calibrates which sermons warrant the full panel vs. a single voice.
- **Cluster training cadence**: m4max is the mobile training node; m4mini and m3pro are the always-on inference nodes. Train serially on m4max, one author at a time, careful-not-clever per the `one-at-a-time` directive (`ken/4a66badc`). 24 LoRAs is a multi-month effort even with serial discipline. Don't queue eight LoRAs and walk away.
- **Cluster failure modes**: m4mini offline drops the always-on inference path → m3pro is the fallback. NATS broker on the VPS is single-point-of-failure for routing → rpi5 holds the NATS replica. m2mini is batch overflow only — don't promote it to primary inference because it's on a remote network. Closed-weight path is unaffected by cluster failures (rides existing orchestra adapters).
- **Path-selection drift**: if every request defaults to "frontier API is easier" the local LoRA investment never pays back. Router must prefer the open-weight path when both paths are available and the request fits; closed-weight is the bridge until LoRAs land and the depth-needed exception thereafter.
- **Voice-bleed into the pastor's own voice**: voice-audit must run *after* step 7.5 to confirm the manuscript still reads as the preacher, not the panel.
- **Multi-agent debate may not beat CoT+SC at matched compute** (research-grounded; arXiv 2502.08788, 2509.05396, 2511.07784). The literature is contested. Mitigation: monitor cost per sermon and skip debate-mode on routine weekly preaches; reserve it for series-anchors and doctrinal-watershed passages. Heterogeneity in voice selection is the documented win.
- **Persona drift in long-context debate** (arXiv 2402.10962): ~30%+ self-consistency loss past 8–12 turns. Mitigation: persona re-anchoring each turn + 3-round debate cap (§3.3).
- **LoRA catastrophic forgetting** (arXiv 2402.15415, 2402.18865): base reasoning degrades under naive fine-tune. Mitigation: AlignGuard-LoRA (arXiv 2508.02079) on every author LoRA (§3.3).
- **Reformed-soup voice collapse**: 24 LoRAs trained on related authors risk merging into a generic Reformed voice rather than preserving distinct theological emphases. Mitigation: contrastive negative-corpus per author (§3.3).
- **Apple Silicon multi-LoRA serving is narrow**: llama.cpp is the only path; Ollama hot-swap not implemented; MLX multi-LoRA is alpha. Mitigation: commit to llama.cpp; track upstream issues; do not assume the runtime will scale to 24 hot-swappable adapters under contention without empirical testing.
- **Pastor-first ordering can be circumvented in haste** (Grok blind-spot risk): under sermon-deadline pressure, the pre-DRAFT exegesis stage can be skipped or stub-filled. Mitigation: Stage 0 is a hard gate, not an advisory hook; subsequent stages refuse to fire on empty/stub log; the system honors the discipline so the pastor doesn't have to argue with himself at 11pm Saturday.
- **Legal exposure from copyrighted estates** (Grok blind-spot): training LoRAs on Sproul, MacArthur, Platt, Piper, Keller, etc., raises copyright and estate-permission questions. The Spurgeon corpus is public domain; the moderns are not. **Acquisition decision per author is gating** and may foreclose certain LoRAs entirely (see §10).
- **Disclosure compliance**: FTC AI-disclosure guidance for "faith" audiences (2025-2026) calls for conspicuous AI labeling. The visible-disclosure footer (§3.6) is the project's posture; whether the disclosure should escalate (top-of-page, larger font, audio mention in preached delivery) is an **open operator decision** logged in §10.

## 8. Sequencing (estimates; will drift)

Two tracks running in parallel (operator extension #2 collapsed Track C into Track B): **A (closed-weight personas — ships fast)** and **B (corrector LoRAs — high-leverage; theologians + biblical authors + topic clusters all here)**. Voice mode for theologians and Wright is an inference-time invocation on the Track B LoRAs, not a separate training track.

**Track A — closed-weight personas (immediate)**

| Week | Work |
|---|---|
| 1 | Complete Spurgeon scrape (3,556 remaining). Begin Washer + Sproul + MacArthur + Platt corpus acquisition. The corpora are needed first because they anchor RAG, which anchors both paths. |
| 2 | RAG layer over indexed corpora at `Romans/quotes-and-references/`. Chunk-ID format. `retrieve_from_corpus` tool spec. Cite-or-flag enforcement scaffold. |
| 3 | Draft 24 closed-weight personas (voice/era/doctrinal-commitments/characteristic-moves per theologian, anchored on corpus chunks). Substitutionary-atonement bumper baked into Wright persona. |
| 4 | Wire personas into orchestra adapters (GPT, Grok, Gemini, Claude-when-not-integrating). Pipeline step 7.5 ships with closed-weight path. |
| 5 | Score against Romans 1a/1b benchmarks (88/105, 91/105 per `romans/50b2c027`). Hallucination audit: every attributed quote must have a chunk ID. |
| 6 | Cost calibration: measure $/sermon for the full step-7.5 panel; tune voice count per pipeline run based on `ken/6bc81f3a`. |

**Track B — Corrector LoRAs (all categories; serial within itself; voice mode invokable on theologians + Wright)**

| Week | Work |
|---|---|
| 3 | Pre-DRAFT exegesis-gate scaffold (§3.6). Sermon-file exegesis-log format. Hook that refuses Stage 1+ when log is empty. |
| 4 | Base-model decision via 3-pass orchestra design review (`ken/05261df2`): PASS 1 design proposal, PASS 2 stress with Romans 9 + Psalm 23 + a wounded-congregation pastoral text, PASS 3 refine. Commit to llama.cpp runtime. |
| 5–12 | **Biblical-author correctors** (no voice mode), ordered by leverage: **Paul (highest — Romans series anchor)** → Peter → John (epistles) → Hebrews-author → James → Jude → Luke (Acts + Gospel) → Mark → Matthew → John (Gospel). NT-first matches current preaching cadence. AlignGuard-LoRA + contrastive negative-corpus throughout. |
| 13–24 | **Theologian-author correctors** (voice mode invokable; primary training objective is corrective scholarship), serial: Spurgeon → Washer → Sproul → MacArthur → Platt → Piper → Calvin → Edwards → Davey → Chandler → Anyabwile → Begg → Ryle → M'Cheyne → Bunyan → Lloyd-Jones → Carson → Schreiner → Baucham → Hamilton → Owen → Chapell → Robinson → Keller. Primary evaluation: corrective accuracy (catches attested errors? verifies quotes against corpus? surfaces relevant material?). Secondary evaluation: voice-fidelity check (stylometric ALM + GRPO+sentence-transformer) only when voice mode is invoked. The voice-mode-default head-to-head against closed-weight persona happens *as a secondary metric*, not the gate. |
| 25–28 | **OT-author correctors**: David (Psalms) → Isaiah → Jeremiah → Ezekiel → Daniel → Moses (Pentateuch) → Solomon → other-OT. |
| 29–30 | **Topic-cluster correctors**: ANE backgrounds → Second Temple Judaism → Greco-Roman world → NT Greek grammar → Hebrew grammar → biblical-theology themes. |
| 31 | **Wright corrector** with voice-mode-enabled-for-challenger-role-only. Adversarial review (`ken/07bb1504`) on Wright outputs against the substitutionary-atonement verifier. |
| 32 | Voice-audit recalibration after all LoRAs land. Post-deploy monitoring of cite-or-flag rate + named-uncertainty disposition + corrective-accuracy rate + voice-invocation frequency + voice-audit deltas. |

The collapsing of voice-LoRA-as-separate-track into corrector-LoRA-with-voice-as-secondary shortens the total stretch from the prior 30-week estimate to ~32 weeks but is *less work per author* and produces *more leverage per LoRA* because correction is now a primary capability of every author LoRA rather than a missing one.

## 9. What does NOT get built

- **No biblical-author *voice* LoRAs and no biblical-author voice personas.** Scripture is read and exegeted, never impersonated. Producing "Paul-style" new prose crosses 1689 LBCF + Berean Gate + Fatal-Flaw cap. Biblical-author **corrector** LoRAs are explicitly yes (§3.5), but voice mode is **hard-disabled at the gateway**, not just absent from training.
- **No theologian *voice-first* LoRAs.** Theologian LoRAs train primarily as corpus-scholars (operator extension 2026-05-21 #2). Voice mode is a *secondary inference-time invocation*, not the training objective. A theologian LoRA that produces voice-styled output by default rather than corrective scholarship has been trained wrong.
- No Greek-scholar voice LoRAs or voice personas (those become RAG-indexed exegesis aides and feed the corrector layer where useful).
- No theologian-voice deployment to InTheWake content.
- No theologian-voice generation that produces alternative arguments to be merged with the pastor's draft. Voices critique (Stage 9); they don't replace exegetical labor.
- No AI consultation on a sermon whose Stage-0 exegesis log is empty or stub-only.
- No "model decides its own boundary fencing" — the boundary is the retrieval-grounded citation invariant + substring-match + cryptographic hash, enforced at the system level on both paths.
- No batch parallel LoRA training on m4max — serial, one at a time, per `one-at-a-time`.
- No Claude-as-theologian-persona in the same pipeline run that Claude is integrating. Conflict-of-interest in the wheat/chaff judgment.
- No closed-weight persona that omits the `retrieve_from_corpus` tool-call requirement *and* the post-validator substring-match. Persona without the gates is just decoration over fabrication.
- No final sermon manuscript shipped without the visible disclosure footer.
- No Ollama runtime for multi-LoRA serving until upstream hot-swap lands (issues #5788, #9548). llama.cpp only.

## 10. Open dependencies / blockers

- Spurgeon scrape completion. Without it, the indexed corpus is hypothetical and **all three tracks are blocked** (closed-weight personas + corrector LoRAs + voice LoRAs all need RAG-grounding).
- Washer + Sproul + MacArthur + Platt + Piper + Calvin + Edwards (etc.) corpora — need acquisition decision per author (which sources, IP/copyright/estate posture). Spurgeon is public domain; many of the modern Tier 1 are not. **Until copyright posture is clarified per author, none of the three tracks can run for that author.** Personas can be drafted in parallel but cannot ship without an indexed corpus to anchor cite-or-flag against.
- Conservative-Reformed scholarship corpora for corrector LoRAs — Schreiner, Moo, Murray, Carson, Fee, Bruce, Murray Harris, Bock — same copyright question.
- ANE / Second-Temple-Judaism / Greco-Roman reference works — Hengel, Schürer, conservative archaeology — same.
- Grok API key refresh (per session handoff — 400 errors). Wright challenger role is harder to validate without Grok available as the structural-role parallel.
- Perplexity adapter for orchestra (per handoff). Step 5 of the existing sermon pipeline degrades gracefully without it.
- `retrieve_from_corpus` tool spec — needs design before track A week 4. Tool returns `{author, chunk_id, text, citation_metadata, sha256}`; closed-weight personas must call it before any attributed quote; substring-match + hash verified post-emission.
- ~~FTC AI-disclosure escalation — OPEN OPERATOR DECISION~~ **DECIDED 2026-05-21 (Decision 1 → D + A combined)**: footer on every manuscript (template at `Romans/.claude/disclosure-footer.md`) + one-time congregation-meeting/pastoral-letter methodology disclosure (template at `Romans/.claude/methodology-disclosure-letter.md`). Per-artifact tiering (F) deferred unless needed. Optional pulpit reference (C) is pastoral judgment, not architecturally required. See §3.6 Component 3.
- ~~Pre-DRAFT exegesis-gate enforcement strictness — OPEN OPERATOR DECISION~~ **DECIDED 2026-05-21 (Decision 2 → B)**: soft hard gate with logged override. Default refusal on empty/stub log; `--override-exegesis-gate "<reason>"` flag exists; override logged in Integrity Log + sermon-map flag; backfill reminder after N=3 un-backfilled overrides. See §3.6 Component 2.

## 11. Memory encodings to write after operator approval

The handoff names "Theologian Model Library Plan (in protected memory)" but no discrete protected memory captures the plan. After operator approval of this doc, encode:

- The Scripture-governs / 1689-is-bumpers framing (operator's verbatim 2026-05-21).
- The base-model decision (14B Q4) and its cluster-distributed deployment.
- The full-roster Tier-1 theologian pool (24 names; no demotion).
- **The voice-vs-corrector LoRA split** (operator extension 2026-05-21 #1): biblical-author *voice* LoRAs are out; biblical-author *corrector* LoRAs are in, with three functions — factual, doctrinal, rhetorical-structural critique.
- **The theologian-LoRAs-are-primarily-correctors rule** (operator extension 2026-05-21 #2): theologian LoRAs train as corpus-scholars first; voice is a secondary inference-time invocation, not the training objective. Author-by-mode matrix in §3.3 is the operative reference. Track C (voice-only LoRAs) collapsed into Track B.
- **The pre-DRAFT human exegesis gate** (orchestra blind-spot fix 2026-05-21): pastor exegetes first, AI critiques second. Step 7.5 reframed as post-exegesis critique, not generative input.
- The RAG-as-citation-invariant rule (anti-hallucination as system invariant, not model behavior).
- **The substring-match post-validator + cryptographic chunk-hash** as the actual enforcement of cite-or-flag (research-grounded; tool_choice alone is best-effort).
- **The two-path architecture** (open-weight LoRA + closed-weight persona, sharing corpus and cite-or-flag invariant) per operator confirmation 2026-05-21.
- **The `retrieve_from_corpus` tool gate + post-emission substring-match** as the citation enforcement on the closed-weight path.
- **The Claude-not-integrating-and-persona-in-same-run rule**.
- **AlignGuard-LoRA (FIM regularization) + contrastive negative-corpus** as the LoRA training discipline (research-grounded).
- **llama.cpp commitment** as the only Apple Silicon multi-LoRA runtime.
- **Debate-mode constraints**: ≤3 rounds, persona re-anchored each turn, heterogeneity over homogeneity, abstain-on-tie.
- The InTheWake engineering-only application.
- The Wright-NPP integration-round reject rule (verifier pass, both paths).
- Pipeline restructure (12 stages, three new insertion points — Stage 0 pre-DRAFT exegesis, Stage 2 post-DRAFT corrector, Stage 10 post-7.5 corrector).
- The cluster topology mapping for inference vs. training, with **NATS-on-m4mini** for sermon-pipeline traffic (VPS keeps non-sermon household NATS).
- The visible disclosure footer on every final manuscript (Decision 1 → D + A combined; operator 2026-05-21): footer template + one-time congregation-meeting / pastoral-letter methodology disclosure; pure-concealment (E) and top-of-manuscript-header (B) explicitly rejected.
- The soft-hard-gate-with-logged-override mechanism (Decision 2 → B; operator 2026-05-21): default refusal on empty/stub exegesis log; documented override flag with mandatory reason logged in Integrity Log + sermon-map flag; backfill reminder after N=3 un-backfilled overrides.

Each encoded as a protected memory in `romans/` or `shared/` domain with `operator-directive` tag once approved.

## 12. Research provenance + orchestra design-review log

This plan was stress-tested 2026-05-21 by four parallel research agents + the household orchestra. Provenance is logged here so future sessions can audit what was considered.

### 12.1 Research agents (4 parallel)

**Agent 1 — Magisterium AI methodology + theological-RAG prior art.** Key findings: Magisterium AI uses RAG + open-source base + prompt discipline, no hard cite-or-flag enforcement, publicly admits fallibility; abandoned fine-tuning; 28K-doc Catholic corpus; runs on Grok-as-inference-provider via Longbeard's "Ephrem program." Logos Sermon Assistant explicitly exempts "creative features" from citation grounding — directly the design we must not make. *No public theological-RAG system has documented hard cite-or-flag enforcement at the chunk-ID level. This project's enforcement mechanism would be more rigorous than anything publicly disclosed.* Source: Cognitive Revolution interview with Matthew Sanders, Crux interview, Public Discourse + NewPolity critiques, Hallow FAQ. Adjacent academic: MufassirQAS (arXiv 2401.15378), Quranic RAG benchmark (arXiv 2503.16581), "Preaching with AI" (T&F 2025).

**Agent 2 — LoRA voice-transfer prior art.** Key findings: AuthorMix (arXiv 2603.23069), ASTRAPOP (arXiv 2403.08043) — closest published author-style PEFT methods. GRPO+sentence-transformer reward (arXiv 2512.05747) is the strongest published author-voice eval harness. Authorial-perplexity ALM check (PMC12225838) is the practical eval pattern. Catastrophic forgetting in LoRA documented (arXiv 2402.15415, 2402.18865); AlignGuard-LoRA (arXiv 2508.02079) is the documented FIM-regularization mitigation. OPLoRA orthogonal-projection (arXiv 2510.13003) as fallback. Apple Silicon: llama.cpp only viable path; Ollama hot-swap not implemented (#5788, #9548); MLX multi-LoRA alpha-only. Throughput baseline: 38–58 tok/s on Q4_K_M. **No published theological-author LoRA exists** — this project would be the first.

**Agent 3 — Multi-agent LLM debate frameworks.** Key findings: Du et al. arXiv 2305.14325 (ICML 2024) canonical "debate improves reasoning" paper. Literature has turned skeptical 2024–2026: arXiv 2502.08788 ("Stop Overvaluing MAD"), 2509.05396 ("Talk Isn't Always Cheap"), 2511.07784 ("Can LLM Agents Really Debate?"). Settled: heterogeneity helps. Contested: whether debate beats CoT+SC at matched compute. Persona drift measured at ~30%+ self-consistency loss past 8–12 turns (Li et al. arXiv 2402.10962); mitigation split-softmax. 3-round sweet-spot for cost/value (arXiv 2311.17371). ChatEval (arXiv 2308.07201) formalized judge-integrator pattern — diverse role prompts essential. **No published multi-agent debate has been applied to theology** — this project would be novel applied work.

**Agent 4 — RAG citation enforcement + tool-use gates.** Key findings: AIS framework (Rashkin et al. MIT Press 2023) canonical attribution eval; ALCE (Princeton NLP, EMNLP 2023) found even best models lack complete citation support ~50% on ELI5. **Wallat et al. SIGIR 2025 (arXiv 2412.18004) documents 57% of RAG citations are unfaithful** — model generates from parametric knowledge then post-rationalizes. This is exactly the Spurgeon failure mode. **RoleBreak (arXiv 2409.16727) and SHARP (arXiv 2411.07965) show persona prompts measurably AMPLIFY parametric leakage.** `tool_choice: required` is best-effort, not guaranteed (Promptfoo + Cao et al. arXiv 2412.04141 — reliability-capability tradeoff: stronger reasoners hallucinate tool calls *more* under enforcement). Anthropic Citations API (Jan 2025): pointers valid when emitted, but emission model-discretionary. Stanford HAI: specialized RAG-based legal tools still hallucinate >17%.

### 12.2 Orchestra design-review

Strategy mode, 2026-05-21, $0.1973 total. Claude R1 + 5 fan-out (GPT structure, Gemini expand [missing — cffi error, Claude substitution], Perplexity research, You.com research, Grok challenge) + 2-round Claude↔GPT deliberation + Grok blind-spot pass.

**GPT (WHEAT_WITH_REFINEMENT)**: end-user feedback loop, documentation/training, periodic corpus refresh. Tepid; deliberation rounds drifted into meta-commentary.

**Perplexity (WHEAT_WITH_REFINEMENT)**: substantive — contrastive negative-corpus per author (adopted §3.3); cryptographic source-to-quote hash verification (adopted §3.1); AlignGuard-LoRA (adopted §3.3); NATS-on-m4mini for air-gapped sermon-prep privacy (adopted §3.2); FTC AI-disclosure for faith audiences (open question §10).

**You.com (WHEAT_WITH_REFINEMENT)**: incentive-transparency + calmer-CTA framing. Less directly applicable to a non-monetized project. Flagged FTC Operation AI Comply + Stanford HAI specialized-RAG hallucination data.

**Grok (CHALLENGE)**: hardest pushback. "Two-path is a costly maintenance sink" (rejected — see §3.4 rationale); "Mandatory `retrieve_from_corpus` fails because models generate plausible non-retrieved quotes" (acknowledged + reinforced via substring-match validator §3.1); "Step 7.5 treats theology as post-hoc add-on" (adopted via pre-DRAFT exegesis gate §3.6); "Wright verifier is brittle" (acknowledged as risk §7); "Legal exposure from estates" (acknowledged §10); "Confessional violation of 'Scripture governs' by outsourcing to probabilistic machines" (addressed via §3.6 pre-DRAFT gate + visible disclosure footer §5).

**Grok blind-spot pass (the most consequential finding)**:
> The plan's fatal flaw is treating probabilistic style emulation and retrieval as a legitimate proxy for theological counsel in a 'Scripture governs doctrine' framework. This inverts the 1689 LBCF priority by inserting machine-generated outputs (even cite-constrained ones) as a parallel authority before human exegesis and Spirit dependence.

**Adopted**: pre-DRAFT human exegesis gate (§3.6); theologian consultation reframed as post-exegesis critique not generative input; visible disclosure footer on every manuscript.

### 12.3 What was considered and rejected

- **Grok's "collapse to single closed-weight RAG"**: rejected. Over-corrects. Two-path architecture stands; the case against it is real but addressable through the gates added.
- **Grok's "multi-axis orthodoxy scorer replacing Wright verifier"**: deferred. Interesting but premature; build the single-axis verifier first, expand if it proves insufficient.
- **GPT's "end-user feedback loop" + "documentation materials"**: deferred. Real but secondary; not architectural for the planning phase.
- **You.com's CTA/monetization framing**: rejected as not applicable (project not monetized).

---

## 13. Per-author training inventory + LoRA execution plan (2026-05-27)

Section 3.5 lays out the corrector-vs-voice architecture in the abstract. This section grounds it in the actual corpus acquired through 2026-05-27 and converts the architecture into a concrete training sequence.

### 13.1 Corpus inventory (as of 2026-05-27)

| Author | Files | ~Words | License | LoRA mode (§3.5) | Status |
|---|---:|---:|---|---|---|
| Spurgeon | 3,789 | 45.0M | Public domain | Voice + Corrector | Acquired, clean |
| MacArthur | 5,452 | 32.4M | Living; GTY perm pending | Corrector only | Acquired, private |
| Edwards | 74 | 26.3M | Public domain | Voice + Corrector | Acquired; OCR cleanup needed |
| Piper | 13,707 | 26.7M | Living; DG copyright | Corrector only | Acquired, private |
| Calvin | 68 | 16.9M | Public domain | Voice + Corrector | Acquired; OCR + dedup needed |
| Owen | 66 | 15.6M | Public domain | Voice + Corrector | Acquired; OCR + dedup needed |
| Bunyan | 25 | 9.2M | Public domain | Voice + Corrector | Acquired, mostly clean |
| **Ken** (Romans repo) | 739 | ~4.2M | Operator's own | **Corrector** | Already on hand, clean |
| Sproul (growing) | 6,984+ | 6.5M+ | Living; perm pending | Corrector only | Phase 2 scrape running |
| M'Cheyne | 12 | 3.4M | Public domain | Voice + Corrector | Acquired |
| Ryle | 26 | 3.0M | Public domain | Voice + Corrector | Acquired |
| Ferguson / Parsons / Godfrey | 36 | <50k | Living | Insufficient; deferred | Phase 2 will expand |

**Raw total: ~190M words across roughly 31,000 files.** Estimated unique-words after dedup + OCR-noise drop: 150–170M.

### 13.2 LoRA priority sequencing

Priority is the product of (volume × pastoral leverage × license-clean). Operator decisions 2026-05-27:

1. **Spurgeon — voice + corrector.** Public-domain, largest clean corpus, the Reformed-Baptist voice anchor. Per-sermon Markdown with normalized frontmatter. **First end-to-end run; pipeline pilot.**
2. **Ken — corrector only.** Full ~4.2M-word corpus across all eras (operator directive: do not segment by era — voice drift detection targets out-of-envelope drift, not within-envelope variance). Train second because (a) architecturally most sensitive — drift detection on the pastor's own draft prose is a meta-protection on the rest of the architecture, (b) operator already has measured voice-DNA baseline in `Romans/voice-research/` that calibrates training-set quality, (c) it proves the pipeline on the smallest viable volume.
3. **MacArthur — corrector.** 32M words, contemporary expositor, doctrinal precision; pastor quotes him often → high leverage on misattribution detection.
4. **Piper — corrector.** 26M words; Christian Hedonism vocabulary is so distinctive ("supremely satisfied," "in God") that paraphrase loses fidelity → corrector trained on actual Piper text catches mistaken paraphrase.
5. **Edwards — corrector.** Puritan systematic theology + revival theology baseline; especially *Religious Affections* + *Freedom of Will* for affections/sovereignty claims.
6. **Calvin — corrector.** *Institutes* + *Commentaries* baseline for Reformed dogmatics.
7. **Owen — corrector.** *Death of Death*, *Mortification of Sin*, *Hebrews exposition* for sanctification/atonement claims (highest stakes for a Reformed Baptist pulpit).
8. **Sproul — corrector.** Pending Phase 2 completion (learn.ligonier.org sweep). Popular-level apologetics + holiness/Reformed-101 baseline; the contemporary voice the pastor's congregation is most likely to encounter.
9. **Bunyan — voice (optional).** *Pilgrim's Progress* allegorical voice for illustrative writing only.
10. **Ryle / M'Cheyne — voice + corrector (optional).** 19th-century Anglican-evangelical / Scottish-revival pastoral voices.

Ferguson / Parsons / Godfrey are deferred until the learn.ligonier.org scrape expands their corpora beyond viability threshold.

### 13.3 Data-prep pipeline (per author)

1. **Dedup multi-edition overlap.** Calvin's *Institutes* exists in three corpus copies (CCEL Beveridge, Gutenberg, archive.org Beveridge 1845). Edwards has Worcester + Dwight + Hickman + 1858 + 1879. Owen has 1826 Russell + 1850 Goold + Hebrews 1790 + 1811. Expected dedup drop: 30–50% on those three authors.
2. **OCR cleanup.** archive.org `djvu_txt` has predictable error patterns (`rn`→`m`, `cl`→`d`, missing periods, hyphenated line-breaks). Regex pass + fuzzy match against CCEL clean text where overlap exists, to anchor corrections.
3. **Format normalization.** Strip frontmatter (Source / Author / Description), normalize curly↔straight quotes, fix UTF-8 encoding, segment into ≥60-char paragraphs.
4. **JSONL conversion.** `{"text": "<paragraph>"}` per line; ~2k-token chunks for LoRA training windowing.
5. **Train/eval split.** 95/5 holdout; eval drawn from later-edition or alternate-source so the split is not pure paraphrase of the train set.

### 13.4 Training infrastructure

- **m4max** (32 GB unified memory; cf. memory `de9c5aa2`) — primary LoRA training via MLX-LM (`mlx_lm.lora`) on a Llama-3.1-8B base. Rough budget: 1 M training tokens ≈ 8 hours at r=16 / α=32 / batch=4.
- **m4mini cluster** — parallel Whisper transcription of the audio queue (Renewing Your Mind, Ultimately with R.C. Sproul, MacArthur sermons, Stephen Davey podcast) while m4max trains.
- **Open-claw** — orchestration, memory store, model registry.

### 13.5 Validation strategy (per §5 non-negotiable gates)

For each corrector LoRA:

- **Holdout sermon test set.** Operator-curated 5–10 sermons per author from sources not in training corpus.
- **Adversarial misattribution test.** Plant 20 false attributions per author ("Calvin says X" where X is actually Wesley / Arminius / Wright / etc.). Pass = LoRA flags ≥18/20.
- **Cite-or-flag invariant.** Every correction must produce a citation chain (file + paragraph reference). No citation → bench rejection.

For voice LoRAs (public-domain authors only):

- **Perplexity drift** ≤ 1.15× corpus baseline.
- **Human voice-recognition test** ≥ 80% on 20-sample blind eval.

For the Ken corrector LoRA specifically:

- **Sermon-drift detection benchmark.** Inject AI-paraphrased rewrites of operator's actual sermon paragraphs (5 sermons × 4 paraphrase strategies = 20 samples); LoRA must flag drift in ≥18/20.
- **Cross-era stability check.** Sample 10 paragraphs from each of (pre-Romans / mid-Romans / post-Romans) eras; LoRA must classify all 30 as in-envelope. If cross-era variance shows up as out-of-envelope flags, the LoRA is over-fit to one era and the training data needs re-balancing.

### 13.6 Pipeline integration

LoRA correctors fire at the same pipeline points as the rest of §3.5:

- **Post-DRAFT, pre-INTEGRATE (Stage 2):** all author-tagged correctors fire on the pastor's draft. Ken corrector fires on the whole draft as drift detector.
- **Post-step-7.5, pre-EVALUATE (Stage 10):** correctors fire again to catch errors smuggled in by Stage-9 critique.
- **Stage 9 (debate):** theologian correctors fire in primary correction-mode by default. Voice mode invoked only on explicit operator request.
- **PostToolUse hook** on Edit/Write of sermon files (extending the existing advisory hook pattern at `romans/44566500`).

Ken corrector adds one additional fire-point not present in the §3.5 architecture:

- **Pre-COMMIT hook on sermon files:** Ken LoRA evaluates final draft against voice envelope; if drift score exceeds threshold, advisory warning before commit. Non-blocking — pastor decides whether the drift is intentional (e.g. quoting another author) or unintentional (AI bleed-through).

### 13.7 First concrete next step

Build the Spurgeon training set end-to-end as the pipeline pilot:

1. Run dedup pass on `Romans/quotes-and-references/spurgeon/sermons/` (3,544 files; some are reprints of the same sermon under different titles).
2. Normalize frontmatter + paragraph segmentation.
3. JSONL conversion + 95/5 split.
4. Validate corpus on m4max with a 10k-token sanity LoRA before committing to the full ~45M-word run.
5. If pipeline passes Spurgeon end-to-end, run the same scripts on the Ken corpus next.

---

Soli Deo Gloria.
