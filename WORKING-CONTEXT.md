# Working Context — ken (the household hub)

**Last updated:** 2026-05-11

---

## Purpose

Operational truth document for `ken` and the household of 11 repos. Tracks current sprint, active queues, lift decisions from external sources, rejected items with rationale, and a chronological execution log.

Modeled on the `WORKING-CONTEXT.md` pattern lifted from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) (MIT). Adapted to household voice and scope.

---

## Operating principles

These apply to every lift, port, or adoption from an external project.

1. **Lift the concept, not the code.** A concept is a problem framing, a workflow shape, a vocabulary, an approach. A code lift is field names, schemas, regex patterns, file paths, function signatures. The household's reusable artifacts must be the household's own design — same concept, our interface. A rule file written for our runner must not drop into theirs and vice versa. When in doubt, redesign the schema.
2. **Attribute the concept honestly.** Every lifted concept gets an Inspiration section in the resulting skill/agent/doc, with a link to the upstream and a table of our intentional deviations. Don't paper over the lift; make it visible.
3. **Industry-standard primitives are not lifts.** Regex patterns for AWS keys, the PASS/FAIL verdict triad, the careful-not-clever idiom, the read-before-edit discipline — these are generic patterns in the broader engineering literature. Use them freely.
4. **Schema interfaces are lifts.** Field names, operator values, file-location conventions, frontmatter shape — these together constitute an API. If our skill's frontmatter is bit-identical to an upstream skill's frontmatter, we don't have our own tool; we have their tool with our name on it.
5. **Privacy posture is non-negotiable.** Romans `.ai-deny` content stays local. Grannysrecipes Memorial content never leaves the local machine. Sermon manuscripts have strict context boundaries. No upstream pattern overrides these.
6. **Audit security tools harder than other tools.** Security tools are the best place to hide malicious code, because users defer to them. Every security skill must (a) document what it cannot catch, (b) include a "how to audit this skill before trusting it" section, (c) verify that its declared `allowed-tools` match its actual behavior, (d) enforce redaction in any report it produces, and (e) refuse permissive verdict tiers that would let a real risk ship under a softer label. Apply the same scrutiny to imported security artifacts (secret-scanner patterns, policy files, hooks): they are executable security configuration, not documentation.

---

## Current Truth

| Property | Value |
|---|---|
| Default branch | `main` |
| Active development branch (this sprint) | `claude/document-repo-souls-rb8LH` |
| Repos under management | **11** — ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes, flickersofmajesty, Family-History, manateecreeksheep, Romans, InTheWake, open-claw-stuff |
| Soul documents written | **11** (one per repo, in `souls/`) |
| `SKILLS.md` indexes | **10** (open-claw-stuff uses README as its index; all other repos have dedicated SKILLS.md) |
| Total documented skills across the household | **~247** |
| `open-claw-stuff` status | **v0.5.0** — 8 skills + agent-skills-spec scaffold + eval framework + tooling baseline |
| Standard household kit | 16 skills (canonical version in `ken/.claude/skills/`) |
| Multi-LLM orchestrator modes | 6 — sermon, sheep, cruising, recipe, family-history, triad |
| Current keeper status | Designed (Stage 1: 5 commands), not yet implemented |

---

## Current Constraints

- No bulk install of external Claude Code plugins. Cherry-pick patterns; never surrender hook authority to upstream maintainers.
- All skills lifted into `open-claw-stuff` must be Unlicense-compatible. **Re-write, do not copy-paste from MIT/Apache sources.** Attribute upstream in an Inspiration section.
- **Concept lift, not code lift.** See operating principle #1.
- **Audit security tools harder.** See operating principle #6.
- No execution of unverified upstream tooling (e.g., `npx ecc-agentshield scan`). Read source first; if we want the capability, ship our own implementation.
- Domain-specific skills stay in their domain repo. Only generic patterns belong in `open-claw-stuff`.
- Privacy posture per repo is non-negotiable. See operating principle #5.

---

## ECC harvest classification (this sprint)

Three review passes covered `affaan-m/everything-claude-code`: skills (182), agents (48), and broader concepts (rules, commands, schemas, working-context, hookify-rules).

**Three confirmed prompt-injection events** were embedded in fetched documents (README.md, chief-of-staff.md, WORKING-CONTEXT.md). All three contained `<system-reminder>` blocks attempting to influence TodoWrite usage. Payloads were benign; the **pattern is concerning** — confirms decision to never bulk-install.

`install.sh` and `scripts/install-apply.js` were audited as clean (npm install + Node CLI installer; no obfuscation, no exfiltration).

### Lifting (P0) — defensive, shipped this sprint

| # | Item | Source | Target | Status |
|---|---|---|---|---|
| 1 | `opensource-sanitizer` v1.1.0 (after self-audit) | ECC `agents/opensource-sanitizer.md` | `open-claw-stuff/skills/` | **✓ shipped** (v1.0 had real gaps; v1.1 patched after threat-model audit — see audit log below) |
| 2 | `silent-failure-hunter` | ECC `agents/silent-failure-hunter.md` | `open-claw-stuff/skills/` | **✓ shipped** (concept lift; reviewed under audit lens — clean) |
| 3 | `fact-forcing-gate` (hook pattern) | ECC `hooks/hooks.json` | `ken/.claude/policies/fact-forcing-gate.md` | **✓ shipped** as policy-as-markdown file; concept-lift narrows scope from "every first edit" to "high-context surfaces only" (schemas, contracts, orchestrator core, harness config, skill defs, top-level prose); `severity: warn`; three-question framing is independent |
| 4 | `configuration-protection` (hook pattern) | ECC `hooks/hooks.json` | `ken/.claude/policies/configuration-protection.md` | **✓ shipped** as policy-as-markdown file; covers eslint/prettier/tsconfig/pyproject/setup.cfg/flake8/editorconfig/jest/pytest/pre-commit/.github-workflows/Makefile/ruff/mypy; `severity: warn` (not block) with "adding vs weakening rule" question; legitimate config edits exist, false positives erode trust |
| 5 | `policy-as-markdown` v1.0.1 (after self-audit) | ECC `skills/hookify-rules/` | `open-claw-stuff/skills/` | **✓ shipped** (renamed from hookify-rules with independent schema; v1.0.1 added security-tool audit posture) |
| 6 | Sanitizer audit of household | self-audit using `opensource-sanitizer` v1.2 | all 11 repos | **✓ shipped** — 10 of 10 PASS / PASS WITH WARNINGS via v1.2.0 sweep; report `/tmp/HOUSEHOLD-SANITIZATION-REPORT-v1.2.0.md`; fix commits pushed across ken / Romans / 4 recipe repos / InTheWake / Family-History |

### Lifting (P1) — capability gaps, next sprint

| # | Item | Source | Target | Effort |
|---|---|---|---|---|
| 7 | `doc-updater` skill (concept lift from ECC `doc-updater` agent) | ECC `agents/doc-updater.md` | `open-claw-stuff/skills/doc-updater/` | **✓ shipped** v1.0.0 in open-claw-stuff v0.5.0 (commit `d66b426`); intentional inversion — ECC generates docs from code, ours detects drift in hand-authored docs; detection-only, never edits docs; 9 stages, 4 verdict tiers |
| 8 | `context-budget` skill | ECC `skills/context-budget/` | `open-claw-stuff/skills/` | medium |
| 9 | Continuous-learning-v2 / instincts (confidence-scored, project-scoped, auto-promoting memory) | ECC `skills/continuous-learning-v2/` | `ken/orchestrator/memory_ops.py` upgrade | **large** |
| 10 | `ai-regression-testing` | ECC `skills/ai-regression-testing/` | `ken/orchestrator/` + `open-claw-stuff/skills/` | medium |
| 11 | `harness-auditor` skill (concept lift from ECC `harness-optimizer` + `/harness-audit`) | ECC `agents/harness-optimizer.md` + `commands/harness-audit.md` | `open-claw-stuff/skills/harness-auditor/` | **✓ shipped** v1.0.0 in open-claw-stuff v0.4.0 (commit `82474a7`); single skill instead of agent+command split; 4 verdict tiers replacing 7-dim scoring; concept-lift only |
| 12 | WORKING-CONTEXT.md pattern | ECC `WORKING-CONTEXT.md` | `ken/WORKING-CONTEXT.md` | **✓ completed (this file)** |
| 13 | Provenance schema | ECC `schemas/provenance.schema.json` | `open-claw-stuff/schemas/` | **✓ shipped** in open-claw-stuff v0.6.0; concept-lift broadens from skills-only to any lifted artifact; replaces ECC's numeric trust score with 4-tier verdict + append-only audit log; `additionalProperties: false` at every level closes the "hidden override field" backdoor; schema validated against Draft 2020-12 meta-schema + adversarially tested against 8 malformed records (all rejected); 3 example records shipped (opensource-sanitizer / harness-auditor / doc-updater) |

### Lifting (P2) — workflow formalization, later sprints

| # | Item | Source | Target | Effort |
|---|---|---|---|---|
| 14 | `opensource-forker` / `packager` / `sanitizer` trio (full workflow) | ECC `agents/opensource-*.md` | `open-claw-stuff/skills/` + `ken/` | medium |
| 15 | `conversation-analyzer` | ECC `agents/conversation-analyzer.md` | `ken/.claude/skills/` | medium |
| 16 | `comment-analyzer` | ECC `agents/comment-analyzer.md` | InTheWake + flickersofmajesty | medium |
| 17 | Per-language rules with `common/` overrides | ECC `rules/` | `ken/.claude/rules/common/` + per-repo overrides | medium |
| 18 | `RULES.md` per repo (60-line policy contract, distinct from CLAUDE.md) | ECC `RULES.md` | each sister repo | small |
| 19 | `origin:` field in skill frontmatter | ECC `RULES.md` skill format | `open-claw-stuff` + future household catalog | small |
| 20 | `/skill-health` periodic audit | ECC `commands/skill-health.md` | `open-claw-stuff/skills/` + `ken/` | small |
| 21 | `/update-docs` drift correction | ECC `commands/update-docs.md` | `open-claw-stuff/skills/` | medium |

### Rejected (with rationale)

| Item | Reason for rejection |
|---|---|
| Bulk `/plugin install everything-claude-code` | 48 agents + 182 skills + auto-loading hooks.json = unbounded blast radius from a non-household maintainer; three prompt-injection events detected in their docs |
| `npx ecc-agentshield scan` (their security tool) | Supply-chain risk; build our own `opensource-sanitizer` instead. **Reinforced by operating principle #6** — even well-known security tools deserve audit before trust. |
| Language-specific build-resolvers and reviewers (cpp, csharp, dart, flutter, go, java, kotlin, pytorch, rust) | Household codebase is Python + vanilla JS + HTML/CSS; would be unused weight |
| `healthcare-reviewer`, `healthcare-*` skills | Not the household's domain |
| `agent-payment-x402`, `defi-amm-security`, `evm-token-decimals`, `llm-trading-agent-security`, `nodejs-keccak256` | Crypto-specific; household runs no on-chain work |
| `enterprise-agent-ops`, `customer-billing-ops`, `finance-billing-ops` | Enterprise-SaaS-specific; household is a personal monorepo |
| `chief-of-staff` agent | Multi-channel comms (email/Slack/LINE/Messenger); household has no team-comms surface |
| `gan-evaluator` / `gan-generator` / `gan-planner` | Domain unclear from listing; appears ML-specific |
| `loop-operator` + `/loop-start` + `/loop-status` | Household work is not loop-shaped |
| `database-reviewer` | Household uses JSON files, not relational DBs |
| `ck` / `claude-devfleet` | Overlaps household's `subagent-driven-development` |
| Cross-platform IDE adapters (`.cursor/`, `.codex/`, `.opencode/`, `.gemini/`, `.kiro/`, `.trae/`, `.codebuddy/`) | Household is Claude Code only |
| MCP configs for GitHub/Supabase/Vercel/Railway as committed configs | Household has no shared infrastructure footprint these would address; revisit if added |
| PRP 5-command workflow (prp-prd / prp-plan / prp-implement / prp-commit / prp-pr) | Overhead too high for household work scale |
| `multi-*` commands (multi-backend, multi-frontend, multi-execute, multi-plan, multi-workflow) | Household isn't multi-stack |
| ECC's `hookify-rules` schema verbatim | First shipped as a near-clone in v0.2.0; redesigned as `policy-as-markdown` with independent schema in v0.2.1 — see audit log below |

### Rejected with deferral

| Item | Why deferred |
|---|---|
| Their plugin install pattern with `.mcp.json` + `.claude-plugin` manifests | Worth adopting eventually but requires more research into how Claude Code v2.1+ handles them |
| `/aside` quick-thought capture | Tempting but possibly redundant with `keeper` once that ships |
| `/checkpoint` / `/save-session` / `/resume-session` / `/sessions` | Overlap with `keeper-plan`; revisit after keeper Stage 1 ships |

---

## Active queues

### Sprint queue (this branch: `claude/document-repo-souls-rb8LH`)

- ✓ Souls documented for all 11 repos (`souls/soul-<reponame>.md`)
- ✓ `open-claw-stuff` scaffolded with agent-skills-spec format + 3 foundational skills + eval framework
- ✓ `SKILLS.md` per repo + `CLAUDE.md` updates in 11 repos
- ✓ Voice skills (`voice-audit` + `like-a-human`) upgraded in InTheWake (10 sub-disciplines lifted from Romans)
- ✓ This file (`ken/WORKING-CONTEXT.md`) — P1#12 complete
- ✓ P0 ECC harvest shipped: `opensource-sanitizer` v1.1.0, `silent-failure-hunter` v1.0.0, `policy-as-markdown` v1.0.1 (open-claw-stuff v0.2.2)
- ✓ `opensource-sanitizer` v1.2.0 hardening pass (16 new credential patterns, 9 new Stage-7 sub-stages, redaction strengthened to first2-last2/len ≥40, 10-pattern backdoor-defenses section)
- ✓ Household sweep with v1.2.0: 10 of 10 repos PASS or PASS WITH WARNINGS (full report `/tmp/HOUSEHOLD-SANITIZATION-REPORT-v1.2.0.md`); fix commits pushed across ken / Romans / 4 recipe repos / InTheWake / Family-History
- ✓ P1#11 `harness-auditor` v1.0.0 shipped (open-claw-stuff v0.4.0, commit `82474a7`)
- ✓ P1#7 `doc-updater` v1.0.0 shipped (open-claw-stuff v0.5.0, commit `d66b426`); smoke-test against ken caught the `v0.2.2 → v0.5.0` drift in WORKING-CONTEXT.md:38 on first run (fixed in same commit as this entry)
- ✓ P0.5#3 `fact-forcing-gate` and P0.5#4 `configuration-protection` shipped as policy-as-markdown files in `ken/.claude/policies/`; concept-lift only, both regex patterns validated against representative match + non-match sets per the schema's testing requirement
- ✓ P0#6 bookkeeping closed — sanitizer-sweep row updated to reflect v1.2.0 household pass already shipped on 2026-05-11
- ✓ P1#13 provenance schema shipped (open-claw-stuff v0.6.0); concept-lift broadens scope from skills-only to any-lifted-artifact and replaces ECC's numeric trust score with 4-tier verdict + append-only audit log; schema valid against Draft 2020-12 + rejects 8/8 adversarial malformed records; 3 example records covering opensource-sanitizer / harness-auditor / doc-updater
- ✓ Audit + redesign of `policy-as-markdown` (schema independence vs upstream)
- ✓ Threat-model self-audit of `opensource-sanitizer` and `policy-as-markdown` per operating principle #6

### Cross-repo queue

- Sanitizer audit of all 11 repos (scheduled next session; uses `opensource-sanitizer` v1.1.0 with expanded coverage)
- doc-updater pass on the 11 soul docs and 10 SKILLS.md files (scheduled for P1)
- continuous-learning-v2 upgrade of ken's cognitive-memory (scheduled for P1)
- Policy-as-markdown propagation: write `.claude/policies/*.md` files per repo from the documented "never do" lists in CAREFUL.md / claude.md / CLAUDE.md across the household

### Long-running

- Keeper Stage 1 implementation (designed; not yet built; see `ken/keeper-plan.md`)
- ICP-2 / ITW-Lite / FOM-Lite protocol convergence
- 9-repo `cross-repo-health` skill quarterly run

---

## Interfaces

| Surface | Authority |
|---|---|
| **Public truth** | GitHub repos under `jsschrstrcks1/` |
| **Internal execution truth** | this file (`ken/WORKING-CONTEXT.md`) |
| **Per-session truth** | `HANDOFF.md` files per repo (when present) |
| **Cross-session truth** | `ken/orchestrator/memory_ops.py` cognitive-memory store |
| **Per-repo voice and identity** | `ken/souls/soul-<reponame>.md` |
| **Per-repo skill catalog** | `<repo>/SKILLS.md` (or `open-claw-stuff/README.md`) |

---

## Update rule

This file stays detailed only for the current sprint and active queues. Completed work moves to the **Latest Execution Notes** log below. When the log gets long (rough threshold: 50+ entries or older than 90 days), summarize older entries into `docs/sprint-archive/<YYYY-MM>.md`.

When a P0/P1/P2 item ships, mark it **completed** in the classification tables and move the line item to the execution log with the commit SHA.

---

## Latest execution notes

### 2026-05-11 — security-tool audit (operating principle #6 added)

Triggered by user feedback: *"Security tools are the best place to hide malicious code."*

**Audit scope:** the two safety-category skills shipped this sprint — `opensource-sanitizer` and `policy-as-markdown`. Reviewed line-by-line through a threat-model lens (not just "is it correct" but "could this be a backdoor").

**`opensource-sanitizer` v1.0.0 audit findings:**

| Finding | Type | Fix in v1.1.0 |
|---|---|---|
| "Read-only by design" claim contradicted the report-writing behavior (no `Write` tool yet a report file gets created) | Contradiction | Clarified: skill describes the report; agent's own Write materializes it |
| Output template said `(redacted match)` but didn't enforce | Data leak risk | Mandatory redaction rule with format spec (`first4****last4`) |
| PASS WITH WARNINGS allowed shipping with HIGH findings | Permissive verdict | New tier: PASS WITH ACCEPTED RISK; HIGH without acceptance = FAIL |
| Missing patterns: Stripe, Twilio, SendGrid, Google API, GCP service accounts, Azure, npm, PyPI, Mailgun, DigitalOcean, Discord, GitLab, modern OpenAI/Anthropic formats | Coverage gap (16+ providers) | Expanded pattern table to 25+ patterns across 5 provider categories |
| DB URL pattern missed `redis://`, `mssql://`, `mariadb://`, `oracle://` | Coverage gap | Added |
| Slack webhook regex was case-restricted | Coverage gap | Made case-insensitive |
| Stage 5 pseudocode only checked `src/` and only handled JS+Python | Wouldn't work as written | Language-agnostic (10 languages); discovers all source dirs via `git ls-files` |
| Stage 6 git scan only checked `.env`/`.pem`/`.key` extensions | Coverage gap (missed credentials in regular files committed-then-removed) | Pattern-matches across full history; large-repo fallback to date-bounded walk |
| No "What this skill cannot do" section | Honesty gap | Added explicit limits |
| No "How to audit this skill" meta-section | Trust-without-verification | Added; user should audit the skill before trusting the output |
| Tool-scoping caveat about Bash arg injection not flagged | Architectural gap | Added section |
| No troubleshooting for large repos | Operational gap | Added |
| Allowed-tools missing `Bash(git diff:*)` and `Bash(git ls-files:*)` | Minor | Added |

Commit: `1ba9f5a` (opensource-sanitizer v1.1.0).

**`policy-as-markdown` v1.0.0 audit findings:**

| Finding | Type | Fix in v1.0.1 |
|---|---|---|
| No "audit imported policies" guidance | Trust gap | Added 7-step "How to audit a policy file" section |
| No explicit "what this skill cannot do" disclaimer | Honesty gap | Added section listing 7 things the skill won't catch |
| Tool scoping for `Write` / `Edit` not flagged | Architectural gap | Added "Tool scoping note" explaining the platform limit and the convention pinning writes to `.claude/policies/` |
| `severity: info` on sensitive operations not flagged as exfiltration risk | Threat-model gap | Added warning to "Patterns to refuse" and "How to audit" sections |
| Validation checklist didn't verify imported policies were audited | Procedural gap | Added two new checklist items |
| Common pitfall: impossible match-when conditions not documented | Operational gap | Added pitfall and troubleshooting row |

Commit: `8dbbae8` (policy-as-markdown v1.0.1).

**`silent-failure-hunter` reviewed:** clean. allowed-tools is read-only; no report-writing contradiction; no external URLs; no destructive suggestions; no prompt-injection in body. Same `Bash(grep:*)` arg-scoping caveat as the other Bash-using skills (Claude Code platform limit, not skill-specific).

**Operating principle #6 added** to this file. Codifies the audit posture so future security-tool lifts apply the same scrutiny by default.

**Plumbing:** open-claw-stuff bumped to v0.2.2 (commit `5bd7f3e`).

### 2026-05-11 — audit of P0 shipped skills + rename hookify-rules → policy-as-markdown

- **Audit finding.** The `hookify-rules` skill shipped in v0.2.0 (commit `80d7afc`) lifted upstream ECC's schema verbatim — field names (`name`, `event`, `action`, `pattern`, `conditions`, `field`, `operator`), event values (`bash` / `file` / `stop` / `prompt` / `all`), operator values (`regex_match` / `not_contains` / etc.), and file location (`.claude/hookify.<name>.local.md`). A rule file written for ECC's runner would have dropped into our runner unmodified. That's a clone, not our tool.
- **Operating principle #1 violated.** Concept lift, not code lift. Documented this principle at the top of this file so it can't drift again.
- **Audit of the other two P0 skills.** Both `opensource-sanitizer` and `silent-failure-hunter` were concept lifts. The regex patterns in `opensource-sanitizer` are industry-standard primitives (not ECC-specific). The 5-category taxonomy in `silent-failure-hunter` is generic to code review. Examples and severity rubrics in both are original. Kept as-is. (Note: a deeper threat-model audit of `opensource-sanitizer` on the same day found additional gaps — see entry above.)
- **Redesign.** Replaced `hookify-rules` with `policy-as-markdown`. Same concept (markdown-as-policy at the harness layer). Independent schema:
  - `rule` (vs their `name`)
  - `trigger` with 6 values, including split `before-edit` / `before-write` (vs their `event` with 5 values, unified `file`)
  - `severity` 3-tier: `block` / `warn` / `info` (vs their `action` 2-tier)
  - `match` / `match-when` (vs `pattern` / `conditions`)
  - `check` / `is` / `value` (vs `field` / `operator` / `pattern` in conditions)
  - hyphenated operator values (`matches-regex`) vs snake_case (`regex_match`)
  - `.claude/policies/<rule>.md` (vs `.claude/hookify.<name>.local.md`)
- **Rule files for one runner do not drop into the other.** Confirmed by walking both schemas field-by-field.
- **README quality bar updated.** Added "Concept-lift, not code-lift" to the contribution guidelines so the principle propagates to future contributors.
- **Commits:** `4eb9fa2` (deletion of old SKILL.md), `228445b` (new SKILL.md + plumbing v0.2.1).

### 2026-05-11 — ECC harvest sprint (P0 shipped, initial)

- **Reviewed** `affaan-m/everything-claude-code` in three passes: skills (182), agents (48), and broader concepts (rules, commands, schemas, working-context, hookify-rules).
- **Three prompt-injection events detected** — `<system-reminder>` blocks embedded in their README, chief-of-staff.md, and WORKING-CONTEXT.md. All attempted to influence TodoWrite usage. Treated as confirmed. Flagged in writeup. Ignored. None malicious in payload, but pattern is concerning enough to refuse bulk install.
- **install.sh + scripts/install-apply.js audited as clean** (npm install + Node CLI installer; no obfuscation; no exfiltration).
- **Created this file** (`ken/WORKING-CONTEXT.md`) as the household's lift of ECC's WORKING-CONTEXT.md pattern. P1#12 complete as a side-effect of writing the plan.
- **P0 skills shipped in `open-claw-stuff`** v0.2.0: `opensource-sanitizer`, `silent-failure-hunter`, `hookify-rules`. Commit `80d7afc`. (`hookify-rules` later renamed to `policy-as-markdown` after audit; both safety skills later patched to v1.1.0 / v1.0.1 after security-tool audit.)
- **P0#3 (`fact-forcing-gate`) and P0#4 (`configuration-protection`)** deferred to P0.5: they are hook patterns that need a per-repo hook-spec design before shipping. With `policy-as-markdown` now shipped, both will land as policy files (`.claude/policies/fact-forcing-gate.md` etc.).
- **P0#6 (sanitizer audit)** scheduled for next session. Audit order: ken first (hub; orchestrator/.env), then Romans (private + .ai-deny), then Grannysrecipes (memorial content), then the four recipe repos, then InTheWake + flickersofmajesty (public commerce/content), then Family-History, then manateecreeksheep.

### 2026-05-10 — voice skills upgrade

- Lifted 10 sub-disciplines from Romans's `like-a-human` into InTheWake's `like-a-human` (v3.1.0): copula avoidance, decorative adverbs, rule of three, low-probability details, dead metaphor, one-point dilution, syntactic template repetition, punctuation fingerprint, controlled flaw, building pattern.
- Lifted 4 sub-disciplines from Romans's `voice-audit` into InTheWake's `voice-audit` (v2.1.0): grep pattern for announcement-before-move, grep pattern for assumed-familiarity, image-density scan, must-be-absent list with explicit drift indicators.
- `voice-dna` left at parity (no upgrade needed).
- Commit: `5a6c123` on `claude/document-repo-souls-rb8LH` in InTheWake.

### 2026-05-10 — SKILLS.md per repo

- Created `SKILLS.md` (human-facing skill index) in 10 repos.
- Updated `CLAUDE.md` (and InTheWake's `claude.md`) in each to reference SKILLS.md.
- `open-claw-stuff`'s `README.md` serves as its skill index; CLAUDE.md updated to point at the README.
- Standard structure across all SKILLS.md: quick-reference table, "How invocation works" explainer, domain-specific skill detail with example trigger prompts, standard household kit table, multi-LLM orchestrator section per repo's mode, "See also."
- Total: ~247 skills documented across the household.

### 2026-05-10 — youdotcom-oss/agent-skills harvest

- Reviewed `youdotcom-oss/agent-skills` for the agent-skills-spec format.
- Adopted the format directly: `skills/{name}/SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `license`, `category`, `keywords`, `allowed-tools`, `compatibility`).
- Lifted the `<external-content>` wrapping pattern as a foundational skill in `open-claw-stuff`.
- Adopted the eval framework pattern: `data/prompts/prompts.jsonl` per skill.
- Tooling baseline lifted: Biome (TS) + Ruff (Python) + uv.

### 2026-05-09 — open-claw-stuff scaffolded

- Built `open-claw-stuff` into a working agent-skills-spec compliant repository (commit `ce80ba5`).
- 3 foundational skills: `careful-not-clever`, `verification-before-completion`, `external-content-wrapping`.
- Eval framework: `data/prompts/prompts.jsonl` with 9 trigger prompts (3 per skill).
- Tooling baseline: Biome (TS) + Ruff (Python) + uv.
- Public domain (Unlicense). README, CLAUDE.md, CONTRIBUTING.md, docs/spec.md, .claude-plugin/plugin.json, package.json all in place.

### 2026-05-09 — Souls written

- Documented soul (identity, voice, philosophy, technical anatomy, distinguishing marks, what-would-be-lost) for all 11 repos.
- Stored in `ken/souls/soul-<reponame>.md`.
- ken's soul includes the household's three nested systems (`tz` + orchestrator + keeper) and their continuity-over-throughput theme.
- Each soul ~10–15 KB; total ~140 KB of voice-and-identity documentation.


---

## v1.2.0 hardening audit log (2026-05-11)

Pipeline: async research agent (a2876f61c) → GPT challenge → Grok backdoor-design challenge → You.com critique → Claude-side synthesis.

**v1.2.0 changes vs v1.1.0 (full skill at `skills/opensource-sanitizer/SKILL.md`, 743 lines):**
- +16 credential patterns (ASIA, sk-ant-oat01-, ghr_, hf_, rk_/pk_/sk_live_, github_pat_, DeepSeek, Snowflake, Databricks, MCP server tokens, glpat-, etc.)
- 9 new sub-stages under Stage 7 (decode-rescan, Unicode hygiene, MCP config content scan, GH Actions workflow lint, SBOM compromised-package check, pre-install audit, SKILL.md prompt-injection lint, lookalike-domain detection, trufflehog/gitleaks invocation context)
- Stage 6 expansion: `git fsck --unreachable`, reflog scan, `.gitattributes` filter audit
- Redaction strengthened: full redaction ≤39 chars; `first2****last2 (len N)` ≥40 (was `first4****last4` — leaked 25% of high-entropy keys)
- "May 2026 threat context" section with 13 cited incidents and 25 source URLs
- "Backdoor defenses" section with 10 PR-rejection patterns derived from Grok red-team, each attributed
- Self-audit checklist (8 items, including no-soft-verdict-tier tripwire and external-link tamper-detection)

**Household sweep performed 2026-05-11 against 10 local repos.** Full report at `/tmp/HOUSEHOLD-SANITIZATION-REPORT-v1.2.0.md`.

Results:
- 10 of 10 PASS or PASS WITH WARNINGS
- 0 real credential exposures
- 0 git-history leaks
- 0 compromised packages, MCP configs, or pull_request_target triggers
- 2 MEDIUM findings (ken/.env.example incomplete; Family-History/Maurice SSN — deceased subject, accepted risk per user direction)
- 8 LOW findings (uniformly: mutable major-version action tags on official `actions/*`)
- 1 LOW (InTheWake): worked-example dummy creds in `admin/validator-spec/rules/SEC-005.md` re-trigger Stage 1 regex
- 1 LOW (InTheWake): `lycheeverse/lychee-action@v2.1.0` is a community action on a mutable tag

**Fix commits queued locally (push when proxy returns):**
- ken: 5 keys added to `orchestrator/.env.example`; 4 actions in `.github/workflows/static.yml` pinned to commit SHAs
- Romans: 1 action pinned in `.github/workflows/validate.yml`
- Grannysrecipes/Allrecipes/MomsRecipes/Grandmasrecipes: all `actions/*` references pinned across all workflows
- InTheWake: dummy credentials in `admin/validator-spec/rules/SEC-005.md` replaced with non-pattern-matching placeholders; `actions/*` pinned in `quality.yml` and `static.yml`; `lycheeverse/lychee-action@v2.1.0` pinned to commit SHA `f81112d0d2814ded911bd23e3beaa9dda9093915`
- Family-History: accepted-risk note added to README.md re: pre-2000 deceased-subject SSNs (per SSDI public-record convention)

---

## v1.2.1 queued hardening items (NOT YET IMPLEMENTED)

Identified during the v1.2.0 household sweep. Per user direction: ship v1.2.0 first, gather field data, then patch. Do **not** implement these as v1.2.0 hot-fixes.

1. **Stage 7.2 — skip Office container formats.** `.docx`/`.xlsx`/`.pptx`/`.odt`/`.odp`/`.ods` are zip archives whose embedded XML routinely contains U+200D (zero-width joiner) in metadata. v1.2 raised a false positive on `admin/inthewake/ship quiz tool planning.docx`. Add explicit skip globs to Stage 7.2.
2. **Stage 2 — pre-strip ISBN-formatted numbers** before SSN scan. The SSN regex `\b\d{3}-\d{2}-\d{4}\b` matches ISBN-13 prefixes like `978-84-7798`. False positives in Family-History on `978-84-7798-160-2` and `978-88-6969-403-5`. Add ISBN-13 pre-filter.
3. **Stage 7.4 — distinguish official `actions/*` from community actions.** v1.2 currently lumps both into one LOW severity for mutable major-version tags. Community actions (e.g., `lycheeverse/lychee-action`) deserve a separate tier (MEDIUM) given they're easier to compromise. Different attack surface.
4. **Stage 7.7 — add a "worked-examples-as-pattern" detection routine.** If a Stage 1 credential match occurs inside a file whose path contains `rules/`, `validator/`, `spec/`, `examples/`, or `tests/`, surface as "worked-example overlap" rather than CRITICAL. The InTheWake SEC-005.md case generalized. **Do NOT solve this by allowlisting paths** (Grok backdoor patterns #6 and #9). Solve it with a verdict downgrade only, no scan suppression.

---

## Operating principles update

No change to the 6 standing operating principles. The v1.2.0 sweep validated principle #6 (audit security tools harder) — the procedure's own self-audit checklist caught the InTheWake SEC-005.md worked-example overlap on first run.

---

## See also

| File | Purpose |
|---|---|
| [`README.md`](README.md) | Public-facing overview |
| [`CLAUDE.md`](CLAUDE.md) | Agent context with handoff protocol |
| [`SKILLS.md`](SKILLS.md) | Skill catalog (30 skills) |
| [`souls/`](souls/) | Voice and identity profiles per sister repo |
| [`keeper-plan.md`](keeper-plan.md) | Session-continuity tool design (in design) |
| [`plan.md`](plan.md) | Active plan for the hub |
| [`new-skills-proposal.md`](new-skills-proposal.md) | Proposed additions |
| [`skills-audit.md`](skills-audit.md) | Historical skill audit |
| [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) | Source for this sprint's harvest (MIT) |
| [`youdotcom-oss/agent-skills`](https://github.com/youdotcom-oss/agent-skills) | Source for the agent-skills-spec format (MIT) |
| [`jsschrstrcks1/open-claw-stuff`](https://github.com/jsschrstrcks1/open-claw-stuff) | Household's public-domain skill outflow |

---

*Soli Deo Gloria.*
