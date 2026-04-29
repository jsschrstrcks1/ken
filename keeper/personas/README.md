# Personas — `keeper review` (spike, not yet wired)

This directory holds persona prompt files for `keeper review`, a planned command that runs the current family state through multiple Claude personas — each with a distinct POV and rubric — to surface things the original session may have missed. Combines pantheon-nick's daemon protocol with PrometheanLink/pantheon's Verifier role.

**Status:** spike. No code wired yet. These are draft prompts for review.

## Directory layout

```
personas/
├── README.md           # this file
├── skeptic.md          # baseline (3 of 5 drafted)
├── architect.md
├── future-self.md
├── (content-quality.md — pending)
├── (user-experience.md — pending)
├── allrecipes/         # 3 personas — recipe aggregator
├── flickersofmajesty/  # 3 personas — devotional photography
├── heritage-cookbooks/ # 3 personas — shared by Grandmas/Grannys/Moms
├── inthewake/          # 6 personas — cruise planning
├── ken/                # 3 personas — hub / orchestrator
├── manateecreeksheep/  # 3 personas — working sheep flock
├── romans/             # 3 personas — sermon content
└── sermon-library/     # 5 personas — sermon production suite
```

**29 persona files drafted** across 9 baseline + per-repo locations covering 10 repositories (3 heritage-cookbook repos share one persona set). 2 baseline personas pending (content-quality, user-experience).

## The protocol (lifted from pantheon-nick, adapted for keeper)

Each persona is a separate Claude call that follows this exact 4-step chain:

1. **Generate** N candidate critiques as the persona, given the family state. (Default 10; was 20 in pantheon-nick — trimmed per orchestra advice.)
2. **Rate** each on the persona's three criteria (10-point scale per criterion).
3. **Aggregate** by taking the **minimum** of the three scores. (One weakness sinks the candidate. Stricter than sum-of-points.)
4. **Penalty** −1 for generic / lazy critiques (per persona's penalty list).
5. **Select** the highest-aggregate candidate. Format as a single 1-3 sentence comment.

The output of `keeper review` is the **min-aggregate winner from each persona**, plus an overall pass/fail.

## Baseline personas (apply to all repos)

| Persona | Looks for | Status |
|---|---|---|
| `skeptic` | Unexamined assumptions, missing alternatives | drafted |
| `architect` | Design holes, scope creep, missing tests | drafted (criteria reword for non-software repos: "testability" → "verifiable in practice") |
| `future-self` | Gaps a returning author hits in 3 months | drafted |
| `content-quality` | Clarity, coherence, engagement | **pending** |
| `user-experience` | Usability, accessibility, audience-comprehension | **pending** |

## Per-repo rosters

Each repo's "roster" is the set of personas that run by default for `keeper review` in that repo. Rosters compose: baseline 3-5 + repo-specific.

### InTheWake (cruise planning) — 11-persona library, 7 default

| Persona | Source | Criticality | Default? |
|---|---|---|---|
| skeptic / architect / future-self / content-quality / UX | baseline | — | ✓ default |
| `weather-realist` | inthewake/ | 1 | ✓ |
| `mechanical-pessimist` | inthewake/ | 2 | ✓ |
| `provisioning-auditor` | inthewake/ | 3 | ✓ |
| `anchorage-tactician` | inthewake/ | 4 | ✓ |
| `crew-fatigue-monitor` | inthewake/ | 5 | flag-driven (`--persona crew-fatigue-monitor`) |
| `compliance-officer` | inthewake/ | 6 | opt-in for international trips |

### Romans (sermon content) — 8-persona library, 5-6 default

| Persona | Source | Criticality |
|---|---|---|
| skeptic / future-self / content-quality / UX | baseline | — |
| architect | baseline | (reword: "testability" → "deliverable as written") |
| `exegetical-guardian` | romans/ | 1 — bad exegesis collapses everything else |
| `pastoral-shepherd` | romans/ | 2 |
| `application-bridge` | romans/ | 3 |

### sermon-library (production suite) — 10-persona library, 7-8 default

| Persona | Source | Criticality |
|---|---|---|
| baseline 5 | — | applies (all software dimensions) |
| `asset-completeness` | sermon-library/ | 1 |
| `series-coherence` | sermon-library/ | 2 (skip for one-offs) |
| `archive-discoverability` | sermon-library/ | 3 |
| `pipeline-scalability` | sermon-library/ | 4 (relevant before high-volume seasons) |
| `integration-guardian` | sermon-library/ | 5 (relevant when external feeds touched) |

### Allrecipes (recipe aggregator) — 8-persona library, 6 default

| Persona | Source | Criticality |
|---|---|---|
| baseline 5 | — | applies |
| `source-integrity` | allrecipes/ | 1 — legal/reputational |
| `dedupe-curator` | allrecipes/ | 2 |
| `search-findability` | allrecipes/ | 3 |

### Heritage cookbooks (Grandmas / Grannys / Moms) — 8-persona library each, 6 default

| Persona | Source | Criticality |
|---|---|---|
| skeptic / future-self / content-quality / UX | baseline | applies |
| architect | baseline | (reword: "testability" → "reproducibility — can someone reproduce on first try?") |
| `voice-keeper` | heritage-cookbooks/ | 1 — the elder's voice IS the heritage |
| `technique-archivist` | heritage-cookbooks/ | 2 |
| `modernization-marker` | heritage-cookbooks/ | 3 |

### flickersofmajesty (devotional photography) — 8-persona library, 6 default

| Persona | Source | Criticality |
|---|---|---|
| baseline 5 | — | applies |
| `visual-sacredness` | flickersofmajesty/ | 1 — the seeing IS the work |
| `spiritual-resonance` | flickersofmajesty/ | 2 |
| `subject-respect` | flickersofmajesty/ | 3 |

### manateecreeksheep (working sheep flock) — 8-persona library, 5 default

⚠️ **Domain-expert review needed** for husbandry-specific thresholds (parasite windows, heat-stress, predator behavior). Persona shapes are sound; specific timing values are placeholders.

| Persona | Source | Criticality |
|---|---|---|
| skeptic / future-self / content-quality | baseline | applies |
| architect / UX | baseline | (architect criteria mostly N/A for animal records; UX = "human caretaker comprehension") |
| `flock-guardian` | manateecreeksheep/ | 1 — welfare gaps |
| `genealogist-auditor` | manateecreeksheep/ | 2 — recordkeeping |
| `environmental-guardian` | manateecreeksheep/ | 3 — Florida seasonal + perimeter |

### ken (hub / orchestrator) — 8-persona library, 7 default

The only fully-software repo in the set. All baseline 5 directly apply.

| Persona | Source | Criticality |
|---|---|---|
| baseline 5 | — | applies (all dimensions) |
| `downstream-impact-guardian` | ken/ | 1 — multi-repo blast radius |
| `cost-containment-auditor` | ken/ | 2 — multi-LLM \$ cascade |
| `cognitive-memory-steward` | ken/ | 3 — shared schema across repos |

## How rosters compose

When `keeper review` runs in a repo:

1. Load baseline personas (skeptic / architect / future-self / + content-quality + UX once drafted).
2. Load repo-specific personas from `personas/<repo>/`.
3. Apply criteria-reword rules per repo (e.g., architect's "testability" rewords for non-software).
4. Filter by default-vs-flag (`--persona <name>` to add flag-driven, `--no-persona <name>` to drop default).
5. Filter by `when_not_to_use` per persona (e.g., `compliance-officer` skips automatically for domestic-only trips if a context flag indicates).

## Why minimum-of-criteria aggregation

A naive sum-of-points lets one strong dimension paper over weakness on others. The min-aggregate forces all-around quality: a critique that's brilliantly falsifiable but irrelevant scores low; one that's relevant but unfalsifiable scores low; only critiques strong on every criterion survive.

Sharp failure mode: if ALL candidates score 1 on at least one criterion, the "winner" is still terrible. Mitigation (in the not-yet-built code): require winning aggregate to clear a floor (default 4); below that, output "no critique met threshold for this persona" instead of garbage.

## What this isn't

- **Not a replacement for `keeper validate`.** Validate runs structural lint checks (file existence, branch drift, journal sync) — fast, deterministic, free. Review runs cognitive critique — slow, probabilistic, costs Claude calls.
- **Not gated by `complete` by default.** Orchestra-trim verdict still applies: complete stays validate-only. Review is opt-in (`keeper complete --review` to gate, or run separately).
- **Not run on every beat.** It's an explicit moment ("am I at a good stopping point?"), not background noise.

## Total persona library

29 drafted, 2 pending = 31 personas at v1. Roster sizes per repo range 5-7 default-active personas. Cost per `keeper review` invocation depends on roster size (≈ \$0.05 / persona / review), so default rosters cost ≈ \$0.25-\$0.40 each.

## Source

All repo-specific personas drafted via 7 sequential `/orchestra triad` runs (one per repo grouping). Total cost: ≈ \$0.70 across all runs. Grok was the most consistent contributor of fully-structured persona drafts; Gemini and GPT contributed where they had domain awareness; all three were self-aware about domain limits (especially manateecreeksheep, where all three flagged "needs domain-expert review").
