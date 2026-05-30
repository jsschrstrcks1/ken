---
name: ai-regression-testing
description: Catches drift in AI-touched artifacts that the AI itself wouldn't notice. Captures stable shape descriptors (SKILL.md frontmatter field sets, JSON schema top-level keys, markdown heading structure) for a set of artifacts, commits the shape as a baseline, and detects when later edits introduce shape drift. Cross-artifact path-parity check — multiple artifacts that should share a shape (every SKILL.md in a catalog, every orchestrator mode's state schema, every provenance record) are diffed against each other. CRITICAL finding when the same commit changes both an artifact and its baseline — the "agent moves the goalpost while moving the artifact" backdoor pattern.
version: 1.0.0
license: Unlicense
category: integrity
keywords:
  - ai-regression-testing
  - shape-parity
  - baseline-drift
  - regression-anchor
  - blind-spot
  - path-parity
  - detection-only
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(diff:*)
  - Bash(jq:*)
  - Bash(find:*)
  - Bash(ls:*)
  - Bash(wc:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git diff:*)
compatibility:
  claude-code: ">=2.1"
---

# AI Regression Testing

> When the same agent writes the artifact and writes the test, the test catches nothing. **This skill catches that.**

## Why this skill exists

A regression test is a tripwire across time: "this thing had this shape; tell me when it doesn't." But if the agent that edited the thing also edited the tripwire, the wire was never crossed. The whole point of a regression test is to be **external** to the work it watches. When an AI agent maintains both sides, you don't have a regression test — you have an AI marking its own homework.

This skill addresses that directly. The core mechanic is normal regression testing (capture shape → commit baseline → diff later); the twist is **the skill flags same-commit drift + baseline updates as CRITICAL.** If the agent edits the artifact and the baseline in one PR, the test isn't working — it's confirming the agent's new opinion of what the shape should be. That's the blind spot.

**Why detection-only.** Same logic as the rest of the household auditor family. A skill that auto-rebaselines is a skill that the agent could be persuaded to rebaseline at the wrong time. Baseline updates require an explicit, separately-reviewed commit with a human approval in the message. Structurally enforced by read-only `allowed-tools`.

## How to audit this skill before trusting it

1. **Verify `allowed-tools` is read-only.** `Read`, `Glob`, `Grep`, scoped `Bash` (`diff`, `jq`, `find`, `ls`, `wc`, `git log`, `git show`, `git diff`). No `Write`, no `Edit`, no `WebFetch`, no `Bash(*)`.
2. **Verify there is no `--rebaseline` / `--update-baseline` flag.** Same logic as `--ignore-stale` / `--auto-prune`. Rebaselining is a human decision committed deliberately, not a flag.
3. **Verify Stage 6 (same-commit-drift CRITICAL) is wired.** A test fixture: edit a SKILL.md to remove a frontmatter field AND edit `.regression-baselines/<id>.json` to remove the same field, both in one commit. Run the skill. It must report CRITICAL. If it reports PASS, the central guard is broken.
4. **Verify no auto-merge of "shape moved" suggestions.** Output is a markdown report with paths, diffs, and questions for the user. Output is **not** a generated patch the agent could apply.
5. **Verify the four verdict tiers are locked.** PASS / WARNINGS / ACCEPTED-RISK / FAIL. No fifth tier.
6. **Verify the baseline format itself can be audited.** Baselines are JSON files in `.regression-baselines/`. A baseline that's binary, compressed, or otherwise opaque is rejected — humans need to be able to read what they're approving.

## Scope: what counts as "an AI-touched artifact"

In-scope:
- `skills/*/SKILL.md` frontmatter field sets (every skill should share a stable frontmatter contract)
- `.claude/agents/*` definitions
- `.claude/commands/*.md`
- JSON Schema files (`schemas/*.json`) — top-level structure
- Provenance records (`schemas/records/*.json`) — required field shape
- Orchestrator mode state schemas (if present) — JSON keys returned per mode
- Recipe schema across recipe-site repos — if applicable
- API response shapes — if applicable

Out of scope:
- Code (use language-native test frameworks; pytest etc. catch code regressions)
- Free-prose content (READMEs, soul docs — use `doc-updater` for those)
- Logs, generated files, anything in `dist/`, `build/`, `node_modules/`
- Anything matching `*.generated.*`

## Stages

### Stage 1: Scope selection

For each repo, decide which artifact classes are in regression scope. Per the repo's `WORKING-CONTEXT.md` or `.regression-baselines/scope.md` if present. If neither is present, default scope is `skills/*/SKILL.md` frontmatter + `schemas/records/*.json` (the items the household ships and lifts).

The scope decision should be explicit, not implicit. The skill reports "scope: <list>" in every report — silent expansion of scope between runs is its own form of drift.

### Stage 2: Shape extraction

For each in-scope artifact, capture a **shape descriptor** — a structural summary that is stable under content edits but unstable under structural edits.

| Artifact class | Shape descriptor |
|---|---|
| `SKILL.md` | Sorted list of frontmatter field names; `allowed-tools` entries (sorted, deduped); top-level markdown headings (`## `) sorted |
| `schemas/records/*.json` | Sorted list of top-level JSON keys; sorted list of `audit.log` entry field names; `lift.type` enum value |
| `.claude/agents/*` | Frontmatter field names + first-level instruction headings |
| Orchestrator mode state JSON | Sorted list of top-level keys; nested key paths for one level deep |
| JSON Schema files | `required` array; sorted list of `properties` keys; `additionalProperties` value |

The shape descriptor is **deliberately coarser than the content**. A SKILL.md body can change every commit without triggering drift; the descriptor only changes when fields are added, removed, or reordered (and order-sensitivity is opt-in per artifact class).

### Stage 3: Baseline commit

Baselines live at `.regression-baselines/<artifact-id>.json`:

```
.regression-baselines/
├── scope.md                              ← in-scope declaration
├── skills/
│   ├── careful-not-clever.json
│   ├── doc-updater.json
│   └── ...
└── schemas/
    └── records/
        ├── opensource-sanitizer.json
        └── ...
```

Each baseline is a JSON file the human can read. No binary, no compression, no hashing-only — when a future human reviews "baseline update for opensource-sanitizer," they see what fields are claimed at baseline.

**Baselines are committed.** They live in version control. Rebaselining requires a deliberate commit; the commit message documents what shape moved and why.

### Stage 4: Drift detection

For each in-scope artifact:

- Re-extract the shape descriptor
- Diff against the committed baseline
- Classify the drift

| Drift type | Severity | What it means |
|---|---|---|
| Field present in baseline, missing from current | **HIGH** | Field was removed. Could be an intentional removal or an accidental deletion. The agent should not auto-update the baseline. |
| Field present in current, missing from baseline | **MEDIUM** | Field was added. Likely intentional; baseline should be updated in a *separate* commit with rationale. |
| Field present in both, value-shape changed (e.g., `allowed-tools` changed from list of 3 to list of 5) | **MEDIUM** | Surface-level signal. Look at the specific change. |
| Order changed (when order-sensitive) | **LOW** | Reordering usually harmless; flagged for awareness. |

### Stage 5: Path parity

For each artifact class that should share a shape across multiple instances, cross-check parity:

- All 9 SKILL.md files in `skills/` should share frontmatter fields: `name`, `description`, `version`, `license`, `category`, `keywords`, `allowed-tools`, `compatibility`.
- All provenance records in `schemas/records/` should have the same top-level keys (per the provenance schema's `required` list).
- All orchestrator mode state JSONs (if present) should return the same top-level keys.

A finding here means **multiple instances diverged from each other**, even if each individually matches its own baseline. This is the "sandbox vs prod schemas drifted" case from ECC, adapted to our artifact classes.

| Path parity finding | Severity |
|---|---|
| One artifact missing a field that ≥80% of peers have | **HIGH** |
| One artifact has a field that <20% of peers have (potentially erroneous addition) | **MEDIUM** |
| Subset of peers (40-60%) have a field; rest don't (catalog is in transition) | **LOW** — documented; not actionable until the household decides |

### Stage 6: Same-commit drift + baseline update — CRITICAL

The central blind-spot guard.

If the current commit (or staged changes) modifies BOTH:
- An in-scope artifact's shape descriptor, AND
- That artifact's `.regression-baselines/` file

…this is a **CRITICAL** finding. The agent (or human) has moved both sides of the tripwire in the same commit, and the regression test was never crossed.

Detection mechanic (read-only):
- For staged changes: `git diff --cached --name-only` — does the set include both an artifact under `skills/` (or other in-scope path) and its baseline under `.regression-baselines/`?
- For the most recent commit: `git log -1 --name-only` — same question.

The finding is CRITICAL because it represents the failure mode this skill exists to catch. The remediation is structural: **split into two commits.** Commit 1 changes the artifact. Commit 2 updates the baseline with a message explaining the shape move and (ideally) a human-author signoff.

Exception: the *first* commit that introduces both an artifact and its baseline (i.e., adopting a new skill into regression coverage) is not a Stage 6 finding — there's no previous baseline to "move." The skill detects this via baseline being a new file (`git log` shows no prior history) and downgrades the finding to INFO with note "initial baseline capture."

### Stage 7: Regression anchoring

When a real drift is fixed (e.g., a SKILL.md frontmatter accidentally lost its `compatibility` field and the field is restored), an entry should be added to `.regression-baselines/anchors.md`:

```markdown
## 2026-05-11 — compatibility field restored on doc-updater

**Drift class:** required frontmatter field absent
**Affected artifact:** `skills/doc-updater/SKILL.md`
**Detection:** Stage 4 HIGH — `compatibility` in baseline, missing from current
**Root cause:** [investigated reason]
**Anchored against future recurrence by:** keeping `compatibility` in the Stage 5 path-parity required set
```

This is the "tests grow alongside actual bugs" principle from ECC, adapted: anchors are markdown notes, not test fixtures. They tell future maintainers *why* the path-parity rules are what they are.

### Stage 8: Self-audit

**8.1 — Read-only `allowed-tools`.** Confirmed.
**8.2 — No silent skips.** Files in scope that couldn't be read surface as INFO findings.
**8.3 — Baseline format is human-readable JSON.** No binary, no compression.
**8.4 — No `--rebaseline` flag exists.** Verified by inspection of this SKILL.md.
**8.5 — Stage 6 same-commit-drift check runs unconditionally.** Cannot be opted out of per-artifact.

## Verdicts (four-tier, locked)

| Verdict | When |
|---|---|
| **PASS** | 0 findings |
| **PASS WITH WARNINGS** | LOW and/or MEDIUM findings only |
| **PASS WITH ACCEPTED RISK** | HIGH findings with documented "accept this drift because X" rationale in the report |
| **FAIL** | Any CRITICAL finding (Stage 6 same-commit drift) — OR HIGH findings without written acceptance |

CRITICAL has exactly one source in this skill: **Stage 6 same-commit drift + baseline update**. No other finding category produces CRITICAL. This focus is deliberate: when the central guard fires, the user should know it's *that* guard, not generic noise.

## Output

The skill describes a `REGRESSION_REPORT.md` that the calling agent's `Write` tool materializes; the skill itself never writes.

```markdown
# AI Regression Report

**Date:** YYYY-MM-DD
**Repo:** <repo>
**Branch:** <branch>
**Auditor:** ai-regression-testing v1.0.0
**Scope:** skills/*/SKILL.md frontmatter + schemas/records/*.json

## Stage results

| Stage | Findings |
|---|---|
| 1 | Scope: N artifact classes, M artifacts total |
| 2 | M shape descriptors extracted |
| 3 | M baselines compared (or "K artifacts have no baseline — initial-capture INFO") |
| 4 | A HIGH, B MEDIUM, C LOW |
| 5 | Path parity: X HIGH, Y MEDIUM, Z LOW |
| 6 | Same-commit drift: PASS / CRITICAL |
| 7 | Anchors file: present (N entries) / absent |
| 8 | Self-audit: PASS |

## Findings (severity-ranked)
...

## Verdict
**PASS** / **PASS WITH WARNINGS** / **PASS WITH ACCEPTED RISK** / **FAIL**

## Self-audit checklist
- [x] allowed-tools is read-only
- [x] No rebaseline flag was used
- [x] Stage 6 same-commit-drift check ran unconditionally
```

## Backdoor defenses (5 PR-rejection patterns)

This skill is the **canary on the AI-marking-its-own-homework problem**. Any PR that weakens its central guard is a high-severity rejection.

1. **A `--rebaseline` / `--update-baseline` / `--auto-fix` flag.** Rebaselining is a *deliberate human commit*, not a CLI toggle. Reject.
2. **Removing the Stage 6 same-commit-drift check.** This is the skill's reason for existing. Removing it is the same as removing the skill. Reject.
3. **Allowing binary or compressed baselines.** Baselines must be human-readable. A hash-only baseline that says "the shape is `8a3f...`" is unauditable. Reject.
4. **A fifth verdict tier.** Four tiers, locked.
5. **Network egress.** No `WebFetch`, no `curl`. The baselines and diff are local; no telemetry. Reject.

## What this skill is intentionally NOT

- **Not a unit-test framework.** Pytest, vitest, etc. catch code regressions; this catches *artifact-shape* regressions. Different layer.
- **Not a property-based tester.** No fuzzing, no generation of inputs. Static shape diff only.
- **Not a continuous monitor.** Runs on demand or as part of a pre-commit / pre-PR check. Snapshot at a point in time.
- **Not an auto-fixer.** Detection only. The user decides whether to update the artifact or update the baseline (in a separate commit).
- **Not a substitute for `harness-auditor`.** Harness-auditor finds *current* config problems. This skill finds *drift over time* in any AI-touched artifact. Both should run before a release.
- **Not a substitute for `doc-updater`.** Doc-updater compares docs to *current* filesystem ground truth. This skill compares artifacts to a *committed historical baseline*. Different question.

## Worked example: baseline for open-claw-stuff's skill frontmatters

After this skill ships, the initial baseline for the 9 skills in `open-claw-stuff/skills/` will be committed at `.regression-baselines/skills/<name>.json`. Each file looks like:

```json
{
  "id": "doc-updater",
  "artifact-path": "skills/doc-updater/SKILL.md",
  "captured-at": "YYYY-MM-DD",
  "captured-in-commit": "<sha>",
  "shape": {
    "frontmatter-fields": ["name", "description", "version", "license", "category", "keywords", "allowed-tools", "compatibility"],
    "allowed-tools": ["Read", "Grep", "Glob", "Bash(grep:*)", "..."],
    "top-level-headings": ["Why this skill exists", "...", "Inspiration"]
  }
}
```

A future agent that adds a `vendor` field to one SKILL.md without updating the baseline trips Stage 4 MEDIUM. A future agent that adds `vendor` to the SKILL.md AND to the baseline in one commit trips Stage 6 CRITICAL.

## Inspiration and design provenance

Concept-lifted from `affaan-m/everything-claude-code`'s `skills/ai-regression-testing/` (MIT). Intentional departures:

| ECC | Ours |
|---|---|
| Tests AI-written application code | Tests **shape stability** of AI-touched artifacts (skill frontmatters, provenance records, orchestrator mode schemas) — household has no production app code in this catalog |
| Path parity: sandbox vs prod schemas | Path parity: 9 SKILL.md frontmatters in a catalog; N provenance records under one schema |
| Tests grow alongside bugs (test cases) | Anchors grow alongside drift (markdown notes in `.regression-baselines/anchors.md`) |
| Implicit baseline (whatever the test asserts) | Explicit committed JSON baseline; rebaselining is a separate commit |
| No "same-commit drift" guard | **Central guard:** Stage 6 CRITICAL when the same commit touches both an artifact and its baseline — the "agent marks its own homework" failure mode |
| No threat-model | 5-pattern backdoor-defenses: reject rebaseline flags, reject Stage 6 removal, reject opaque baselines, reject fifth verdict tier, reject network egress |

This is a `concept-only` lift per the provenance schema. ECC's *insight* about AI testing blind spots ports directly; the *implementation* is independent and addresses the household's artifact-shape stability rather than app-code regression.
