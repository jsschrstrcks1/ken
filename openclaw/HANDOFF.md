# OpenClaw Build — Handoff

> **PIVOT NOTICE:** OpenClaw is an existing third-party project
> (`github.com/openclaw/openclaw`), not a runtime we are building. The
> current canonical plan is **`MASTER_PLAN.md`** (v2.0.0) in this
> directory. `ARCHITECTURE_v1.md` is historical and labelled as such at
> its top — do not follow it.
>
> If you are an AI session picking this up to set up OpenClaw on
> m4mini: read `MASTER_PLAN.md` Section 0 first. It tells you what to
> read before writing any code.

## What Was Done (in this repo)

- `openclaw-tools.yaml` at repo root: top-level manifest, the single discovery surface OpenClaw will read. Seven tools across three execution classes:
  - `hello_world` (safe) — Phase 2 smoke test.
  - `consult`, `orchestrate`, `orchestra`, `investigate` (external) — orchestrator wrappers, $5/day cap each, `subprocess_env_keys` for Keychain injection.
  - `sync_clock`, `tz_wakeup` (destructive) — local utilities, confirmation required.
- `tools/hello-world/hello.py`: returns `{ok, node, git_sha}`. SHA from `OPENCLAW_MANIFEST_SHA` env var (set by OpenClaw at spawn) or `git rev-parse HEAD` fallback.
- `openclaw/ARCHITECTURE_v1.md`: full v1 architecture spec.
- `openclaw/MULTI_REPO_EXTENSION.md`: forward-looking notes for extending OpenClaw to the other 8 repos. Not part of v1.
- Smoke test passes locally: `python3 tools/hello-world/hello.py` returns valid JSON.

## What Still Needs Doing (on m4mini, separate repo)

OpenClaw itself doesn't exist yet. It needs to be built on m4mini in its own repository (not in `ken`). Per Section 9 of the architecture doc, that repo needs:

1. `tool_loader.py` — repo scan, manifest parse, validation per the loader-enforced rules in Section 9, registry rebuild on hot reload.
2. `git_sync.py` — scheduled `git pull` every 15 min via `launchd` or cron. No webhook in v1.
3. `keychain.py` — read deploy-key path, bearer tokens, and tool secrets from macOS Keychain.
4. `subprocess_runner.py` — spawn external tools with Keychain-injected env vars per `subprocess_env_keys`.
5. `audit.py` — publish to `tool.audit` NATS subject, track per-tool daily spend.
6. The `POST /chat` Phase 1 stub with bearer-token middleware on every endpoint.

When that repo is set up, hand it `openclaw/ARCHITECTURE_v1.md` and the existing `openclaw-tools.yaml` from this repo. The manifest is the contract; OpenClaw should make this hello-world tool callable as the Phase 2 smoke test.

## Pi infrastructure additions (v2.0.1)

Three Raspberry Pis joined the architecture:
- `rpi5` (Pi 5 8GB) — NATS replica + Prometheus scrape. PCIe slot reserved for AI HAT+ if vision pre-screen becomes worth it.
- `rpi4a` (Pi 4B 8GB) — photo ingest worker (folder watch + pHash + dedupe). USB SSD staging.
- `rpi4b` (Pi 4B 8GB) — scheduled jobs + hot spare.

3-node JetStream cluster (vps + rpi5 + m2mini) preserves batch durability under any single-node loss. The vision pre-screen stage (HAT-accelerated YOLO pre-classification before LLaVA) is documented in `MASTER_PLAN.md` Appendix A but is **deferred** to Phase 6 — a measurement-driven buy decision after the photo pipeline runs in daily use, not a speculative purchase.

## Anthropic ToS Compliance (hard requirements)

`CLAUDE.md` now contains a top-level "OpenClaw Integration — Anthropic ToS Hard Requirements" section. Read it before any OpenClaw work. The short version:

- API key only (`sk-ant-...` from `console.anthropic.com`). Never Claude.ai subscription OAuth.
- Single-user, single-tenant. No public endpoint, no other-person access.
- Agentic skills require `requires_human_confirmation: true`.
- No auto-publish of pastoral/Scripture/family-history content.
- Don't use "Claude" as a product/skill name — runtime is "OpenClaw."
- Every Anthropic call produces a `tool.audit` record.

These derive from Anthropic's Usage Policy, Commercial Terms, and Consumer Terms. They override convenience.

## Key Decisions (don't revisit)

- Bearer-token auth from Phase 1, not Phase 4. Tailscale gates devices, not processes.
- Tool discovery scans only top-level `openclaw-tools.yaml` and files it references. `.claude/skills/` is invisible to OpenClaw.
- Branch tracked: `main`. Merges gated by the user. Stricter branch (`openclaw-release` with signed commits) is a Phase 4 concern.
- Webhook deferred past v1 — 15-minute pull only.
- Confirmation channel: in-band for real-time callers; **fail-closed `needs_human_confirmation`** for batch (3 a.m. case). No notification system in v1.
- Spend caps: per-tool daily, default $5. Global cap is Phase 4.
- Audit log to `tool.audit` NATS subject, durable. Loader forces `audit_log: required` for `destructive` and `external`.
- Orchestrator stays as-is. OpenClaw injects Keychain-fed env vars when it spawns; orchestrator's own `.env` flow stays unchanged for direct human invocation.
- Multi-repo extension is forward-looking. v1 is ken-only. See `MULTI_REPO_EXTENSION.md` when adopting.

## Files Created/Modified

```
openclaw-tools.yaml                  (new, top-level)
tools/hello-world/hello.py           (new, executable)
openclaw/ARCHITECTURE_v1.md          (new)
openclaw/MULTI_REPO_EXTENSION.md     (new)
openclaw/HANDOFF.md                  (this file)
```

Nothing modified outside `openclaw/`, `tools/`, and the new top-level manifest. Existing repo content (orchestrator, keeper, .claude/skills, etc.) is untouched.

## Known Doc Bug to Fix

`ARCHITECTURE_v1.md` Phase 4 still lists "Authentication on inference endpoints (bearer tokens)" as a hardening item, but Phase 1 now mandates it. Drop that bullet on the next doc revision.

## Doc Source-of-Truth Note

The canonical architecture doc lives in the user's Claude Project folder (`~/Documents/Claude/Projects/OpenClaw distributed ai system on mac cluster/ARCHITECTURE_v1.md`). The copy in this repo is a snapshot of v1.000.000. When the doc is revised there, push the update to this repo so OpenClaw sessions referencing it stay in sync.

## How to Resume

If you're picking this up to build OpenClaw on m4mini:

1. Read `openclaw/ARCHITECTURE_v1.md` end to end. Section 9 is the contract.
2. Read `openclaw-tools.yaml` at the repo root — that's what your `tool_loader.py` must parse.
3. Run `python3 tools/hello-world/hello.py` here — that's the Phase 2 success criterion (your loader pulls this file, your runner spawns it, your audit module records the call).
4. Build OpenClaw in its own repo on m4mini per the seven items under "What Still Needs Doing."

If you're picking this up to add another repo to OpenClaw:

1. Read `openclaw/MULTI_REPO_EXTENSION.md`.
2. Don't start until ken-only is in stable daily use.
3. Decide which repos expose tools at all — most of the nine probably shouldn't.

Delete this file when v1 is in daily use and the OpenClaw repo on m4mini has its own handoff.
