# Soul of `ken`

> *Soli Deo Gloria. This hub serves nine other projects whose work is offered as worship. Excellence here is stewardship of every downstream task.*

The hub. The workshop. The repo that holds the tools every other repo borrows. Named after the person, because it *is* the person — three unrelated systems that only cohere because one human needs all three.

---

## Identity

`ken` is a personal monorepo with three nested systems that share neither dependencies nor domain, but share an owner:

1. **`tz` and clock sync** — a 1,200+ city/port database, boot/wake/network hooks for **Devuan + SysVinit** (not systemd; this is a deliberate choice), and a `tz <city>` command that doubles as a cruise itinerary planner.
2. **The multi-LLM orchestrator** — `/consult`, `/orchestrate`, `/orchestra`, `/investigate`. Claude leads. GPT, Gemini, Grok, Perplexity, You.com consult. Six modes (`sermon`, `sheep`, `cruising`, `recipe`, `family-history`, `triad`) parameterize the pipeline for each sister repo.
3. **Keeper** — checkpoints sessions so timeouts and rate limits don't lose work. Family-scoped. Lease-arbitrated. Heartbeat-as-mtime. The README for keeper-plan.md cites ZFS TXG+ZIL, Git refs+reflog, and Restic write order as mental models.

Three things that don't sound related until you notice they're all about the same thing: **continuity** — of time across travel, of context across LLM boundaries, of memory across session timeouts. The repo's deep theme is that nothing should be lost in the seams.

## Who it serves

Itself last. Nine sister repos first:

- `Romans` (sermons) — mode: `sermon`, lead: Claude
- `manateecreeksheep` (Florida flock) — mode: `sheep`, lead: GPT
- `InTheWake` (cruise blog) — mode: `cruising`, lead: Claude
- `flickersofmajesty` (photography e-commerce) — mode: `cruising`, lead: Claude
- `Allrecipes`, `Grandmasrecipes`, `Grannysrecipes`, `MomsRecipes` — mode: `recipe`, lead: GPT
- `Family-History` — mode: `family-history`, lead: Claude

Every one of them reaches into `ken/orchestrator/` for `/consult` and `/orchestrate`. `ken` is the toolbox carried into every other room. The README's repo-modes table is the canonical map of the entire estate.

## Voice

**Utility prose.** The README of `ken` reads like a sysadmin's notes to a future sysadmin who happens to be the same person. It assumes you know what `flock`, `ntpd -g -q`, `O_CREAT|O_EXCL`, and `install(1)` mean. It explains *why* you'd want path-traversal validation on a GeoIP response (an attacker controls the response body) but not what path traversal is.

**Command-and-path exact.** Every command is shown verbatim, with realistic output. Every file lives at a stated absolute path. `/usr/local/bin/sync-clock.sh`, `/etc/init.d/sync-clock`, `/var/cache/tz/`, `/etc/network/if-up.d/tz-network-check`. No abstractions, no "configure your system to..." — the actual paths are the documentation.

**Doxological framing, never overlay.** *Soli Deo Gloria* appears once in the README's epigraph and once at the very end, as a benediction. In between: 17,000 bytes of installation steps, security model, schema definitions, troubleshooting. The faith is the frame, not the content. Code does not preach.

**Terse where it can be, dense where it must be.** Compare the `tz` command's example output (eight lines, all signal) to the keeper-plan's CONTINUITY spike comparison table (24 rows of architectural tradeoffs). The voice scales with the problem.

## Style markers

- **Tables over paragraphs** for any reference material — commands, files, modes, invariants, lifted concepts. The keeper plan has at least nine tables in 28 KB.
- **Citations in tables.** When a concept is borrowed from `mclaude` or `CONTINUITY`, the borrow is logged with attribution: "Lifted from mclaude" / "CONTINUITY-derived." Credit is non-negotiable.
- **Rejection lists.** What was *not* lifted, and why, gets a table too. `sqlitedict` rejected for CVE-2024-35515. `portalocker` rejected for Debian #1058077. The repo records what it considered and discarded, so future-self doesn't relitigate.
- **Numbered invariants.** Keeper has 12 invariants, each one a one-line rule with a link to the line of code that enforces it.
- **No emoji. No marketing voice. No "delightful" or "powerful" or "elegant" or "blazing-fast."** The closest the README comes to praise is "*This is the repo where carefulness compounds.*"
- **Imperative commit messages, scoped.** `tz: add Cabo San Lucas alias` / `orchestrator: …` / `keeper: …`. Never bare `fix`.
- **Branches are `claude/<topic>-<id>`.** Twelve such branches currently exist. PRs into `main`, never direct pushes.

## Philosophy

### Hub, not cathedral

`ken` is a hub. It does not centralize content; it centralizes *infrastructure*. Recipes live in their own repos. Sermons live in `Romans`. Photographs live in `flickersofmajesty`. What lives in `ken` is the orchestrator that *every* repo calls into, and the timezone tools that the *human* needs across all of them. The hub does not own anything except the wiring.

### Claude leads; consultants advise

This is the load-bearing architectural decision. The orchestrator's pipeline shape (`Read Standards → Generate → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate`) is unambiguous: Claude reads project standards, integrates consultant output, and commits. Consultants never receive full codebases. There is no committee. There is a lead with advisors.

This solves the social problem of multi-model orchestration before it becomes a technical problem.

### Continuity over throughput

Every system in `ken` is about preventing loss in the seams:

- The `tz` system prevents your *clock* from drifting between time zones during travel — at boot, on wake, on network change.
- The orchestrator's cognitive memory prevents *context* from being lost between Claude sessions.
- Keeper prevents *work in progress* from being lost when a session is killed mid-task.

Throughput is never the metric. Survival across discontinuities is.

### Stewardship via downstream consequence

The README states it directly: "*Excellence here is stewardship of every downstream task.*" This is not a slogan. It's why the security model section is the longest part of the README — every script runs as root, and a bug here breaks recipe transcription and sermon prep both. So:

- Timezone strings validated against `^[A-Za-z0-9_/+-]+$` and rejected on `..`
- Atomic file writes via tmp + `mv` with unique suffixes (`f".tmp.{uuid.uuid4().hex[:8]}"`)
- `flock` on every entry point to prevent same-second races
- AWK variables passed via `-v`, never string interpolation
- `grep -F` for user input, never regex
- `curl --fail` to reject HTML error pages as data

The carefulness is not paranoia. It's stewardship of the nine downstream repos that don't see it.

### Trim, don't enhance

The keeper-plan documents nine review rounds (five-model chain + mclaude spike + CONTINUITY spike + memory-tool spike + orchestra triad). The orchestra's verdict was unanimous: **trim, don't enhance**. Stage 1 went from 11 commands to 5. The repo lives by this verdict. Features are removed when they don't earn their keep. Feature creep is treated as a bug.

### Don't reinvent; lift with credit

Twenty-two concepts in keeper are explicitly lifted: ten from `AnastasiyaW/mclaude` (MIT), six from `duke-of-beans/CONTINUITY` (MIT), three from a memory-tool spike of five sources, three from the orchestra. Each one has a one-line attribution in `CREDITS.md`. The repo is allergic to NIH syndrome and explicit about it.

### Don't compete with what already shipped

When Anthropic shipped Auto Memory in Claude Code v2.1.59+, keeper's scope was rewritten the same week to *coexist*. Keeper handles in-flight work; Auto Memory handles persistent project knowledge. Two layers, never overlapping. The repo is willing to redraw its own boundaries when the platform moves.

## Technical anatomy

### Three subsystems, one repo

```
ken/
├── tz / tz-cities / sync-clock.sh / tz-wakeup.sh / tz-network-check
│       └─ SysVinit + ACPI + if-up.d hooks; root-owned; flocked; atomic writes
├── orchestrator/
│   ├── orchestrate.py / orchestra.py / investigate.py / consult.py
│   ├── adapters/{gpt,gemini,grok,perplexity,youdotcom}
│   ├── modes/{sermon,sheep,cruising,recipe,family-history,triad}.yaml
│   ├── memory_ops.py            ← TF-IDF cognitive memory
│   ├── verify.py                ← claim verification
│   ├── iteration.py             ← format validation, iteration control
│   ├── smart_routing.py         ← trigger detection, weighted voting
│   ├── checkpoint.py            ← legacy; migrating into keeper/
│   ├── repo-modes.json          ← canonical repo→mode map
│   └── env_seed.py              ← .env decode/encode for committed seeds
├── keeper/                      ← session-continuity tool (in design)
│   └── (family.json + heartbeat + journal.jsonl per family)
├── build-tz-cities.py / build_port_list.py / fetch_*.sh / map_remaining.py
└── whatsinport_*.csv / .json / .txt   ← 1,200+ port source data
```

### Cruise-port database

Generated from scraping WhatsInPort, mapped to IANA timezones, fuzzy-matched. `tz cabo san lucas`, `tz cabo`, `tz cabo-san-lucas` all resolve. `tz tamapa` (typo) suggests `tz tampa` with fuzzy correction. The database doubles as itinerary fuel: `tz trip start 2027-05-12 tokyo` begins a schedule, and subsequent `tz <port>` commands append entries instead of changing the clock immediately. Auto-SEA inference fills sea days when the timezone changes between consecutive ports. `+kobe` marks a same-day port.

### Orchestrator pipeline (cruising mode example)

```
Read Standards (Claude) → Generate (Claude) → Content (GPT)
  → Completeness (Gemini) → UX (Grok) → Integrate (Claude)
```

The lead model (Claude) is always responsible for reading standards, integrating consultant output, and committing. Consultants get scoped prompts, never full codebases or internal docs.

### Keeper architecture (final design, post-9-rounds)

- **Single source of truth:** one `family.json` per family, atomic-rewritten under heartbeat-gated lease.
- **Heartbeat = mtime.** No JSON timestamp. `Path.touch()` on a 0-byte file is the canonical liveness signal.
- **Journal-before-state ordering.** Append to `journal.jsonl` first, then update `family.json`. Crash leaves either old or new generation, never half. Restic pattern.
- **Composed staleness.** `(wall_clock_silent > 90 min) AND (heartbeat_seq_unchanged across two scans)`. Survives laptop sleep without false-positive eviction.
- **Lease + `instance_token` validation** at the data layer; bypass attempts rejected on read.
- **Generation counter** for clock-skew-safe ordering of takeovers.
- **Auto-escalation:** every N beats (default 15), a full snapshot is written to `completed/snapshots/`, bounding crash-recovery loss.
- **Handoff quality scoring** (0–100) blocks `keeper complete` below threshold unless `--force`.
- **`family.json.backup`** retains the immediately-prior generation so a corrupt primary can fall back.

### Security model (root-running scripts)

| Threat | Mitigation |
|---|---|
| Path traversal via GeoIP response | Timezone regex `^[A-Za-z0-9_/+-]+$`, reject `..` |
| Symlink attack on state files | tmp + `mv` atomic write to `0700 root:root` directories |
| Concurrent triggers (boot + ACPI + if-up.d firing together) | `flock` on every entry point |
| WiFi SSID injection | Strip non-printable, truncate to 32 bytes |
| Shell injection via AWK | Variables via `-v`, never string interpolation |
| Regex injection via search terms | `grep -F` (fixed strings), never `sed s/.../.../ ` with user delimiters |
| HTTP error pages accepted as timezone data | `curl --fail` |
| Numeric injection via timestamp/cooldown files | Validate as integer before arithmetic |

### Handoff protocol (the human-readable half of session continuity)

`HANDOFF.md` files are written **before** risky/long work, not after. Format is fixed: *What Was Done, What Still Needs Doing, Key Decisions, Files Created/Modified, How to Resume*. Locations are scoped: `.claude/skills/<skill>/HANDOFF.md` for skill work, `orchestrator/HANDOFF.md` for orchestrator work, `HANDOFF.md` at repo root for general work. Rule: under 100 lines. Rule: include IDs, paths, exact values — never vague descriptions. Rule: delete when fully complete.

## Distinctive marks

- **Three unrelated systems coexisting because one person needs all three.** A 1,200-port cruise database living next to a Python multi-LLM orchestrator living next to SysVinit boot scripts. The monorepo is the person.
- **Devuan, not Debian.** No systemd. The boot service is SysVinit init.d. ACPI handlers, not logind. This is a values choice that shows up in the code.
- **Doxology as bookend, not load-bearing.** *Soli Deo Gloria* opens and closes the README. In between, 17 KB of `install(1)` flags and `flock` rationale. The faith underwrites the carefulness; it does not narrate the carefulness.
- **Two layers of session continuity.** `keeper` is the automated half (machine-readable `family.json` + heartbeat). `HANDOFF.md` is the human-readable half. Together they let any session resume without re-discovery cost.
- **A photo in the repo: `frenchpolynesia-1.jpeg`.** 480 KB. Sitting in the root of a hub repo for no obvious technical reason. The repo carries small artifacts of the life it documents.
- **The author signs nothing.** No `// added by Ken`, no `Author:` lines, no contributor list. The README's only first-person artifact is the `me.md`-rejection note in keeper-plan ("Personal-data fields … were dropped per orchestra: privacy concerns"). The stewardship is anonymous on purpose.

## What would be lost

If `ken` disappeared, the nine sister repos would still have their content, but they'd lose their shared brain. No more cross-session memory. No more multi-LLM second opinions. No more `tz tampa` after a flight. No more session recovery after a rate limit. Each repo would become an island again, and the carefulness that compounds across them — the path-traversal validation that protects every recipe transcription, the keeper that lets every sermon draft survive a timeout — would have to be reinvented eleven times.

## One-line summary

**`ken` is the workshop where one person tools up to do nine kinds of work, written in the voice of a sysadmin keeping notes for himself, and dedicated to the glory of God without ever sermonizing about it.**
