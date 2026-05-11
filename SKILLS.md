# Skills — ken

> The hub. Hosts the multi-LLM orchestrator and the canonical version of every household-wide skill.

This document is the human-facing index of all Claude Code skills configured in this repository. The agent-facing pointer lives in [`CLAUDE.md`](CLAUDE.md). Skills follow the agent-skills-spec format and live under `.claude/skills/`.

**Total skills configured: 30.** Of those, 16 are the standard household kit (see below) and 14 are ken-specific — most importantly the four orchestrator skills (`/consult`, `/orchestrate`, `/orchestra`, `/investigate`) that every sister repo borrows.

---

## Quick reference

| Skill | Activation | Default | Domain |
|---|---|---|---|
| [`consult`](#consult) | explicit | on | Multi-LLM orchestrator |
| [`orchestrate`](#orchestrate) | explicit | on | Multi-LLM orchestrator |
| [`orchestra`](#orchestra) | explicit | on | Multi-LLM orchestrator |
| [`investigate`](#investigate) | explicit | on | Multi-LLM orchestrator |
| [`orchestrator-monitor`](#orchestrator-monitor) | explicit | on | Multi-LLM orchestrator |
| [`cross-repo-health`](#cross-repo-health) | explicit | on | Hub ops |
| [`google-sheets-migration`](#google-sheets-migration) | explicit | on | Hub ops |
| [`indexnow`](#indexnow) | automatic on page edits | on | Hub ops |
| [`person-page`](#person-page) | explicit | on | Genealogy support |
| [`skill-developer`](#skill-developer) | automatic + explicit | on | Skill authoring |
| [`like-a-human`](#like-a-human) | automatic on documentation writing | on | Voice |
| [`voice-audit`](#voice-audit) | automatic post-draft | on | Voice |
| [`voice-dna`](#voice-dna) | explicit | on | Voice |
| [`icp-2`](#icp-2) | automatic on content writing | on | Standards |
| Standard household kit (16 skills) | mixed | on | See [section below](#standard-household-kit) |

---

## How invocation works

Claude Code skills can fire three ways:

**1. Automatic activation.** Each skill's YAML frontmatter declares `keywords:`. When those keywords appear in your prompt, in surrounding context (file paths, recent tool output), or in the operation Claude is about to perform, the skill auto-activates without being asked.

**2. Explicit invocation.** Name the skill directly:

```
"Use the <skill-name> skill to ..."
/skill <skill-name>
```

The orchestrator skills also have slash commands: `/consult`, `/orchestrate`, `/orchestra`, `/investigate`. Those are the canonical entry points.

**3. Implicit invocation by task shape.** Skills fire on certain operations regardless of keywords — bulk edits trigger `careful-not-clever`-style guardrails (delegated downstream), completion claims trigger `verification-before-completion`, page writes trigger `indexnow`, etc.

**Disabling for a session:** "For this session, do not apply the X skill — I just want a sketch." Skills respect explicit user override.

**Permanently disabling:** Remove from `.claude/skills/` or set `enabled: false` in `.claude/settings.json`.

---

## Multi-LLM orchestrator skills

This repo hosts the orchestrator at `orchestrator/`. These four skills are the hub's primary export to every sister repo. **All four require dependencies installed once per session:**

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

### `consult`

**Path:** `.claude/skills/consult/SKILL.md`
**Slash command:** `/consult`

Quick single-model second opinion. Sends a single prompt to GPT, Gemini, Grok, You.com, or Perplexity with a role-based system prompt and returns structured feedback.

**Manual invocation:**

```
/consult <model> <role> "<prompt>"
/consult gpt structure "review this product page layout"
/consult grok challenge "is this Romans 5 outline gospel-clear?"
/consult perplexity research "recent FAMACHA studies in Florida sheep"
```

**When to use:** when you want one model's view, fast. Cheaper than `/orchestrate`. Returns within seconds.

### `orchestrate`

**Path:** `.claude/skills/orchestrate/SKILL.md`
**Slash command:** `/orchestrate`

Full multi-model linear pipeline. Each repo has a default mode (`sermon`, `sheep`, `cruising`, `recipe`, `family-history`, `triad`); `ken` is the hub and has **no default** — specify the mode explicitly.

**Manual invocation:**

```
/orchestrate <mode> "<task>"
/orchestrate cruising "generate gallery page content for Mountain Majesty"
/orchestrate sheep "evaluate fall breeding pairs"
```

**Pipeline shapes by mode:**

| Mode | Pipeline |
|---|---|
| `sermon` | Draft (Claude) → Challenge (Grok) → Expand (Gemini) → Structure (GPT) → Integrate (Claude) → Evaluate (Claude) → Voice Audit (Claude) |
| `cruising` | Read Standards (Claude) → Generate (Claude) → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate (Claude) |
| `sheep` | Plan (GPT) → Context (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT) |
| `recipe` | Transcribe → Validate → Integrate (lead: GPT) |
| `family-history` | Research → Synthesize → Verify (lead: Claude) |
| `triad` | Three-model concurrent + deliberation |

### `orchestra`

**Path:** `.claude/skills/orchestra/SKILL.md`
**Slash command:** `/orchestra`

Round-robin multi-LLM consultation with full-context debate. GPT proposes, Gemini refines, Grok challenges — each sees the full chain including wheat/chaff verdicts and justifications. **Nothing is filtered between rounds.**

**Manual invocation:**

```
/orchestra "<task>"
/orchestra "design the breeding pen layout for parasite-resistance selection"
```

**When to use:** when a single linear pipeline is too narrow and you want models to argue. Slower and more expensive than `/orchestrate`.

### `investigate`

**Path:** `.claude/skills/investigate/SKILL.md`
**Slash command:** `/investigate`

4-phase chained investigation pipeline: reconnaissance → triage → deep research → synthesis. Produces content pages from thorough multi-LLM research. Used heavily in `Family-History` (`research_orchestra.py --deep`).

**Manual invocation:**

```
/investigate <mode> "<subject>"
/investigate family-history "Manuel Lorenzo Solana, Spanish Dragoon, St Augustine 1763-1821"
```

### `orchestrator-monitor`

Tracks API costs, response quality, and failure rates per model across the multi-LLM orchestrator. Makes usage data queryable.

**When to use:** when investigating cost overruns or model regressions. Read-only.

---

## Hub-ops skills

### `cross-repo-health`

One-command health check across all 9 repositories. Checks content freshness, link integrity, validation status, memory health, and git status.

**When to use:** before a release pass; when something feels off across the household; weekly maintenance.

### `google-sheets-migration`

Migrates real data from old 113-tab spreadsheet to new 26-tab structure. Chunked execution with checkpoint/resume to survive Apps Script 6-minute timeout and Claude Code rate limits. Currently used for the manateecreeksheep migration; pattern is reusable.

### `indexnow`

Auto-submits pages to IndexNow when created or edited. Notifies Bing, Yandex, Naver, Seznam, Yep — no waiting for crawlers. Activates automatically on page edits.

### `person-page`

Builds or rebuilds person pages section-by-section using the v2 template. Prevents timeout on data-rich pages by writing incrementally with checkpoint saves between sections. Used in `Family-History`.

### `skill-developer`

Creates and manages Claude Code skills following Anthropic best practices. Covers skill structure, YAML frontmatter, trigger types (keywords, intent patterns, file paths, content patterns), enforcement levels (block/suggest/warn), hook mechanisms (UserPromptSubmit, PreToolUse), session tracking, and the 500-line rule.

**When to use:** when authoring a new skill, modifying `skill-rules.json`, or debugging skill activation.

---

## Voice skills

### `like-a-human`

Voice & Presence guard — fires during ken documentation writing (READMEs, CLAUDE.md, HANDOFF.md, plan docs, orchestrator prompt templates). Guards utility-prose voice: terse, specific, command-and-path exact, no marketing or sermon overlay.

**Activation:** automatic during documentation writing.

### `voice-audit`

Post-draft diagnostic. Scans READMEs, CLAUDE.md, HANDOFF files, plan docs, and orchestrator prompt templates for LLM-doc-fluff and marketing drift.

**Activation:** automatic post-draft, before commit.

### `voice-dna`

Discovers voice patterns from ken's documentation corpus. Measures rhythm, vocabulary, structural fingerprints. Calibrates `like-a-human` and `voice-audit` for technical prose, distinct from sermon and cruise voices.

**Activation:** explicit. Run when calibrating voice tooling.

---

## Standards skill

### `icp-2`

ICP-2 — Human-First SEO & Answer Engine Optimization (AEO) standard for 2026.

**Activation:** automatic when content writing surfaces SEO/AEO concerns.

---

## Standard household kit

These 16 skills are common to every sister repo. ken hosts the canonical versions; sister repos sync from here.

| Skill | Activation | One-line |
|---|---|---|
| `brainstorming` | automatic on creative work | Pre-implementation creative exploration. Fires before features, components, or behavior changes. |
| `cognitive-memory` | automatic on session start | Cross-session knowledge persistence with semantic search (TF-IDF). Memory scope: `/ken`. |
| `executing-plans` | explicit | Use when you have a written implementation plan to execute in a separate session. |
| `finishing-a-development-branch` | explicit | Use when implementation is complete and you need to decide how to integrate (merge, PR, cleanup). |
| `prompt-optimizer` | automatic on prompt-improvement requests | Analyzes raw prompts and outputs an optimized version. Advisory only. |
| `receiving-code-review` | explicit | Use when receiving review feedback before implementing suggestions, especially if feedback seems unclear. |
| `requesting-code-review` | explicit | Use when completing tasks or before merging to verify work meets requirements. |
| `safety-guard` | automatic on destructive ops | Prevents destructive operations on production systems or when running agents autonomously. |
| `security-review` | automatic on auth/secrets/payment | Comprehensive security checklist + patterns. |
| `security-scan` | explicit | Scans `.claude/` config for vulnerabilities and injection risks via AgentShield. |
| `session-checkpoint` | automatic + explicit | Atomic commits, checkpoint summaries, rate-limit recovery. Writes to cognitive-memory. |
| `subagent-driven-development` | explicit | Use when executing implementation plans with independent tasks in current session. |
| `systematic-debugging` | automatic on bug/test-failure | Use when encountering any bug, test failure, or unexpected behavior — before proposing fixes. |
| `using-git-worktrees` | explicit | Use when starting feature work that needs isolation, or before executing implementation plans. |
| `verification-before-completion` | automatic on completion claims | Refuses "complete/fixed/passing" without observed verification output. |
| `writing-plans` | explicit | Use when you have a spec for a multi-step task, before touching code. |

---

## See also

- [`CLAUDE.md`](CLAUDE.md) — agent context for this repo
- [`README.md`](README.md) — public-facing overview
- [`orchestrator/`](orchestrator/) — multi-LLM pipeline implementation
- [`orchestrator/repo-modes.json`](orchestrator/repo-modes.json) — canonical repo → mode → lead-model mapping
- [`open-claw-stuff`](https://github.com/jsschrstrcks1/open-claw-stuff) — public-domain skills (generic versions of `careful-not-clever`, `verification-before-completion`, `external-content-wrapping`)
- [`souls/`](souls/) — voice and identity profiles per sister repo
- [`skills-audit.md`](skills-audit.md) — historical audit of skill coverage
- [`new-skills-proposal.md`](new-skills-proposal.md) — proposed additions
