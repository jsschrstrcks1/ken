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

These feed *other* models. Voice rules still apply but with two additions:

- **Role boundaries explicit.** The prompt names what the consultant model is and is not for.
- **No leakage of internal-only context.** Voice-audit also flags any prompt that references private paths or internal docs that consultants shouldn't see.

### CLAUDE.md

The bar is highest. CLAUDE.md is read by every Claude session that starts here. Every fluff word costs every session forever. Target: zero LLM-doc-fluff, zero hedged rules, zero marketing drift. Treat any non-Low rating as blocking.

### HANDOFF.md

Telegraph style. Bullets. State. Paths. Numbers. The audit's specificity check is the hardest gate — if a HANDOFF reads like prose, it has already failed its purpose.

---

## AI-Tell Detection Framework (v3)

Added 2026-05-25. This section codifies a layered framework for identifying probable AI authorship in completed prose. The framework was refined through adversarial iteration; earlier versions overclaimed on isolated features (chiasmus, performative tone, "humans don't usually open this way"). The v3 version corrects those errors and operationalizes the core insight: **AI authorship is detected by clustering and density, not by individual features.**

### The operational rule: cluster, don't single

No single feature is a verdict. A passage flagged only for one item in any layer below is at most a yellow flag, not a finding. The framework requires clustering across layers — at least one strong signal and one or more supporting signals, with counter-signals weighed against them — before any AI-likelihood claim is made.

### Layer 1 — Strong signals (high confidence when clustered)

- **Semantic placeholders where concrete referents could go.** AI gravitates to "the mission," "the work," "the hard questions," "the rooms where decisions get made," "the journey," "the challenge." Test each instance: can the abstraction be traced to a concrete referent in surrounding context? If yes, the placeholder is shorthand and acceptable. If no, the placeholder is filler.
- **Broad authority claims with no specifics.** "I've been in the rooms where decisions get made" without naming a single room is the canonical case. Acceptable form: the claim with the anchor. Unacceptable form: the claim without the anchor.
- **Triplet closures carrying rhythm but not content.** Test: if the third item in the triplet is deleted, does meaning collapse or does the sentence just lose its musical close? If only the music is lost, the closure was decoration.
- **Clean, linear persuasion arc** with no digression, no authorial uncertainty, no moment where the writer admits something doesn't fit cleanly. Human prose has friction; optimized AI output rarely does.

### Layer 2 — Supporting signals (need Layer 1 to confirm)

- Stock consultant phrases ("seamlessly," "robust," "leverage," "best-in-class," "world-class")
- Clichés ("every shape and size," "more with less")
- Sustained staccato fragment-clustering without rhythm variation
- Parallel structures and chiasmus when they read manufactured-clean (chiasmus is ancient rhetoric — its presence is human-first; the signal is overuse and unbroken cleanness, not appearance)
- "Too smooth" delivery — no awkwardness, no recovered phrases, no second thoughts

### Layer 3 — Counter-signals (favor human authorship)

- Named entities, places, dates, paths, file names, command outputs, version numbers
- Mild awkwardness, sentence-shape variation, unexpected word choices
- Localized claims with bounded scope ("on Devuan," "in the November release cycle")
- Authorial hedging that names the limit of what's claimable
- Specific verifiable quotes with attribution
- Friction, contradiction, or admitted uncertainty within the prose

### Hard constraints (non-negotiable; these override the cluster test)

Earlier framework versions produced false positives by violating these. They are absolute:

- **Performative is not artificial.** Humans are routinely performative — especially in testimony, advocacy, preaching, public speaking. A passage that reads "performed" is not on that basis AI-generated.
- **Rhetorical devices are human first.** Chiasmus, anaphora, parallelism, triplet closures, contrast reframing — all are ancient rhetoric, all predate AI by centuries. Their presence is never evidence of AI authorship. Their clean, mechanized overuse without substance is the actual signal.
- **Specificity strongly favors human authorship; lack of specificity does not prove AI.** Many human writers are vague. Vagueness alone is not a verdict.
- **All conclusions are probabilistic.** The framework produces "likely AI," "likely human," or "unclear" — never a definitive label.
- **Context matters.** Testimony, preaching, advocacy, sermon, eulogy, and political address operate at elevated register by genre convention. Apply the framework with awareness of which register the passage is in.

### Cluster scoring (operational)

To produce a verdict, count by layer:

- 0 Layer 1 signals → likely human regardless of Layer 2
- 1 Layer 1 + 0 Layer 2 → unclear (yellow flag, no verdict)
- 1 Layer 1 + 2+ Layer 2 → likely AI, modulo counter-signals
- 2+ Layer 1 → likely AI, modulo counter-signals

Counter-signals modulate the verdict downward by one notch each. Three or more counter-signals override any combination of Layer 1 + Layer 2 signals; this is what protects skilled human writing from false positives.

### Falsification test

Before any change to this framework, run the modified framework against the passages in `falsification-test.md` in this directory. Those passages are highly polished human writing with multiple features the framework lists as AI signals. They should pass the cluster test and produce "likely human" verdicts. If a framework update causes any of those passages to be flagged as AI, the update is too aggressive and must be revised.

### Note on documentation context

This framework is general — it applies to any prose. For ken-specific documentation (README, CLAUDE.md, HANDOFF), the framework's hard constraints still hold, but the counter-signals weight is higher: docs are expected to be specific, hedged, and friction-laden by their nature. A doc that reads as smooth marketing prose is almost always AI-template-shaped. A doc that reads as terse, awkward, command-and-path-exact is almost always human-authored or carefully AI-edited under human discipline. The five-axis scan above (LLM-doc-fluff, specificity, imperative mood, marketing drift, cadence/density) is the documentation-tuned application of the same underlying detection logic.

---

*Documentation is the work, six months from now. Audit before commit.*
