<!--
  Soli Deo Gloria. Every line of this design is offered as worship to God.
  "Whatever you do, work heartily, as for the Lord and not for men." — Colossians 3:23
  "Unless the LORD builds the house, those who build it labor in vain." — Psalm 127:1
-->

> ## ⚠ HISTORICAL — DO NOT FOLLOW
> This document predates the discovery that OpenClaw is an existing
> third-party project (`github.com/openclaw/openclaw`), not something we
> are building. It assumes a custom Python runtime that is no longer the
> plan.
>
> **Current canonical plan: [`MASTER_PLAN.md`](./MASTER_PLAN.md)** (v2.0.0).
>
> Kept here for historical context: many of the cluster-topology, photo
> pipeline, and partition-rules sections survive the pivot and are
> carried forward into v2. The skill-loader, audit-subject, and
> bearer-middleware sections do not — OpenClaw provides those.

---

# OpenClaw Distributed AI System — v1 Architecture
**Version:** 2026-05-09 · v1.000.000
**Status:** Superseded — see MASTER_PLAN.md
**Author:** Ken Baker
**Scope:** Distributed local AI workflow system across four Apple Silicon nodes plus a coordinator VPS.
---
## 1. Objective
Build a distributed, partition-tolerant AI workflow system that:
- Runs inference **natively** on Apple Silicon with Metal acceleration. Inference never runs inside Linux containers, because containers on macOS lose access to Metal.
- Routes tasks to the appropriate node based on model resident state, node capability, and node availability.
- Survives the M4 Max being mobile and the M2 mini being on a moderate-bandwidth remote link.
- Supports the user's primary workloads: pastoral content, code automation, photo processing, and family history work.
This is **not** a distributed compute framework. It is a **message-driven workflow system with specialized workers**. That distinction governs every other choice in this document.
---
## 2. Hardware and Network Topology
| Node | Hardware | Location / Network | Reliability | Role |
|------|----------|---------------------|-------------|------|
| `vps` | RackNerd VPS (Linux) | Datacenter, real bandwidth, always on | Highest | Coordinator (queue, metrics, AdGuard, thin proxy) |
| `m4mini` | Mac mini M4 | Home LAN | High (always on at home) | LAN core — primary brain, default inference, model storage |
| `m3pro` | MacBook Pro M3 Pro | Home LAN | High when home, lid-closed risk | LAN core — code/specialized inference, parallel worker |
| `m2mini` | Mac mini M2 | Different network, moderate internet | High (always on, but remote) | Regional worker — small models, batch overflow |
| `m4max` | MacBook Pro M4 Max | Mobile, traveling | Opportunistic | Heavy compute when LAN-resident; autonomous batch worker when traveling |
All five nodes share a Tailscale tailnet with MagicDNS. Hostnames above are the canonical references throughout this document.
**Bandwidth tiers used in routing decisions:**
- LAN intra-link (m4mini ↔ m3pro): gigabit, sub-millisecond
- Tailscale to VPS: tens of milliseconds, low jitter
- Tailscale to m2mini: tens to hundreds of milliseconds, moderate jitter
- Tailscale to m4max: variable (LAN-fast when home, hostile when on hotel wifi)
---
## 3. Service Map
### `vps` (Linux)
| Service | Port | Notes |
|---------|------|-------|
| AdGuard | 53, 80/3000 (admin) | Existing — do not disturb |
| NATS JetStream | 4222 (client), 8222 (monitor) | Durable queue, persistent storage |
| Prometheus | 9090 | Scrapes nodes via Tailscale |
| Grafana | 3001 | Dashboards (avoid AdGuard's 3000) |
| Caddy (reverse proxy) | 443 | TLS via Tailscale certs, auth required |
**Constraints:** No model files. No inference. No large-object storage. Coordination metadata only.
### `m4mini` (LAN core, primary brain)
| Service | Port | Notes |
|---------|------|-------|
| Ollama | 11434 | Default 7B/8B models (Llama 3.1 8B, Mistral 7B) |
| MLX-LM server | 8000 | Optional — alternative serving for MLX-quantized models |
| MinIO | 9000 (S3), 9001 (console) | Canonical model file storage |
| OpenClaw control brain | 7700 | Routing, scheduling, workflow orchestration |
| Tool sync (git) | n/a | Pulls Ken repo on schedule + webhook (see Section 9) |
| LLaVA worker | n/a | Subscribes to `vision.tag` |
| Embedding worker | n/a | Subscribes to `embed.*` |
| Folder watcher | n/a | Photo pipeline ingestion |
### `m3pro` (LAN core, specialized worker)
| Service | Port | Notes |
|---------|------|-------|
| Ollama | 11434 | Code-specialized models (DeepSeek Coder, Qwen Coder) |
| Whisper worker | n/a | Subscribes to `whisper.transcribe` |
| Photo scoring worker | n/a | Blur detection, exposure, dedupe |
| Photo crop worker | n/a | Classical CV (OpenCV) |
| Caffeinate / pmset | — | Prevent sleep when on AC |
### `m2mini` (regional worker)
| Service | Port | Notes |
|---------|------|-------|
| Ollama | 11434 | Small models (3B–7B) |
| Whisper worker (overflow) | n/a | Pulls from `whisper.transcribe` when LAN saturated |
| NATS replica | 4222 | Optional secondary for queue durability |
### `m4max` (opportunistic heavy compute)
| Service | Port | Notes |
|---------|------|-------|
| Ollama | 11434 | Heavy models (Llama 3.3 70B Q4, Mixtral 8x7B Q4) — local copy on SSD |
| MLX-LM server | 8000 | Preferred for 70B-class on Apple Silicon |
| SDXL (ComfyUI or Diffusers) | 8188 | Image generation when home |
| Mode detector | n/a | Measures latency to m4mini; switches LAN/Travel mode |
---
## 4. Execution Model
Three distinct request flows. Every task fits into exactly one.
### 4.1 Real-time requests (interactive)
```
client (on Tailscale) → m4mini:7700 (OpenClaw)
                       → routes to local Ollama (m4mini or m3pro)
                       → streams response back
```
- Stays on the LAN. Never round-trips through VPS.
- Used for: chat, code completion, quick questions, verse-suggestion *requests* (never auto-publish).
- Latency budget: first token under 1 second on LAN.
### 4.2 Batch / scheduled work
```
caller → vps:4222 (NATS publish to topic)
       → workers on capable nodes pull
       → results published back to results topic
       → caller subscribes for completion
```
- Used for: photo pipeline, sermon transcription, embedding batches, image generation runs.
- Survives node failures: jobs remain in JetStream until acknowledged.
- Caller may be a human-triggered script or OpenClaw itself.
### 4.3 Opportunistic processing (m4max while traveling)
```
m4max → polls vps:4222 for `batch.heavy.*` topics
       → processes locally when network allows
       → publishes results back to vps
```
- m4max may be offline for hours or days. Jobs wait in JetStream.
- m4max never serves real-time requests while traveling. Travel-mode is batch-only.
- When m4max is home and on LAN, mode detector flips it to LAN mode and OpenClaw begins routing real-time heavy-reasoning jobs to it.
---
## 5. Storage Architecture
**Originals are immutable.** All processing writes new files to a parallel tree. Metadata is stored separately so it can be regenerated without touching photos.
```
/photos/
  originals/
    2026-05-09-cruise/
      IMG_1234.CR2
  derivatives/
    2026-05-09-cruise/
      tagged/
      cropped/
      enhanced/
      web/
  metadata/
    2026-05-09-cruise/
      IMG_1234.json    (pipeline status, AI tags, scoring)
      IMG_1234.xmp     (Lightroom-compatible sidecar)
```
**MinIO buckets on `m4mini`:**
- `models` — canonical model weights, replicated to m4max local SSD
- `photos-originals` — read-only after ingest
- `photos-derivatives` — pipeline outputs
- `audio-originals` — sermon recordings, voice notes
- `transcripts` — Whisper outputs
**MinIO bucket on `vps`** (small artifacts only):
- `coordination` — workflow definitions, configs, job manifests
- `results-archive` — finalized outputs the user wants reachable from anywhere
Model files live on `m4mini` MinIO and on `m4max` local SSD (cached). They are never shipped through the VPS.
---
## 6. Scheduler / Routing Logic
Routing logic lives **on `m4mini`** inside OpenClaw, not on the VPS. The VPS holds only the queue and the routing-rules config; it never makes per-request decisions.
### Pseudocode
```python
def route(task):
    # Real-time path
    if task.mode == "interactive":
        node = pick_realtime_node(task.class)
        return direct_call(node, task)
    # Batch path
    topic = topic_for_class(task.class)
    nats.publish(topic, task)
    return queued(task.id)
def pick_realtime_node(task_class):
    candidates = capable_nodes(task_class)
    # Prefer node with model already resident
    warm = [n for n in candidates if model_resident(n, task_class)]
    if warm:
        return least_loaded(warm)
    # Fall back to capable but cold node
    available = [n for n in candidates if reachable(n, latency_ms_max=5)]
    if not available:
        # Degrade gracefully: queue it instead
        nats.publish(topic_for_class(task_class), task)
        return queued(task.id)
    return least_loaded(available)
```
### Task class to preferred node
| Task class | Preferred | Fallback | Notes |
|------------|-----------|----------|-------|
| `general` (7B/8B chat) | `m4mini` | `m3pro` | Default path |
| `code` | `m3pro` | `m4mini` | Code-specialized models |
| `heavy_reasoning` (70B) | `m4max` (LAN mode only) | queue for batch | Never block real-time on m4max |
| `vision.tag` | `m4mini` | `m3pro` | LLaVA |
| `whisper.transcribe` | `m3pro` | `m2mini` | M4 mini reserved for chat |
| `embed` | `m4mini` | `m2mini` | Small model, replicated |
| `image.generate` | `m4max` (LAN mode) | queue for batch | SDXL, batch-only when traveling |
### Model warm-state tracking
Each Ollama/MLX worker reports `loaded_models` to the VPS heartbeat every 30 seconds. The scheduler reads this when deciding placement so cold starts don't dominate latency.
### Mode detection (m4max LAN vs Travel)
The mode detector on `m4max` does **not** flip modes on a single latency reading. Hotel wifi and cellular hotspots produce wildly variable single samples. Use a hysteresis window:
- Sample latency to `m4mini` over Tailscale every 30 seconds.
- Track packet loss percentage and median latency over the last 5 samples.
- Switch to **LAN mode** only after 3 consecutive samples show latency < 5 ms and loss = 0%.
- Switch to **Travel mode** after 3 consecutive samples show latency > 50 ms or any loss > 0%.
- In between, hold the current mode. Flapping between modes is worse than being slightly stale in either direction.
### Model contention on `m4mini`
`m4mini` is the brain and is also targeted for chat, LLaVA tagging, and embeddings. Running all three large models concurrently will cause Ollama to thrash on load/unload. For Phase 2, start with **one large model resident at a time**: either chat-mode (Llama 3.1 8B + small embedding model) or LLaVA-mode (LLaVA-1.6 13B + small embedding model), and switch by config rather than serving both simultaneously. Revisit only after measuring actual usage patterns.
---
## 7. Partition Rules
Three failure modes will happen often. The system handles each explicitly.
**`m4max` offline (frequent).** LAN cluster serves all real-time work using 7B/8B models. Heavy-reasoning real-time requests degrade to "best available smaller model" with a flag in the response, or are queued for when m4max returns. Per-task-class default is configured in OpenClaw.
**LAN ↔ VPS link flaky (occasional).** LAN keeps serving real-time. Batch publishes buffer locally on `m4mini` until VPS is reachable; on reconnect, buffered messages flush in order. NATS client handles this natively with reconnect logic.
**VPS down entirely (rare).** LAN keeps serving real-time. New batch jobs queue locally on `m4mini` (in-memory, not durable) until VPS returns. Document as accepted: VPS-down means batch durability is suspended, not that the system is down.
**`m4mini` down.** This is the only true single-point-of-failure. Real-time inference stops; m3pro can serve as fallback if OpenClaw is replicated (Phase 4 work, not v1). Accept this for v1.
---
## 8. Constraints
### Must
- All inference runs natively on macOS with Metal acceleration.
- All OpenClaw endpoints require bearer-token authentication from Phase 1 onward. Tokens live in the macOS Keychain on every caller and on the OpenClaw host. Tailscale gates devices, not processes; bearer auth is the application-level guarantee.
- All scripture associations require human review. The system **never auto-publishes Scripture associations** under any circumstance. This is a doctrinal constraint, not a technical one, and it is enforced at the manifest loader (see Section 9).
- Tool discovery scans only `/tools/` and the top-level `openclaw-tools.yaml` in the ken repo. Everything else in the repo (`.claude/skills/`, generated outputs, CSVs, sermon files) is invisible to OpenClaw.
- All `destructive` and `external` tool calls emit an audit record to the `tool.audit` NATS subject (durable). `safe` calls may opt in.
- Batch jobs that publish a tool call pin the manifest commit SHA at queue time. Workers refuse to execute against a different SHA unless explicitly re-authorized.
- All disclaimers and accessibility commitments from the parent project (cruisinginthewake.com et al.) carry forward to any user-facing output.
- Originals (photos, audio, source documents) are immutable. Pipelines write derivatives to parallel trees.
- Idempotency: every workflow stage records status before acknowledging. Reruns are safe.
### Must not
- No inference inside containers on macOS (loses Metal).
- No model files on the VPS (bandwidth and disk).
- No vLLM on Apple Silicon (no production Metal backend as of this writing — verify before assuming otherwise).
- No Ray (wrong abstraction for these workloads; NATS + workers covers the need).
- No k3s in v1 (overkill for four nodes, two of which sleep).
- No Scripture text overlaid on images by automated process.
- No publishing of pastoral or family-history content without explicit human approval step.
---
## 9. Tool Integration via Ken Repository
OpenClaw exposes tools sourced from a single canonical GitHub repository: the user's `ken` repo. This makes Ken's accumulated automation directly available to the AI system without copying or reimplementation. The repo is the source of truth for tool surface area; OpenClaw only registers what the repo declares.
### Repository placement
- Cloned to `m4mini` at `/opt/openclaw/tools/ken-repo` (or `~/openclaw/tools/ken-repo` if running OpenClaw under the user account rather than as a system service — confirm during install).
- Read-only from OpenClaw's perspective. All updates come from `git pull`. OpenClaw never writes to the working tree.
- Pulled on schedule (every 15 minutes via `launchd` or cron). Webhook-driven pulls are deferred past v1; if added later, the receiver must verify the GitHub HMAC signature with the webhook secret. v1 relies on polling.
- v1 tracks the `main` branch. Merges to `main` are gated by the user. A separate `openclaw-release` branch with signed-commit requirement is a Phase 4 concern, not v1.
### Authentication
- Deploy key (SSH) on `m4mini` with read access to the `ken` repo.
- Private key stored in the macOS Keychain, referenced by ssh-agent. Not committed, not in env files, not in plain config.
- No GitHub PAT in environment variables.
### Tool discovery
OpenClaw scans the cloned repo on startup and after each successful pull. Discovery is **strictly limited** to:
- The top-level `openclaw-tools.yaml` manifest, and
- Files referenced by manifest entries (typically under a `tools/` directory).
Nothing else in the repo is read or registered. `.claude/skills/` is out of scope (those are Claude Code prompt assets, not callable executables). Generated outputs, data files, and the orchestrator source tree are likewise invisible to the loader unless explicitly referenced from a manifest entry.
Each manifest entry declares: `name`, `description`, `input_schema`, `executor` (CLI command or Python entry point), `execution_class` (`safe | destructive | external`), `requires_human_confirmation` (bool), `audit_log` (`required | optional`), `timeout_seconds`, and optional `node_hint`, `daily_spend_limit_usd`, `subprocess_env_keys`, `external_endpoints`.
Surface area is opt-in. The repo is the source of truth for what OpenClaw can do.
### Execution model
- **Python tools:** imported as modules, invoked in-process within OpenClaw. Lower overhead, shared logging, but tools must not pollute global state.
- **Shell or binary tools:** spawned as subprocesses with the working directory set to the repo root, captured stdout/stderr, enforced `timeout_seconds`.
- **Node-pinned tools:** if a tool declares `node_hint: m3pro` (etc.), OpenClaw publishes a `tool.exec.<node>` message to NATS rather than running locally. The target node's worker subscribes and executes.
### Execution classes
Every tool declares an `execution_class`. OpenClaw enforces different rules per class:
- **`safe`** — read-only or sandboxed operations (file reads, queries, formatting, transformations). Runs without confirmation. Default for new tools.
- **`destructive`** — modifies user-owned local state (writes files outside `/tmp`, deletes, moves, irreversible local changes). Requires explicit confirmation per call.
- **`external`** — touches APIs, public systems, or anything beyond the local machines (publishes to a website, sends email, posts to social, hits a paid API). Requires explicit confirmation per call AND must log the call to the durable results-archive on the VPS.
A tool with `requires_human_confirmation: true` always confirms regardless of class. A tool may not be both `safe` and touch external systems — that combination is a manifest error and the loader rejects it.
### Confirmation channel
For **real-time** tool calls (caller is a human-facing agent like Claude Code with an inline conversation), confirmation is requested in-band: OpenClaw returns a pending status with the prompt text, the caller surfaces it to the user, the user approves or rejects, and the call proceeds or aborts.
For **batch** tool calls (NATS-triggered, no human in the loop — the 3 a.m. case), v1 behavior is **fail-closed**: any tool that requires confirmation returns immediately with status `needs_human_confirmation`, the call does not proceed, and the audit record reflects the rejection. The job stays in the queue or moves to a `pending_review` topic depending on the workflow. A push/email notification system or approval queue is a Phase 4 concern. v1 does not block batch jobs waiting for a human and does not auto-approve them.
### Audit log
A durable NATS subject `tool.audit` receives one record per tool call, regardless of node:
```json
{
  "tool": "consult",
  "execution_class": "external",
  "node": "m4mini",
  "manifest_sha": "a1b2c3...",
  "ts": "2026-05-09T10:00:00Z",
  "input_hash": "sha256:...",
  "status": "success | failed | needs_human_confirmation | refused | daily_cap_exceeded",
  "duration_ms": 1240,
  "cost_estimate_usd": 0.04
}
```
The manifest field `audit_log: required | optional` controls whether `safe` calls are logged. The loader **forces `required`** for any tool with `execution_class: destructive` or `external`, regardless of what the manifest declares. Bad manifests don't get to opt out of the audit trail for risky calls.
### Spend caps (`external` tools)
Every `external` tool must declare `daily_spend_limit_usd` in its manifest. OpenClaw aggregates per-tool spend from the audit log's `cost_estimate_usd` field and refuses calls that would exceed the cap, returning status `daily_cap_exceeded`. Default cap if unspecified: `5`. Cap resets at midnight local time. Caps apply per-tool; a global aggregate cap is a Phase 4 concern.
For v1, cost estimation can be coarse — a declared per-call cost in the manifest is acceptable; refining to actual token-based metering is a follow-up. The point is to make a runaway batch worker hit a wall, not to perfectly bill.
### Manifest validation (loader-enforced)
The manifest loader rejects any manifest that violates these rules. Rejection means the previous registry stays in effect; bad commits do not silently degrade the system.
- A tool with `execution_class: external` must declare `daily_spend_limit_usd`.
- A tool with `execution_class: external` must have `audit_log: required` (or unset, which the loader fills in).
- A tool whose name matches `publish_*`, or whose `external_endpoints` include any host considered a public-facing surface (configured allowlist), must have `requires_human_confirmation: true`. This is the mechanical enforcement of the doctrinal "no auto-publish Scripture" constraint from Section 8 — the loader will not register a `publish_to_cruising_in_the_wake` tool that lacks the flag.
- A tool with `execution_class: safe` that declares any `external_endpoints` is rejected. If it touches the network, it is `external`, not `safe`.
### Subprocess secrets injection (orchestrator-as-tool pattern)
Tools that exist outside OpenClaw's process — subprocesses, shell scripts, the existing orchestrator under `orchestrator/` — often have their own secret-loading pattern (`.env` files, project-local config). **Don't migrate them.** That breaks standalone use and other repos that depend on the existing pattern.
Pattern: OpenClaw reads required secrets from the macOS Keychain (e.g., `OPENAI_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY`, `PERPLEXITY_API_KEY`) and injects them into the subprocess environment when spawning. The subprocess sees env vars as if they came from its usual `.env` loader. The tool's own `.env` mechanism stays in place for direct human invocation. Two paths, same code, no migration.
The manifest declares `subprocess_env_keys: [OPENAI_API_KEY, XAI_API_KEY, ...]` so OpenClaw knows which Keychain items to fetch and inject for that tool.
### Hot reload
- On a successful `git pull` showing changes to manifest or tool files, OpenClaw rebuilds its tool registry without restart.
- In-flight tool calls finish on the old version; new calls use the new version.
### Constraints
- Tools execute with OpenClaw's user privileges. Do not register tools that need root.
- Tools must be safe to retry (idempotent or stateless). Long-running stateful operations belong in NATS workflows, not tool calls.
- Any tool that touches a public production site (e.g., cruisinginthewake.com) must require an explicit human-in-the-loop confirmation step, per the project's existing stewardship principles. The manifest field `requires_human_confirmation: true` enforces this.
- Secrets needed by tools (API keys, etc.) come from the macOS Keychain, never from the repo itself.
### What Claude Code should build for this section
When Claude Code implements this:
1. A `tool_loader.py` module in OpenClaw that handles repo scan, manifest parse, validation (per the loader-enforced rules above), and registry rebuild on hot reload.
2. A `git_sync.py` module that handles scheduled pulls. Webhook endpoint deferred past v1.
3. A small `openclaw-tools.yaml` example committed to the `ken` repo demonstrating one tool of each `execution_class` (Python in-process `safe`, shell subprocess `destructive`, orchestrator wrapper `external`).
4. A `keychain.py` helper for reading deploy-key path, bearer tokens, and tool secrets from macOS Keychain.
5. A `subprocess_runner.py` that spawns external tools with Keychain-injected env vars per `subprocess_env_keys`.
6. An `audit.py` module that publishes to `tool.audit` and tracks per-tool daily spend for cap enforcement.
7. **End-to-end Phase 2 test:** a `hello-world` tool published in the repo, pulled, registered, and callable via OpenClaw. Returns `{"ok": true, "node": "<hostname>", "git_sha": "<manifest_sha>"}`. The git_sha return is a free check that hot-reload pinning works — call before and after a manifest change and confirm the SHA flips on new calls but not on in-flight ones.
---
## 10. Build Plan
### Phase 1 — This Saturday (LAN-only proof of life)
Goal: prove m4mini + m3pro can serve interactive inference with intelligent routing.
1. Install Tailscale on m4mini and m3pro. Verify `tailscale status` shows both. Confirm MagicDNS works.
2. Install Ollama natively on both nodes. Pull `llama3.1:8b` on m4mini, `qwen2.5-coder:7b` on m3pro.
3. Generate a bearer token, store it in macOS Keychain on m4mini under item `openclaw_api_token`, and on every calling device under the same item name.
4. Write the OpenClaw stub on m4mini that exposes `POST /chat` and routes by task class to the right Ollama instance. Plain Python with `httpx`. **Bearer-token middleware on every endpoint** — reject anything without a valid `Authorization: Bearer <token>` header. No queue yet. Expect this to grow from ~100 lines to 250–300 once streaming, timeouts, and error fallback are added; that's normal.
5. Test from a third device on the tailnet: chat hits m4mini, code hits m3pro, both stream tokens, both reject calls without the bearer token.
6. Configure `caffeinate` on m3pro to prevent sleep when on AC.
Success criterion: end-of-day Saturday, you can ask the system a code question from your phone and watch m3pro do the work.
### Phase 2 — Next week (VPS coordinator + batch path + tool integration)
1. Install NATS JetStream on the VPS. Verify it doesn't conflict with AdGuard. Configure JetStream explicitly: enable persistent streams, set `AckExplicit` ack policy on every consumer, set message retention to at least 24 hours (or work-queue policy with explicit ack). Defaults will silently drop messages — do not rely on them.
2. Install MinIO on m4mini. Create the buckets listed in Section 5.
3. Add NATS publish/subscribe to OpenClaw. Wire up a single batch path: photo tagging.
4. Build the photo pipeline MVP (see Appendix A).
5. Wire up Ken-repo tool integration on m4mini per Section 9: deploy key, clone, manifest scan, manifest validation, hot reload, audit log subject (`tool.audit`), commit-SHA pinning at queue time, and the end-to-end `hello-world` tool that returns `{ok, node, git_sha}`.
6. Add the orchestrator to the manifest as four `external` tools (`consult`, `orchestrate`, `orchestra`, `investigate`) with subprocess Keychain injection per Section 9. Set conservative `daily_spend_limit_usd` per tool — start at $5 each, raise after observed usage.
### Phase 3 — When stable (m2mini + m4max integration)
1. Bring m2mini onto the tailnet. Install Ollama with a small model. Subscribe to overflow topics.
2. Bring m4max onto the tailnet. Install heavy models locally. Implement mode detector (LAN vs travel).
3. Add m4max as opportunistic worker for `heavy_reasoning` and `image.generate`.
### Phase 4 — Hardening (after the system is in daily use)
- OpenClaw replication for m4mini failover.
- Prometheus + Grafana on VPS.
- Authentication on inference endpoints (bearer tokens).
- Backup strategy for MinIO.
- Workflow library evaluation (Prefect or Temporal) — only if plain async Python becomes painful.
---
## Appendix A — Photo Pipeline (First Concrete Workload)
### Pipeline stages (in order)
```
ingest → hash/dedupe → score/filter → tag → crop → enhance → export
```
Hash before score, score before tag. Burst shooting produces near-identical frames that scoring alone won't catch; perceptual hashing eliminates them before any compute is spent on them. Then scoring filters out blur and bad exposure. Only what survives both gates reaches LLaVA.
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
`scripture_suggestions` is always null in v1. If/when added, it returns *themes only* (e.g., `["creation", "stillness"]`) — never verse text, never pairings, never overlays.
### Pipeline branching
Every image carries a `pipeline` field: `cruise` or `personal`. Workers branch on this:
- `cruise` → polished tags, web-ready exports, SEO-aware caption, XMP sidecar
- `personal` → archival tags, family-context metadata, no web export
### MVP scope (Phase 2)
Build only:
1. Folder watcher on m4mini (`watchdog` library)
2. Publish to `photo.ingest`
3. Scoring worker on m3pro (Laplacian variance + histogram)
4. Tagging worker on m4mini (LLaVA-1.6 13B Q4 — verify RAM headroom first)
5. Status JSON written to `metadata/` per image
**Defer until MVP is in daily use:** crop suggestions, SDXL enhancement, web export, UI.
### Models and RAM budget (verify on first run)
- LLaVA-1.6 13B Q4 ≈ 8 GB resident. M4 mini with 16 GB is tight if running other models simultaneously. Consider 24 GB+ M4 mini, or run LLaVA exclusively on this node.
- LLaVA-1.6 34B Q4 ≈ 20 GB resident. Only if M4 mini has 32 GB+ and no co-resident models.
These numbers are from public model cards and should be verified empirically on first load.
---
## Appendix B — Open Questions (validate empirically)
- Exact M4 mini RAM SKU and headroom for co-resident models.
- Exact M4 Max RAM SKU (determines feasibility of 70B at full context).
- AdGuard's current port bindings on the VPS — confirm before adding services.
- Whether m4max's typical traveling network supports any usable Tailscale throughput, or whether it should be treated as fully offline most of the time.
- Whether existing photo cataloging tool (Lightroom? Apple Photos? bare folders?) needs XMP sidecar compatibility — design varies.
- Current structure of the `ken` GitHub repo: does it already follow a `tools/` convention or have a manifest? Does it contain Python modules, shell scripts, or both? On first pull, inspect and either confirm the manifest pattern proposed in Section 9 or adapt to what's actually there. Update this doc with a follow-up note once the answer is known.
---
## Footer
> Soli Deo Gloria — Every pixel and part of this project is offered as worship to God. The plans of the diligent lead surely to abundance, but the Lord establishes the steps. (Proverbs 21:5; 16:9)
