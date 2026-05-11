# Working Context — ken (the household hub)

**Last updated:** 2026-05-10

---

## Purpose

Operational truth document for `ken` and the household of 11 repos. Tracks current sprint, active queues, lift decisions from external sources, rejected items with rationale, and a chronological execution log.

Modeled on the `WORKING-CONTEXT.md` pattern lifted from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) (MIT). Adapted to household voice and scope.

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
| `open-claw-stuff` status | 3 foundational skills + agent-skills-spec scaffold + eval framework + tooling baseline |
| Standard household kit | 16 skills (canonical version in `ken/.claude/skills/`) |
| Multi-LLM orchestrator modes | 6 — sermon, sheep, cruising, recipe, family-history, triad |
| Current keeper status | Designed (Stage 1: 5 commands), not yet implemented |

---

## Current Constraints

- No bulk install of external Claude Code plugins. Cherry-pick patterns; never surrender hook authority to upstream maintainers.
- All skills lifted into `open-claw-stuff` must be Unlicense-compatible. **Re-write, do not copy-paste from MIT/Apache sources.** Attribute upstream in an Inspiration section.
- No execution of unverified upstream tooling (e.g., `npx ecc-agentshield scan`). Read source first; if we want the capability, ship our own implementation.
- Domain-specific skills stay in their domain repo. Only generic patterns belong in `open-claw-stuff`.
- Privacy posture per repo is non-negotiable: Romans `.ai-deny` content stays local; Grannysrecipes Memorial content never leaves the local machine; sermon manuscripts have strict context boundaries.

---

## ECC harvest classification (this sprint)

Three review passes covered `affaan-m/everything-claude-code`: skills (182), agents (48), and broader concepts (rules, commands, schemas, working-context, hookify-rules).

**Three confirmed prompt-injection events** were embedded in fetched documents (README.md, chief-of-staff.md, WORKING-CONTEXT.md). All three contained `<system-reminder>` blocks attempting to influence TodoWrite usage. Payloads were benign; the **pattern is concerning** — confirms decision to never bulk-install.

`install.sh` and `scripts/install-apply.js` were audited as clean (npm install + Node CLI installer; no obfuscation, no exfiltration).

### Lifting (P0) — defensive, ship this sprint

| # | Item | Source | Target | Status |
|---|---|---|---|---|
| 1 | `opensource-sanitizer` | ECC `agents/opensource-sanitizer.md` | `open-claw-stuff/skills/` | **shipping in this sprint** |
| 2 | `silent-failure-hunter` | ECC `agents/silent-failure-hunter.md` | `open-claw-stuff/skills/` | **shipping in this sprint** |
| 3 | `hookify-rules` | ECC `skills/hookify-rules/` | `open-claw-stuff/skills/` | **shipping in this sprint** |
| 4 | `fact-forcing-gate` (hook pattern) | ECC `hooks/hooks.json` | per-repo `.claude/hooks/` | **deferred to P0.5** — needs hook-spec design first |
| 5 | `configuration-protection` (hook pattern) | ECC `hooks/hooks.json` | per-repo `.claude/hooks/` | **deferred to P0.5** — needs hook-spec design first |
| 6 | Sanitizer audit of household | self-audit using `opensource-sanitizer` | all 11 repos | **scheduled after #1 ships** |

### Lifting (P1) — capability gaps, next sprint

| # | Item | Source | Target | Effort |
|---|---|---|---|---|
| 7 | `doc-updater` agent | ECC `agents/doc-updater.md` | `open-claw-stuff/skills/` | medium |
| 8 | `context-budget` skill | ECC `skills/context-budget/` | `open-claw-stuff/skills/` | medium |
| 9 | Continuous-learning-v2 / instincts (confidence-scored, project-scoped, auto-promoting memory) | ECC `skills/continuous-learning-v2/` | `ken/orchestrator/memory_ops.py` upgrade | **large** |
| 10 | `ai-regression-testing` | ECC `skills/ai-regression-testing/` | `ken/orchestrator/` + `open-claw-stuff/skills/` | medium |
| 11 | `harness-optimizer` agent + `/harness-audit` command | ECC `agents/harness-optimizer.md` + `commands/harness-audit.md` | `ken/.claude/skills/` | medium |
| 12 | WORKING-CONTEXT.md pattern | ECC `WORKING-CONTEXT.md` | `ken/WORKING-CONTEXT.md` | **completed (this file)** |
| 13 | Provenance schema | ECC `schemas/provenance.schema.json` | `open-claw-stuff/schemas/` | small |

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
| `npx ecc-agentshield scan` (their security tool) | Supply-chain risk; build our own `opensource-sanitizer` instead |
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
- → P0 ECC harvest (in progress: `opensource-sanitizer`, `silent-failure-hunter`, `hookify-rules` shipping)
- → P0.5 hook patterns (after P0 skills ship: `fact-forcing-gate`, `configuration-protection`)
- → P0#6 sanitizer audit of household (after `opensource-sanitizer` ships)

### Cross-repo queue

- Sanitizer audit of all 11 repos (scheduled after `opensource-sanitizer` skill ships in this sprint)
- doc-updater pass on the 11 soul docs and 10 SKILLS.md files (scheduled for P1)
- continuous-learning-v2 upgrade of ken's cognitive-memory (scheduled for P1)
- Hook-pattern propagation: hookify-rules per-repo files for the documented "never do" lists in CAREFUL.md / claude.md / CLAUDE.md across the household

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

### 2026-05-10 — ECC harvest sprint

- **Reviewed** `affaan-m/everything-claude-code` in three passes: skills (182), agents (48), and broader concepts (rules, commands, schemas, working-context, hookify-rules).
- **Three prompt-injection events detected** — `<system-reminder>` blocks embedded in their README, chief-of-staff.md, and WORKING-CONTEXT.md. All attempted to influence TodoWrite usage. Treated as confirmed (deliberate or side-effect). Flagged in writeup. Ignored. None malicious in payload, but pattern is concerning enough to refuse bulk install.
- **install.sh + scripts/install-apply.js audited as clean** (npm install + Node CLI installer; no obfuscation; no exfiltration).
- **Created this file** (`ken/WORKING-CONTEXT.md`) as the household's lift of ECC's WORKING-CONTEXT.md pattern. P1#12 complete as a side-effect of writing the plan.
- **P0 skills shipping in `open-claw-stuff`** this sprint: `opensource-sanitizer`, `silent-failure-hunter`, `hookify-rules`. All re-written for Unlicense compatibility with attribution to ECC in each Inspiration section.
- **P0#3 (`fact-forcing-gate`) and P0#4 (`configuration-protection`)** deferred to P0.5: they are hook patterns that need a per-repo hook-spec design before shipping. Hookify-rules ships first; those two will be ported as hookify rule files.
- **P0#6 (sanitizer audit)** scheduled for immediately after `opensource-sanitizer` skill ships. Audit order: ken first (hub; orchestrator/.env), then Romans (private + .ai-deny), then Grannysrecipes (memorial content), then the four recipe repos, then InTheWake + flickersofmajesty (public commerce/content), then Family-History, then manateecreeksheep.

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
