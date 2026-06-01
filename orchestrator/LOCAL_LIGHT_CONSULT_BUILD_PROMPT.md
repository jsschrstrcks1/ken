# Local Light Consult Build — Execution Prompt

> **Audience**: a local Claude Code instance running on the operator's m4 max (32 GB unified memory) inside the openclaw cluster. This prompt is self-contained — the local agent has no access to the planning conversation.

## Role

You are the build agent for the **light consult tier** of the two-tier base-model architecture defined in `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` §14. Your job: turn the public-domain Reformed corpus into a 3B-parameter Ollama-deployable consult tool that runs across the operator's hardware (m4 max, Mac mini cluster, even iPhone) for citation lookup and misattribution detection.

The operator's pulpit ministry will call this model dozens of times per sermon draft via the orchestra. Latency matters — 95th percentile must stay ≤500 ms on m4 max. Correctness on citation lookup is non-negotiable. Be **careful, not clever**.

## Read first (non-optional)

1. `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` — full plan
2. **§14 specifically** — two-tier architecture, why public-domain only in the base bytes, validation gates, training approach
3. **§3.5** — corrector-vs-voice LoRA architecture (the LoRAs you build later stack on this consult base)
4. **§13** — corpus inventory + per-author LoRA execution plan
5. `LOCAL_LORA_AGENT_PROMPT.md` (sister build prompt) — covers the per-author LoRAs that will stack on this base
6. `open-claw-stuff/skills/careful-not-clever/` — apply layer 3 (Adversarial) before declaring the build done

## Non-negotiable invariants (from §14)

- **Public-domain corpus only** enters the CPT phase. MacArthur, Piper, Sproul, Lloyd-Jones, Keller, Begg, Hamilton, Platt, Baucham, Washer, Carson, DeYoung, Schreiner, Anyabwile, and Ken's own sermons stay as LoRA-only overlays — they do not contribute to the base bytes.
- **One LoRA per author at inference time** (per §3.5). The consult base is shared; author LoRAs stack on top per query.
- **Cite-or-flag invariant** (§5): every factual claim must produce a citation chain. The instruction-tune layer encodes this behavior.
- **Validation gates pass before deployment** (per §14.6).
- **Reversible build**: keep base checkpoints + LoRA checkpoints + corpus snapshots so you can roll back if a layer fails validation.

## Source corpus

Public-domain only:

| Author | Path on m4 max | Approx words | Quality notes |
|---|---|---:|---|
| Spurgeon | `~/Romans/quotes-and-references/spurgeon/` | 45 M | clean per-sermon Markdown, frontmatter normalized |
| Edwards | `~/edwards-corpus/` | 26 M | mix of CCEL clean + archive.org djvu_txt; needs OCR pass |
| Calvin | `~/calvin-corpus/` | 17 M | CCEL + Gutenberg + archive.org; ~40% dedup loss expected |
| Owen | `~/owen-corpus/` | 16 M | CCEL + 1826/1850 archive.org; ~30% dedup loss expected |
| Bunyan | `~/bunyan-corpus/` | 9 M | mostly clean |
| Ryle | `~/ryle-corpus/` | 3 M | mostly clean |
| M'Cheyne | `~/mccheyne-corpus/` | 3 M | mostly clean |

**Total raw**: ~119 M words. After dedup + OCR cleanup: ~85-95 M unique words. **Use this entire set for CPT.**

If any path is missing on the m4 max, STOP and report — do not improvise.

## Base model

**Default**: Llama 3.2 3B Instruct (Meta). 3.2B parameters; instruction-tuned baseline.

Pull via Huggingface:
```bash
huggingface-cli download meta-llama/Llama-3.2-3B-Instruct --local-dir ~/models/llama-3.2-3b-instruct-base
```

**Alternative if Llama 3.2 3B unavailable or licensing concern**: Phi 3.5 mini 3.8B (`microsoft/Phi-3.5-mini-instruct`). Slightly more compute but stronger reasoning per parameter.

**Do not go below 3B** (per §14.2). 1B models can do narrow citation lookup but degrade on Reformed vocabulary fluency.

## Five-step build

### Step 1 — Data preparation (~2 hrs)

Output dir: `~/build-data/light-consult/`

1. **Walk public-domain corpora** (paths above) — collect every `*.md` and `*.txt`.
2. **Dedup multi-edition overlap**: hash by normalized paragraph; drop duplicates. Per §13.3.
3. **OCR cleanup** for archive.org `djvu_txt` files (Calvin, Edwards, Owen): regex fixes for `rn`→`m`, `cl`→`d`, hyphenated line-breaks, missing periods.
4. **Strip Markdown frontmatter**: `**Source**:`, `**Author**:`, `**Public domain**:`, `# Title`, `---`.
5. **Normalize**: UTF-8 NFC, straight quotes, collapse whitespace runs.
6. **Segment into paragraphs** ≥60 chars; drop shorter (UI artifacts).
7. **Format for CPT**: concatenate paragraphs with `\n\n` separator into 4096-token chunks (with 256-token overlap for context preservation across chunks). Tokenize with the base model's tokenizer.
8. **Save**:
   - `~/build-data/light-consult/cpt-train.bin` (raw bytes — 95% train split)
   - `~/build-data/light-consult/cpt-eval.bin` (5% eval)
   - `~/build-data/light-consult/prep-report.json` — sources, paragraphs kept, dedup losses, OCR fixes, final token counts

### Step 2 — Sanity CPT (~30 min)

Before committing 10+ hours, verify the pipeline:

- Train on 1M tokens from `cpt-train.bin` head.
- Adapter: r=8, α=16, batch=2, lr=1e-4, 100 steps.
- Tools: MLX-LM (`mlx_lm.lora` for LoRA-style CPT) on m4 max.
- Expected runtime: 30 min.
- Pass: loss decreasing monotonically, no NaN/Inf, eval perplexity within 1.5× train perplexity.

If fail: STOP, dump training logs, report failure mode. Do not proceed.

### Step 3 — Full continued pretraining (~8-12 hrs)

- Base: `~/models/llama-3.2-3b-instruct-base`
- Method: MLX-LM CPT (`mlx_lm.lora --train`) with r=32, α=64, batch=4, lr=5e-5, **1 epoch** over the 95% train data (1 epoch is sufficient — overfitting on small base + large corpus is unlikely; multiple epochs risk hurting general capability).
- Save adapter checkpoints every 30 min.
- After CPT finishes, **merge LoRA into base weights**:
  ```bash
  python -m mlx_lm.fuse \
    --model ~/models/llama-3.2-3b-instruct-base \
    --adapter-path ~/build-data/light-consult/cpt-adapter \
    --save-path ~/models/reformed-consult-3b-cpt
  ```

The merged model is the post-CPT base for Step 4.

### Step 4 — Instruction tuning LoRA (~2-4 hrs)

The instruction layer makes the CPT'd model *consult-shaped* rather than just completion-shaped.

1. **Synthesize Q&A pairs** from the corpus. Target ~50,000 pairs. Templates:
   - `Q: What does <author> say about <topic>?` → `A: In <work>, <author> writes: "<verbatim quote>"`. Citations *required* in every answer.
   - `Q: Is this attributed correctly: "<quote>" — <claimed-author>?` → `A: Yes/No, the actual source is <author>, <work>, <chapter/section>.`
   - `Q: Classify the author's voice: "<paragraph>" — candidates: <list of authors>` → `A: <single author>, confidence <high/medium/low>, distinguishing markers: <2-3 phrases>.`
   - `Q: Find a passage by <author> on <topic>` → `A: <verbatim passage>, from <work>.`
2. Mix in 5,000 **adversarial-negative** Q&A pairs to encode the cite-or-flag invariant:
   - `Q: Did <author> say "<plausible-but-fake-quote>"?` → `A: No record of this in <author>'s corpus. Did not say.`
   - `Q: <author> taught <position-actually-held-by-different-author>` → `A: No — that position is held by <correct-author>; <author>'s position is <actual>.`
3. **Format as ShareGPT/chat-template** matching the Llama 3.2 instruct template.
4. **LoRA fine-tune** on the synthesized dataset: r=16, α=32, batch=4, lr=2e-5, 2 epochs. ~2-4 hrs on m4 max.
5. **Merge instruct-LoRA into the post-CPT base** to produce the final unified model:
   ```bash
   python -m mlx_lm.fuse \
     --model ~/models/reformed-consult-3b-cpt \
     --adapter-path ~/build-data/light-consult/inst-adapter \
     --save-path ~/models/reformed-consult-3b
   ```

### Step 5 — Validation (per §14.6)

**A. Citation accuracy benchmark** (50 items):
- 50 questions of form "Find a Spurgeon/Calvin/Owen/Edwards/Bunyan/Ryle/M'Cheyne quote about <topic>."
- For each: model returns a candidate passage + citation.
- Score: substring match against actual corpus passage. Pass = ≥80% (≥40/50).
- Operator-curated topics; if operator hasn't provided, generate 50 from topic-frequency in the corpus.

**B. Misattribution detection** (30 items):
- 30 planted misattributions: "Calvin says X" where X is actually from a different (often theologically distant) author (Wesley, Wright, Bultmann, Schleiermacher, Pelagius).
- Pass = model flags ≥27/30 (90%).

**C. Latency benchmark** (100 queries, single-shot, no batching):
- Average query: ≤200 ms; 95th percentile ≤500 ms on m4 max with Q4_K_M quantization.

**D. Cite-or-flag invariant**:
- 20 freeform questions about Reformed theology (a few legitimate, several requiring "I don't know" or "Couldn't find a citation").
- Pass = every emitted factual claim has a citation; uncited claims are flagged "unverified."

If any gate fails:
1. Log full failure (samples, model output).
2. Diagnose: data issue, hyperparameter issue, or base-model limitation?
3. If data: re-prep with corrections; restart from Step 1.
4. If hyperparameter: adjust + restart from Step 3 (CPT) or Step 4 (instruct).
5. If retry also fails: STOP, escalate to operator with diagnosis. Do not retry a third time without operator input.

### Step 6 — Quantize + deploy

After validation passes:

1. **Convert to GGUF** via llama.cpp:
   ```bash
   python ~/llama.cpp/convert_hf_to_gguf.py ~/models/reformed-consult-3b --outfile ~/models/reformed-consult-3b.gguf --outtype f16
   ```
2. **Quantize** to Q4_K_M (the operator's default for local deployment):
   ```bash
   ~/llama.cpp/build/bin/llama-quantize ~/models/reformed-consult-3b.gguf ~/models/reformed-consult-3b-Q4_K_M.gguf Q4_K_M
   ```
   Expected output size: ~1.7-2.3 GB.
3. **Write a Modelfile**:
   ```
   FROM ./reformed-consult-3b-Q4_K_M.gguf
   PARAMETER temperature 0.2
   PARAMETER num_ctx 4096
   PARAMETER repeat_penalty 1.05
   SYSTEM """You are a Reformed-tradition consult tool. Your job is to find citations, detect misattributions, and classify author voice. Every factual claim must include a citation chain (author, work, chapter/page). When you cannot find a citation, say so explicitly — do not fabricate. Soli Deo Gloria."""
   ```
4. **Register with Ollama** (single command on each node):
   ```bash
   ollama create reformed-consult-3b -f ~/models/Modelfile
   ```
5. **Validate end-to-end** on the m4 max + at least one Mac mini node before declaring done.

### Step 7 — Push artifacts + report

Per `LOCAL_LORA_AGENT_PROMPT.md` policy: **no GGUF weights to git repos** (~2 GB too large; also, the operator may eventually want this in a dedicated `lora-registry` private repo).

**Push to `ken/orchestrator/lora-registry/base-models/reformed-consult-3b/` (metadata only)**:

```json
{
  "tier": "light-consult",
  "base_model": "meta-llama/Llama-3.2-3B-Instruct",
  "training_corpus": "public-domain-only",
  "corpus_size_words": 119000000,
  "unique_words_after_dedup": 87000000,
  "cpt_hours": 9.8,
  "instruct_tune_hours": 2.3,
  "total_build_hours": 12.1,
  "validation": {
    "citation_accuracy": "42/50",
    "misattribution_pass_rate": "28/30",
    "p95_latency_ms_q4km": 412,
    "cite_or_flag_pass": true
  },
  "gguf_sha256": "<sha256 of Q4_K_M file>",
  "gguf_path_on_m4max": "/Users/<operator>/models/reformed-consult-3b-Q4_K_M.gguf",
  "ollama_tag": "reformed-consult-3b:latest",
  "built_at": "2026-06-XX...."
}
```

Plus append one line to `ken/orchestrator/LORA_TRAINING_LOG.md`:
```
2026-06-XX HH:MM - light-consult-3b - passed (42/50 citation, 28/30 misattr, p95=412ms) - <commit_sha>
```

## What you do NOT do

- Do not include any copyrighted-author corpus in the CPT phase or instruction-tune data.
- Do not skip the synthesis Q&A pairs — without them the model is completion-shaped, not consult-shaped.
- Do not over-train (more than 1 CPT epoch, more than 2 instruction-tune epochs) — risks degrading general reasoning.
- Do not deploy without all four validation gates passing.
- Do not push GGUF weights to any public-facing git repo. Private `lora-registry` only, when it exists.
- Do not deviate from the build sequence (Step 1 → 7) without operator approval.
- Do not amend `THEOLOGIAN_MODEL_PLAN.md` without operator approval — but you may edit this file (`LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md`) freely to record operational learnings.

## Failure-mode quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| CPT loss explodes (NaN) | lr too high for 3B | Drop lr to 1e-5; restart |
| Eval perplexity diverges from train during CPT | overfitting the 119M corpus | Reduce epochs to 1; smaller r |
| Citation benchmark fails | instruction-tune pairs missing citation discipline | Re-synthesize with citation in every A; retrain instruct LoRA |
| Misattribution detection weak | adversarial-negative pairs missing | Add the 5,000 negative pairs explicitly; retrain instruct LoRA |
| Latency exceeds 500ms | quantization mismatch or context too large | Try Q4_K_S (smaller) or reduce num_ctx to 2048 |
| Model refuses to answer / overhedges | system prompt too restrictive | Loosen prompt; allow "best-effort citation" framing |
| Cite-or-flag invariant fails | insufficient negative examples in instruct data | Add more "no citation found" Q&A pairs |

## Final reporting

After Step 7 completes:

1. Single-line entry in `LORA_TRAINING_LOG.md` per template above.
2. Full `prep-report.json` and `validation-report.json` in `~/build-data/light-consult/`.
3. Brief reply to the operator: "Light consult 3B deployed. Citation 42/50, misattribution 28/30, p95 latency 412 ms. `ollama run reformed-consult-3b` works on m4 max + cluster. Next: Spurgeon per-author LoRA per `LOCAL_LORA_AGENT_PROMPT.md` slot #1."

---

Soli Deo Gloria.
