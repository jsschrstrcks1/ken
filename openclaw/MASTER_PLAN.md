<!--
  Soli Deo Gloria. Every line of this design is offered as worship to God.
  "Whatever you do, work heartily, as for the Lord and not for men." — Colossians 3:23
  "Unless the LORD builds the house, those who build it labor in vain." — Psalm 127:1
-->
# Ken's Mac Cluster + OpenClaw Integration — Master Plan
**Version:** 2026-05-09 · v2.0.0
**Status:** Approved for build — investigation phase first, then build
**Author:** Ken Baker (with Claude Code)
**Audience:** The AI session running on `m4mini` (and any sibling node) that will set up OpenClaw and wire in the ken-repo skills.
**Supersedes:** `openclaw/ARCHITECTURE_v1.md` (kept for historical context — pre-pivot, do not follow).

---

## 0. Before You Touch Anything

Read these in order. Do not start work until you have read all of them.

1. **This document.** Top to bottom. It is the source of truth for the integration plan.
2. **`/home/user/ken/CLAUDE.md`** — section *"OpenClaw Integration — Anthropic ToS Hard Requirements"*. Those rules override convenience and override anything in this doc that contradicts them. If you see a conflict, the CLAUDE.md hard requirements win.
3. **The OpenClaw runtime, in its own words.** Fetch and read:
   - `https://github.com/openclaw/openclaw/blob/main/README.md`
   - `https://github.com/openclaw/openclaw/blob/main/VISION.md`
   - `https://github.com/openclaw/openclaw/blob/main/SECURITY.md`
   - `https://github.com/openclaw/openclaw/blob/main/AGENTS.md`
   - `https://github.com/openclaw/openclaw/blob/main/CLAUDE.md`
   - `https://github.com/openclaw/openclaw/blob/main/CONTRIBUTING.md`
   - The `docs/` directory tree for skill-authoring guides.
4. **One existing OpenClaw skill of each shape**, to learn the manifest format empirically:
   - `skills/skill-creator/` — should document how to author a skill.
   - `skills/gemini/` — closest analog to our multi-LLM use case.
   - `skills/coding-agent/` — to understand how OpenClaw handles agentic tools.
   - `skills/healthcheck/` — likely the simplest example.
5. The **`pyproject.toml`** at `skills/pyproject.toml` (visible at the top of `skills/`) — confirms whether and how Python skills are loaded.

When you have read those, write your understanding of OpenClaw's skill manifest format, Python skill loading, auth model, audit/logging, and confirmation/consent mechanism to `openclaw/RUNTIME_NOTES.md` in this repo. That file becomes the empirical reference for everything below that is currently marked `(verify)`. Do not skip this — much of this plan is approximate until you confirm.

---

## 1. Mission

Build a personal, multi-node Mac AI workflow system that supports Ken's primary workloads: pastoral content, code automation, photo processing, and family history. The runtime is the existing **OpenClaw** project (`github.com/openclaw/openclaw`). Our job is the integration on top of it: the Mac cluster topology, the ken-repo skill set, and the doctrinal/operational guardrails.

We are **not** building a runtime. We are not writing a skill loader, a gateway server, a confirmation prompt, an audit log, or a multi-channel messaging layer. OpenClaw provides those. We configure them, we extend them, we integrate with them.

---

## 2. Hard Requirements (Anthropic ToS — non-negotiable)

These are lifted from `CLAUDE.md` so this document is self-contained. The CLAUDE.md version is canonical; if it diverges, follow CLAUDE.md.

- **Auth:** API keys only (`ANTHROPIC_API_KEY=sk-ant-...`) from a `console.anthropic.com` billing account. **Never** Claude.ai (Free/Pro/Max) subscription OAuth. Keep this key separate from Claude Code's auth.
- **Tenancy:** single user, single tenant. Bearer auth on every OpenClaw endpoint. No other natural persons. No public endpoint, no Tailscale Funnel, no port forward.
- **Agentic skills:** anything taking external action declares `requires_human_confirmation: true` (or OpenClaw's equivalent — verify in Phase 0).
- **No auto-publish** of pastoral, Scripture, or family-history content. Manifest-loader-enforced where possible.
- **Universal usage standards:** no prohibited categories under Anthropic's policy.
- **Trademark:** don't label any local skill or surface as "Claude" or use the Claude trademark as a product name. Factual references in logs (`model: claude-opus-4-7`) are fine.
- **Audit:** every Anthropic API call through a ken-repo skill produces an audit record.

If a planned change would violate any of these, halt and flag.

---

## 3. The Runtime: OpenClaw

### What it is

OpenClaw is a personal, self-hosted AI assistant runtime created by Peter Steinberger. Originally launched November 2025 as "Clawdbot," renamed to "Moltbot" then "OpenClaw" by January 2026 after Anthropic trademark complaints over the original name. As of March 2026: 247K GitHub stars, 47.7K forks, MIT-licensed, TypeScript/pnpm workspace, ~52 skills shipping in-repo.

It runs on your hardware (Mac, Linux, VPS), exposes itself via messaging channels (Slack, Telegram, Discord, iMessage, etc.), persists memory across sessions, can run scheduled jobs, and has a skill-plugin model for extending capabilities.

### What we get for free (don't reimplement)

- **Gateway server** with bearer auth (`OPENCLAW_GATEWAY_TOKEN`).
- **Skill discovery and loading** — its own manifest format and registry.
- **Multi-provider model auth** — slots for `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, plus tool/media keys (Brave, Perplexity, ElevenLabs, Deepgram, etc.).
- **Multi-channel surface** — Slack, Telegram, Discord, iMessage, Mattermost, Twitch, etc.
- **Voice and screen** — `voice-call`, `peekaboo`, `camsnap`, `video-frames`, `sherpa-onnx-tts`, `openai-whisper`.
- **Mac integrations** — `apple-notes`, `apple-reminders`, `things-mac`, `bear-notes`, `imsg`.
- **Coding agent** — `coding-agent` skill ships in-tree.
- **Hot reload** of skills (verify in Phase 0).
- **Audit and security plumbing** — `security/` directory exists in repo (verify scope in Phase 0).
- **Health checks** — `healthcheck` skill.
- **Plugin SDK** — `tsconfig.plugin-sdk.dts.json`, `extensions/` directory.

### What it does NOT do (this is our job)

- **Multi-node distribution** across the Mac cluster. OpenClaw is single-machine. Our job is to bridge to remote workers (m3pro, m2mini, m4max) for heavy or specialized inference.
- **Mac-specific Metal-accelerated local inference orchestration** — Ollama / MLX-LM management, model warm-state tracking, mode detection (LAN vs travel for m4max).
- **The doctrinal constraint enforcement** — OpenClaw's confirmation system handles "ask before acting," but the project-specific rule that no skill auto-publishes Scripture is ours to mechanically enforce.
- **The photo pipeline** as a multi-stage NATS workflow — that's a backend service we build, surfaced in OpenClaw via skills.

---

## 4. Hardware and Network Topology

(Unchanged from v1.)

| Node | Hardware | Network | Reliability | Role |
|------|----------|---------|-------------|------|
| `vps` | RackNerd VPS (Linux) | Datacenter, always on | Highest | Coordinator: NATS JetStream (one of three replicas), MinIO results-archive, Prometheus/Grafana, Caddy. **Not** an OpenClaw host. |
| `m4mini` | Mac mini M4 | Home LAN | High | **OpenClaw host.** Default chat inference (Ollama). MinIO model storage. Cluster routing logic for distributed work. |
| `m3pro` | MacBook Pro M3 Pro | Home LAN | High when home | Cluster worker: code-specialized inference (Ollama), Whisper, photo scoring/crop. |
| `m2mini` | Mac mini M2 | Different network, moderate internet | High but remote | Cluster worker: small models, batch overflow. NATS JetStream replica (one of three). |
| `m4max` | MacBook Pro M4 Max | Mobile | Opportunistic | Cluster worker: heavy reasoning (70B), SDXL when home. Mode-detected (LAN ↔ travel). |
| `rpi5` | Raspberry Pi 5 8GB | Home LAN ethernet | High (always on) | Infrastructure: NATS JetStream replica (one of three), Prometheus scraping. PCIe slot reserved for an AI HAT+ if vision pre-screen becomes worth it (Phase 6 decision). |
| `rpi4a` | Raspberry Pi 4B 8GB | Home LAN | High (always on) | **Photo ingest worker:** folder watch + pHash + dedupe. USB SSD attached for staging. Frees m4mini from per-frame ingest. |
| `rpi4b` | Raspberry Pi 4B 8GB | Home LAN | High (always on) | Scheduled jobs (cron-style triggers via NATS) + hot spare. Can take over `rpi5` or `rpi4a` role on hardware failure. |

All on a Tailscale tailnet with MagicDNS. Hostnames above are canonical.

**Bandwidth tiers used in routing:**
- LAN intra-link (m4mini ↔ m3pro): gigabit, sub-ms
- Tailscale to VPS: tens of ms, low jitter
- Tailscale to m2mini: tens to hundreds of ms, moderate jitter
- Tailscale to m4max: variable (LAN-fast when home, hostile on hotel wifi)

---

## 5. Topology: OpenClaw + Cluster

Two systems coexist:

```
┌─────────────────────────────────────────────────────────────┐
│ m4mini                                                      │
│                                                             │
│   ┌───────────────────────┐     ┌────────────────────────┐ │
│   │  OpenClaw runtime     │     │  Cluster bridge        │ │
│   │  (TypeScript, the     │ ──▶ │  (skill exposing NATS  │ │
│   │  upstream project)    │     │  publish to VPS)       │ │
│   │                       │     │                        │ │
│   │  - gateway + auth     │     │                        │ │
│   │  - skills loader      │     │                        │ │
│   │  - channel adapters   │     │                        │ │
│   │  - confirmation UI    │     │                        │ │
│   │  - local Ollama       │     │                        │ │
│   │    (chat 7B/8B)       │     │                        │ │
│   └───────────────────────┘     └─────────┬──────────────┘ │
└─────────────────────────────────────────────┼──────────────┘
                                              │
                                              ▼
                                ┌─────────────────────────────┐
                                │ vps                         │
                                │  NATS JetStream             │
                                │  MinIO (coordination,       │
                                │         results-archive)    │
                                └──────┬──────────┬───────────┘
                                       │          │
                          ┌────────────┘          └────────────┐
                          ▼                                    ▼
                   ┌──────────────┐                    ┌──────────────┐
                   │ m3pro        │                    │ m4max        │
                   │ Ollama code  │                    │ Ollama 70B   │
                   │ Whisper      │                    │ SDXL         │
                   │ Photo score  │                    │ Mode detector│
                   └──────────────┘                    └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ m2mini       │
                   │ Ollama small │
                   │ Whisper      │
                   │  overflow    │
                   └──────────────┘
```

**Key idea:** OpenClaw on m4mini handles real-time chat + skill execution. Heavy or specialized work crosses the bridge to NATS, which fans it out to cluster workers. Results return through the bridge to OpenClaw, which presents them to the caller.

OpenClaw is **not** distributed. The cluster is **not** an OpenClaw replacement. They are two layers, glued by the cluster-bridge skill.

---

## 6. Execution Model

Three flows. Every task fits exactly one.

### 6.1 Real-time chat (via OpenClaw, no cluster)

```
caller (Slack / Telegram / iMessage / etc.)
   → OpenClaw on m4mini
   → bearer auth check
   → routes to local Ollama (chat 7B/8B) or to a model-provider skill
   → streams response back through the channel
```

OpenClaw handles this entirely. The cluster is not involved. Latency budget: first token under 1 second on LAN.

### 6.2 Real-time inference needing cluster (via cluster bridge skill)

```
caller → OpenClaw skill (e.g., code_assist)
       → cluster_bridge skill: NATS publish to topic.realtime.<class>
       → m3pro Ollama (code) responds
       → bridge subscribes to result
       → OpenClaw returns to caller
```

Used when the task class needs a specific worker (code → m3pro, heavy reasoning → m4max-when-LAN). Cluster bridge skill enforces a short timeout (≤5s) and falls back to OpenClaw-local Ollama on timeout.

### 6.3 Batch / scheduled work (via NATS direct, OpenClaw observes)

```
trigger (folder watcher, scheduler, manual skill call)
   → NATS publish to topic.batch.<class>
   → cluster worker pulls, processes, publishes result to results-archive on VPS MinIO
   → OpenClaw skill (`batch_status`) lets caller check completion
```

Used for: photo pipeline, sermon transcription, embedding batches, image generation runs, m4max opportunistic processing while traveling. Survives node failures via JetStream durability.

---

## 7. Storage Architecture

(Unchanged from v1.)

**Originals are immutable.** All processing writes new files to a parallel tree.

```
/photos/
  originals/2026-05-09-cruise/IMG_1234.CR2
  derivatives/2026-05-09-cruise/{tagged,cropped,enhanced,web}/
  metadata/2026-05-09-cruise/IMG_1234.{json,xmp}
```

**MinIO buckets on `m4mini`:** `models`, `photos-originals` (RO after ingest), `photos-derivatives`, `audio-originals`, `transcripts`.

**MinIO buckets on `vps`** (small artifacts): `coordination`, `results-archive`.

Model files: `m4mini` MinIO + `m4max` local SSD (cached). Never through VPS.

---

## 8. Cluster Routing (m4mini's job, not OpenClaw's)

OpenClaw routes among its own loaded skills. The **cluster** routing — which of m3pro, m4max, m2mini handles a given workload — is implemented in the cluster-bridge skill. Pseudocode:

```python
def cluster_route(task_class: str, mode: str):
    # mode: "realtime" or "batch"
    candidates = capable_nodes_for(task_class)

    if mode == "realtime":
        warm = [n for n in candidates if model_resident(n, task_class)]
        if warm:
            return least_loaded(warm)
        available = [n for n in candidates if reachable(n, latency_ms_max=5)]
        if not available:
            # degrade to OpenClaw-local Ollama on m4mini
            return None
        return least_loaded(available)

    # batch path — publish, don't pick
    return publish(topic_for(task_class), task)
```

### Task class → preferred node

| Task class | Preferred | Fallback | Notes |
|------------|-----------|----------|-------|
| `general` (chat 7B/8B) | OpenClaw-local on m4mini | m3pro | Default |
| `code` | m3pro | m4mini | Code-specialized models |
| `heavy_reasoning` (70B) | m4max (LAN mode only) | queue for batch | Never block real-time |
| `vision.tag` | m4mini | m3pro | LLaVA |
| `whisper.transcribe` | m3pro | m2mini | m4mini reserved for chat |
| `embed` | m4mini | m2mini | Small model, replicated |
| `image.generate` | m4max (LAN mode) | queue for batch | SDXL, batch-only when traveling |

### Worker warm-state tracking

Each Ollama/MLX worker reports `loaded_models` to VPS heartbeat every 30 seconds. Bridge skill reads this when picking placement.

### Mode detection (m4max LAN vs Travel)

Same hysteresis as v1. Sample latency to m4mini every 30s. Switch to **LAN** only after 3 consecutive samples with latency < 5ms and loss = 0%. Switch to **Travel** after 3 consecutive samples with latency > 50ms or any loss > 0%. In between, hold current mode.

### Model contention on m4mini

m4mini is the OpenClaw host *and* a target for chat/LLaVA/embeddings. Three large models concurrent will thrash. Phase 4: **one large model resident at a time**. Either chat-mode (Llama 3.1 8B + small embedding) or LLaVA-mode (LLaVA-1.6 13B + small embedding). Switch by config. Revisit only after measuring actual usage.

---

## 9. Partition Rules

(Unchanged from v1, restated for completeness.)

- **m4max offline (frequent):** LAN cluster serves real-time with 7B/8B. Heavy-reasoning real-time degrades to "best available smaller model" with a flag, or queues for when m4max returns.
- **LAN ↔ VPS link flaky (occasional):** LAN keeps serving real-time. Batch publishes buffer locally on m4mini until VPS is reachable. NATS reconnect handles flush.
- **VPS down entirely (rare):** LAN keeps serving real-time. Batch durability is preserved by the 3-node JetStream cluster (`vps` + `rpi5` + `m2mini`); losing one node keeps quorum. Losing two nodes (vps + either replica, or both replicas) suspends batch durability until quorum returns; new batch jobs queue locally on m4mini in-memory in that window.
- **m4mini down:** Single point of failure. OpenClaw and real-time inference stop. Phase 6 may add OpenClaw failover; v2 accepts this.

---

## 10. Skills (the ken-repo half)

### Where they live

```
ken/
├── skills/                         ← OpenClaw's expected skill location (verify exact path in Phase 0)
│   ├── hello-world/
│   ├── consult/                    ← wraps orchestrator/consult.py
│   ├── orchestrate/
│   ├── orchestra/
│   ├── investigate/
│   ├── cluster-bridge/             ← publishes to NATS for distributed work
│   ├── photo-pipeline-status/      ← read-side skill for the photo workflow
│   ├── sync-clock/                 ← wraps sync-clock.sh
│   └── tz-wakeup/
└── (everything else unchanged)
```

The exact skill manifest format and the precise directory layout are **TBD**. Phase 0 establishes them by reading `skills/skill-creator/` and an existing skill, then writes findings to `openclaw/RUNTIME_NOTES.md`.

### What's currently in the repo (pre-pivot drafts)

`openclaw-tools.yaml` at the repo root and `tools/hello-world/hello.py` were committed under the assumption we were building our own runtime. Both are in the **wrong format** for real OpenClaw. Phase 2 either reformats them under `skills/` to match OpenClaw's convention or removes them. Don't follow them as a template.

### Skill categories

- **Multi-LLM (`external` execution class — paid APIs):**
  `consult`, `orchestrate`, `orchestra`, `investigate`. Each wraps the corresponding `orchestrator/<name>.py` script. Subprocess Keychain injection: OpenClaw fetches `OPENAI_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`, `PERPLEXITY_API_KEY`, `YOUCOM_API_KEY` from Keychain and injects into the subprocess env when spawning. The orchestrator's own `.env` mechanism stays in place for direct human invocation. Per-skill daily spend cap (default $5).

- **Cluster bridge (`safe` execution class — local network only):**
  `cluster-bridge` exposes one verb (`run_on_cluster(task_class, payload, mode)`) that publishes to NATS and (for realtime mode) blocks for up to 5s on the result topic. Other ken skills delegate to this rather than calling NATS directly. Single source of truth for cluster topology.

- **Local utilities (`destructive` — modify system state):**
  `sync-clock`, `tz-wakeup`. Wrap existing shell scripts. Require human confirmation per ToS hard requirements.

- **Smoke test (`safe`):**
  `hello-world`. Returns `{ok, node, manifest_sha_or_version}`. Phase 1 success criterion.

### Discovery boundary

OpenClaw scans **only** `skills/` (or the path it documents) and the manifest entries within. The rest of this repo (`.claude/skills/` — those are Claude Code prompt assets, generated outputs, CSVs, sermon files, the orchestrator's source tree, etc.) is invisible to OpenClaw. Don't expand the boundary without explicit decision.

### Doctrinal constraint enforcement

Per `CLAUDE.md` and Anthropic ToS: no skill auto-publishes pastoral, Scripture, or family-history content. Mechanical enforcement strategies, in order of preference:

1. **Loader-level rejection** of any skill named `publish_*` that doesn't carry `requires_human_confirmation: true` (or OpenClaw's equivalent).
2. **External-endpoint allowlist** rejecting `safe` skills that touch the network.
3. **Audit assertion** that every call writing to a public surface has a corresponding human-approval record.

Phase 0 verifies which of these OpenClaw natively supports; the rest get implemented as a manifest-validator skill.

### Subprocess secret injection (orchestrator-as-skill pattern)

The orchestrator under `orchestrator/` reads its own `.env` (decoded from `env_seed.py`). **Don't migrate it.** It works, and it's used by humans directly outside OpenClaw. Pattern:

- OpenClaw reads required secrets from macOS Keychain.
- When spawning the orchestrator subprocess, OpenClaw injects them as env vars.
- The orchestrator's `.env` loader sees them as if they came from `.env`.
- Standalone human use of the orchestrator continues to work via the original `.env` path.

Two paths, same orchestrator code, no migration. The skill manifest declares which keychain items it needs.

---

## 11. Multi-LLM via OpenClaw

OpenClaw already has a `gemini` skill in-repo. That tells us multi-LLM-as-skill is a known pattern — we follow it, not reinvent it.

Strategy: each of `consult`, `orchestrate`, `orchestra`, `investigate` becomes its own ken-repo skill. Don't merge them into one configurable skill; the cost / latency / confirmation profiles differ enough that separate skills give cleaner manifest enforcement. Specifically:

- `investigate` carries `requires_human_confirmation: true` because of cost and scope (4-phase research, ~$1–3 per run).
- `consult` is cheap (cents) and doesn't need per-call confirmation.
- `orchestrate` and `orchestra` sit between (~$0.50 typical); confirmation off, daily cap on.

All four log to the project audit destination — OpenClaw's native audit if available, otherwise our own `tool.audit` NATS subject.

---

## 12. Build Plan

### Phase 0 — Investigation (start here, no code yet)

1. Read all docs listed in Section 0.
2. Inspect `skills/skill-creator/`, `skills/gemini/`, `skills/coding-agent/`, `skills/healthcheck/`. Document the actual skill manifest format empirically.
3. Inspect `skills/pyproject.toml` and any Python skill in-tree to confirm Python skill loading model.
4. Read `SECURITY.md` carefully. Document OpenClaw's auth model, audit/logging, confirmation-prompt mechanism, and the security boundaries it claims.
5. Check whether OpenClaw has any built-in mechanism for distributed/cluster work, message queues, or external worker dispatch. Almost certainly no — but verify, because if yes, our cluster-bridge design simplifies.
6. Write findings to `openclaw/RUNTIME_NOTES.md`. This is the empirical reference. Sections 10 and 11 of this doc get revised against it before Phase 2.

**Exit criterion:** `RUNTIME_NOTES.md` exists, names the actual skill manifest format with a working hello-world example reformatted to that format, names the auth/audit/confirmation primitives, and identifies the multi-node story (custom or built-in).

### Phase 1 — OpenClaw running on m4mini, BYO key

1. Install OpenClaw on m4mini per the project's install guide (read it; do not assume).
2. Install Tailscale on m4mini and m3pro. Verify `tailscale status` shows both. Confirm MagicDNS works.
3. Generate a fresh Anthropic API key at `console.anthropic.com` in a billing account **separate** from any Claude Code or Claude.ai relationship. Store as `ANTHROPIC_API_KEY` per OpenClaw's `.env.example`.
4. Generate a bearer token, store under macOS Keychain item `openclaw_gateway_token`, point `OPENCLAW_GATEWAY_TOKEN` at it.
5. Start OpenClaw. Run a built-in skill that doesn't touch external state (`healthcheck`). Confirm the gateway accepts authed requests and rejects unauthed ones.
6. Configure `caffeinate` on m3pro (will be a worker in Phase 4).

**Exit criterion:** OpenClaw responds to an authed request from another tailnet device with a valid `healthcheck` response. Unauthed requests are rejected.

### Phase 2 — First ken skill (hello-world, in OpenClaw's format)

1. Reformat `tools/hello-world/hello.py` and `openclaw-tools.yaml` to OpenClaw's actual skill convention (per `RUNTIME_NOTES.md`). Move under `skills/hello-world/` if that's the right directory.
2. Make ken-repo discoverable to OpenClaw — likely a clone at `/opt/openclaw/skills-extra/ken` or similar (verify in Phase 0). Read-only deploy key with read access to the ken repo, stored in macOS Keychain, referenced via ssh-agent.
3. Pull schedule: 15 minutes via `launchd` or cron. No webhook in v2.
4. Tracked branch: `main`. Merges gated by Ken.
5. Verify hello-world skill loads, returns `{ok, node, version_or_sha}`, and produces an audit record.
6. Remove `tools/` and `openclaw-tools.yaml` if they're now redundant. They were Phase 0 drafts.

**Exit criterion:** Calling `hello-world` from OpenClaw on m4mini returns the expected JSON. Audit record present.

### Phase 3 — Multi-LLM skills (orchestrator wrap)

1. Add four skills: `consult`, `orchestrate`, `orchestra`, `investigate`. Each wraps the corresponding `orchestrator/<name>.py` via subprocess.
2. Implement subprocess secret injection: OpenClaw reads `OPENAI_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`, `PERPLEXITY_API_KEY`, `YOUCOM_API_KEY` from Keychain on call, injects into child env. Orchestrator's own `.env` flow stays unchanged.
3. Set per-skill daily spend caps: $5 each. `investigate` carries `requires_human_confirmation: true`.
4. End-to-end: invoke `consult` from a chat channel, see the API call happen against the user's own keys, see audit record, see daily-cap counter increment.

**Exit criterion:** All four skills callable, costs aggregating per skill, caps enforce on overrun.

### Phase 4 — Coordinator + Pi infrastructure + photo pipeline

1. Install NATS JetStream as a 3-node cluster on `vps` + `rpi5` + `m2mini`. Verify no AdGuard conflict on VPS. Configure explicitly: persistent streams, `AckExplicit` on every consumer, retention ≥ 24 hours or work-queue with explicit ack. Defaults silently drop messages — do not rely on them.
2. Install MinIO on m4mini. Create buckets per Section 7.
3. Bring up `rpi4a` as the photo ingest worker. USB SSD attached for staging. `watchdog` library watches the import folder; pHash + dedupe runs on-Pi; survivors publish to `photo.ingest`.
4. Bring up `rpi4b` as the scheduled-job runner. Initial jobs: heartbeat poller (every 60s, publishes per-node liveness to NATS), placeholder for future cron triggers (e.g., "every Sunday 14:00, kick off sermon transcription if a new file in `audio-originals/`").
5. Build cluster-bridge skill on m4mini: one verb `run_on_cluster(task_class, payload, mode)`. Realtime mode blocks ≤5s on result topic. Batch mode publishes and returns.
6. Photo pipeline MVP per Appendix A — minus the ingest stage, which now lives on `rpi4a`.

**Exit criterion:** `rpi4a` watches the folder, hashes/dedupes, publishes to NATS; m3pro scoring worker picks up survivors via NATS; LLaVA on m4mini tags what scoring keeps; status JSON written per image. NATS quorum survives any one node going down.

### Phase 5 — Full cluster (m2mini, m4max)

1. m2mini onto tailnet. Ollama with a small model. Subscribe to overflow topics.
2. m4max onto tailnet. Heavy models on local SSD. Mode detector (LAN vs travel) per Section 8. Adds `heavy_reasoning` and `image.generate` workloads when LAN-resident; batch-only when traveling.

**Exit criterion:** A 70B query routed through OpenClaw lands on m4max when home, queues for batch when traveling.

### Phase 6 — Hardening

- OpenClaw replication for m4mini failover.
- Prometheus + Grafana on VPS, scraping nodes including the Pis via `rpi5`.
- Backup strategy for MinIO.
- A separate `openclaw-release` branch in the ken repo with signed-commit gating, replacing the `main`-tracked v2 default.
- Confirmation-channel for batch jobs that need it (push notification via ntfy.sh or Pushover) — replaces Phase 1's fail-closed default.
- Workflow-library evaluation (Prefect / Temporal) only if plain async Python becomes painful.
- **Vision pre-screen decision.** After Phase 4 photo pipeline is in daily use, measure actual LLaVA throughput on m4mini. If it's a real bottleneck (waits long enough to bother you, or blocks chat-mode contention), buy the AI HAT+ (Hailo-8, 26 TOPS, ~$130) for `rpi5` and add the `vision-screen` stage per Appendix A. If LLaVA throughput isn't actually the limiter, save the money. Trigger to revisit: any new vision workload (security cam, doorbell cam, multi-stream video) — those make the HAT worth it independent of photo pipeline.

---

## Appendix A — Photo Pipeline (first concrete cluster workload)

(Unchanged from v1 — still valid as a workload spec, independent of runtime.)

### Stages

```
ingest → hash/dedupe → score/filter → tag → crop → enhance → export
```

Hash before score, score before tag. Burst shooting produces near-identical frames; perceptual hashing eliminates them before any compute is spent. Then scoring filters blur and bad exposure. Only what survives reaches LLaVA.

### NATS topics

```
photo.ingest      — file path, EXIF, sha256
photo.hash        — perceptual hash (pHash), dedupe decision
photo.score       — blur, exposure, similarity score
photo.tag         — LLaVA tags + caption
photo.crop        — composition suggestion (no auto-crop)
photo.enhance     — color/contrast/sharpening proposal
photo.export      — final write to derivatives/web/
```

### Idempotency record (per image)

```json
{
  "file": "IMG_1234.CR2",
  "sha256": "...",
  "pipeline": "cruise",
  "status": {
    "hashed":   {"done": true,  "ts": "2026-05-09T09:59:30Z"},
    "scored":   {"done": true,  "ts": "2026-05-09T10:00:00Z"},
    "tagged":   {"done": true,  "ts": "2026-05-09T10:01:30Z"},
    "cropped":  {"done": false, "ts": null},
    "enhanced": {"done": false, "ts": null},
    "exported": {"done": false, "ts": null}
  },
  "phash": "f8d1c3e7...",
  "dedupe_group": null,
  "tags": ["sunset", "ocean", "ship-rail"],
  "caption": "Wake at golden hour off the stern.",
  "scripture_suggestions": null
}
```

`scripture_suggestions` is always null in v2. If/when added, it returns *themes only* (`["creation", "stillness"]`) — never verse text, never pairings, never overlays.

### Branching

Every image carries `pipeline: "cruise" | "personal"`.

- `cruise` → polished tags, web-ready exports, SEO-aware caption, XMP sidecar.
- `personal` → archival tags, family-context metadata, no web export.

### MVP scope (Phase 4)

1. Folder watcher on **`rpi4a`** (`watchdog`), USB SSD attached
2. pHash + dedupe on `rpi4a`; survivors publish to `photo.ingest`
3. Scoring worker on m3pro (Laplacian variance + histogram)
4. Tagging worker on m4mini (LLaVA-1.6 13B Q4 — verify RAM headroom first)
5. Status JSON in `metadata/`

Defer until MVP is in daily use: vision pre-screen (see below), crop suggestions, SDXL enhancement, web export, UI.

### Vision pre-screen (deferred — Phase 6 decision)

Optional stage between `score/filter` and `tag`. Runs on a Pi with hardware acceleration:
- **AI HAT+ (Hailo-8, 26 TOPS, ~$130)** on `rpi5` — preferred, more capable, supports model-zoo YOLO and scene classifiers out of the box.
- **Coral USB Accelerator (~$60)** on `rpi4a` or `rpi4b` — cheaper, weaker, MobileNet-class only. Reasonable hedge if you want vision acceleration without committing to the HAT.

Pre-classifies each scoring-survivor with YOLO + scene classifier; only "interesting" images proceed to LLaVA on m4mini. Estimated 60–80% reduction in LLaVA invocations.

**Don't buy hardware speculatively.** Run the photo pipeline through one heavy-volume cycle (a real cruise or family event) first. Measure LLaVA wall-clock. If it's not annoying you, the savings aren't worth the spend. If you add a security cam or doorbell cam to the project, the HAT becomes worth it on its own merits independent of photo pipeline.

### RAM budget (verify on first run)

- LLaVA-1.6 13B Q4 ≈ 8 GB resident. M4 mini with 16 GB is tight if other models co-resident. Consider 24 GB+ M4 mini, or run LLaVA exclusively on this node.
- LLaVA-1.6 34B Q4 ≈ 20 GB resident. Only if M4 mini has 32 GB+ and no co-resident models.

---

## Appendix B — Open Questions (validate empirically)

### OpenClaw runtime (resolve in Phase 0)

- Exact skill manifest format and required fields.
- Python skill loading model — `pyproject.toml` integration or subprocess only.
- Long-running batch / scheduled work pattern within OpenClaw.
- Built-in confirmation/consent prompt mechanism (channel surface, fail-closed semantics).
- Audit log facilities (where calls are recorded, retention, query interface).
- Hot-reload semantics for skill changes.
- Multi-node / cluster awareness (almost certainly absent — verify).

### Cluster (validate during build)

- Exact M4 mini RAM SKU and headroom for co-resident models.
- Exact M4 Max RAM SKU (determines feasibility of 70B at full context).
- AdGuard's current port bindings on the VPS — confirm before adding services.
- Whether m4max's typical traveling network supports any usable Tailscale throughput, or whether it should be treated as fully offline most of the time.
- Photo cataloging tool compatibility — does anything in use need XMP sidecar? Lightroom? Apple Photos? Bare folders? Design varies.

### Multi-repo expansion (defer until v2 stable)

- Which of the other 8 repos should expose skills at all (most probably shouldn't).
- Per-repo policy: branch tracked, allowed execution classes, name-collision namespacing (`<repo>.<skill>`).
- Setup forms for the per-repo deploy keys in macOS Keychain.

See `openclaw/MULTI_REPO_EXTENSION.md` (forward-looking notes).

---

## Appendix C — References

- **OpenClaw runtime:** `https://github.com/openclaw/openclaw` · `https://openclaw.ai`
- **Anthropic Usage Policy:** `https://www.anthropic.com/legal/aup`
- **Anthropic Commercial Terms:** `https://privacy.claude.com/en/collections/10663361-commercial-customers`
- **Anthropic policy on third-party harnesses:** `https://www.theregister.com/2026/02/20/anthropic_clarifies_ban_third_party_claude_access/` (background reading; the policy itself is in the Consumer Terms of Service).
- **Background on the OpenClaw / Anthropic dispute and rename:** `https://en.wikipedia.org/wiki/OpenClaw`, `https://thenextweb.com/news/anthropic-openclaw-claude-subscription-ban-cost`.
- **Project hard requirements:** `/home/user/ken/CLAUDE.md` (section: *OpenClaw Integration — Anthropic ToS Hard Requirements*).
- **Pre-pivot architecture (historical):** `/home/user/ken/openclaw/ARCHITECTURE_v1.md`. Do not follow.
- **Multi-repo extension notes (forward-looking):** `/home/user/ken/openclaw/MULTI_REPO_EXTENSION.md`.

---

## Footer
> Soli Deo Gloria — Every pixel and part of this project is offered as worship to God. The plans of the diligent lead surely to abundance, but the Lord establishes the steps. (Proverbs 21:5; 16:9)
