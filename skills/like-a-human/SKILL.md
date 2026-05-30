---
name: like-a-human
description: "Voice & Presence — fires during ken documentation writing (READMEs, CLAUDE.md, HANDOFF.md, plan docs, orchestrator prompt templates). Guards utility-prose voice: terse, specific, command-and-path exact, no marketing or sermon overlay. For post-draft diagnostics, see voice-audit."
version: 1.0.0
---

# like-a-human — ken Documentation Voice Standard

## Core Principle

ken is a personal hub for nine repos. Its prose is **utility**: a reader skims for the command, the path, the constraint, the failure mode. The voice serves that scan.

The standard is not literary. It is also not marketing. The reader of ken's docs is one of two people:

1. **The author six months from now.** Wants the exact path and the exact command, fast. Doesn't need to be sold.
2. **A future Claude session.** Wants the rule ("never push to main"), the protocol ("write the handoff before the work"), and the exact file location.

Either reader is hurt by marketing prose, by hedged language, and by LLM-doc-fluff. So the voice rejects all three.

## Three Trust Signals (in priority order)

1. **Specificity.** Exact paths, exact commands, exact filenames, exact failure modes.
2. **Imperative directness.** "Run X." "Never Y." "Edit Z." Tell, don't suggest.
3. **Failure-mode honesty.** Real errors, named, with the fix. "If you see `cannot import name 'genai' from 'google'`, run `pip install google-genai`."

If prose lands all three, the voice is intact regardless of length.

## Hard-Banned Vocabulary

**LLM-doc-fluff (zero tolerance):**

`seamlessly, robust, leverage, dive into, dive in, unlock, transform, holistic, comprehensive, cutting-edge, state-of-the-art, best-in-class, world-class, powerful, intelligent, smart (as adjective for tools), elegant (as adjective for code), beautifully (as adverb), effortlessly, intuitively, organically, naturally (as filler)`

**Filler transitions:**

`Moreover, Furthermore, Additionally, In essence, In conclusion, Ultimately, At its core, In summary, To summarize, As you can see, It's important to note that, It should be noted that`

**Marketing verbs (use plain alternatives):**

`enables, empowers, streamlines, accelerates, optimizes, unleashes, facilitates, drives (as in "drives results"), elevates, supercharges`

Replace with: `runs, installs, writes, reads, sets, returns, fails, succeeds, prints, exits, raises, allows`. Or rephrase so the verb is unnecessary.

**Hedge words (cut unless the uncertainty is real):**

`might, could, perhaps, generally, typically, often, sometimes, somewhat, fairly, rather, quite, very, really, simply, just, basically, essentially`

If an instruction is conditional, name the condition: "On Devuan/SysVinit, run X." Do not write "You might want to consider running X."

## Specificity Rules

- **Paths are absolute or unambiguous.** `/Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/.env`, not "the env file."
- **Commands are runnable.** Show the exact incantation, including flags. If a command is dangerous, say so on the line before.
- **Errors are quoted.** Real error strings, in `code spans`, with the exact remediation.
- **Numbers are real.** "1,200+ ports," "throttled to once per five minutes," "6-minute Apps Script timeout" — these are signature ken specifics.
- **Failure modes are named.** `_cffi_backend` / `cryptography` errors, `401 / no-credentials`, `ModuleNotFoundError` — name what the user actually sees.

## Replace Vague with Concrete

- "the orchestrator" → fine on first reference; afterward, name the script (`orchestrate.py`)
- "a config file" → the exact path
- "various adapters" → list them: GPT, Gemini, Grok, Perplexity, You.com
- "some setup is required" → give the setup command
- "in certain cases" → name the case
- "the right way" → give the way

## Machine Tells to Eliminate

**Announcement-Before-Move.** "In this section, we'll discuss..." Cut. Just discuss it.

**Scope-Statement Filler.** "This guide covers everything you need to know about X." Cut. The guide is the coverage.

**Conclusion Bloat.** "In summary, we've seen that the orchestrator..." Sections end when the work ends. No closer required.

**Adjective Stacking.** "a powerful, flexible, robust orchestrator" → "the orchestrator." One adjective is the maximum; usually zero.

**False Ranges.** "From simple scripts to complex pipelines" — cut unless both endpoints are concrete.

**Universal-Audience Hedging.** "Whether you're a beginner or expert..." ken's docs assume the reader has the context the prose has already established. They don't address every possible reader.

**Synonym Cycling.** "command… utility… tool… function…" rotating to avoid repetition. Pick the right word and reuse it.

**Synthetic Earnestness.** "Here's the thing:" "Let's be real:" "The truth is:" — these belong in blog posts, not in ken's docs.

**Marketing Pivot.** A docs section that starts technical and slides into pitch ("…making it the most powerful X you'll ever use"). Cut the pivot. The user is already here.

## Native Moves (Protect These)

- **Imperative mood.** "Run X." "Never Y." "Edit Z."
- **Path-and-command sentences.** Half a sentence of prose, half a code span.
- **Tables for fixed-shape information.** Commands, modes, repos, files — all of these belong in tables.
- **Code blocks for runnable commands.** Always.
- **Failure-then-fix pairs.** "If `pip install google-genai` fails with `_cffi_backend` errors, run: `pip install cffi cryptography --force-reinstall --ignore-installed`."
- **Negative rules stated directly.** "Never push to `main` directly." "Never commit `.env`."
- **Why-comments where the choice is non-obvious.** Brief. One sentence. Only when the rule would otherwise look arbitrary.
- **Bracketed soli-deo-gloria at the natural close** of a top-level doc. Sparingly. Never mid-document.

## Cadence

ken's voice is short sentences for rules and constraints; longer sentences only when explaining a non-obvious *why*. Bullets and tables carry the load.

**Protect:**

- One-sentence paragraphs for important rules
- Code blocks immediately following the prose that introduces them
- Tables for any 3+ items of fixed shape
- Section transitions by heading, not by bridge prose

**Avoid:**

- Bridge prose between sections ("Now that we've covered X, let's look at Y")
- Long paragraphs of explanation when a bulleted list would do
- Padding before code blocks ("Here's an example:" — just show the example)
- Padding after code blocks ("As you can see…" — the reader can see)

## What Fails the Standard

- Sentences longer than 25 words for rules/instructions (allowed only in plan-doc reasoning)
- Marketing adjectives anywhere
- Hedge words on rules that aren't actually conditional
- LLM-doc-fluff vocabulary in any document
- Closing summaries that restate what was just shown
- Adjective stacks of 2+
- A section that reads like a pitch
- Generic "power" or "flexibility" claims with no concrete proof
- Documentation that could be about any project (not specifically ken)

## The Safety Root Cause

LLM-doc-fluff comes from one place: **writing for legitimacy instead of usefulness**. The diagnostic question: *Am I including this because the doc needs it, or because I'm trying to make the project sound more impressive?*

When in doubt, cut. ken's docs are short on purpose. The reader's time is more valuable than the writer's pride.

---

*The orchestrator is the work. The keeper is the work. The tz command is the work. The docs serve the work, not the other way around.*
