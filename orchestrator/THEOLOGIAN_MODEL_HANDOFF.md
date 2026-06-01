# HANDOFF — Theologian Model Library Plan

**Branch**: `claude/theological-model-planning-VU2zD` (pushed to ken, Romans, InTheWake, open-claw-stuff)
**Canonical plan**: `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` (14 sections + provenance log)
**Status**: Planning complete + §13–§14 added 2026-05-27/31 (corpus-grounded LoRA execution + two-tier base architecture). Corpus acquisition in flight across 8 per-author + 1 TGC scrapers. Three local-build prompts written and committed.

## What Was Done

| Phase | Output |
|---|---|
| Memory recall | 488 protected memories pulled and filtered; ~200 reviewed for theological/architectural relevance |
| Initial plan | §1–§11 written across canonical plan + Romans/InTheWake/open-claw pointers |
| Research | 4 parallel agents: Magisterium AI, LoRA voice-transfer, multi-agent debate, RAG citation enforcement |
| Orchestra design-review | Strategy mode, $0.1973, 5 fan-out + 2-round deliberation + Grok blind-spot |
| Extension #1 | Voice-vs-corrector LoRA split for biblical authors |
| Extension #2 | Theologians-primarily-correctors with voice as secondary inference-time mode |
| Decision 1 | Disclosure: D + A combined (footer + congregation methodology letter) |
| Decision 2 | Stage 0 gate: B (soft hard gate with logged override + backfill reminder) |
| Templates committed | `Romans/.claude/disclosure-footer.md` + `Romans/.claude/methodology-disclosure-letter.md` |
| §13 added (2026-05-27, `27b7bb6`) | Corpus inventory table (190M words / 31k files / 11 authors + Ken ~4M); 10-step LoRA priority sequence (Spurgeon pilot → Ken corrector slot 2 → MacArthur/Piper/Edwards/Calvin/Owen/Sproul → optional Bunyan/Ryle/M'Cheyne); data-prep pipeline; m4max+m4mini infra; per-LoRA validation gates + Ken-specific drift detection + cross-era stability; Spurgeon first concrete step |
| LoRA build prompt (2026-05-27, `26ad25e`) | `LOCAL_LORA_AGENT_PROMPT.md` — self-contained 5-step per-author build agent for m4max (data prep → sanity LoRA → full training → validation → push); covers all §13 authors |
| §14 added (2026-05-31, `3c75e55`) | Two-tier base-model architecture: light 3B consult (Llama 3.2 3B + CPT + instruct-LoRA, ~10-16 hrs m4max, GGUF Q4_K_M ~2GB, cluster-wide deploy) + heavy 32B consultant (Qwen 2.5 32B + CPT only, no instruct-tune, ~48-96 hrs m4max, GGUF ~20GB, m4max-only deploy); base bytes use public-domain corpus only; private/copyrighted authors stay as LoRA-only overlays; per-author LoRAs from §13 stack on either base |
| Light + heavy build prompts (2026-05-31, `3c75e55`) | `LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md` + `LOCAL_HEAVY_CONSULT_BUILD_PROMPT.md` — 7-step self-contained build agents; light covers CPT+instruct-LoRA+validation gates (citation accuracy/misattribution/p95 latency/cite-or-flag); heavy covers CPT-only+hourly checkpointing+crash-recovery+5 gates (reasoning/hallucination/vocab/cite-or-flag/latency) |
| Corpus scrapes in flight | 8 per-author + 1 TGC API scrape running across distinct hosts; 9 author corpora committed to `open-claw-stuff/corpus-tools/`; resume-safe via per-author manifest.json; container hibernation between operator activity kills processes — each session relaunches dead ones |

## What Still Needs Doing — prioritized

### **Now (corpus acquisition gates everything else)**

1. **Complete in-flight scrapes** (resume-safe via manifest). Active: Sproul learn.ligonier.org, Lloyd-Jones MLJ Trust, Keller GospelInLife, Begg TFL, Hamilton, Platt, Washer HeartCry, TGC (Carson + DeYoung + acf.authors filter for Schreiner/Anyabwile/Mohler/Ferguson/etc.). Baucham complete (310 metadata + audio queue). Per-corpus progress in each `<author>-corpus/_notes/manifest.json`.
2. **Audio acquisition + Whisper transcription** on m4mini cluster — for MLJ (1,643), Begg (1,504), Keller (1,979), Baucham (310), Sproul sermons, etc. Media URLs registered in each corpus's `_notes/media-urls.json`. Per memory `de9c5aa2`.

### **Next (build phase — execute on m4max)**

3. **Spurgeon LoRA pilot** (per §13.7) — `LOCAL_LORA_AGENT_PROMPT.md` slot #1. Proves the data-prep pipeline end-to-end on cleanest corpus. ~16 hrs.
4. **Light consult 3B** (per §14.5 step 2) — `LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md`. Immediately useful Ollama-deployable consult tool across cluster. ~10-16 hrs.
5. **Ken corrector LoRA** (§13.2 slot 2) — operator's own voice on whichever base passes validation. ~3 hrs.
6. **Heavy 32B CPT** (per §14.5 step 4) — `LOCAL_HEAVY_CONSULT_BUILD_PROMPT.md`. Multi-day run; serious local Reformed consultant. ~48-96 hrs.
7. **Remaining per-author LoRAs** (MacArthur, Piper, Edwards, Calvin, Owen, Sproul; optional Bunyan/Ryle/M'Cheyne) — `LOCAL_LORA_AGENT_PROMPT.md` slots 3–10. Parallel with 32B CPT.

### **Encode protected memories (operator instruction required)**

18 design calls listed at canonical plan §11 + cross-repo pointer at `open-claw-stuff/.memory/PLAN_THEOLOGIAN_MODEL.md`. Encode after operator approval; tag `operator-directive` + `theologian-model`.

### **Held**

- **ITW parallel plan** — operator asked "how do we make something like this for ITW?" Architecture sketched in chat; not yet written to `InTheWake/.claude/plan-cruise-model.md`. Awaiting direction.

## Key Decisions (do not revisit)

1. **Scripture governs; 1689 LBCF is bumpers** (operator framing 2026-05-21).
2. **Two-path architecture**: open-weight LoRA + closed-weight persona, shared RAG, shared cite-or-flag invariant.
3. **No biblical-author voice LoRAs** (gateway-blocked, not just absent from training).
4. **Theologian LoRAs are primarily correctors** with voice as secondary inference-time mode (extension #2).
5. **Pre-DRAFT exegesis gate is a soft hard gate** with documented override (Decision 2 → B).
6. **Disclosure footer + congregation methodology letter** (Decision 1 → D + A combined).
7. **One LoRA per author**, not a pair; voice mode is inference-time flag, hard-disabled at gateway for living/copyrighted authors (§3.5).
8. **Public-domain corpus only in base-model bytes** (§14.7); private/copyrighted authors are LoRA-only overlays.
9. **Two-tier base architecture**: light 3B (cluster-wide) + heavy 32B (m4max-only); per-author LoRAs stack on either at inference time.
10. **Ken LoRA trains on full ~4M-word corpus across all eras** (no era segmentation, operator directive 2026-05-27).

## Files Created/Modified

- `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` — canonical plan (~860 lines, 14 sections + provenance log)
- `ken/orchestrator/THEOLOGIAN_MODEL_HANDOFF.md` — this file
- `ken/orchestrator/LOCAL_LORA_AGENT_PROMPT.md` — per-author LoRA build prompt (`26ad25e`)
- `ken/orchestrator/LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md` — light 3B base build prompt (`3c75e55`)
- `ken/orchestrator/LOCAL_HEAVY_CONSULT_BUILD_PROMPT.md` — heavy 32B base build prompt (`3c75e55`)
- `Romans/.claude/theologian-model-plan.md` + `disclosure-footer.md` + `methodology-disclosure-letter.md`
- `InTheWake/.claude/plan-theologian-model-engineering-borrow.md`
- `open-claw-stuff/.memory/PLAN_THEOLOGIAN_MODEL.md`
- `open-claw-stuff/corpus-tools/{spurgeon,macarthur,piper,bunyan,ryle,mccheyne,owen,edwards,calvin,sproul,ferguson,godfrey,burk-parsons,lloyd-jones,keller,begg,hamilton,platt,baucham,washer,tgc}/` — per-author scraper scripts + READMEs
- `/home/user/<author>-corpus/` (gitignored content + `_notes/manifest.json` + scripts) on operator's persistent hardware

## How to Resume

Read canonical plan §13 + §14 first (corpus inventory + base-model architecture). Then:

1. **If continuing corpus acquisition**: relaunch any dead scrapes per `open-claw-stuff/corpus-tools/<author>/` — each is resume-safe via manifest. Container hibernates between operator activity; expect to relaunch on each session.
2. **If starting build phase on m4max**: paste either `LOCAL_LORA_AGENT_PROMPT.md` (per-author LoRAs) or `LOCAL_LIGHT_CONSULT_BUILD_PROMPT.md` (light 3B base) or `LOCAL_HEAVY_CONSULT_BUILD_PROMPT.md` (heavy 32B base) into Claude Code on m4max as the system prompt. Each is self-contained; agent reads `THEOLOGIAN_MODEL_PLAN.md` for context and proceeds.
3. **If ITW parallel plan is next**: ask operator for write/hold direction.

Branch is `claude/theological-model-planning-VU2zD` across all 4 repos; check it out and pull before continuing.

Soli Deo Gloria.
