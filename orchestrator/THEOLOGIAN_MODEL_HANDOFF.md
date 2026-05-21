# HANDOFF — Theologian Model Library Plan

**Branch**: `claude/theological-model-planning-VU2zD` (pushed to ken, Romans, InTheWake, open-claw-stuff)
**Canonical plan**: `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` (12 sections + provenance log)
**Status**: Planning complete. All operator decisions closed 2026-05-21. Implementation work begins with corpus acquisition.

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

## What Still Needs Doing — prioritized

### **Now (corpus acquisition gates everything else)**

1. **Spurgeon scrape** — IN PROGRESS. Script at `Romans/quotes-and-references/spurgeon/download-spurgeon.sh`. Target: 3,563 sermons + indexes + prefaces from spurgeongems.org. PDFs gitignored; only `maps/*.md` get committed. **Container is ephemeral** — final run should happen on m4mini or m4max for persistent storage. See `Romans/quotes-and-references/spurgeon/HANDOFF.md` for scrape-specific status.
2. **Modern-theologian corpus copyright posture** — per-author IP decision required before scraping Washer, Sproul, MacArthur, Platt, Piper, Calvin (translated), Edwards, Owen, Lloyd-Jones, Carson, Schreiner, Baucham, Hamilton, Chapell, Robinson, Keller, etc. Spurgeon is public domain (d. 1892); the moderns are not. Without this decision, neither LoRA training nor RAG indexing can proceed per author.
3. **Conservative-Reformed scholarship corpora for corrector LoRAs** — Schreiner, Moo, Murray, Carson, Fee, Bruce, Murray Harris, Bock. Same copyright question per source.

### **Next (after corpus)**

4. **`retrieve_from_corpus` tool spec** — design before Track A week 4. Tool signature: `{author, chunk_id, text, citation_metadata, sha256} = retrieve_from_corpus(author: str, query: str)`. Substring-match + hash verified post-emission.
5. **Pre-DRAFT exegesis-log format** — sermon-file section schema; minimum-content threshold for gate-validation; override-flag wiring; sermon-map `⚠️ EXEGESIS-OVERRIDE` column. Spec before any LoRA fires.
6. **Base-model decision** — 3-pass orchestra design review (sermon mode), PASS 1 design + PASS 2 stress with Romans 9 + Psalm 23 + a wounded-congregation text + PASS 3 refine. Default: Llama 3.1 14B Q4 or Qwen 2.5 14B Q4.
7. **llama.cpp runtime** — commit explicitly; benchmark hot-swap on m4max with 2-3 prototype LoRAs; verify NATS-on-m4mini sermon-traffic routing.

### **Encode protected memories (operator instruction required)**

18 design calls listed at canonical plan §11 + cross-repo pointer at `open-claw-stuff/.memory/PLAN_THEOLOGIAN_MODEL.md`. Encode after operator approval; tag `operator-directive` + `theologian-model`. Includes the two extensions and the two decisions.

### **Held**

- **ITW parallel plan** — operator asked "how do we make something like this for ITW?" Architecture sketched in chat; not yet written to `InTheWake/.claude/plan-cruise-model.md`. Awaiting direction (write now / hold for research+orchestra first / hold entirely).

## Key Decisions (do not revisit)

1. **Scripture governs; 1689 LBCF is bumpers** (operator framing 2026-05-21).
2. **Two-path architecture**: open-weight LoRA + closed-weight persona, shared RAG, shared cite-or-flag invariant.
3. **No biblical-author voice LoRAs** (gateway-blocked, not just absent from training). Voice LoRAs forbidden for Paul/John/Peter/David/Isaiah/etc.
4. **Theologian LoRAs are primarily correctors** with voice as secondary inference-time mode (extension #2).
5. **Pre-DRAFT exegesis gate is a soft hard gate** with documented override (Decision 2 → B).
6. **Disclosure footer + congregation methodology letter** (Decision 1 → D + A combined).
7. **llama.cpp only** as Apple Silicon multi-LoRA runtime (Ollama hot-swap unimplemented).

## Files Created/Modified

- `ken/orchestrator/THEOLOGIAN_MODEL_PLAN.md` — canonical plan (565+ lines, 12 sections)
- `ken/orchestrator/THEOLOGIAN_MODEL_HANDOFF.md` — this file
- `Romans/.claude/theologian-model-plan.md` — Romans pointer
- `Romans/.claude/disclosure-footer.md` — canonical AI-disclosure footer template
- `Romans/.claude/methodology-disclosure-letter.md` — draft congregation methodology letter
- `InTheWake/.claude/plan-theologian-model-engineering-borrow.md` — engineering-only borrow
- `open-claw-stuff/.memory/PLAN_THEOLOGIAN_MODEL.md` — cross-repo design-call list

## How to Resume

Read canonical plan §12 (research provenance + orchestra log) first to ground in what was considered and rejected. Then:
1. If corpus acquisition is the blocker: continue Spurgeon scrape on persistent hardware; resolve modern-theologian copyright per-author.
2. If `retrieve_from_corpus` tool design is the next step: spec it before any LoRA work.
3. If ITW parallel plan is the next step: ask operator for write/hold direction.

Branch is `claude/theological-model-planning-VU2zD` across all 4 repos; check it out and pull before continuing.

Soli Deo Gloria.
