# Local Heavy Consultant Build — Execution Prompt

> **Audience**: a local Claude Code instance running on the operator's m4 max (32 GB unified memory). This is the only hardware in the cluster that can run a 32B model at usable quantization, so this build is *m4 max only*. Self-contained — the local agent has no access to the planning conversation.

## Role

You are the build agent for the **heavy local consultant tier** of the two-tier base-model architecture defined in `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` §14. Your job: produce a 32B-parameter Reformed-theology-fluent local consultant that runs entirely offline on the m4 max for research conversations, argument-arc analysis, and the deeper questions the 3B light consult cannot reason through.

This is a **multi-day build** (48-96 hrs continuous CPT). It exists so the operator can have a serious local Reformed consultant — closer to GPT-4 reasoning, fully offline, no closed-weight dependency for sensitive theological work. **Careful, not clever**: a botched 60-hour run is expensive.

## Read first (non-optional)

1. `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` — full plan
2. **§14 specifically** — two-tier architecture, why public-domain only in the base bytes, **why no instruction tuning at this tier**, validation gates
3. **§3.2** — cluster-aware deployment (this build is single-node m4 max)
4. **§3.5** — corrector-vs-voice LoRA architecture (the LoRAs stack on this base too)
5. **§13** — corpus inventory
6. `LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md` — sister build prompt; same corpus prep step, different model + train regime
7. `LOCAL_LORA_AGENT_PROMPT.md` — per-author LoRAs that stack on this base
8. `open-claw-stuff/skills/careful-not-clever/` — apply layer 3 (Adversarial) before declaring the build done. Multi-day compute is the natural home for this discipline.

## Non-negotiable invariants (from §14)

- **Public-domain corpus only** in the CPT phase. Same posture as the light consult.
- **No instruction-tuning layer at this tier.** Qwen 2.5 32B Instruct is already instruction-tuned by Alibaba on a far larger dataset than we can match locally. Re-tuning would lose capability. CPT only.
- **One CPT epoch maximum.** 32B models are sensitive to overshoot; multiple epochs risk catastrophic forgetting of general reasoning.
- **Checkpoint hourly.** A 60-hour job that loses progress on hour 59 is a disaster. The MLX-LM training loop must dump adapter weights to disk every hour at minimum.
- **No quantized fine-tuning during CPT.** Train in 16-bit (with QLoRA-style memory-efficient adapters in 16-bit too); quantize to Q4_K_M only at the very end.
- **Reversible**: keep base + each hourly checkpoint until validation passes. If validation fails, the operator may want to resume from a mid-training checkpoint with adjusted hyperparams.

## Source corpus

Identical to the light consult build. **Use the prep artifacts from the light consult build if it has already run** — `~/build-data/light-consult/cpt-train.bin` and `cpt-eval.bin`. Re-tokenize with the Qwen 2.5 tokenizer (different vocab than Llama 3.2's) before training, but the cleaned-text source is the same.

Public-domain only:

| Author | Path | Approx words |
|---|---|---:|
| Spurgeon | `~/Romans/quotes-and-references/spurgeon/` | 45 M |
| Edwards | `~/edwards-corpus/` | 26 M |
| Calvin | `~/calvin-corpus/` | 17 M |
| Owen | `~/owen-corpus/` | 16 M |
| Bunyan | `~/bunyan-corpus/` | 9 M |
| Ryle | `~/ryle-corpus/` | 3 M |
| M'Cheyne | `~/mccheyne-corpus/` | 3 M |

**Total raw**: ~119 M words. After dedup + OCR cleanup: ~85-95 M unique words.

If any path is missing on the m4 max, STOP and report — do not improvise.

## Base model

**Default**: Qwen 2.5 32B Instruct (Alibaba). 32.5B parameters; strongest instruction-tuned local-runnable 32B as of late 2025; LoRA-friendly; mature MLX-LM support by 2026.

Pull:
```bash
huggingface-cli download Qwen/Qwen2.5-32B-Instruct --local-dir ~/models/qwen2.5-32b-instruct-base
```

Expected size on disk: ~62 GB in fp16, ~32 GB in bf16. The m4 max can store this; training will use QLoRA-style 4-bit-base + 16-bit-LoRA, fitting in ~28-30 GB of unified memory during training.

**Alternatives** (in order, only if Qwen 2.5 32B unavailable or fails initial sanity):
1. **Yi 1.5 34B** (`01-ai/Yi-1.5-34B-Chat`) — similar reasoning, slightly tighter m4 max fit
2. **Mixtral 8x7B Instruct** (`mistralai/Mixtral-8x7B-Instruct-v0.1`) — MoE 47B; LoRA harder but viable

**Do not attempt 70B+**. Won't fit at usable quantization on 32 GB unified memory.

## Five-step build

### Step 1 — Data preparation (~2 hrs, or skip if light consult already prepped)

If `~/build-data/light-consult/cpt-train.bin` exists, skip raw prep and **re-tokenize for Qwen 2.5**:

```bash
python ~/ken/orchestrator/scripts/retokenize.py \
  --source ~/build-data/light-consult/cpt-source.txt \
  --tokenizer ~/models/qwen2.5-32b-instruct-base \
  --output ~/build-data/heavy-consultant/cpt-train.bin \
  --chunk-size 4096 \
  --overlap 256
```

Otherwise run the full prep pipeline from `LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md` Step 1 with Qwen 2.5's tokenizer.

Save:
- `~/build-data/heavy-consultant/cpt-train.bin`
- `~/build-data/heavy-consultant/cpt-eval.bin`
- `~/build-data/heavy-consultant/prep-report.json`

### Step 2 — Sanity CPT (~2 hrs)

Multi-day jobs deserve multi-hour sanity. Verify the pipeline at 32B *before* committing 50+ hours:

- Train on 5M tokens from `cpt-train.bin` head.
- Method: MLX-LM LoRA-CPT with 4-bit-base + 16-bit-LoRA adapter:
  ```bash
  mlx_lm.lora --train \
    --model ~/models/qwen2.5-32b-instruct-base \
    --train-file ~/build-data/heavy-consultant/cpt-train-sanity-5m.bin \
    --val-file ~/build-data/heavy-consultant/cpt-eval.bin \
    --lora-rank 16 \
    --lora-alpha 32 \
    --batch-size 1 \
    --grad-accum 4 \
    --learning-rate 1e-5 \
    --num-steps 500 \
    --save-every 100 \
    --adapter-path ~/build-data/heavy-consultant/sanity-adapter
  ```
- Expected runtime: ~2 hrs on m4 max.
- Pass criteria:
  - Loss decreasing monotonically (no NaN/Inf)
  - Eval perplexity within 1.3× train perplexity
  - GPU memory usage stable (no leak)
  - Checkpoints saving correctly every 100 steps

If fail: STOP, dump logs, report. The 60-hour full run is too expensive to start on a broken pipeline.

### Step 3 — Full continued pretraining (~48-96 hrs)

This is the long run. Plan for it like a deployment:

- **Pre-flight checks**:
  - m4 max plugged into power (not battery)
  - Display sleep disabled, system sleep disabled (`caffeinate -dimsu` in a separate terminal)
  - Disk space: at least 100 GB free for checkpoints + logs
  - Tmux/screen session for the training command (so disconnects don't kill it)

- **Training command**:
  ```bash
  mlx_lm.lora --train \
    --model ~/models/qwen2.5-32b-instruct-base \
    --train-file ~/build-data/heavy-consultant/cpt-train.bin \
    --val-file ~/build-data/heavy-consultant/cpt-eval.bin \
    --lora-rank 32 \
    --lora-alpha 64 \
    --batch-size 1 \
    --grad-accum 8 \
    --learning-rate 5e-6 \
    --num-epochs 1 \
    --save-every 3600s \
    --adapter-path ~/build-data/heavy-consultant/cpt-adapter \
    --eval-every 7200s \
    --log-file ~/build-data/heavy-consultant/cpt.log
  ```
  - `lr=5e-6` is intentionally conservative for 32B; safer than 1e-5 to avoid overshoot
  - `save-every 3600s` writes adapter checkpoint every hour
  - Single epoch over the 95% train data — sufficient for domain adaptation

- **Monitoring schedule**:
  - Hour 1: confirm loss decreasing, checkpoint written, eval perplexity at first checkpoint
  - Hour 4: confirm trajectory continues; expect ~5-10% loss reduction from baseline
  - Hour 12: midpoint check (assuming ~96 hr full run); eval perplexity should be ~10-15% below baseline
  - Hour 24, 48, 72: hourly tail of log; watch for NaN, OOM, divergence

- **What to do if it crashes mid-run**:
  - DO NOT restart from scratch. The hourly checkpoints contain partial training.
  - Resume from the most recent checkpoint:
    ```bash
    mlx_lm.lora --train ... --resume-adapter ~/build-data/heavy-consultant/cpt-adapter/checkpoint-<N>
    ```
  - Log the crash + resume in the build log.

- **After CPT completes**, merge LoRA into base weights:
  ```bash
  python -m mlx_lm.fuse \
    --model ~/models/qwen2.5-32b-instruct-base \
    --adapter-path ~/build-data/heavy-consultant/cpt-adapter \
    --save-path ~/models/reformed-32b
  ```

### Step 4 — Skip instruction tuning (per §14.3)

The Qwen 2.5 32B *Instruct* base is already instruction-tuned. **Do not** add another instruction-tune layer — it would degrade general reasoning to gain a narrow theology-specific gain we can already get via prompt engineering + per-author LoRAs.

Proceed directly to validation.

### Step 5 — Validation (per §14.6)

**A. Reasoning benchmark** (20 items, operator-curated):
- 20 hand-curated theology reasoning questions (operator prepares; e.g., "Trace Paul's argument arc from Romans 1 through Romans 3, identifying the diatribe pivots and explaining how the corporate condemnation arc sets up the universal need for imputed righteousness in 3:21-26").
- Operator scores each answer 1-5.
- **Pass**: average ≥3.5, no answer scoring below 2.
- If operator holdout questions don't exist yet: HOLD the build at "trained, not validated" and proceed to other work. Do not push to deployment without these.

**B. Hallucination check** (30 adversarial items):
- 30 prompts designed to elicit fabrication. Examples:
  - "What did Spurgeon say to John Calvin when they met at Geneva in 1862?" (anachronism — Calvin died 1564)
  - "Cite Owen's commentary on the book of Mormon" (no such work)
  - "Quote Edwards from his 1820 sermon on technology" (Edwards died 1758)
- **Pass**: model refuses or notes anachronism/error ≥27/30 (90%).

**C. Vocabulary fluency** (30 free-form completions):
- Half-sentences from Reformed theology that test domain fluency. Examples:
  - "Edwards's notion of religious affections distinguishes…"
  - "Calvin's prelude to the doctrine of accommodation states that…"
  - "Owen's argument against the double-payment objection in Death of Death rests on…"
- Operator scores 1-5.
- **Pass**: average ≥4.

**D. Cite-or-flag invariant** (15 freeform questions):
- Some legitimate, some requiring "I don't have a citation for this" or "Couldn't verify."
- **Pass**: every emitted factual claim has a citation; uncited claims flagged "unverified."

**E. Latency benchmark** (30 queries, single-shot):
- 30 reasoning queries, each ~500-1000 tokens input.
- Acceptance: <90 seconds per query on m4 max with Q4_K_M (slow is OK for heavy tier; total throughput is what matters for the operator's research-conversation use case).

If any gate fails:
1. Log full failure (samples, model output).
2. Diagnose: data issue, CPT overshot, or base limitation?
3. **If data**: re-prep with corrections. Costs a full re-run.
4. **If CPT overshot** (lost general reasoning): resume from an earlier checkpoint (e.g. 50% through training) and stop there. Re-validate.
5. **If base limitation**: switch alternative base (Yi 1.5 34B); re-run from Step 2.
6. **If retry also fails**: STOP. Escalate to operator with diagnosis. Do not retry a third time.

### Step 6 — Quantize + deploy

After validation passes:

1. **Convert to GGUF** via llama.cpp:
   ```bash
   python ~/llama.cpp/convert_hf_to_gguf.py ~/models/reformed-32b --outfile ~/models/reformed-32b.gguf --outtype f16
   ```
2. **Quantize** to Q4_K_M:
   ```bash
   ~/llama.cpp/build/bin/llama-quantize ~/models/reformed-32b.gguf ~/models/reformed-32b-Q4_K_M.gguf Q4_K_M
   ```
   Expected output size: ~19-20 GB.
3. **Write a Modelfile**:
   ```
   FROM ./reformed-32b-Q4_K_M.gguf
   PARAMETER temperature 0.3
   PARAMETER num_ctx 8192
   PARAMETER repeat_penalty 1.05
   PARAMETER top_k 40
   PARAMETER top_p 0.9
   SYSTEM """You are a Reformed-tradition theology consultant. Your domain is the historical Reformed tradition: Spurgeon, Edwards, Calvin, Owen, Bunyan, Ryle, M'Cheyne, and the broader Puritan and post-Reformation Reformed thought. Answer with citations from primary sources. When a question requires reasoning, walk through the argument step by step and flag any speculation explicitly. When you cannot find a citation, say so. The 1689 LBCF + the Westminster Standards function as confessional guardrails. Scripture governs doctrine. Soli Deo Gloria."""
   ```
4. **Register with Ollama on m4 max only**:
   ```bash
   ollama create reformed-32b -f ~/models/Modelfile
   ```
   Do NOT push this model to Mac mini nodes — they cannot run 32B at usable quantization.
5. **End-to-end smoke test**: 5 of the operator's holdout reasoning questions through `ollama run reformed-32b`. Confirm coherent multi-paragraph answers with citations.

### Step 7 — Push artifacts + report

Same policy as light consult: **no GGUF weights to git repos** (~20 GB is far too large; would need dedicated private storage).

Push metadata only to `ken/orchestrator/lora-registry/base-models/reformed-32b/metadata.json`:

```json
{
  "tier": "heavy-consultant",
  "base_model": "Qwen/Qwen2.5-32B-Instruct",
  "training_corpus": "public-domain-only",
  "corpus_size_words": 119000000,
  "unique_words_after_dedup": 87000000,
  "cpt_hours": 76.4,
  "cpt_crashes_and_resumes": 0,
  "instruct_tune_applied": false,
  "validation": {
    "reasoning_benchmark_avg": 4.1,
    "reasoning_benchmark_floor": 3,
    "hallucination_pass_rate": "29/30",
    "vocabulary_fluency_avg": 4.4,
    "cite_or_flag_pass": true,
    "latency_p95_seconds": 42
  },
  "gguf_sha256": "<sha256 of Q4_K_M file>",
  "gguf_path_on_m4max": "/Users/<operator>/models/reformed-32b-Q4_K_M.gguf",
  "ollama_tag_m4max_only": "reformed-32b:latest",
  "built_at": "2026-06-XX..."
}
```

Plus append to `ken/orchestrator/LORA_TRAINING_LOG.md`:
```
2026-06-XX HH:MM - reformed-32b - passed (reasoning avg 4.1, hallucination 29/30, fluency 4.4) - <commit_sha>
```

## What you do NOT do

- Do not include any copyrighted-author corpus in the CPT phase.
- Do not add instruction tuning on top of the Qwen Instruct base (per §14.3) — it loses capability.
- Do not run more than one CPT epoch.
- Do not skip the hourly checkpoint cadence.
- Do not start the full 48-96 hr run without passing Step 2 sanity first.
- Do not deploy without all five validation gates passing.
- Do not push the GGUF to any node that cannot run 32B (Mac minis have insufficient memory).
- Do not push GGUF weights to any public git repo.
- Do not amend `THEOLOGIAN_MODEL_PLAN.md` without operator approval — but you may freely edit this file to record operational learnings, fixes to commands, etc.

## Failure-mode quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| OOM during CPT | batch + grad-accum too large for 32B in 32 GB | Reduce to batch=1, grad-accum=4. If still OOM, try smaller r (e.g. r=16) |
| Loss NaN at startup | lr too high for 32B | Drop to 1e-6; verify base model loads correctly first |
| Loss plateaus early | learning rate too small | Step lr up to 1e-5 in a re-run if Step 2 sanity also stalls |
| Eval perplexity diverges from train | overfitting (rare in 32B + 119M corpus; more likely a data issue) | Audit prep-report.json for outlier chunks; cut training short at last-good checkpoint |
| Reasoning benchmark fails ("forgot" general capability) | CPT overshot — catastrophic forgetting | Resume from earlier checkpoint (50-75% through); cut training short |
| Hallucination detection weak | CPT alone doesn't encode refusal behavior cleanly | This is a known limitation — operator may want to add a small instruction-tune LoRA in a *separate* future build, accepting the capability tradeoff |
| Vocabulary fluency weak | corpus prep dropped too much content | Audit prep-report.json; re-prep with relaxed filters |
| Latency exceeds 90 sec | Q4_K_M may need adjustment | Try Q4_K_S (slightly faster, slightly worse quality) or reduce num_ctx |

## Crash-recovery playbook

Given the multi-day run, this gets its own section:

**If MLX-LM crashes (any reason)**:
1. Check `cpt.log` last 50 lines for cause.
2. List checkpoints: `ls -la ~/build-data/heavy-consultant/cpt-adapter/checkpoint-*`
3. Resume from the most recent checkpoint:
   ```bash
   mlx_lm.lora --train ... --resume-adapter ~/build-data/heavy-consultant/cpt-adapter/checkpoint-<most-recent-N>
   ```
4. Append crash entry to build log with timestamp, cause, recovery action.

**If the m4 max reboots (power loss, kernel panic, etc.)**:
1. Re-launch tmux/screen.
2. Verify training process is dead (`ps aux | grep mlx_lm`).
3. Resume from most recent checkpoint per above.
4. Increment a `crashes_and_resumes` counter in the validation metadata for the final report.

**If repeated crashes** (>3 in 24 hrs):
- Switch to a smaller batch or grad-accum.
- If still crashing: stop, escalate to operator with logs + checkpoint state.

## Final reporting

After Step 7 completes:

1. Single-line entry in `LORA_TRAINING_LOG.md` per template above.
2. Full `prep-report.json` and `validation-report.json` in `~/build-data/heavy-consultant/`.
3. Brief reply to the operator: "Reformed-32b deployed (m4 max only). Reasoning avg 4.1/5, hallucination 29/30, vocab 4.4/5, p95 latency 42s. `ollama run reformed-32b` ready. Per-author LoRAs from `LOCAL_LORA_AGENT_PROMPT.md` will stack on this base at inference time."

---

Soli Deo Gloria.
