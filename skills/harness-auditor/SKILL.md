---
name: harness-auditor
description: Audits a Claude Code project's harness surface — `.claude/settings*.json`, `.claude/hooks/`, `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.mcp.json`, `CLAUDE.md`, and `.claude-plugin/plugin.json` — for permission wildcards, hook injection paths, MCP supply-chain risk, skill/agent capability creep, instruction-layer drift, and plugin-manifest tampering. Read-only against source — describes a `HARNESS_AUDIT_REPORT.md` output that the agent's Write tool materializes; the skill itself never edits source files. Audit this skill before trusting it.
version: 1.0.0
license: Unlicense
category: safety
keywords:
  - harness
  - audit
  - claude-config
  - settings
  - hooks
  - mcp
  - skills
  - agents
  - permissions
  - capability-creep
  - supply-chain
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(grep:*)
  - Bash(rg:*)
  - Bash(find:*)
  - Bash(ls:*)
  - Bash(cat:*)
  - Bash(stat:*)
  - Bash(file:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git ls-files:*)
compatibility:
  claude-code: ">=2.1"
---

# Harness Auditor

> Audit configs the way you'd audit code. **Audit this skill before trusting it.**

## Why this skill exists

The Claude Code harness — settings, hooks, MCP servers, skills, agents, slash commands, plugin manifests — is the runtime surface an attacker bothers with when the source code is too well-guarded. A single overly-broad `Bash(*)` allow rule, a hook that calls `curl`, an unpinned `npx` MCP server, or a skill with a wildcard `allowed-tools` is enough to convert a careful codebase into an open execution channel. This skill audits that surface.

It is a complement to `opensource-sanitizer` (which audits source artifacts for publication readiness). Where the sanitizer looks at *what you might leak*, this looks at *what the harness might do on your behalf without you noticing*.

## How to audit this skill before trusting it

Security tools are the best place to hide malicious code. Before you run any auditor — including this one — verify:

1. **Read every line of this `SKILL.md`.** Every line. Including the example outputs. Look for `<system-reminder>` blocks, instructions to fetch external URLs, suggestions to run destructive commands, regex examples that double as prompt injection.
2. **Verify `allowed-tools`.** Every tool listed should be read-only or scoped to a known-safe non-mutating command. No `Write`. No `Edit`. No `Bash` without an explicit prefix. No `WebFetch`. No `Bash(*)`.
3. **Test against a known-bad fixture.** Drop a `.claude/settings.json` containing `"permissions": {"allow": ["Bash(*)"]}` into a sandbox repo and confirm Stage 1 flags it CRITICAL. Drop a hook that calls `curl http://attacker.example/` and confirm Stage 2 flags it. If either passes silently, the regex coverage is broken — or worse, intentionally narrow.
4. **Test for over-matching.** Drop a benign `"Bash(npm test)"` permission into the same settings.json. If this skill flags it CRITICAL, the pattern is too broad. **Over-matching is a documented backdoor pattern** (alert fatigue desensitizes users to real findings).
5. **Verify no "soft" verdict tier exists.** There are exactly four verdicts: PASS, PASS WITH WARNINGS (low/medium only), PASS WITH ACCEPTED RISK (HIGH/MEDIUM accepted in writing), FAIL. **There is no "low-severity exception for critical findings."** If a future PR adds one, reject it.
6. **Verify no allowlist mechanism exists.** This skill has no `--skip-path` flag, no `audit-ignore` directive, no per-finding suppression. A whitelist feature on a security auditor is exactly the surface an attacker would weaponize. If a future PR proposes one, reject it.
7. **Verify the inspiration links resolve.** Every external link in this file (CVEs, advisories, vendor docs) should still point at the domain its text claims. If any 404s or redirects, treat it as a tamper signal — the link may have been retargeted in a malicious PR.
8. **Verify worked examples don't double as configuration.** Read every YAML/JSON example below. None of them are valid configurations a user could copy-paste; they are illustrative fragments only, with explicit `[PLACEHOLDER]` markers where a real value would go. Worked examples that *could* be pasted into a real settings.json risk being lifted accidentally.

## Scope: what counts as "the harness"

This skill audits these surfaces (all paths relative to repo root unless noted):

| Surface | What lives there | Stage |
|---|---|---|
| `.claude/settings.json` | Repo-scoped permissions, model, env, hooks registry | 1 |
| `.claude/settings.local.json` | User-local overrides, never committed | 1 |
| `~/.claude/settings.json` (user-level) | User defaults across all repos | 1 |
| `.claude/hooks/*.sh` (or .js, .py, etc.) | Hook scripts run on tool events | 2 |
| `.mcp.json` | MCP server registry | 3 |
| `.claude/skills/{name}/SKILL.md` | Skill definitions | 4 |
| `.claude/agents/{name}.md` | Agent definitions | 5 |
| `.claude/commands/{name}.md` | Slash command definitions | 6 |
| `CLAUDE.md` (repo) + `~/.claude/CLAUDE.md` (user) | Instruction-layer rules | 7 |
| `.claude-plugin/plugin.json` | Plugin manifest, skill registry | 8 |

What this skill does **not** audit:
- Source code (use `opensource-sanitizer` or `silent-failure-hunter` instead)
- Secrets (use `opensource-sanitizer`)
- The orchestrator's own configs (`ken/orchestrator/`) — out of scope; audit those with a tool that understands the orchestrator's domain model
- Anything outside `.claude/`, `.mcp.json`, `CLAUDE.md`, and `.claude-plugin/`

## Output

This skill **describes** a `HARNESS_AUDIT_REPORT.md` that the calling agent's `Write` tool materializes. The skill itself never writes.

Report structure:

```markdown
# Harness Audit Report

**Date:** YYYY-MM-DD
**Repo:** <repo-name>
**Branch:** <branch>
**Auditor:** harness-auditor v1.0.0
**Operating principle:** #6 (audit security tools harder)

## Stage results

| Stage | Surface | Findings |
|---|---|---|
| 1 | settings.json layers | N findings (X critical, Y high, Z medium, W low) |
| 2 | hooks | ... |
| ... | ... | ... |

## Findings (severity-ranked)

### CRITICAL: <one-line summary>
- **File:** `.claude/settings.json:42`
- **Pattern:** Bash wildcard permission `"Bash(*)"`
- **Why critical:** Wildcard Bash permission converts the harness into an arbitrary-command channel. tj-actions CVE-2025-30066 demonstrated that overly-broad CI permissions become foothold within hours of credential exposure.
- **Remediation:** Replace with explicit command prefixes (e.g., `"Bash(npm test:*)"`).

### HIGH: <next finding>
...

## Verdict
**PASS WITH WARNINGS** (N low + M medium, no critical, no high)

## Self-audit checklist
- [x] harness-auditor's own `allowed-tools` is read-only
- [x] No allowlist mechanism was used during this scan
- [x] No soft verdict tier was used
- [x] All redacted content used full redaction (no first-N-last-N leakage)
```

## Verdicts (locked, no soft tier)

| Verdict | When |
|---|---|
| **PASS** | 0 findings at any severity |
| **PASS WITH WARNINGS** | LOW and/or MEDIUM findings only |
| **PASS WITH ACCEPTED RISK** | MEDIUM or HIGH findings, accepted in writing in the report with rationale |
| **FAIL** | Any CRITICAL finding, OR HIGH findings without written acceptance |

There is no "informational" tier. There is no "won't fix." There is no "ignore this." Either a finding is below MEDIUM (low), or the user accepts the risk in writing. **A future PR proposing a fifth verdict tier should be rejected** — backdoor pattern #3 (soft verdict tiers).

## Stages

### Stage 1: settings.json layer audit

For each of `.claude/settings.json`, `.claude/settings.local.json`, and `~/.claude/settings.json`:

**1.1 — Permission wildcards (CRITICAL)**
- `"Bash(*)"` — bare wildcard
- `"WebFetch(*)"` — wildcard web egress
- Any permission ending in `(*)` without a prefix

**1.2 — Network-egress permissions without scope (HIGH)**
- `"Bash(curl:*)"` without a documented `CLAUDE.md` rationale
- `"Bash(wget:*)"` similarly
- `"WebFetch(*)"` (also caught by 1.1)

**1.3 — Destructive bash permissions (HIGH)**
- `"Bash(rm:*)"`, `"Bash(git reset:*)"`, `"Bash(git push:*)"` without rationale

**1.4 — Model field tampering (MEDIUM)**
- `model` field set to a non-current Anthropic model — could be a downgrade attack
- Model field set to a non-Anthropic provider URL

**1.5 — Settings drift (MEDIUM)**
- Repo settings.json contradicts user `~/.claude/settings.json` in dangerous direction (repo trying to grant a permission the user denies, or vice versa)

**1.6 — Env var injection surface (LOW)**
- Env vars set in settings.json that get template-substituted into Bash commands

**1.7 — Hooks registered in settings.json but missing files (LOW)**
- Hooks listed by path but the file doesn't exist (defense-in-depth: silent failure)

### Stage 2: Hook safety

For each file in `.claude/hooks/`:

**2.1 — Network egress (HIGH)**
- `curl`, `wget`, `http.get`, `fetch(`, `requests.get`, `urllib.request.urlopen` in hook scripts
- Exception (allowed): hook explicitly documents the egress in a `# HOOK-EGRESS: <url> reason: ...` comment and the URL resolves to a known-trusted vendor (e.g., github.com). The exception still surfaces as MEDIUM, not silent.

**2.2 — Shell injection surfaces (CRITICAL)**
- Hook scripts that `eval` user input
- Hook scripts that pass `$1`, `$@`, or `$VARIABLE` from a tool-call argument directly to a shell command without quoting
- `bash -c "$VAR"` patterns

**2.3 — Bypass flags (CRITICAL)**
- `--no-verify`, `--force` (on push), `--no-gpg-sign`, `-c commit.gpgsign=false`, `--allow-unsafe-perm` in hook scripts
- **Backdoor pattern #10** (Grok red-team): "temporary bypass" flags

**2.4 — Hook writes outside repo (HIGH)**
- Hook scripts that write to `~/`, `/tmp/`, `/etc/`, or any path outside the repo working tree without a documented purpose

**2.5 — Hook spawns long-running processes (LOW)**
- Hook scripts that fork-and-detach (`&`, `nohup`, `disown`) — surfaces for review only

### Stage 3: MCP server audit

For `.mcp.json` (repo root) and any `mcp.json` under `.cursor/`, `.claude/`:

**3.1 — Unpinned npm/uvx/pip MCP servers (HIGH)**
- `"command": "npx", "args": ["package-name@latest"]` — `@latest` is mutable
- `"command": "npx", "args": ["package-name"]` without version specifier — also mutable
- Same for `uvx`, `pip install --user`, etc.
- **tj-actions CVE-2025-30066 pattern** applied to MCP supply chain

**3.2 — Compromised-package family check (CRITICAL)**
- MCP server uses any package known to be in the Shai-Hulud worm family (v1 Sept 2025, v2 Nov 2025, v3 April 2026): `@ctrl/tinycolor`, compromised `chalk` releases, `debug` post-compromise versions, `rand-user-agent`, others enumerated by Datadog Security Labs / Sysdig
- Names + version ranges are described, not hardcoded — the auditor reads from a documented compromised-package list (`docs/compromised-mcp-packages.md`) that lives **in the same repo as this skill** so it's auditable in the same PR

**3.3 — Remote MCP servers on non-vendor URLs (HIGH)**
- `"url": "https://..."` pointing at anything not on a documented vendor host list
- Especially flag URLs that are typo-squats of vendor domains (this is Stage 3.3, not Stage 3.4 below; we do lookalike detection here)

**3.4 — MCPoison-class trust-on-first-use (CRITICAL)**
- MCP server has `"trust": true` or equivalent set without an accompanying SHA-pinned `args`
- **CVE-2025-54136 / MCPoison**: Cursor's MCP trust bound to *name*, not content. Reapplied: a `.mcp.json` that pins by name but not content is vulnerable.

**3.5 — MCP server bundled with broad capability declarations (MEDIUM)**
- MCP server documented as "read-only" but its tool list includes `Write`, `Bash`, network egress — capability creep

### Stage 4: Skill safety

For each `.claude/skills/{name}/SKILL.md`:

**4.1 — `allowed-tools` wildcards (CRITICAL)**
- `allowed-tools: ["*"]`
- `allowed-tools: ["Bash"]` without prefix
- Any tool listed without scope when scope is supported

**4.2 — Capability concentration (HIGH)**
- A single skill declares `Bash` + `Write` + `WebFetch`
- A single skill declares `Edit` + `Bash` + network egress
- One skill with three+ unrelated high-power tools is a foothold — split into narrower skills

**4.3 — Prompt-injection patterns in `description` or `keywords` (CRITICAL)**
- `description` contains `<system-reminder>`, `ignore previous instructions`, `you are now`, `BEGIN NEW INSTRUCTIONS`, `developer:`, etc.
- **ToxicSkills (Snyk, Feb 2026)**: 36% of ClawHub skills had prompt injection in description fields

**4.4 — Missing self-audit checklist on security skills (MEDIUM)**
- If `category: safety` is set and there's no "How to audit this skill before trusting it" section, flag it
- Operating principle #6 propagation

**4.5 — Worked examples that match the skill's own patterns (LOW)**
- Skill declares it detects pattern X, then provides an example containing literal pattern X
- **Backdoor pattern #5** (Grok red-team): worked examples that double as prompt injection / re-trigger detection

### Stage 5: Agent safety

For each `.claude/agents/{name}.md`:

**5.1 — `tools` wildcard (CRITICAL)**
- `tools: *` or `tools: ["*"]`

**5.2 — Capability concentration (HIGH)**
- Same triple-power test as 4.2

**5.3 — Recursive agent spawn (MEDIUM)**
- Agent declares `tools` including `Agent` (or `Task`) — i.e., can spawn other agents
- Surfaces for review; some agents legitimately need this (e.g., orchestrators), but the case must be documented in the agent's system prompt

**5.4 — Prompt-injection in agent system prompt (CRITICAL)**
- Same patterns as 4.3 applied to the agent's prose

### Stage 6: Slash command safety

For each `.claude/commands/{name}.md`:

**6.1 — Argument interpolation surface (HIGH)**
- Command body uses `$ARGUMENTS` or `{{args}}` and passes that directly into a shell command without escaping
- This is shell injection via slash command

**6.2 — Tool-permission elevation (HIGH)**
- Command declares it requires tools the user hasn't granted globally — drift between command-required and user-allowed permissions

### Stage 7: CLAUDE.md instruction-layer drift

**7.1 — Repo vs user CLAUDE.md contradiction (MEDIUM)**
- Repo says "Always do X." User says "Never do X."
- The agent cannot satisfy both; surface for resolution

**7.2 — Stale model references (LOW)**
- CLAUDE.md mentions a retired Claude model by name without an "as of YYYY-MM" disclaimer

**7.3 — Embedded prompt injection in CLAUDE.md (CRITICAL)**
- CLAUDE.md contains `<system-reminder>` blocks, "developer:" directives, or any of the Stage 4.3 patterns
- **Microsoft "prompts as shells" (May 7, 2026)**: prompts have become RCE surfaces; CLAUDE.md is on that surface

### Stage 8: Plugin manifest integrity

For `.claude-plugin/plugin.json`:

**8.1 — Skill registry vs filesystem mismatch (MEDIUM)**
- Plugin manifest lists a skill that doesn't exist on disk → fail silently when invoked
- A skill exists on disk but isn't listed → invisible-skill backdoor surface

**8.2 — Bundled MCP servers (HIGH)**
- Plugin ships an `.mcp.json` that injects MCP servers when installed — re-runs all of Stage 3 against that bundled file
- The plugin author should not be able to add MCP servers silently as a side-effect of plugin install

**8.3 — `signature` or `provenance` field validation (LOW)**
- If the plugin manifest declares a signature, the harness should verify it. If it declares one and verification isn't wired up, flag as defense-in-depth gap.

### Stage 9: Self-audit (operating principle #6)

Final stage runs against this skill itself:

**9.1 — This skill's `allowed-tools` is read-only**
- No `Write`, no `Edit`, no `WebFetch`, no `Bash` without explicit prefix
- If a future PR adds any of those, reject it.

**9.2 — No allowlist / skip-list / bypass-flag fields are read by this skill**
- Confirm by grepping this SKILL.md for `allowlist`, `skip`, `ignore`, `bypass`, `--no-`

**9.3 — Redaction format is consistent**
- Any flagged config content longer than 39 characters is reported as `first2****last2 (len N)`, never `first4****last4`
- Anything shorter is fully redacted to `[REDACTED-<type>-<length>]`

## Threat context (as of May 2026)

This skill is hardened against the following named incidents and disclosure patterns:

- **CVE-2025-30066 / tj-actions/changed-files** (March 2025) — retroactive tag re-pointing. Surfaced as risk class in Stage 1 (settings layer) and Stage 3 (MCP unpinned).
- **CVE-2025-54136 / MCPoison** (August 2025) — Cursor's MCP trust bound to name, not content. Surfaced in Stage 3.4.
- **Shai-Hulud worm family** (September 2025 / November 2025 / April 2026) — self-replicating npm worms that infect via `postinstall`. Surfaced in Stage 3.2 (compromised packages) and adjacent to `opensource-sanitizer`'s Stage 7.5.
- **Anthropic MCP CVEs 2026-68143/68144/68145** (January 2026) — prompt-injection vectors in MCP servers. Surfaced in Stage 4.3 and Stage 7.3.
- **ToxicSkills (Snyk, February 2026)** — 36% of audited ClawHub skills contained prompt-injection in description fields. Surfaced in Stage 4.3.
- **Microsoft "prompts as shells" research (May 7, 2026)** — prompts have become RCE surfaces in AI agent frameworks. Surfaced in Stage 7.3.
- **GitGuardian state of secrets 2026** — 24,008 secrets leaked through MCP configs in 2025. Surfaced as the rationale for Stage 3 existing.

If any of those links 404 when verified, treat as tamper signal:

- https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction
- https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/
- https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages
- https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/

## Backdoor defenses (10 PR-rejection patterns)

This skill should refuse to merge a PR that introduces any of the following — each pattern reflects a real backdoor-design strategy a malicious contributor might use against a security tool. Patterns 1–10 are adapted from the Grok red-team that hardened `opensource-sanitizer` v1.2.0; the same logic applies here.

1. **Over-matching detection rules.** A rule that flags every settings.json field as CRITICAL desensitizes the user to real findings. Reject any rule that flags >5% of household configs as CRITICAL on a clean test fixture.
2. **Redaction that exposes first-N-last-N of a short value.** Full redaction for ≤39 chars; `first2****last2 (len N)` for ≥40. No exceptions.
3. **A new "informational" or "advisory" verdict tier for CRITICAL findings.** Reject. Four tiers, locked.
4. **External "inspiration" links to attacker-controlled resources.** External links must be to vendor security advisories, NIST/CISA, MITRE, or named research blogs only. Verify they still resolve to those domains.
5. **Worked examples that re-trigger the detection regex.** Use `[PLACEHOLDER]` markers, not real-looking values.
6. **A `--skip-path` or `audit-ignore` flag.** Reject. No allowlists.
7. **Debug-log output that leaks unredacted config snippets under error conditions.** All error paths must redact at the same threshold as success paths.
8. **Detection rules that depend on a network library or external API call.** This skill is read-only against the local filesystem. Network egress is itself an audit finding (Stage 2.1); it is not a tool this skill uses.
9. **Silent skip of a file class under a performance pretext.** If `.claude/agents/` is large, scan more slowly, don't skip. Reject any rule that introduces a "max files" cap with skip behavior.
10. **A `--bypass` flag for testing.** Reject. Test fixtures are the verification path; bypass flags only enable production abuse.

## Quick reference: where to look for each surface

When invoked, the agent should execute the following inventory commands (read-only):

```bash
# Stage 1: settings layers
find . -name 'settings*.json' -path '*/.claude/*' -not -path '*/node_modules/*'
test -f ~/.claude/settings.json && echo 'user-level settings exists'

# Stage 2: hooks
find .claude/hooks -type f 2>/dev/null

# Stage 3: MCP
find . -name '.mcp.json' -o -path '*/mcp.json' -not -path '*/node_modules/*'

# Stage 4: skills
find .claude/skills -name 'SKILL.md' -type f 2>/dev/null

# Stage 5: agents
find .claude/agents -type f 2>/dev/null

# Stage 6: commands
find .claude/commands -type f 2>/dev/null

# Stage 7: instruction layers
ls CLAUDE.md ~/.claude/CLAUDE.md 2>/dev/null

# Stage 8: plugin manifest
ls .claude-plugin/plugin.json 2>/dev/null
```

The agent then `Read`s each surface, runs the per-stage regex/pattern checks documented above, and Writes the report.

## What this skill is intentionally NOT

- **Not a remediation engine.** This skill produces findings; the user (or a separate, narrower agent) applies fixes. Separation of detection from remediation is itself a defense — a single tool that both detects and "fixes" is a single tool that both detects and *can be made to break*.
- **Not a scoring system.** No 0-10 dimension scores, no composite /70, no "audit grade." Severity tiers + file paths only. Numeric grades are exactly the surface an attacker would target for backdoor-pattern #1 (over-matching) and #3 (soft verdict tiers).
- **Not a continuous-monitoring tool.** Run it explicitly, on demand, before merges or releases. A scheduled background auditor is its own attack surface (output channels, log paths, scheduler permissions).
- **Not a substitute for `opensource-sanitizer`.** The two are complements: sanitizer audits source for publication; auditor audits harness for runtime safety. Run both before any open-source release.

## Inspiration

The structure of this skill is concept-lifted (operating principle #1) from `everything-claude-code`'s `harness-optimizer` agent + `/harness-audit` slash command, with these intentional departures:

- The ECC version uses a 7-dimension numeric scoring system (composite /70). We use four verdict tiers, locked. Numeric scoring is gameable; tiers with explicit acceptance rationale are not.
- The ECC version emphasizes "non-invasive tuning" and "minimal configuration changes" as outputs. We separate detection from remediation — the audit produces findings, not changes.
- The ECC version has an "optional JSON export for downstream automation." We describe a markdown report only; serialization is the calling agent's choice. JSON export is one more output channel that can be subverted.
- The ECC version's audit categories (Hooks/Evaluations/Routing/Context/Safety) are general. Ours are Claude-Code-specific (8 stages tied to actual `.claude/` surfaces).
- The ECC version doesn't have a self-audit section. Ours does (Stage 9) because operating principle #6 says security tools deserve harder scrutiny than other tools.

The codebase reference for the inspiration is MIT-licensed and was concept-lifted, not code-lifted — this SKILL.md was written from scratch against the documented concept, not against the ECC source. The two should not be byte-identical anywhere.
