# Ken — Personal Hub & Multi-LLM Orchestrator

A personal monorepo that hosts three connected systems used across all 9 of Ken's
project repositories:

1. **Timezone & Clock Sync** — A `tz` command, boot/wake/network hooks for
   Devuan/SysVinit, and a 1,200+ cruise-port database for trip scheduling.
2. **Multi-LLM Orchestrator** — The hub for `/consult`, `/orchestrate`,
   `/orchestra`, and `/investigate` skills used by every sister repo.
3. **Keeper** — A session-continuity checkpoint tool for surviving Claude Code
   timeouts and rate limits.

> **Soli Deo Gloria.** This hub serves nine other projects whose work is
> offered as worship. Excellence here is stewardship of every downstream task.

See [`CLAUDE.md`](CLAUDE.md) for project conventions (handoff protocol,
orchestrator setup, memory scope).

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [1. Timezone & Clock Sync (Devuan/SysVinit)](#1-timezone--clock-sync-devuansysvinit)
  - [What it does](#what-it-does)
  - [The `tz` command](#the-tz-command)
  - [Cruise-port database](#cruise-port-database)
  - [Installation](#installation)
  - [Security model](#security-model)
  - [Files & uninstall](#files--uninstall)
- [2. Multi-LLM Orchestrator](#2-multi-llm-orchestrator)
  - [Skills](#skills)
  - [Modes](#modes)
  - [Adapters](#adapters)
  - [Setup & troubleshooting](#setup--troubleshooting)
  - [Layout](#layout)
- [3. Keeper — Session Continuity](#3-keeper--session-continuity)
- [4. Sister Repositories](#4-sister-repositories)
- [Repo Conventions](#repo-conventions)
- [Contributing](#contributing)

---

## Quick Reference

| Command | What it does |
|---|---|
| `tz` | Show current timezone status |
| `tz <city>` | Set timezone by city (fuzzy match) |
| `tz here` | Detect timezone from network (IP geo + WiFi SSID) |
| `tz trip start <date> <city>` | Begin building an itinerary |
| `tz schedule` | Show upcoming itinerary entries |
| `tz list <region>` | Search the city/port database |
| `/consult <model> <role> "<prompt>"` | Quick multi-LLM second opinion |
| `/orchestrate <mode> "<task>"` | Run a linear multi-model pipeline |
| `/orchestra "<task>"` | Fan-out + deliberation debate |
| `/investigate <mode> "<subject>"` | 4-phase deep research → page |
| `python -m keeper checkpoint <family>` | Write a recovery checkpoint |
| `python -m keeper recover <family>` | Produce a recovery brief for next session |

---

## 1. Timezone & Clock Sync (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot, wake, and
network change. Includes a `tz` command with 1,200+ cruise-port lookup, fuzzy
matching, and trip scheduling.

### What it does

#### At boot and wake (`sync-clock.sh`)

1. Checks the timezone schedule (trip itinerary) — no network needed.
2. Falls back to IP geolocation (with caching and confidence check).
3. Falls back to an alternate GeoIP provider.
4. Force-syncs the clock using `ntpd -g -q` (with retry).

#### On network change (`tz-network-check`)

Runs automatically when a network interface comes up. Detects SSID and gateway
changes and triggers timezone detection only when the network fingerprint
changes. Throttled to once per five minutes to avoid hammering GeoIP services.

### The `tz` command

**Check status:**

```
tz
```

```
14:32  America/New_York  (UTC-05:00)

Trip:  tokyo -> los angeles
Source: schedule
Next:  May 28 -> America/Los_Angeles (los angeles)
```

**Set timezone by city name:**

```
tz tampa
tz cabo san lucas
tz barcelona
```

Fuzzy matching suggests corrections:

```
$ tz tamapa
'tamapa' not recognized.
Did you mean:
  tz tampa                     (America/New_York)
```

**Detect timezone from network:**

```
tz here
```

**Plan a trip:**

```
tz trip start 2027-05-12 tokyo
tz shimizu
tz nagoya
tz osaka
tz +kobe                       # same day as osaka
tz sea
tz sea
tz los angeles
```

When a trip is active, `tz <city>` adds to the itinerary instead of changing
the timezone immediately. The schedule auto-compiles on every change. No
`end` command is required (though `tz trip end` is available).

Auto-SEA inference inserts sea days when the timezone changes between ports.
Use `+port` for same-day ports (e.g. Osaka and Kobe on the same calendar day).
Use `tz sea` for explicit sea days.

**Load itinerary from a file:**

```
tz trip load ~/cruises/japan-2027.txt
```

File format (first line = start date, then one port per line):

```
2027-05-12
tokyo
shimizu
nagoya
osaka
+kobe
sea
sea
los angeles
```

**Search for cities:**

```
tz list caribbean
tz list mediterranean
```

**Remove a mistake:**

```
tz undo
```

**Other schedule commands:**

```
tz schedule                    # show schedule
tz schedule add <date> <city>  # add single entry
tz schedule clear              # remove all entries
```

Old schedule entries are pruned automatically.

### Cruise-port database

The `tz-cities` file maps 1,200+ city/port names to IANA timezones. It is
generated and curated from several sources captured in this repo:

| File | Purpose |
|---|---|
| `tz-cities` | The shipped lookup table (installed to `/usr/local/share/`) |
| `build-tz-cities.py` | Builder for the lookup table from raw inputs |
| `build_port_list.py` | Aggregates ports across providers |
| `export_ports.py` | Dumps port data to CSV/JSON |
| `whatsinport_*.txt` / `*.csv` / `*.json` | Source data scraped from WhatsInPort |
| `fetch_country_ports.sh` / `fetch_remaining.sh` / `fetch_final.sh` | Scrapers (rate-limited) |
| `map_remaining.py` | Maps unresolved port entries to timezones |

### Dependencies

- `curl`
- `ntpd`
- `logger` (from `bsdutils`)
- `acpid` (for the wake hook)
- `wireless-tools` (optional, for `iwgetid` in network-change detection)

### Installation

#### Prerequisites

```
sudo apt install curl ntp acpid wireless-tools
```

`acpid` enables wake-from-sleep detection. `wireless-tools` provides
`iwgetid` for WiFi SSID detection on network changes. Both are optional but
recommended.

#### Install

```
git clone <repo-url> && cd ken
sudo ./install.sh
```

This installs:

- `/usr/local/bin/sync-clock.sh` — boot/wake timezone detection and NTP sync
- `/usr/local/bin/tz` — timezone helper command
- `/usr/local/bin/tz-network-check` — network change trigger
- `/usr/local/share/tz-cities` — city-to-timezone mapping (1,200+ ports)
- `/etc/init.d/sync-clock` — SysVinit service (runs at boot)
- `/etc/acpi/tz-wakeup.sh` — ACPI wake hook (if `acpid` is installed)
- `/etc/network/if-up.d/tz-network-check` — network interface hook

State directories (`/var/lib/tz/`, `/var/cache/tz/`) are created with mode
`0700` and owned by root.

#### Verify

```
tz                   # show current timezone status
tz here              # detect timezone from network
tz list caribbean    # search city database
```

### Security model

All scripts run as root (boot, wake, and network hooks). The following
hardening measures are in place:

- **Timezone validation** — All timezone strings are validated against
  `^[A-Za-z0-9_/+-]+$` and rejected if they contain `..` (path traversal).
  This applies to GeoIP API responses, cache reads, and user input.
- **Atomic file writes** — State files (`/var/cache/tz/`, `/var/run/`) are
  written via temp file + `mv` to prevent symlink attacks.
- **Restrictive permissions** — State directories are `0700 root:root`.
  Installed scripts use `install(1)` with explicit ownership.
- **Concurrency control** — `sync-clock.sh`, `tz-network-check`, and
  `tz-wakeup.sh` all use `flock` to prevent races from concurrent triggers.
- **Input sanitization** — WiFi SSIDs are stripped of non-printable
  characters and truncated to 32 bytes. Cooldown/timestamp files are
  validated as numeric before being used in arithmetic.
- **No shell injection** — AWK variables are passed via `-v` (not string
  interpolation). `grep -F` is used for user-supplied search terms.
  `sed` with user-controlled delimiters has been replaced with `grep -Fxv`.
- **`curl --fail`** — HTTP error pages (4xx/5xx) are rejected rather than
  accepted as timezone data.

### Files & uninstall

| File | Location | Purpose |
|---|---|---|
| `sync-clock.sh` | `/usr/local/bin/` | Boot/wake timezone detection + NTP sync |
| `tz` | `/usr/local/bin/` | Timezone helper command |
| `tz-network-check` | `/usr/local/bin/` + `/etc/network/if-up.d/` | Network change trigger |
| `tz-cities` | `/usr/local/share/` | City-to-timezone mapping |
| `sync-clock` | `/etc/init.d/` | SysVinit boot service |
| `tz-wakeup-event` | `/etc/acpi/events/` | ACPI event definition |
| `tz-wakeup.sh` | `/etc/acpi/` | Wake hook script |

#### Adding custom cities

Edit `/usr/local/share/tz-cities` and add entries at the bottom:

```
my hometown|America/Chicago
the office|America/New_York
```

#### Uninstall

```
sudo update-rc.d sync-clock remove
sudo rm /etc/init.d/sync-clock
sudo rm /usr/local/bin/sync-clock.sh /usr/local/bin/tz /usr/local/bin/tz-network-check
sudo rm /usr/local/share/tz-cities
sudo rm -f /etc/tz-schedule
sudo rm -rf /var/lib/tz /var/cache/tz
sudo rm -f /etc/acpi/events/tz-wakeup /etc/acpi/tz-wakeup.sh
sudo rm -f /etc/network/if-up.d/tz-network-check
sudo rm -f /var/run/tz.lock /var/run/tz-network-check.lock /var/run/tz-wakeup.lock
sudo rm -f /var/run/last-clock-sync
```

---

## 2. Multi-LLM Orchestrator

This repo hosts the orchestrator at `orchestrator/`. It is the hub for all
multi-LLM operations across Ken's nine personal repos. External models
(GPT, Gemini, Grok, Perplexity, You.com) serve as **consultants only** —
Claude remains the lead developer and decision-maker.

### Skills

| Skill | Usage | Purpose |
|---|---|---|
| `/consult` | `/consult <model> <role> "<prompt>"` | Quick single-model second opinion |
| `/orchestrate` | `/orchestrate <mode> "<task>"` | Linear multi-model pipeline |
| `/orchestra` | `/orchestra "<task>"` | Fan-out + deliberation debate |
| `/investigate` | `/investigate <mode> "<subject>"` | 4-phase deep research → content page |
| Cognitive Memory | Automatic on session start | Cross-session knowledge persistence |

### Modes

`sermon`, `sheep`, `cruising`, `recipe`, `family-history`, `triad`. This
repo is the hub — **no default mode**. Specify the mode explicitly when
running `/orchestrate` or `/investigate`. Each sister repo defaults to its
own mode (see [Sister Repositories](#4-sister-repositories) below).

### Adapters

GPT (OpenAI), Gemini (`google-genai`), Grok (xAI), Perplexity, You.com.
Each adapter lives under `orchestrator/adapters/` and implements a common
interface so a mode pipeline can target any subset of models.

### Setup & troubleshooting

#### First-time setup (per session)

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

Silent when already installed. If `/consult` or `/orchestrate` fails with
`ModuleNotFoundError`, run this first.

#### Gemini (`google-genai` import error)

The Gemini adapter uses `from google import genai` which requires the
`google-genai` package (NOT `google-generativeai`). If you see
`cannot import name 'genai' from 'google'`:

```bash
pip install google-genai
```

If that fails with `_cffi_backend` / `cryptography` errors (common in
containerized environments where system cryptography is outdated):

```bash
pip install cffi cryptography --force-reinstall --ignore-installed
```

#### Grok (xAI authentication error)

If Grok returns `401 / no-credentials`, the `XAI_API_KEY` is missing from
`.env`. Re-decode from the committed seed:

```bash
rm /home/user/ken/orchestrator/.env
python3 /home/user/ken/orchestrator/env_seed.py --decode
```

If the seed is blank, re-encode after editing `.env`:

```bash
python3 /home/user/ken/orchestrator/env_seed.py --encode
```

#### GPT

Usually works out of the box after `pip install openai`. Key is in `.env`
as `OPENAI_API_KEY`.

### Layout

```
orchestrator/
├── orchestrate.py         ← Linear pipeline runner (/orchestrate)
├── orchestra.py           ← Fan-out + deliberation (/orchestra)
├── investigate.py         ← 4-phase investigation (/investigate)
├── research_orchestra.py  ← Staged research (used by /investigate)
├── consult.py             ← Quick consultation CLI (/consult)
├── verify.py              ← Claim verification
├── iteration.py           ← Iteration control, format validation
├── smart_routing.py       ← Trigger detection, weighted voting
├── memory_ops.py          ← Cognitive memory (TF-IDF semantic search)
├── adapters/              ← gpt, gemini, grok, perplexity, youdotcom
├── modes/                 ← sermon, sheep, cruising, recipe, family-history, triad
├── state/                 ← Runtime state (JSON output)
├── repo-modes.json        ← Repo-to-mode mapping
└── .env                   ← API keys (gitignored, seeded via env_seed.py)
```

#### Pipeline shape (cruising mode example)

```
Read Standards (Claude) → Generate (Claude) → Content (GPT)
  → Completeness (Gemini) → UX (Grok) → Integrate (Claude)
```

The lead model (Claude) is always responsible for reading project
standards, integrating consultant output, and committing changes.
Consultants never receive full codebases or internal-only documents.

---

## 3. Keeper — Session Continuity

`keeper/` is a checkpoint tool for surviving Claude Code session timeouts
and rate limits. It writes session state to disk so the next session can
resume cleanly.

### Commands

```
python -m keeper checkpoint <family> ...   # write a checkpoint
python -m keeper status <family>           # show session state
python -m keeper snapshot <family>         # capture full snapshot
python -m keeper validate <family>         # quality rubric + lint checks
python -m keeper recover <family>          # produce recovery brief
python -m keeper complete <family>         # mark session done
python -m keeper install-hooks             # SessionStart / PreCompact / SessionEnd
```

A "family" groups related sessions (e.g. a feature branch). State lives
under `.keeper/<family>/` in the repo root.

`keeper` is the automated half of session continuity; the human-readable
half is `HANDOFF.md` files (see [Repo Conventions](#repo-conventions)).
Together they let any session — interrupted by timeout, rate limit, or
user pause — be resumed by the next session without re-discovery cost.

See `keeper/` source and the Handoff Protocol section in
[`CLAUDE.md`](CLAUDE.md) for the full continuity model.

---

## 4. Sister Repositories

This hub orchestrates work across nine repositories. Each defaults to a
specific orchestrator mode.

| Repo | Mode | Purpose |
|---|---|---|
| [ken](https://github.com/jsschrstrcks1/ken) | *(hub)* | This repo — orchestrator, tz, keeper |
| [InTheWake](https://github.com/jsschrstrcks1/InTheWake) | `cruising` | cruisinginthewake.com — Christ-shaped cruise planning site |
| [manateecreeksheep](https://github.com/jsschrstrcks1/manateecreeksheep) | `sheep` | Florida sheep flock management & breeding pipeline |
| [Family-History](https://github.com/jsschrstrcks1/Family-History) | `family-history` | Baker / Raulerson / Stokes / Montes de Oca genealogy |
| [MomsRecipes](https://github.com/jsschrstrcks1/MomsRecipes) | `recipe` | MomMom Baker's recipes |
| [Grandmasrecipes](https://github.com/jsschrstrcks1/Grandmasrecipes) | `recipe` | Grandma Baker's recipes (Michigan→Florida) |
| [Grannysrecipes](https://github.com/jsschrstrcks1/Grannysrecipes) | `recipe` | Granny Hudson's recipes (Florida→Boston→back) |
| [Allrecipes](https://github.com/jsschrstrcks1/Allrecipes) | `recipe` | Reference cookbooks & magazine clippings |
| [flickersofmajesty](https://github.com/jsschrstrcks1/flickersofmajesty) | *(none yet)* | Fine-art photography e-commerce (FOM-Lite protocol) |

---

## Repo Conventions

- **Handoff files** (`HANDOFF.md`) are written *before* risky/long work,
  not after. Format and locations are documented in [`CLAUDE.md`](CLAUDE.md).
- **Cognitive memory scope** for this repo is `/ken`.
- **Branches** — Feature work happens on `claude/<topic>-<id>` branches;
  PRs into `main`.
- **Commit style** — Imperative mood. Reference the affected subsystem
  (e.g. `tz: …`, `orchestrator: …`, `keeper: …`).
- **Never push to `main` directly.**

### Documents in this repo

| Document | Purpose |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | AI-assistant context: handoff protocol, orchestrator setup |
| [`keeper-plan.md`](keeper-plan.md) | Keeper architecture and rollout plan |
| [`new-skills-proposal.md`](new-skills-proposal.md) | Proposed additions to the skill set |
| [`skills-audit.md`](skills-audit.md) | Audit of current skill coverage |
| [`plan.md`](plan.md) | Current/active plan for the hub |
| [`llms.txt`](llms.txt) | LLM-facing pointer file |
| [`robots.txt`](robots.txt) / [`sitemap.xml`](sitemap.xml) | Hub web surface |

---

## Contributing

This is a personal monorepo, but contributions from family or close
collaborators are welcome. The workflow:

1. Create a `claude/<topic>-<id>` branch off `main`.
2. Write a `HANDOFF.md` *before* starting risky or long work.
3. Run `keeper checkpoint` at every logical milestone.
4. Open a PR into `main` when the handoff can be marked complete.
5. Never push directly to `main`. Never commit `.env`. Never commit secrets.

Run validation locally before opening a PR:

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh
python3 -m keeper validate <family>
```

---

*Soli Deo Gloria.*
