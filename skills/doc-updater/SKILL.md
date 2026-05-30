---
name: doc-updater
description: Detects documentation drift in a project's `README.md`, `CLAUDE.md`, skill catalogs, soul/charter docs, and cross-repo indexes. Checks count claims against filesystem ground truth, file references for resolution, version numbers for cross-source agreement, skill catalogs for internal consistency, stale model names, broken anchor links, last-updated dates against git history, and cross-document numeric consistency. Read-only — describes a `DOC_DRIFT_REPORT.md` output that the agent's Write tool materializes; the skill itself never edits docs. Detection only, not remediation.
version: 1.0.0
license: Unlicense
category: integrity
keywords:
  - doc-updater
  - documentation-drift
  - stale-docs
  - skill-catalog
  - version-drift
  - link-rot
  - readme-audit
  - count-mismatch
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(grep:*)
  - Bash(rg:*)
  - Bash(find:*)
  - Bash(ls:*)
  - Bash(wc:*)
  - Bash(stat:*)
  - Bash(git log:*)
  - Bash(git ls-files:*)
  - Bash(git diff:*)
compatibility:
  claude-code: ">=2.1"
---

# Doc-Updater

> Documentation lies through count drift, not bugs. **This skill detects the lies.**

## Why this skill exists

Documentation drift is silent and cumulative. A README says "9 repos" when the household has 11. A CLAUDE.md table lists "3 skills" when there are 7. A `version: 1.0.0` in a SKILL.md disagrees with `0.4.0` in `package.json`. None of these break a build. All of them mislead the next reader (human or agent) into wrong decisions.

This skill finds those lies and reports them. It does not fix them — fixing is a human (or narrower agent) job. Detection-only is itself a defense: a single tool that both detects drift and *rewrites docs to match* is a single tool that can be made to *rewrite docs away from truth*.

## How to audit this skill before trusting it

This is a documentation tool, not a security tool — but it reads READMEs, CLAUDE.md files, and skill catalogs that *are* security-relevant. Apply operating principle #6 in lighter form:

1. **Read every line of this `SKILL.md`** including example outputs. Look for `<system-reminder>` blocks, instructions to fetch external URLs, or worked examples that double as instructions.
2. **Verify `allowed-tools` is read-only.** No `Write`, no `Edit`. No `Bash` without an explicit prefix. No `WebFetch`. No `Bash(*)`.
3. **Test against a known-drift fixture.** Drop a markdown file containing "We have 5 skills" into a sandbox repo with 7 SKILL.md files in `skills/`. Confirm Stage 1 flags it. If it doesn't, the count-claim regex is broken.
4. **Test for over-matching.** Drop a file containing the literal string "version 1.0.0 of the GPL-3.0 license" (an unrelated version). If Stage 3 flags this as a drift between SKILL.md and that file, the version-drift logic is too broad — it should only compare version claims tied to the same artifact.
5. **Verify the four-verdict tier discipline.** PASS / PASS WITH WARNINGS / PASS WITH ACCEPTED RISK / FAIL. **No fifth tier.** If a future PR adds an "informational" tier, reject.
6. **Verify no allowlist / skip-list / `--ignore-stale` flag exists.** If a future PR proposes one, reject — same logic as `opensource-sanitizer` and `harness-auditor`.

## Scope: what counts as "documentation"

In-scope:
- `README.md` (repo root, `docs/`, or `skills/*/`)
- `CLAUDE.md` (repo root and `~/.claude/`)
- `SKILLS.md` (per-repo skill index)
- `WORKING-CONTEXT.md` and similar operational truth docs
- Soul / charter / mission docs (`souls/*.md`, `CHARTER.md`, etc.)
- Per-skill `SKILL.md` files (frontmatter version + body cross-refs)
- `package.json`, `.claude-plugin/plugin.json` (read for version + skills array, not edited)
- `CHANGELOG.md`
- Any markdown file at repo root

Out of scope:
- Source code (use `opensource-sanitizer` for content audits, `silent-failure-hunter` for error-handling)
- Test fixtures and `examples/` directories (often contain intentionally-fake versions and counts)
- Generated files (anything matching `*.generated.md`, `dist/`, `build/`, `node_modules/`)
- Git history beyond `git log -1 --format=%cI <file>` for last-modified comparison

## Output

This skill **describes** a `DOC_DRIFT_REPORT.md` that the calling agent's `Write` tool materializes. The skill itself never writes.

Report structure:

```markdown
# Documentation Drift Report

**Date:** YYYY-MM-DD
**Repo:** <repo-name>
**Branch:** <branch>
**Auditor:** doc-updater v1.0.0
**Scope:** <single-repo | household-N-repos>

## Stage results

| Stage | Surface | Findings |
|---|---|---|
| 1 | count claims | N findings (X high, Y medium, Z low) |
| 2 | file references | ... |
| ... | ... | ... |

## Findings (severity-ranked)

### HIGH: Count claim contradicts filesystem
- **File:** `CLAUDE.md:14`
- **Claim:** "3 skills currently"
- **Ground truth:** 7 SKILL.md files under `skills/`
- **Remediation:** Update the claim to "7 skills" (or re-derive: `find skills -name SKILL.md | wc -l`)

### MEDIUM: Version drift
- **Files:** `skills/foo/SKILL.md:4` (`version: 1.0.0`) vs `package.json:3` (`"version": "0.4.0"`)
- **Why medium:** the SKILL.md version is the public-facing API; package.json is the install version. Consumers reading the README will see the package version and assume the skill is at that version.
- **Remediation:** Decide which is authoritative; update the other.

## Verdict
**PASS WITH WARNINGS** (N low + M medium, no critical, no high)

## Self-audit checklist
- [x] doc-updater's own `allowed-tools` is read-only
- [x] No allowlist mechanism was used during this scan
- [x] No soft verdict tier was used
- [x] The scan ran against every file matched by the documented scope (no silent skips)
```

## Verdicts (locked, no soft tier)

| Verdict | When |
|---|---|
| **PASS** | 0 findings at any severity |
| **PASS WITH WARNINGS** | LOW and/or MEDIUM findings only |
| **PASS WITH ACCEPTED RISK** | MEDIUM or HIGH findings, accepted in writing in the report with rationale |
| **FAIL** | Any CRITICAL finding, OR HIGH findings without written acceptance |

CRITICAL is reserved for drift that **lies actively** rather than goes stale passively — e.g., a security-relevant claim that no longer holds ("audited by X on date Y" when no such audit happened), or a skill catalog listing a skill that doesn't exist on disk (an invisible-skill backdoor surface, per `harness-auditor` Stage 8.1).

## Stages

### Stage 1: Count claim verification

For each markdown file in scope, find claims of the form:

- "N skills" / "N agents" / "N commands" / "N hooks"
- "N repos" / "N repositories" / "N projects"
- "N files" / "N entries" / "N rules"
- "N stages" / "N steps"
- "currently N" / "N currently"

Compare against ground truth derived from the filesystem:

| Claim | Ground truth source |
|---|---|
| "N skills" | `find . -path '*/skills/*/SKILL.md' \| wc -l` |
| "N agents" | `find .claude/agents -type f 2>/dev/null \| wc -l` |
| "N commands" | `find .claude/commands -type f 2>/dev/null \| wc -l` |
| "N hooks" | `find .claude/hooks -type f 2>/dev/null \| wc -l` |
| "N repos" (household-scoped) | provided by caller, not inferred |

Severity:
- **HIGH** if drift ≥ 2 (e.g., claim "3" vs actual 7)
- **MEDIUM** if drift = 1 (off-by-one — could be in-progress work)
- **LOW** if claim uses approximate language ("about N", "around N") and drift ≤ 2

### Stage 2: File-reference resolution

For each markdown link or backtick-path reference, verify the target exists:

- `[label](path/to/file.md)` → `path/to/file.md` must exist
- `[label](path/to/file.md#anchor)` → file must exist; anchor checked in Stage 6
- `` `path/to/file.ext` `` (backtick path) → exists if it looks like a file path (contains `/` or known extension)
- `path/to/file.ext:NN` style (path with line number) → file must exist

Severity:
- **HIGH** if a top-level reference (in README or CLAUDE.md) breaks
- **MEDIUM** if reference is in a body section
- **LOW** if reference is in a "Changelog" or "History" section (links to historical files may legitimately not exist anymore)

Exclusions (not findings, just skipped):
- URLs with scheme (`http:`, `https:`, `mailto:`)
- Backtick text that looks like code, not a path (no `/` and no recognized extension)
- Paths inside fenced code blocks marked as a non-markdown language (e.g., `bash`, `json`, `yaml` — these are examples, not references)

### Stage 3: Version drift

Cross-source version comparison:

- For each `skills/<name>/SKILL.md`, read `version:` from frontmatter.
- For the repo, read `version:` from `package.json` and `.claude-plugin/plugin.json` if present.
- Find any narrative mention of "vN.M.K" in README/CLAUDE.md and try to map it to a known artifact via surrounding context (e.g., "open-claw-stuff v0.3.0" → maps to repo version).

Comparisons:

- `package.json:version` vs `plugin.json:version` → MEDIUM if different (repo-level disagreement)
- `SKILL.md:version` vs README narrative mention of that skill's version → MEDIUM if different (catalog says skill is at vX but the skill itself says vY)
- Any `vN.M.K` mention in a CHANGELOG → cross-check that `CHANGELOG.md` has a matching section

Do **not** compare unrelated versions (operating principle: no over-matching). If the README mentions "GPL-3.0" or "Python 3.11", those are not skill versions.

### Stage 4: Skill catalog consistency

The skill catalog has up to four representations:

1. `skills/*/SKILL.md` (filesystem ground truth)
2. `.claude-plugin/plugin.json:skills[].path`
3. `package.json:agent-skills.skills`
4. README skill index table

All four must enumerate the same set.

Severity:
- **CRITICAL** if `plugin.json` lists a skill path that doesn't exist on disk — this is an invisible-skill backdoor surface (see `harness-auditor` Stage 8.1)
- **HIGH** if a skill exists on disk but is missing from `plugin.json` or `package.json` — silent omission also a backdoor surface
- **MEDIUM** if README skill index is out of sync with `plugin.json` (documentation drift, not a security gap)
- **LOW** if CLAUDE.md table mentions a different count than the skill index

### Stage 5: Stale model name detection

Find references to retired or near-retired model names in narrative documentation:

- `claude-1`, `claude-1.3`, `claude-instant`
- `claude-2`, `claude-2.0`, `claude-2.1`
- `claude-3-haiku`, `claude-3-sonnet`, `claude-3-opus`
- `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-7-sonnet`

Severity:
- **MEDIUM** if mentioned in current-tense ("we use claude-3-5-sonnet")
- **LOW** if framed as historical ("originally built on claude-2")
- **LOW** if mentioned in a CHANGELOG entry

Exclusion: do not flag model names that appear inside fenced code blocks marked as `bash`, `json`, or `yaml` if the surrounding context is an example of how a config file *used to* be structured (the documentation is preserving history, not making a current claim).

### Stage 6: Internal anchor drift

For each `[label](#anchor)` or `[label](file.md#anchor)`:

- Extract the heading text from the target file
- Slugify (lowercase, replace non-alphanumerics with `-`, collapse runs of `-`)
- Compare anchor to slugified headings

Severity:
- **MEDIUM** for broken anchor in a README or CLAUDE.md Table of Contents
- **LOW** for broken anchor elsewhere

Edge cases (skip, don't flag):
- Anchors that point at HTML anchors (`<a id="...">`) — these may not match heading slugs but are valid
- Anchors with footnote-style names (`#fn-1`, `#user-content-`)

### Stage 7: Last-updated date drift

For each doc with a `Last updated:` / `**Date:**` / `last-modified:` / similar dated header:

- Parse the date from the header
- Compare with `git log -1 --format=%cI -- <file>` (last commit touching the file)
- Drift = days between header date and git date

Severity:
- **MEDIUM** if drift > 180 days (header claims "Last updated: 2024" but file was edited last month)
- **LOW** if drift > 90 days
- Skip if there's no `Last updated` line at all (absence is not drift)

Exclusion: if the file has a header like `Last updated: YYYY-MM-DD (stable — no changes expected)` or contains the phrase "intentionally not updated" within 3 lines of the date, treat as PASS (the author explicitly disclaimed staleness).

### Stage 8: Cross-document numeric consistency

For numeric claims that should be globally consistent within a repo or household:

- "N repos" claim in `CLAUDE.md` and `WORKING-CONTEXT.md` and `README.md` should all agree
- "N skills" claim in `CLAUDE.md` and `README.md` and `SKILLS.md` should all agree
- Skill counts in `plugin.json.skills.length` and `package.json.agent-skills.skills.length` should agree

Severity:
- **MEDIUM** for any cross-doc disagreement

This is downstream from Stage 1 — Stage 1 finds individual claim-vs-truth gaps; Stage 8 finds claim-vs-claim gaps. They can produce overlapping findings; the report deduplicates by collapsing same-file findings into one entry.

### Stage 9: Self-audit

**9.1 — This skill's `allowed-tools` is read-only.**
Confirmed by listing: `Read`, `Grep`, `Glob`, scoped `Bash` only (`grep`, `rg`, `find`, `ls`, `wc`, `stat`, `git log`, `git ls-files`, `git diff`). No `Write`, no `Edit`, no `WebFetch`, no `Bash(*)`.

**9.2 — No silent file skips.**
The scan reports the count of files scanned and the count matched by scope globs. If a file matches the scope but was skipped (e.g., due to encoding error), it surfaces as an INFO-level finding, not silently dropped. **Silent skips are backdoor pattern #9** (see `harness-auditor`).

**9.3 — Worked examples don't re-trigger Stage 1/8 regex.**
All examples in this SKILL.md use `<N>` or `[COUNT]` placeholders for numeric claims. None of them say literally "we have 7 skills" because that fragment, if pasted out of context, could be mistaken for a real claim by the count-claim regex.

## Backdoor defenses (5 PR-rejection patterns)

This skill has a smaller backdoor surface than `opensource-sanitizer` or `harness-auditor` (documentation drift is rarely a security vector by itself), but reject any PR that introduces:

1. **An `--ignore-stale` or `--skip-file` flag.** Same logic as the security skills: allowlists on auditors weaponize them. Reject.
2. **Detection rules that auto-fix.** Doc-updater detects; it does not rewrite docs. A PR adding "and update the file in place" turns this tool into a doc-rewrite engine, which is a meaningfully different threat surface (an attacker who controls the rewrite can introduce arbitrary content).
3. **Network egress.** This skill is read-only against the local filesystem and git. No HTTP calls, no link-validity checks against external URLs (those belong in a different skill — `link-integrity` or similar). Reject any PR adding `curl`/`fetch`/`WebFetch`.
4. **A fifth verdict tier.** Four tiers, locked.
5. **Detection rules that depend on the contents of a config file the caller controls.** All detection thresholds (e.g., "90 days = LOW, 180 days = MEDIUM") are documented inline in this SKILL.md and not read from a runtime config — that way the rules are auditable in the same PR that changes them.

## Quick reference: inventory commands

When invoked, the agent should execute these read-only inventory commands first:

```bash
# Inventory of documents in scope
find . -maxdepth 3 -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*'
ls README.md CLAUDE.md WORKING-CONTEXT.md SKILLS.md 2>/dev/null

# Skill catalog ground truth
find . -name 'SKILL.md' -not -path '*/node_modules/*' | sort

# Skill counts for Stage 1
find . -path '*/skills/*/SKILL.md' 2>/dev/null | wc -l
find .claude/agents -type f 2>/dev/null | wc -l
find .claude/commands -type f 2>/dev/null | wc -l
find .claude/hooks -type f 2>/dev/null | wc -l

# Version ground truth for Stage 3
test -f package.json && grep -m 1 '"version"' package.json
test -f .claude-plugin/plugin.json && grep -m 1 '"version"' .claude-plugin/plugin.json

# Last-commit dates for Stage 7
for f in README.md CLAUDE.md WORKING-CONTEXT.md SKILLS.md; do
  test -f "$f" && echo "$f: $(git log -1 --format=%cI -- "$f" 2>/dev/null)"
done
```

The agent then `Read`s each in-scope file, runs the per-stage regex/comparison checks, and `Write`s the report.

## What this skill is intentionally NOT

- **Not a doc rewriter.** Detection only. Fixing drift is a separate, narrower job; conflating them is a privilege-escalation pattern.
- **Not a link checker for external URLs.** Stage 2 only resolves local file references. External link rot belongs in a network-aware skill (`link-integrity` in the household for the photography repo).
- **Not a code-aware doc generator.** ECC's doc-updater generates architectural maps from TypeScript source. We don't. If you want generated docs, use a different tool — doc generation is a write-tool and a different threat model.
- **Not a CHANGELOG enforcer.** It reads CHANGELOG.md for version-claim cross-checks (Stage 3), but doesn't require one or police format.
- **Not a substitute for `opensource-sanitizer`.** Sanitizer audits source for publication; doc-updater audits docs for truthfulness. Both should run before a release.

## Inspiration

The structure of this skill is concept-lifted (operating principle #1) from `everything-claude-code`'s `doc-updater` agent, with these intentional departures:

- ECC's agent *generates* architectural maps from TypeScript code analysis. We *detect drift* in hand-authored docs. ECC writes; we report. Detection-only is itself a defense — a single tool that both detects and rewrites becomes a single point of compromise.
- ECC scopes to a TypeScript monorepo. We scope to general markdown documentation (README, CLAUDE.md, skill catalogs, soul docs). Our scope works for any language.
- ECC's drift categories are code-derived (module exports, API routes, DB schemas). Ours are doc-internal (counts, refs, versions, catalogs) — closer to the household's actual failure mode.
- ECC implies remediation in its name ("updater"). Our name is preserved for catalog continuity with the ECC harvest, but the skill itself is detection-only. The naming is intentional debt: a future v2.0 might add a `doc-fixer` skill (separately allowed-tools-scoped, separately auditable) that consumes a `DOC_DRIFT_REPORT.md` produced by this skill. They would be two skills, not one — that's the boundary.

The codebase reference is MIT-licensed and was concept-lifted, not code-lifted. This SKILL.md was written from scratch against the documented concept; the two should not be byte-identical anywhere.
