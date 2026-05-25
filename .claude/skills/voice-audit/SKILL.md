---
name: voice-audit
description: "Post-draft diagnostic for ken documentation. Scans READMEs, CLAUDE.md, HANDOFF files, plan docs, and orchestrator prompt templates for LLM-doc-fluff and marketing drift. Pairs with verification-before-completion before committing documentation changes. For during-writing standards, see like-a-human. For corpus measurement, see voice-dna."
version: 1.0.0
---

# Voice Audit — ken Documentation Diagnostic

## Purpose

`like-a-human` shapes the writing. `voice-dna` measures the corpus. `voice-audit` evaluates a *finished* document: counts the LLM-doc-fluff, finds the marketing drift, flags the hedge stacking, and recommends restoration edits.

Documentation is high-leverage prose. A bad CLAUDE.md or a fluffy README costs every future session that reads it. The audit's job is to keep ken's docs at utility-prose standard before they harden into the canon.

## When to Fire

- Before committing any change to: `README.md`, `CLAUDE.md`, `HANDOFF.md`, `*.md` plan docs, `orchestrator/modes/*`, `.claude/skills/*/SKILL.md`
- On `/voice-audit <path>`
- After any AI-assisted documentation draft (treat AI assists as suspect by default)
- Before opening a PR that touches documentation

## The Five-Axis Scan

### 1. LLM-Doc-Fluff Scan

Count instances of:

- **Banned LLM-doc vocabulary** (`seamlessly, robust, leverage, dive into, unlock, transform, holistic, comprehensive, cutting-edge, state-of-the-art, best-in-class, world-class, powerful, intelligent, smart (as adj), elegant (as adj for code), beautifully, effortlessly, intuitively, organically, naturally (filler)`)
- **Filler transitions** (`Moreover, Furthermore, Additionally, In essence, In conclusion, Ultimately, At its core, In summary, As you can see, It's important to note that`)
- **Marketing verbs** (`enables, empowers, streamlines, accelerates, optimizes, unleashes, facilitates, elevates, supercharges`)
- **Hedge stacks** (multiple `might/could/perhaps/generally/typically` in a single rule — 1 instance is fine, stacking is the tell)
- **Adjective stacks** (2+ adjectives modifying the same noun — "powerful, flexible, robust orchestrator")
- **Universal-audience hedging** ("Whether you're a beginner or expert…" "For developers of all skill levels…")
- **Conclusion bloat** (closing summaries that restate the section)
- **Synthetic earnestness** ("Here's the thing:" "The truth is:" "Let's be real:")
- **Synonym cycling** (`command → utility → tool → function` in one section)
- **Abstract authority clustering** (multiple instances of `mission, work, framework, ecosystem, platform, journey, story` in the same section without concrete referents — single use is fine; clustering without anchors is the tell. Test each instance: does the surrounding two sentences name a path, command, file, or specific behavior? If yes, the abstraction is shorthand. If no, it is filler dressed as authority.)
- **Identity-archetype framing** (prose that positions the doc, the system, or the author as "the one who sees what others miss," "the bridge between approaches," or "the voice that warns" — AI-shaped narrative templates that have no place in utility prose. Rare in command-reference and HANDOFF docs; most likely to appear in plan-doc rationale sections and orchestrator-prompt-template framing.)

Report: **count + line numbers + exact phrase**. No paraphrasing.

### 2. Specificity Check

Verify that the document tethers to ken specifically, not to a generic project:

- [ ] Concrete paths present (`/`, `~/`, `.claude/`, `orchestrator/`)
- [ ] Exact commands runnable (no `your-command-here` placeholders unless explicitly templated)
- [ ] Real errors quoted in code spans where failure modes are discussed
- [ ] Real numbers (sizes, timeouts, throttles, counts)
- [ ] Named modes/adapters/scripts (not "various adapters")

Fail trigger: if every concrete reference were swapped for a placeholder, the doc would still make grammatical sense — the doc is generic. High risk.

### 3. Imperative-Mood Check (rules and instructions only)

For sections that establish rules, protocols, or procedures (CLAUDE.md, HANDOFF.md template sections, install instructions):

- [ ] Rules use imperative mood ("Run X." "Never Y.")
- [ ] No conditional fluff on unconditional rules ("You might want to consider not pushing to main" is wrong; "Never push to main" is right)
- [ ] Negative rules stated directly
- [ ] Where conditions exist, they are named ("On Devuan, X." not "In some cases, X.")

Flag any rule that hedges where it should command.

### 4. Marketing-Drift Check

ken's docs do not sell. Verify:

- [ ] No "powerful," "intelligent," "world-class," "best-in-class," "comprehensive"
- [ ] No promotional verbs (`enables, empowers, streamlines…`)
- [ ] No call-to-action language ("Get started today," "Unlock the power of…")
- [ ] No conclusion that restates earlier value claims
- [ ] No section reads like a pitch
- [ ] No Soli Deo Gloria mid-document; only at the natural close of a top-level doc, sparingly

If any reader could mistake the doc for marketing copy, the voice has drifted. Flag.

### 5. Cadence and Density Check

Verify:

- [ ] Bullets and tables carry fixed-shape information (commands, modes, files — these should not be in paragraph form)
- [ ] Code blocks present where commands are described
- [ ] No bridge prose between sections ("Now that we've covered X…")
- [ ] No pre-padding before code blocks ("Here's an example:")
- [ ] No post-padding after code blocks ("As you can see…")
- [ ] Sentence length variance present (rules short, reasoning longer)
- [ ] No 200+ word paragraphs unless the doc is a plan-doc with reasoning

Flag uniform-paragraph stretches and bridge-prose density.

## Risk Rating

**Low risk** — commit it.
- LLM-doc-fluff: 0–1 instances
- Specificity check passes (concrete paths, commands, errors, numbers)
- Imperative-mood check passes on rules
- No marketing drift
- Cadence varied; bullets/tables/code blocks carry the load

**Medium risk** — restore before commit.
- LLM-doc-fluff: 2–4 instances
- One specificity gap
- 1–2 hedge-stacked rules
- Light marketing drift (one adjective stack, one promotional verb)
- Some bridge prose

**High risk** — hold for revision.
- LLM-doc-fluff: 5+ instances
- Specificity check fails (doc is generic)
- Imperative-mood failures on multiple rules
- Marketing drift dominant (reads like a pitch)
- A CLAUDE.md or a HANDOFF.md — these are infrastructure prose; the bar is *zero* fluff. Any LLM-doc-fluff in these is automatically Medium minimum.

## Restoration, Not Rewriting

When the rating is Medium, recommend **3–6 surgical edits**, each one:

- Quotes the exact phrase to remove
- Provides a 1–3 word replacement OR a deletion
- Names the axis the edit fixes

Do not propose new sections. Do not restructure unless the structure itself is the problem.

When the rating is High, the recommendation is to **rewrite the section from a fresh outline**, working from the actual facts (paths, commands, errors), not to patch.

## Audit Report Format

```
## Voice Audit — [doc-path]
**Path:** [file path]
**Doc type:** [README / CLAUDE.md / HANDOFF / plan / skill / orchestrator-prompt]
**Date:** [YYYY-MM-DD]

### LLM-Doc-Fluff
- Banned vocabulary: [N] — [list with line numbers]
- Filler transitions: [N] — [list]
- Marketing verbs: [N] — [list]
- Hedge stacks: [N]
- Adjective stacks: [N]
- Universal-audience hedging: [N]
- Conclusion bloat: [yes/no]
- Synthetic earnestness: [N]
- Synonym cycling: [N]

### Specificity
- Concrete paths: [count]
- Exact commands: [count]
- Quoted errors: [count]
- Real numbers: [count]
- Named modes/adapters/scripts: [yes/no]
- Verdict: [specific/generic]

### Imperative Mood (rules sections)
- Rules in imperative: [%]
- Hedged rules: [count] — [list]
- Verdict: [pass/fail]

### Marketing Drift
- [pass/fail with specifics]

### Cadence and Density
- Bullets/tables for fixed-shape info: [yes/no]
- Code blocks present where needed: [yes/no]
- Bridge prose: [N instances]
- Pre-padding / post-padding: [N instances]
- Verdict: [varied/uniform]

### Risk Rating: [Low / Medium / High]

### Recommended Edits
1. [exact quote @ line N] → [replacement/deletion] — [axis]
2. ...
```

## Integration With Other Skills

- Run **after** any AI-assisted documentation draft.
- Run **before** `verification-before-completion` for documentation work.
- Run **before** `finishing-a-development-branch` if the branch touched docs.
- Pair with `careful-not-clever` (where present) for content-accuracy review; voice-audit catches mechanical tells, careful-not-clever catches factual cleverness.
- High-risk docs that get rewritten should feed back into `voice-dna` after the rewrite — confirm the rewritten version measures inside the corpus baseline.

## Special Cases

### Orchestrator Prompt Templates (`orchestrator/modes/*`)

These feed *other* models. Voice rules still apply but with three additions:

- **Role boundaries explicit.** The prompt names what the consultant model is and is not for.
- **No leakage of internal-only context.** Voice-audit also flags any prompt that references private paths or internal docs that consultants shouldn't see.
- **No identity-archetype framing.** Prompts that position the consultant as "the one who sees what others miss," "the bridge between approaches," or "the voice that warns" are AI-shaped narrative templates. Address the consultant by role and task only — describe what to evaluate, not who to be.

### CLAUDE.md

The bar is highest. CLAUDE.md is read by every Claude session that starts here. Every fluff word costs every session forever. Target: zero LLM-doc-fluff, zero hedged rules, zero marketing drift. Treat any non-Low rating as blocking.

### HANDOFF.md

Telegraph style. Bullets. State. Paths. Numbers. The audit's specificity check is the hardest gate — if a HANDOFF reads like prose, it has already failed its purpose.

---

## Examples

- [`examples/good-voice.md`](./examples/good-voice.md) — utility-prose handoff that passes the audit.
- [`examples/bad-voice.md`](./examples/bad-voice.md) — same handoff in the failure mode this skill catches.

---

*Documentation is the work, six months from now. Audit before commit.*
