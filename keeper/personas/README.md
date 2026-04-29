# Personas — `keeper review` (spike, not yet wired)

This directory holds persona prompt files for `keeper review`, a planned command that runs the current family state through multiple Claude personas — each with a distinct POV and rubric — to surface things the original session may have missed. Combines pantheon-nick's daemon protocol with PrometheanLink/pantheon's Verifier role.

**Status:** spike. No code wired yet. These are draft prompts for review.

## The protocol (lifted from pantheon-nick, adapted for keeper)

Each persona is a separate Claude call that follows this exact 4-step chain:

1. **Generate** 20 candidate critiques as the persona, given the family state.
2. **Rate** each on the persona's three criteria (10-point scale per criterion).
3. **Aggregate** by taking the **minimum** of the three scores. (One weakness sinks the candidate. This is stricter than sum-of-points and forces all-around quality.)
4. **Penalty** −1 for generic / lazy critiques (per persona's penalty list).
5. **Select** the highest-aggregate candidate. Format as a single 1-3 sentence comment.

The output of `keeper review` is the **minimum-aggregate winner from each persona**, plus an overall pass/fail.

## Default trio

The three personas in this directory are the recommended default set:

| Persona | Looks for | Best at catching |
|---|---|---|
| `skeptic.md` | Unexamined assumptions, missing alternatives | "We never asked whether we needed this at all" |
| `architect.md` | Design holes, scope creep, missing tests | "Two abstractions doing the same thing" |
| `future-self.md` | What someone returning in 3 months would need | "I won't remember why I did this" |

## Optional add-on personas (not yet drafted)

- `verifier.md` — production-facing failure modes (what breaks at 3am)
- `user-advocate.md` — end-user / downstream-caller perspective (errors, docs, edge cases)
- `librarian.md` — prior-art and consistency-with-codebase (have we done this before? differently?)
- `devil.md` — adversarial / red-team perspective (what would an attacker do)

Add these by creating new persona files matching the `skeptic.md` shape.

## Why three by default

Every additional persona is another Claude call (cost) and another set of comments to read (cognitive load). Three personas give:
- Three distinct POVs without redundancy
- A natural odd number for tie-breaking ("2 of 3 personas flagged this")
- Bounded latency (~3 parallel calls = roughly the time of one)

More than 5 starts to dilute attention.

## What this isn't

- **Not a replacement for `keeper validate`.** Validate runs structural lint checks (file existence, branch drift, journal sync) — fast, deterministic, free. Review runs cognitive critique — slow, probabilistic, costs Claude calls.
- **Not gated by `complete` by default.** The orchestra's "trim, don't enhance" verdict applies: `complete` stays validate-only. Review is opt-in (`keeper complete --review` to gate on it, or run separately).
- **Not run on every beat.** It's an explicit moment ("am I at a good stopping point?"), not background noise.
