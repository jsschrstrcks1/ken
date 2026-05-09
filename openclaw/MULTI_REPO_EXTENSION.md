# OpenClaw Multi-Repo Extension Notes

**Status:** Forward-looking. v1 ships ken-only. Adopt this when ken-only is in stable daily use (Phase 3 or later).

The v1 architecture (`ARCHITECTURE_v1.md`) treats the ken repo as the single source of OpenClaw tools. The user has nine repos total. Most of the v1 primitives are per-tool, not per-repo, so extending to additional repos is mechanical, not a redesign.

---

## What Changes

### 1. Repos config on m4mini

A new file alongside OpenClaw config lists every repo OpenClaw pulls from:

```yaml
# openclaw-repos.yaml (lives on m4mini, not in any repo)
repos:
  - name: ken
    url: git@github.com:jsschrstrcks1/ken.git
    branch: main
    deploy_key: keychain://openclaw_deploy_key_ken

  - name: cruisinginthewake
    url: git@github.com:jsschrstrcks1/cruisinginthewake.git
    branch: openclaw-release        # stricter — fast-forward by hand
    deploy_key: keychain://openclaw_deploy_key_citw
    allowed_execution_classes: [safe]   # optional per-repo policy
```

`git_sync.py` loops over the list. `tool_loader.py` scans each repo's top-level `openclaw-tools.yaml` and merges results into one registry.

### 2. Tool name namespacing

Pick the convention now to avoid retrofitting later. Recommendation: **`<repo>.<tool>` qualified names** (e.g., `ken.consult`, `cruisinginthewake.publish_post`).

- Unqualified call (`consult`) resolves only if the name is globally unique.
- Loader rejects unqualified calls when two repos declare the same tool name.
- Manifest entries themselves stay unqualified — the loader prepends the repo name.

### 3. Deploy keys

One key per repo on m4mini, each stored in Keychain under a distinct item name. SSH agent holds them all; `git_sync` references the right key per repo via `GIT_SSH_COMMAND`. Blast radius if a key leaks is one repo, not nine. Matches GitHub's deploy-key best practice.

### 4. SHA pinning becomes a map

Job manifests carry a per-repo SHA map at queue time:

```json
{
  "tool": "cruisinginthewake.publish_post",
  "manifest_shas": {
    "cruisinginthewake": "abc123",
    "ken": "def456"
  }
}
```

Workers check the relevant SHA at execute time. Mostly a serialization change.

### 5. Audit log gains a `repo` field

```json
{
  "repo": "cruisinginthewake",
  "tool": "publish_post",
  "execution_class": "external",
  "...": "..."
}
```

One additional field in the existing `tool.audit` JSON shape.

---

## What Doesn't Change

All Section 8 must-rules still hold per-tool, regardless of repo. Bearer auth, confirmation channel, spend caps, NATS topology, manifest validation, the orchestrator-as-tool pattern (subprocess Keychain injection) — all unchanged.

---

## Per-Repo Policy

Public-facing site repos (`cruisinginthewake`, anything with a deployed website) deserve stricter policy than `ken`. Two cheap mechanisms, layer them:

- **`branch: openclaw-release`** — separate branch fast-forwarded by hand. CI or Claude Code merges to `main` don't auto-ship to OpenClaw.
- **`allowed_execution_classes: [safe]`** — at minimum, blocks any `external` tool from that repo even if the manifest declares one. Pair with the existing name-pattern rule (`publish_*` requires confirmation, per Section 9 manifest validation) for defense in depth.

Repos that are pure content (sermons, photos, family-history records) don't get added to `openclaw-repos.yaml` at all. They aren't tool sources.

---

## Effort Estimate

- Generalize `git_sync.py`: ~30 lines
- Generalize `tool_loader.py` to merge N manifests + namespace: ~50 lines
- Add `repo` field to audit log: 1 line
- Per-repo deploy keys + Keychain entries: setup, not code
- New Section 9 subsection ("Multi-repo configuration") in `ARCHITECTURE_v1.md`: ~30 lines

Half a day on top of v1. Not a redesign.

---

## What to Decide Before Wiring Other Repos In

The harder question isn't technical:

1. **Which of the nine repos should expose tools at all?** Most are probably content, not automation.
2. **What should each one expose?** Default to nothing; whitelist deliberately.
3. **Which are public-facing?** Those get `openclaw-release` branch + `allowed_execution_classes: [safe]` at minimum.

Worth a separate sit-down before any repo gets added to `openclaw-repos.yaml`.
