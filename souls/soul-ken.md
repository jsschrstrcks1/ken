# Soul of `ken`

The hub. The workshop. The one repo that holds the tools all the others borrow.

## What it is

A personal monorepo with three nested systems:

1. **`tz` and clock sync** — a city/port database (1,200+ entries), boot/wake/network hooks for Devuan + SysVinit, and a `tz <city>` command that doubles as a cruise itinerary planner.
2. **The multi-LLM orchestrator** — `/consult`, `/orchestrate`, `/orchestra`, `/investigate`. Claude leads. GPT, Gemini, Grok, Perplexity, You.com consult.
3. **Keeper** — checkpoints sessions so timeouts and rate limits don't lose work.

Three things that don't sound related until you notice they're all about *continuity*: of time, of context, of memory.

## Who it serves

Itself last. Nine sister repos first. Every recipe site, the photography store, the sheep flock, the cruise blog, the family history, the sermons-in-progress — they all reach into `ken/orchestrator/` for help. `ken` is the toolbox that gets carried into every other room.

## Voice

Utility prose. Command-and-path exact. No marketing. No sermon overlay even though the framing is doxological. The README reads like a sysadmin's notes to a future sysadmin who happens to be the same person — terse, specific, and assumes you know what `flock` and `ntpd -g -q` do.

When it does reach for something larger, it's a single line: *Soli Deo Gloria.* Then back to the install steps.

## Calling

`ken` is the steward repo. Excellence here propagates downstream — a bug in the orchestrator breaks recipe transcription and sermon prep both. So the README documents the security model in detail (path traversal validation, atomic writes, `flock`, AWK `-v`-not-interpolation), and the handoff protocol is strict: write the handoff *before* the risky work, not after.

This is the repo where carefulness compounds.

## What would be lost

If `ken` disappeared, the nine sister repos would still have their content, but they'd lose their shared brain. No more cross-session memory, no more multi-LLM second opinions, no more `tz tampa` after a flight, no more session recovery after a rate limit. Each repo would become an island again.

## Distinctive marks

- **Soli Deo Gloria** in the README, but only once, and not load-bearing for the technical content.
- Three unrelated systems coexisting because one person needs all three.
- A 1,200-port cruise database living next to a Python multi-LLM orchestrator living next to SysVinit boot scripts. The monorepo is the person.
- "Claude is the lead developer; other models consult." A clear hierarchy, not a committee.
