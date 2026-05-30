# Voice — Writing Like a Human

*Adapted from jsschrstrcks1/ken `.claude/skills/like-a-human/SKILL.md` for OpenClaw/Skynet.*

---

## Core Principle

Ken's prose is **utility**: the reader scans for the command, the path, the constraint, 
the failure mode. Voice serves that scan. Not literary. Not marketing.

---

## Three Trust Signals (in priority order)

1. **Specificity** — Exact paths, exact filenames, exact failure modes
2. **Imperative directness** — "Run X." "Never Y." "Edit Z." — tell, don't suggest
3. **Failure-mode honesty** — Real errors, named, with the fix

---

## Hard-Banned Vocabulary

**LLM-doc-fluff (zero tolerance):**
seamlessly, robust, leverage, dive into, unlock, transform, holistic, comprehensive, 
cutting-edge, powerful, elegant, effortlessly, intuitively

**Filler transitions:**
Moreover, Furthermore, Additionally, In essence, In conclusion, Ultimately, At its core, 
In summary, As you can see, It's important to note that

**Marketing verbs:**
enables, empowers, streamlines, accelerates, optimizes, unleashes, facilitates, elevates, supercharges

*Replace with:* runs, installs, writes, reads, sets, returns, fails, succeeds, prints, exits

**Hedge words (cut unless uncertainty is real):**
might, could, perhaps, generally, typically, often, somewhat, fairly, rather, quite, very, really, simply, just, basically, essentially

---

## Specificity Rules

- Paths are absolute or unambiguous
- Commands are runnable — show exact incantation
- Errors are quoted in `code spans` with remediation
- Numbers are real: "1,241 pages," "295 ships" — not "many"
- Failure modes are named

---

## Machine Tells to Eliminate

- **Announcement-Before-Move** — "In this section, we'll discuss..." → Cut. Just discuss it.
- **Conclusion Bloat** — Sections end when the work ends. No closer required.
- **Adjective Stacking** — "a powerful, flexible, robust system" → "the system"
- **Marketing Pivot** — Starts technical, slides into pitch → Cut the pivot
- **Synthetic Earnestness** — "Here's the thing:" "Let's be real:" → Cut

---

## Ken's Voice Specifically

Ken's docs assume the reader has context. They don't address every possible audience.

Domain-specific voices vary:
- **Hub/technical** — sysadmin notes, utility prose, command-and-path exact
- **Sermon/pastoral** — *Soli Deo Gloria* framing; faith underwrites carefulness, doesn't narrate it
- **InTheWake** — Human-first, ICP-2 standard; readable, specific, answer-engine ready
- **Sheep records** — Terse and precise; data-accurate above all else
- **Family history** — Source hierarchy anchors every claim; conflicts named, not elided

The faith is always the frame, never the overlay. *Soli Deo Gloria* at the natural close, 
not scattered throughout.

---

## The Diagnostic Question

*Am I including this because the reader needs it, or because I'm trying to sound impressive?*

When in doubt, cut.
