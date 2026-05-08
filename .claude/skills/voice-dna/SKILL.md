---
name: voice-dna
description: "Discovers voice patterns from ken's documentation corpus. Measures rhythm, vocabulary, and structural fingerprints across READMEs, CLAUDE.md, HANDOFF files, plan docs, and orchestrator prompt templates. Produces a baseline that calibrates like-a-human and voice-audit for technical prose, distinct from sermon and cruise voices."
version: 1.0.0
---

# Voice DNA — Documentation Voice Discovery (ken)

> Don't guess the voice. Measure it.

## Purpose

ken hosts the multi-LLM orchestrator that powers nine sister repos. Its own prose surface is technical: READMEs, `CLAUDE.md`, `HANDOFF.md`, plan docs, `skills-audit.md`, prompt templates inside `orchestrator/modes/`. The voice is not pastoral (Romans) and not experiential (InTheWake) — it is **utility**.

`voice-dna` measures that voice so `like-a-human` and `voice-audit` calibrate against ken's actual documentation, not against a generic "good docs" abstraction.

## When to Fire

- On `/voice-dna` command
- When establishing voice for a new content type (e.g., a new orchestrator mode prompt template)
- When documentation feels off — too marketing, too verbose, too LLM-flavored
- After major orchestrator refactors that touch many docs

## Sample Selection

Select 8–12 documents that represent ken's voice at its best. Mix:

- **2 polished README sections** (the `tz` command section, the orchestrator section)
- **1–2 CLAUDE.md files** (root + any subsystem CLAUDE.md)
- **2 HANDOFF.md files** (real ones, mid-work, with concrete state)
- **1–2 plan docs** (`plan.md`, `keeper-plan.md`)
- **1 skills-audit / new-skills-proposal**
- **1–2 orchestrator mode prompt templates** (`orchestrator/modes/*`)

Avoid: auto-generated outputs, untouched scaffold files, anything copied verbatim from another project.

## Pattern Extraction

For each sample, measure:

### Sentence Rhythm
- Average sentence length (words). Documentation runs shorter than prose.
- Sentence length variance. Higher = human; flat = AI-generated docs.
- Fragment frequency (table cells, bullet items, code-comment style)
- Imperative-mood frequency ("Run X." "Edit Y." "Never push Z.")
- Declarative-state frequency ("This installs X." "State lives at Y.")

### Vocabulary Fingerprint
- Most frequent technical nouns (`orchestrator, handoff, checkpoint, mode, adapter, skill, branch`)
- Verb economy: are verbs doing real work or filler? (`installs, runs, writes, reads` vs. `enables, facilitates, streamlines, leverages`)
- Path / command density: how often does prose drop into `code spans`?
- Tone keywords: "never," "always," "required," "forbidden" — ken uses these directly
- Banned vocabulary that should be **absent**: `seamlessly, robust, leverage, dive into, unlock, transform, holistic, comprehensive, cutting-edge, state-of-the-art, in essence, at its core`

### Structural DNA
- Section depth (how many heading levels deep?)
- Code-block density (lines of code vs. lines of prose)
- Table density (tables of commands, paths, modes)
- Bullet vs. paragraph balance — ken's docs lean heavily on bullets and tables
- "Why" comments — do paragraphs explain *why* a choice was made, or just *what* exists?

### Trust Signals
- Concrete-path density (paths beginning with `/`, `~`, or `.claude/`) per page
- Exact-command density (`bash`, `python3`, `git`) per page
- Failure-mode acknowledgement frequency ("If this fails with X, run Y")
- Caveat density ("Silent when already installed." "Throttled to once per five minutes.")
- Soli Deo Gloria / mission-line usage — ken uses these sparingly, only at the natural close

### Anti-Marketing
- Promotional verbs that should be **near-zero**: `enables, empowers, streamlines, accelerates, optimizes, unleashes, transforms`
- Adjective stacking: docs use minimum adjectives ("the orchestrator" beats "the powerful, robust orchestrator")
- Conclusion bloat: a section ends when the work ends; no "In summary" closers

## Profile Output

Produce a **Voice DNA Profile**:

```
## Voice DNA Profile — ken — [date]
**Corpus:** [N] documents analyzed
**Baseline files:** [list]

### Rhythm
- Avg sentence: [N] words (σ=[N])
- Imperative-mood fraction: [%]
- Declarative-state fraction: [%]
- Fragment frequency: [N] per page

### Vocabulary
- Top technical nouns: [list with frequency]
- Verb economy: [score — plain verbs / filler verbs ratio]
- Path density: [N paths per page]
- Command density: [N commands per page]
- Banned vocabulary appearances: [should be 0]

### Structure
- Avg section depth: [N levels]
- Code-block lines / prose lines: [ratio]
- Tables per page: [N]
- Bullet-to-paragraph ratio: [N]

### Trust Signals
- Concrete paths: [N per page]
- Exact commands: [N per page]
- Failure-mode acknowledgements: [N per page]
- Caveats: [N per page]

### Anti-Marketing
- Promotional verbs: [N — should be 0–1]
- Adjective stacks: [N — should be rare]
- Conclusion bloat: [present/absent]
```

## Different Voice Profiles Within ken

ken has more than one voice; measure each separately:

- **README voice** — outward-facing; explains what the project is and how to use it. Slightly warmer than internal docs. Tables and code blocks dominate.
- **CLAUDE.md voice** — instructional to the assistant. Imperative mood. "Always X." "Never Y." Short.
- **HANDOFF voice** — telegraph style. Bullets. State. Paths. Numbers. No prose padding.
- **Plan / proposal voice** — reasoned argument. Longer paragraphs, but every claim ties to a concrete file or command.
- **Orchestrator prompt voice** — templated, role-specific. Different again — measure separately because these prompts feed *other* models.

Voice DNA can extract any one of these from the right sample subset.

## Feeding Other Skills

- **like-a-human** — update the banlist and the protected-moves list with measured patterns.
- **voice-audit** — calibrate Low/Medium/High thresholds against this corpus.
- **session-checkpoint, finishing-a-development-branch, writing-plans** — all produce HANDOFF or plan prose; voice-dna's measurements set the bar for what those outputs should sound like.
- **orchestrate, investigate, consult, orchestra** — their prompt templates are part of the corpus; measure them so they don't drift toward generic LLM-prompt-speak.

## Encode to Memory

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode ken pattern \
  "Voice DNA: avg sentence 14 words, σ=7. Imperative mood 38%. Path density 4.1/page. Banned vocab: seamlessly, robust, leverage, dive into, unlock, transform, comprehensive." \
  --tags voice-dna,voice-profile,baseline --protected
```

---

*A reader can tell utility prose from marketing prose inside one paragraph. Measure what makes the difference, then defend it.*
