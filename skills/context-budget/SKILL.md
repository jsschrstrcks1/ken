---
name: context-budget
description: Inventories the context-window load of a Claude Code project — CLAUDE.md, skills, agents, commands, hooks, MCP server schemas, plugin manifests, system reminders — and ranks components by approximate token weight. Detection only. Surfaces what's heavy, what's catalog-only (always loaded), and what's load-on-activation. Never auto-prunes; every recommendation requires explicit user action. Read-only against the local filesystem; no network egress.
version: 1.0.0
license: Unlicense
category: integrity
keywords:
  - context-budget
  - token-budget
  - context-window
  - skill-catalog-sprawl
  - mcp-bloat
  - context-pressure
  - inventory
  - detection-only
allowed-tools:
  - Read
  - Glob
  - Bash(wc:*)
  - Bash(find:*)
  - Bash(ls:*)
  - Bash(stat:*)
  - Bash(du:*)
compatibility:
  claude-code: ">=2.1"
---

# Context Budget

> The context window is a shared resource. **This skill tells you who's eating it.** It does not eat it back.

## Why this skill exists

Context-window pressure is silent. A repo accumulates skills, an MCP server adds tools, a CLAUDE.md absorbs a new section every week. Each addition is small. The cumulative load is what makes session-start slower, compaction more frequent, and instruction-following degrade as the agent has less headroom to think.

This skill is the inventory pass: read every component, estimate its token weight, classify by load class (always-loaded catalog entry vs load-on-activation body), and rank by weight. The output is a list of decisions for a human to make — not edits the agent applies.

**Why detection-only.** A skill that *both* inventories AND prunes context is a skill that can be made to prune the *wrong* things. The pruning decision is small, frequent, and judgment-laden — exactly the kind of decision that belongs with a human at a checkpoint, not an agent acting on a rubric. Detection + report + explicit human action is the separation; the same separation that opensource-sanitizer / harness-auditor / doc-updater / policy-as-markdown all enforce.

## How to audit this skill before trusting it

This skill reads the entire `.claude/` directory plus `CLAUDE.md` plus all skill/agent/command/hook files. **It has wide read access.** Apply operating principle #6:

1. **Verify `allowed-tools` is read-only.** No `Write`, no `Edit`. No `WebFetch`. No `Bash(*)`. The list should be `Read` / `Glob` / scoped `Bash` with prefixes only (`wc:*`, `find:*`, `ls:*`, `stat:*`, `du:*`).
2. **Verify no network egress.** A context-budget tool that "uploads its inventory to an analytics dashboard" is an exfiltration channel. Reject any PR adding `curl`, `WebFetch`, or `Bash(*)`.
3. **Verify the recommendations format is text-only.** The output is a markdown report. It should never include a generated shell script or a sequence of pre-baked `Edit` calls "to apply the recommendations" — that's exactly the bridge from detection to remediation we are refusing to cross.
4. **Test the formula against a known file.** `wc -c CLAUDE.md` divided by 4 should approximately match the skill's reported token count for `CLAUDE.md` (±20% for prose). If the skill claims significantly different counts without an explicit explanation, the formula has drifted.
5. **Verify no `--apply-recommendations` flag.** Same logic as `--ignore-stale` / `--skip-pattern` / `--allowlist`: any flag that bridges detection to remediation makes the tool weaponizable. Reject.
6. **Verify the report doesn't expose secret values.** The skill reads every file in `.claude/` including config — if those contain inlined tokens, the report should redact them (the report should describe "MCP server X has Y tools", not paste the contents of `~/.claude/.env`).

## Stages

### Stage 1: Inventory

Enumerate every loadable component. For each, capture: path, byte size, approximate token count.

**Components in scope:**

| Component | Where found | Load class |
|---|---|---|
| Project `CLAUDE.md` | repo root | always-loaded (preamble) |
| User-level `CLAUDE.md` | `~/.claude/CLAUDE.md` if present | always-loaded |
| Per-skill frontmatter (`name` + `description`) | `.claude/skills/*/SKILL.md` heads | always-loaded (catalog) |
| Per-skill body | `.claude/skills/*/SKILL.md` bodies | load-on-activation |
| Per-agent description | `.claude/agents/*/agent.md` heads | always-loaded |
| Per-agent body | `.claude/agents/*/agent.md` bodies | load-on-activation |
| Per-command | `.claude/commands/*.md` | always-loaded (slash command surface) |
| Hook scripts | `.claude/hooks/*` | small; metadata only |
| MCP server schemas | `.mcp.json` server list + each server's tool count | always-loaded; can dominate |
| Plugin manifest | `.claude-plugin/plugin.json` | small |
| Policies | `.claude/policies/*.md` | load-when-triggered |
| Skill rules | `.claude/skill-rules.json` | always-loaded |
| Session reminders | system-reminder accumulation per session | runtime only — not pre-loadable |

**Token approximation formula:**

- Default: `tokens ≈ bytes / 4` (English prose)
- JSON / YAML config: `tokens ≈ bytes / 3.5` (denser due to structural chars)
- Tool schemas (MCP): `tokens ≈ bytes / 3.5`
- Code blocks within markdown: counted as part of the surrounding file
- **All counts are approximations within ±20%.** Anthropic's actual tokenizer is BPE-based; this formula is a heuristic that ranks files correctly even when it miscounts. The point is *ranking*, not exact accounting.

### Stage 2: Hot-set classification

Split components into three buckets:

| Bucket | What | When loaded |
|---|---|---|
| **Always** | CLAUDE.md, every SKILL.md frontmatter (the catalog row), every agent description, every command file, every MCP tool schema, `.claude/settings.json` | Session start, every session |
| **Sometimes** | SKILL.md *body* (only when the skill activates) | Per-activation |
| **Rarely** | Policy files, hook scripts, agent bodies | When triggered |

The **always-loaded total** is the most important number: it's what every session pays before any work happens.

### Stage 3: Sprawl detection

Compare current catalog to a baseline:

- Count of skills now vs N sessions ago (if `git log .claude/skills/` is available)
- Average skill description length now vs at first ship
- Number of MCP servers now vs in the last committed `.mcp.json`

**Findings:**

- **HIGH:** catalog count grew >25% since baseline without a corresponding `WORKING-CONTEXT` or sprint note documenting the additions
- **MEDIUM:** average description length grew >50% (descriptions creeping toward novellas)
- **LOW:** MCP server count grew by ≥1 since baseline

Sprawl is not always bad — sometimes you legitimately add skills. The finding is the *prompt* to verify, not a verdict that the additions are wrong.

### Stage 4: Top-K recommendations

Produce a ranked list of components by approximate token weight. For each top-K item (default K=10), list:

- Path
- Approximate tokens
- Load class (Always / Sometimes / Rarely)
- A *question* the user should answer, not an action: e.g., "Is this skill still in active use?" / "Could this MCP server be on-demand instead of always-loaded?" / "Is this CLAUDE.md section duplicated in a SKILL.md body?"

**No suggested edits.** The report ends with the questions. The user answers them by deciding what to do — not by piping the report into an Edit tool.

### Stage 5: MCP audit

Because MCP tool schemas are typically the **single largest always-loaded category** in a Claude Code session, give them a dedicated stage:

- For each MCP server in `.mcp.json`: name, tool count, approximate schema bytes, approximate tokens
- Flag servers with >50 tools as HIGH (a single server saturating the catalog)
- Flag servers used in <10% of sessions over the last 30 days as MEDIUM (low utilization, could be on-demand)
- *Do not* recommend deactivation — the user decides whether utilization justifies the cost

Utilization data requires session-log access. If unavailable, this stage reports tool counts only and notes that utilization could not be assessed (no silent skips — see Stage 7).

### Stage 6: CLAUDE.md inventory

`CLAUDE.md` files are uniquely costly: always-loaded *and* often the largest single document.

- Bytes / approx tokens for repo root `CLAUDE.md`
- Bytes / approx tokens for `~/.claude/CLAUDE.md` if present
- For each top-level heading in repo root `CLAUDE.md`, list heading + section byte count
- Flag sections >5000 bytes as HIGH (a section that large should probably be its own SKILL.md or doc)
- Flag duplication: any heading that exists in both project `CLAUDE.md` and a SKILL.md body

### Stage 7: Self-audit

**7.1 — `allowed-tools` is read-only.**
Confirmed: `Read`, `Glob`, scoped `Bash` (`wc:*`, `find:*`, `ls:*`, `stat:*`, `du:*`). No `Write`, no `Edit`, no `WebFetch`, no `Bash(*)`.

**7.2 — No silent skips.**
Files that match the scope but couldn't be read (permission denied, encoding error) surface as an INFO-level finding, not silently dropped. Same backdoor-pattern logic as `harness-auditor`.

**7.3 — Report contains no secret values.**
The report describes counts and paths. It never includes file *contents* of `.env`, `.envrc`, settings files containing API keys, or any file matching `*key*`, `*token*`, `*secret*`. Path is in scope; content is not.

**7.4 — Token estimates are labeled approximate.**
Every table header reads "approx tokens", not "tokens". The methodology note is included verbatim in every report.

## Verdicts (locked, four-tier discipline)

Although context-budget is informational rather than safety-critical, it inherits the household's four-tier verdict for consistency:

| Verdict | When |
|---|---|
| **PASS** | Always-loaded total < 50K approx tokens, no HIGH findings, no sprawl |
| **PASS WITH WARNINGS** | One or more MEDIUM/LOW findings; no HIGH |
| **PASS WITH ACCEPTED RISK** | HIGH findings with documented "accept this overhead because X" rationale in the report |
| **FAIL** | Any CRITICAL finding |

CRITICAL is reserved for: a discovered exfiltration vector (e.g., a hook that uploads context to an external URL), a hook that runs an unaudited script at every session start, or an MCP server pointing at a non-pinned remote endpoint. These are findings the user should know about *immediately*, not just "your context is heavy."

## Output

The skill describes a `CONTEXT_BUDGET_REPORT.md` that the calling agent's `Write` tool materializes; the skill itself never writes.

Report shape:

```markdown
# Context Budget Report

**Date:** YYYY-MM-DD
**Repo:** <repo>
**Branch:** <branch>
**Auditor:** context-budget v1.0.0
**Approximation note:** Token counts are bytes÷4 for prose, bytes÷3.5 for JSON/YAML/schemas. Accuracy ±20%. The *ranking* is the signal; exact counts are not.

## Always-loaded total
~XX,XXX approx tokens

## Stage results

| Stage | Surface | Findings |
|---|---|---|
| 1 | Inventory | N components catalogued |
| 2 | Hot-set | Always=A | Sometimes=B | Rarely=C |
| 3 | Sprawl | ... |
| 4 | Top-10 | ... |
| 5 | MCP | N servers, M tools, ~K tokens |
| 6 | CLAUDE.md | Repo: X tokens | User: Y tokens |
| 7 | Self-audit | PASS |

## Top-10 heaviest components

| Rank | Path | Approx tokens | Load class | Question for the user |
|---|---|---|---|---|
| 1 | ... | ... | Always | ... |

## Verdict
**PASS WITH WARNINGS** (2 MEDIUM, no HIGH, no CRITICAL)

## Self-audit checklist
- [x] allowed-tools is read-only
- [x] No file contents included (paths and sizes only)
- [x] Token estimates labeled approximate
- [x] No "apply-recommendations" output mode
```

## Backdoor defenses (5 PR-rejection patterns)

This skill has wide read access — that alone makes it a higher-value target than most. Reject any PR that introduces:

1. **An `--apply` / `--auto-prune` / `--fix` flag.** Detection bridges to remediation; the bridge weaponizes the tool. Same logic as `--ignore-stale` in `doc-updater`. Reject.
2. **Network egress.** No `curl`, no `WebFetch`, no `Bash(*)`. A context-budget tool that uploads inventory to "an analytics dashboard" is an exfiltration channel; "telemetry for performance tuning" is the same channel with a friendlier name. Reject.
3. **Inclusion of file *contents* in reports.** Paths and sizes only. A report that includes the body of `.env` because it was "weighing the env file's token cost" has crossed a line. Reject.
4. **A fifth verdict tier.** Four tiers, locked.
5. **Runtime-configurable thresholds.** Thresholds for HIGH/MEDIUM/LOW are documented inline in this SKILL.md, not read from a runtime config — same auditability rule as `doc-updater`.

## What this skill is intentionally NOT

- **Not a token counter.** It approximates. Use Anthropic's tokenizer for exact counts. The skill's purpose is *ranking*, not measurement.
- **Not a pruner.** It surfaces decisions; the user makes them.
- **Not a runtime monitor.** It produces a snapshot. Real-time context-window monitoring is a separate (and harder) problem.
- **Not session-log-aware by default.** Stage 5 flags low-utilization MCP servers *if* utilization data is available; absent that, it reports tool counts only and labels the gap explicitly (no silent skip).
- **Not a substitute for `harness-auditor`.** Harness-auditor finds *security* problems in `.claude/`; context-budget finds *weight* problems. Both should run before adopting a new plugin or MCP server.

## Inspiration and design provenance

Concept-lifted from `affaan-m/everything-claude-code`'s `skills/context-budget/` (MIT). Intentional departures:

| ECC | Ours |
|---|---|
| Recommends pruning actions | Surfaces questions; explicit user action required |
| MCP as the primary lever | MCP **and** skill-catalog sprawl as peer-class levers — household experience: 30+ skills per repo is its own pressure source |
| Top-N recommendations format | Top-10 with one *question* per item, not one *suggestion* |
| No explicit threat-model | "Backdoor defenses (5 PR-rejection patterns)" section |
| No approximation disclaimer | "Approximation note" required in every report; ±20% labeled |
| No four-tier verdict | Same four tiers as the rest of the household (PASS / WARNINGS / ACCEPTED-RISK / FAIL) |
| Could conceivably bridge to auto-apply | Allowed-tools is read-only; bridge is structurally blocked |

This is a `concept-only` lift per the provenance schema (`schemas/records/context-budget.json`).
