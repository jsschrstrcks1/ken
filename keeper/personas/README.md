# Personas — `keeper review` (spike, not yet wired)

This directory holds persona prompt files for `keeper review`, a planned command that runs the current family state through multiple Claude personas — each with a distinct POV and rubric — to surface things the original session may have missed. Combines pantheon-nick's daemon protocol with PrometheanLink/pantheon's Verifier role.

**Status:** spike. No code wired yet. These are draft prompts for review.

## Directory layout

```
personas/
├── README.md           # this file (protocol, baseline, per-repo index)
├── skeptic.md          # baseline: unexamined assumptions
├── architect.md        # baseline: design holes, scope creep
├── future-self.md      # baseline: returning-author gaps
├── inthewake/          # repo-specific: cruise planning
│   ├── weather-realist.md
│   ├── mechanical-pessimist.md
│   ├── provisioning-auditor.md
│   ├── anchorage-tactician.md
│   ├── crew-fatigue-monitor.md
│   └── compliance-officer.md
└── (more repo dirs as they're drafted)
```

## The protocol (lifted from pantheon-nick, adapted for keeper)

Each persona is a separate Claude call that follows this exact 4-step chain:

1. **Generate** N candidate critiques as the persona, given the family state. (Default 10; was 20 in pantheon-nick — we trimmed per orchestra advice.)
2. **Rate** each on the persona's three criteria (10-point scale per criterion).
3. **Aggregate** by taking the **minimum** of the three scores. (One weakness sinks the candidate. Stricter than sum-of-points.)
4. **Penalty** −1 for generic / lazy critiques (per persona's penalty list).
5. **Select** the highest-aggregate candidate. Format as a single 1-3 sentence comment.

The output of `keeper review` is the **min-aggregate winner from each persona**, plus an overall pass/fail.

## Baseline personas

Three universal personas that apply across all repos:

| Persona | Looks for | Best at catching |
|---|---|---|
| `skeptic.md` | Unexamined assumptions, missing alternatives | "We never asked whether we needed this at all" |
| `architect.md` | Design holes, scope creep, missing tests | "Two abstractions doing the same thing" |
| `future-self.md` | What someone returning in 3 months would need | "I won't remember why I did this" |

Two more baseline personas are planned (per orchestra advice):
- `content-quality.md` — clarity, coherence, engagement (for content-heavy repos)
- `user-experience.md` — usability, accessibility (for end-user-facing repos)

## Per-repo rosters

A "roster" is the set of personas that runs by default for `keeper review` in a given repo. Defaults to baseline-3 plus repo-specific.

### InTheWake (cruise planning) — 10-persona roster

| Persona | Source | Critical for |
|---|---|---|
| skeptic | baseline | Always |
| architect | baseline | Always (criteria reword: "testability" → "verifiable underway") |
| future-self | baseline | Always |
| content-quality | baseline (planned) | Documentation entries |
| user-experience | baseline (planned) | Trip-share / dashboard surfaces |
| **weather-realist** | inthewake/ | Passage planning |
| **mechanical-pessimist** | inthewake/ | Equipment-dependent legs |
| **provisioning-auditor** | inthewake/ | Multi-day or remote-anchorage legs |
| **anchorage-tactician** | inthewake/ | Anchorage-dependent legs |
| **crew-fatigue-monitor** | inthewake/ | Overnight or multi-day passages |

Plus opt-in for international trips:
- `compliance-officer` — customs / insurance / quarantine paperwork

Default for InTheWake = baseline 3 + 4 most critical repo-specific (weather/mechanical/provisioning/anchorage) = **7 personas**. The other 3 (crew-fatigue, content-quality, UX) and the opt-in compliance-officer are flag-driven (`--persona crew-fatigue` etc.).

## Optional add-on personas (not yet drafted)

- `verifier.md` — production-facing failure modes (what breaks at 3am)
- `librarian.md` — prior-art and consistency-with-codebase
- `devil.md` — adversarial / red-team perspective

Add these by creating new persona files matching the existing shape.

## Why minimum-of-criteria aggregation

A naive sum-of-points lets one strong dimension paper over weakness on others. The min-aggregate forces all-around quality: a critique that's brilliantly falsifiable but irrelevant scores low; one that's relevant but unfalsifiable scores low; only critiques strong on every criterion survive.

Sharp failure mode: if ALL candidates score 1 on at least one criterion, the "winner" is still terrible. Mitigation (in the not-yet-built code): require the winning aggregate to clear a floor (default 4); below that, output "no critique met threshold for this persona" instead of garbage.

## What this isn't

- **Not a replacement for `keeper validate`.** Validate runs structural lint checks (file existence, branch drift, journal sync) — fast, deterministic, free. Review runs cognitive critique — slow, probabilistic, costs Claude calls.
- **Not gated by `complete` by default.** The orchestra's "trim, don't enhance" verdict applies: `complete` stays validate-only. Review is opt-in (`keeper complete --review` to gate on it, or run separately).
- **Not run on every beat.** It's an explicit moment ("am I at a good stopping point?"), not background noise.
