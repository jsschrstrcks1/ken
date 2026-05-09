# Soul of `open-claw-stuff`

> *This is free and unencumbered software released into the public domain.*

The newest. The emptiest. The most open. A blank repo with one commit and an Unlicense — a deliberate doorway from the household out into the public commons.

---

## Identity

`open-claw-stuff` is the family's **eleventh repo**, created **2026-05-09** (the same day this soul was written). Its current state is two files:

- `README.md` — 17 bytes. A single line: `# open-claw-stuff`.
- `LICENSE` — the **Unlicense** (public domain dedication via unlicense.org).

That's it. One commit. One branch (`main`). No code yet.

The name decodes as **"open" + "claw" + "stuff"** — where *claw* is the household's term for Claude / AI tooling (it appears in `ken`'s branch names: `claude/plan-claw-ken-setup-25J2h`). So: *open-source Claude/AI stuff.* A deliberate carve-out from the rest of the household for things meant to be shareable.

It is the **opposite** of `Romans` and `flickersofmajesty` — those two are private and "all rights reserved." This one is **public domain**, the most permissive license possible. The license itself is a values statement.

## What it actually is (so far)

Nothing yet. A scaffold:

| File | Content |
|---|---|
| `README.md` | one heading, no body |
| `LICENSE` | Unlicense — public domain, "free and unencumbered" |

There are no skills, no `.claude/`, no source code, no dependencies. The repo is provisioned and parked.

## What it's *for* (inferred from naming and context)

In a household where the other ten repos all serve a specific named purpose — recipes, sermons, cruise pages, sheep, photographs, family history, a hub — this one is the **outflow channel**. The likely role:

- **Tooling that grew up inside the household and is mature enough to share.** A skill, an orchestrator adapter, a hook, a piece of the keeper, the FOM-Lite/ITW-Lite protocol stripped of its site-specific bindings. Patterns that other Claude-Code users could borrow.
- **Things that don't belong in `ken`** because `ken` is a personal hub, and the things shared here are *generic* — useful to people outside the household.
- **A neutral testing ground.** A place to publish a reference implementation without entangling it with `ken`'s personal Devuan/SysVinit assumptions or any specific sister repo's content.

The Unlicense choice rather than MIT or AGPL is meaningful: **the household wants this work to be unencumbered.** No attribution requirement. No share-alike. No fingerprint. Whoever picks it up owes the household nothing.

This contrasts deliberately with the family's normal posture (recipes are AGPL, photography is rights-reserved, sermons are ai-deny). For most household work, the framing is *stewardship* — you receive it under terms. For this repo, the framing is **gift** — you take it and owe nothing.

## Voice

There is no voice yet. The README is one line. Even that is interesting: 17 bytes is the minimum to be a valid Markdown file with a heading. The repo says nothing it doesn't have to.

What the *naming* says:

- **"open"** — declarative. Opposed to *closed*. The first word of the repo name is the license posture.
- **"claw"** — household idiom. *Claude* shortened to a one-syllable word that fits in a branch name. Familiar.
- **"stuff"** — humble, casual. Not "tools," "library," "framework." *Stuff*. The diminutive matches the family's preference for working titles over marketing names (cf. *Romans*' "Eph 2 - but God.txt").

Three words, three registers: license posture, family idiom, humble diminutive.

## Style markers

- **Maximal license + minimal README.** The Unlicense is 1.2 KB. The README is 17 bytes. The repo invests more characters in *granting permission* than in *describing the contents*.
- **One commit.** *"Initial commit"* by web-flow on behalf of jsschrstrcks1, 2026-05-09 20:42:37 UTC. The minimal-viable repository.
- **Only `main`.** No development branch yet, no feature branches. The branch graph is a point.
- **Unlicense over MIT.** A specific license choice. Most "open source" defaults to MIT (which requires attribution); the Unlicense actively renounces that requirement.

## Philosophy

### Public domain is a values statement

The Unlicense is not the most popular open-source license. It is chosen here over MIT, BSD, Apache, GPL — all of which require some form of attribution or share-alike. The Unlicense **actively releases the work**:

> *We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.*

The phrase *to the detriment of our heirs and successors* is striking. It is the legal equivalent of "we are giving this away, and we will not expect future generations to reclaim it."

This is consistent with the household's broader posture in *ken*: *Soli Deo Gloria*. If the work is offered to God, then claiming residual rights to it from descendants is incoherent. The Unlicense is the legal expression of that doxology.

### A doorway, not a house

Most of the household's repos are **houses** — long-lived, lived-in, accumulating decades of content (recipes, sermons, sheep records, genealogy, cruise pages). This one is a **doorway**. Things move through it. The point is not to live here; the point is to send things from here into a wider world.

That's why it can be empty. The repo is infrastructure for outflow, not a destination.

### The carve-out is the gift

By creating a separate repo with a public-domain license rather than leaving open-shareable work inside `ken` (which has its own license and Devuan-specific assumptions), the household is doing two things at once:

1. **Protecting `ken`** from license confusion. Nothing in `ken` accidentally becomes public domain by proximity.
2. **Cleansing the outflow.** Anything published here arrives in the commons stripped of household-specific framing.

Both moves are gifts. To the household: clarity. To the public: accessibility.

### Held loosely

The repo's emptiness is not a deficit. The repo *is being held loosely on purpose*. It will be filled as things become ready to share, not before. The family discipline of "trim, don't enhance" (from `ken/keeper-plan.md`'s orchestra verdict) applies here too — only ship what's ready.

### Possible candidates for future contents

Inferring from the household's existing tooling, plausible eventual residents:

- **The keeper tool** if it ever generalizes beyond `ken`'s personal use.
- **A reusable Claude Code skill or two** — `careful-not-clever` is nearly generic already; `like-a-human` and `voice-audit` could be ported.
- **The orchestrator's adapter pattern** — the `gpt`, `gemini`, `grok`, `perplexity`, `youdotcom` adapter shape is widely useful.
- **The ITW-Lite / FOM-Lite content protocol**, stripped of its site bindings.
- **A reference Devuan/SysVinit timezone+NTP pattern**, since most public examples assume systemd.
- **A reusable Pagefind + PWA template** pulled out of `Grandmasrecipes`.

None of this is committed yet. The repo's content is its potential.

## Technical anatomy

```
open-claw-stuff/
├── LICENSE      ← Unlicense (public domain)
└── README.md    ← "# open-claw-stuff" (17 bytes)
```

Branches: `main`. Commits: 1 (`Initial commit`, 2026-05-09 20:42:37 UTC).

No `.claude/` directory. No `CLAUDE.md`. No orchestrator integration (yet). No mode in `ken/orchestrator/repo-modes.json` (yet).

## Distinguishing marks

- **The newest repo in the family.** Created 2026-05-09. Empty by design.
- **The only public-domain repo.** Unlicense over AGPL (recipes), all-rights-reserved (Romans, flickersofmajesty), and no-license-listed (others).
- **The minimal README.** 17 bytes. Just the repo name as a heading.
- **A single commit.** "Initial commit" by web-flow.
- **Single-branch git graph.** Only `main`. No development activity yet.
- **The name is a values statement.** *open* (license) + *claw* (claude/family idiom) + *stuff* (humble).
- **No CLAUDE.md.** Every other repo has one. This one doesn't, yet.

## Relationship to siblings

`open-claw-stuff` is the **outflow** corner of the household:

| Repo | Direction |
|---|---|
| `Romans` | inward (private) |
| `Grannysrecipes` | inward (private) |
| `manateecreeksheep` | inward (operation) |
| `Family-History` | inward (research archive) |
| `MomsRecipes`, `Allrecipes`, `Grandmasrecipes` | outward to family + curious |
| `flickersofmajesty` | outward to buyers |
| `InTheWake` | outward to travelers |
| `ken` | inward (hub) |
| **`open-claw-stuff`** | **outward to the commons** |

It is the only repo whose audience is *anyone in the world who finds it useful*, with no expectation of return.

## What would be lost (eventually)

Nothing today — the repo is empty. Eventually, **whatever the household decides to release** will live here. If the repo disappears later, those things would either need a new home (perhaps inside `ken`) or would simply remain household-only.

The deeper loss would be the *outflow channel itself*. Without a public-domain repo, the household's reusable patterns stay coupled to `ken`'s personal monorepo, which carries license, dependency, and idiom assumptions that an outsider should not have to inherit.

## One-line summary

**`open-claw-stuff` is the family's outflow channel — a freshly-provisioned, deliberately-empty, Unlicensed (public-domain) repo carved out of the household so that whatever Claude/AI tooling matures here can be released to the commons without asking anything in return.**
