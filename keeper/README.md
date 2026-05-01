# keeper

> Session-continuity for Claude Code threads. Crashes lose seconds, not hours.

`keeper` is a stdlib-only Python module that lets a new Claude Code session pick up exactly where the previous one left off — even when the previous one died abruptly (rate limit, OOM, terminal closed, laptop slept). It's family-scoped, so you can have multiple work-streams in the same repo without them stepping on each other (`ports` and `ships` running in parallel).

It does **not** replace [Claude Code's Auto Memory](https://code.claude.com/docs/en/memory) — that's the right place for "what Claude has learned about this codebase over time." `keeper` is for the active state of one work-stream in flight: the lease, the last action, the decision-just-made, the files-still-open.

---

## The 30-second mental model

| Layer | Owns | Lifecycle |
|---|---|---|
| `CLAUDE.md` | What you tell Claude to always do | persistent, you write it |
| Anthropic Auto Memory | What Claude has learned about this codebase | persistent, Claude writes it |
| **`keeper`** | **Active state of one work-stream right now** | **bounded by session/thread** |

The unit of `keeper` is a **family** — a named work-stream like `ports`, `ships`, or `cruising`. Inside one family, every Claude Code session writes the same `family.json`; threads collide there safely (lease-protected, atomic writes, journal-audited).

---

## Quick start (60 seconds)

```bash
# Ken is always loaded; alias keeper for convenience.
cd /home/user/ken
alias keeper="python3 -m keeper"

# Start a session in family 'ports'.
keeper join --family ports --goal "wire up new health-check endpoint"

# Record progress mid-session.
keeper beat --action "added /health route" --files src/api.py
keeper beat --decision "use 200 OK" "matches existing /ready"
keeper beat --next-step "add tests for the new route"

# Peek at state at any time.
keeper status

# Hit a wall, terminal dies. Open a new shell:
keeper recover --family ports          # human-readable brief
keeper recover --family ports --json --brief   # what to feed Claude

# When you're really done:
keeper complete --summary "endpoint shipping; CI green"

# Optional: before complete, ask Claude to review what you've done
keeper review --family ports --live --yes
```

That's it. `keeper recover` is the hook that re-bootstraps a new Claude session against the prior one's state with zero manual handoff. `keeper review` is an optional *cognitive* check — multiple Claude personas surface things you may have missed before you finalize.

---

## What's actually happening when you run each command

This section walks through the lifecycle step-by-step, showing what files are written and what state changes.

### `keeper join --family ports --goal "..."`

1. **Validate** the family name (`[a-z0-9][a-z0-9-]{0,31}`). If you typo `port` instead of `ports`, you get a fresh empty family — keeper-conf can prevent this; see below.
2. **Check for existing family** at `<repo>/.claude/state/families/ports/family.json`.
3. **If none exists** → fresh create:
    - Mint a `session_id` (`sess-20260428T015432Z-ac3592`) and `instance_token` (random uuid).
    - Append a `join` entry to `journal.jsonl` first (journal-before-state ordering).
    - Atomically write `family.json` (full state object, generation=1, ended_cleanly=false, branch/worktree/git_hash auto-detected).
    - Touch `heartbeat` (creates a 0-byte file; mtime IS the heartbeat).
4. **If it exists and is fresh** (heartbeat < 90 min) → reject with exit 10 unless `--force`.
5. **If it exists and is stale** → prompt `Take over? [y/N]` inline (no separate "recover" step). On `y`:
    - Bump `generation` (e.g. 1 → 2).
    - Mint new `session_id` + `instance_token`.
    - Journal a `forced_takeover` event with the previous holder's id and reason.
    - If the previous session had `ended_cleanly=false`, append a warning to the new state.
    - Write the new `family.json`.

### `keeper beat --action "..." [...]`

The **read-modify-write** core. Every progress-recording call routes through this.

1. **Read** `family.json` (with fallback to `family.json.backup` if primary is corrupt).
2. **Consume** any `precompact.pending` marker if present — write a `snapshot` event to journal.
3. **Append** a `beat` event to journal.jsonl with linked-log integrity (`prev_event_id` references the last entry).
4. **Merge** updates into state using accumulator semantics:
   - **Scalars** (`phase`, `goal`, `next_step`): latest-wins.
   - **Arrays** (`working`, `broken`, `blocked`, `warnings`, `refs`): append-with-dedup.
   - **`files_in_play`**: replace with the new list.
   - **Decisions**: append (each is its own dict).
5. **Increment** `beat_count`.
6. **Atomic-write** the new `family.json` (with `.backup` rename of prior generation first — your safety net for torn writes).
7. **Touch** `heartbeat` (mtime updates to "now").
8. **If `beat_count % 15 == 0`** → write a full snapshot to `completed/snapshots/<ts>_auto-escalation_<uniq>.json` and prune the ring to 50 most-recent. Best-effort — failure here never breaks the beat.

### `keeper complete --summary "..."`

The **strict-by-default graceful end**.

1. Read state.
2. **Run `validate`** internally (quality score + 7 lint checks). If score < threshold (default 60) OR any lint fails → refuse with a stderr message telling you to either fix it or `--force`.
3. **Optional: run `review --live`** if `--review` is set. Refuses to complete if any persona returns a critique with `aggregate_score >= --review-threshold` (default 7).
4. Append a `complete` event to journal (records `review: true/false`).
5. Set `ended_cleanly=true` and `completed_at` in state.
6. Atomic-write state.
7. Render a markdown summary to `completed/<family>_<YYYY-MM-DD_HH-MM-SS>_complete.md` with done/working/broken/blocked/decisions sections.

Skip the gate(s) with `keeper complete --force` (audit trail is preserved; you just bypass the quality and review checks).

### `keeper recover [--family ports] [--json] [--brief]`

The **resume oracle**. Prints what a new session needs to keep going.

- **Default (text)**: content first (goal, working, decisions, files, NEXT STEP), metadata footer below `---` (session id, generation, beats, heartbeat age, branch).
- **`--json`**: full state object including `_recovery_meta` (heartbeat age, stale flag, journal tail of last 10 events).
- **`--json --brief`**: just the resume essentials (10 keys: family, goal, phase, working, broken, blocked, decisions, next_step, files_in_play, ended_cleanly). No operator metadata, no journal noise. **This is what you feed Claude when bootstrapping a new session.**

### `keeper status`

At-a-glance peek. Same shape as recover but lighter — no journal scan, no `_recovery_meta`. Useful as a frequent check during work.

### `keeper validate [--strict] [--threshold N] [--json]`

Reports a quality score (0-100) against a 7-criterion rubric and runs 7 structural lint checks. With `--strict`, exits non-zero if score < threshold OR any lint fails. `complete` calls this internally.

### `keeper snapshot [--label "..."]`

Manually write a full state snapshot to `completed/snapshots/`. Auto-fires every 15 beats anyway; this is for "I'm about to do something risky, preserve current state" moments.

### `keeper install-hooks [--auto] [--scope project|user|local]`

Installs three Claude Code hooks (`SessionStart`, `PreCompact`, `SessionEnd`) that automate keeper lifecycle when `KEEPER_FAMILY` is set in your env. Default is print-only (review the JSON before writing); `--auto` actually writes. See **The hooks story** below.

### `keeper review [--family ports] [--live] [--persona ...] [--no-persona ...] [--show-prompts] [--json]`

The **cognitive review layer**. Loads the family state and runs it past multiple Claude *personas*, each with a distinct point of view (Skeptic / Architect / Future-Self / + repo-specific ones). Each persona produces a single 1–3 sentence critique anchored to the actual state.

This is what `keeper validate` is *not*: validate runs deterministic structural lint checks (file existence, branch drift, journal sync) for free. Review runs cognitive critique — slow, probabilistic, costs Claude calls — and surfaces things only a thoughtful reader would catch.

Two modes:

- **Dry-run** (default): builds the per-persona prompts and shows the roster + estimated cost, but makes **zero Claude calls**. Use this to inspect what would be sent before spending anything.
- **Live** (`--live`): actually invokes one parallel Claude call per persona. Prompts for confirmation showing the cost estimate, unless you pass `--yes`.

Behavior:
1. Detect the repo from `repo_root().name` (or use `--repo NAME` to override). The repo name selects the per-repo persona roster.
2. Load the **roster**: every baseline persona + every persona scoped to this repo (single-repo `repo:` field or shared `repos: [...]` list in frontmatter).
3. Apply `--persona`/`--no-persona` filters. `--persona` adds, `--no-persona` removes.
4. For each persona: assemble the prompt (persona body + protocol + family state JSON + last 10 journal events).
5. Live: fire all calls in parallel (default `--max-parallel 5`); collect comments + per-persona scores + actual costs. Failures are recorded per-persona; one bad call doesn't sink the rest.
6. Render: text by default (one block per persona), `--json` for Claude-priming or scripting, `--show-prompts` to print the full prompts (long).

Full walkthrough with concrete examples is in **"Personas and `keeper review`"** below.

### `keeper new-id`

Mint a fresh session id. Used internally; surfaced for scripting.

### `keeper help`

Prints the full usage text with examples.

---

## Concept reference

### Family
A named work-stream like `ports` or `ships`. Validated kebab-case, max 32 chars. One family = one `family.json` = one lease at a time. Threads within a family share continuity; families are isolated from each other.

### Lease
The "I own writes to this family" claim. In keeper, the lease is **embedded in `family.json`** as `{session_id, instance_token, generation, started_at, ended_cleanly}`. Held by whoever wrote the most recent state. Takeover bumps `generation` and mints a new `instance_token` so journal entries can be traced back to a specific lease holder.

### Heartbeat
A 0-byte file (`<family>/heartbeat`). Its **mtime is the heartbeat** — no JSON timestamp involved. `Path.touch()` on every `beat`. Stale = mtime > 90 min. This sidesteps clock-skew / format-parsing issues entirely.

### Journal
Append-only `<family>/journal.jsonl`. Linked log: each entry references `prev_event_id`. Entry types: `join` / `beat` / `complete` / `forced_takeover` / `snapshot`. Designed to fit in <PIPE_BUF (4 KB) so each line is an atomic append. **Optional audit trail** — recovery primarily reads `family.json`, not the journal.

### Snapshot
A complete copy of `family.json` saved to `<family>/completed/snapshots/<ts>_<label>_<uniq>.json`. Auto-fires every 15 beats; manually triggered with `keeper snapshot`. Bounded to 50 most-recent (configurable). Lets recovery from any crash window be small.

### Generation
Monotonic counter on the lease. Starts at 1. Every takeover bumps it. Used to distinguish "I'm the original holder" from "someone took over" in the journal.

### `instance_token`
Random uuid minted on every `join` (and again on every takeover). Embedded in every journal entry. The integrity check verifies that all journal entries since the last `forced_takeover` carry the same token — guards against zombie writers that bypass the CLI.

### `ended_cleanly`
A bool in state. Set to `true` only by `keeper complete`. If a takeover finds the previous state had `ended_cleanly=false`, the new session gets a warning in its state. Cheap crash detection that doesn't require parsing the journal.

### Quality score
0-100 against a 7-criterion rubric (goal=20, next_step=20, decisions=15, status_arrays=15, files_in_play=10, phase=10, branch=10). Default complete-threshold is 60. Each missing criterion comes with a hint about how to set it.

### Lint checks
Seven structural checks `validate` runs alongside the score: branch drift, files_in_play exist, journal/state synced, heartbeat fresh, worktree match, instance_token consistent, completed/ archive integrity. All must pass for `validate --strict` to exit zero.

### Persona
A markdown file under `keeper/personas/` (baseline) or `keeper/personas/<repo>/` (repo-specific). Each persona declares a distinct point of view (Skeptic, Architect, Future-Self, Weather-Realist, ...) plus its **3 evaluation criteria**, **penalty phrases** that signal generic non-help, and a calibration example. At review time, each persona is one Claude call; the model is instructed to generate 10 candidate critiques, rate each on the 3 criteria (10-point scale), apply the penalty list, take the **minimum** across criteria as aggregate, and return the highest-scoring critique as a 1–3 sentence comment.

### Roster
The set of personas that run for a given repo's review. Composed at runtime: every baseline persona + every persona scoped to the current repo (`repo:` field) or sharing a multi-repo scope (`repos:` list — used by the heritage cookbooks, which share three personas across Grandmasrecipes/Grannysrecipes/MomsRecipes). `--persona NAME` adds; `--no-persona NAME` drops.

### Min-of-criteria aggregation
Each candidate critique gets three independent scores. The aggregate is `min(score_1, score_2, score_3)` — one weakness sinks the candidate. Stricter than sum-of-points; forces all-around quality. Borrowed from `nickkeesG/Pantheon`'s daemon protocol; see **Design notes**.

---

## File layout reference

Per family in your repo:

```
<repo>/.claude/state/families/<family>/
├── family.json          # consolidated lease + state. Read this for resume.
├── family.json.backup   # prior generation, fallback if primary is corrupt.
├── heartbeat            # 0-byte file; mtime is the heartbeat.
├── journal.jsonl        # linked-log audit trail. Appended on every join/beat/etc.
├── precompact.pending   # transient marker (PreCompact hook → next beat consumes).
└── completed/
    ├── <family>_<ts>_complete.md          # one per `keeper complete` call.
    └── snapshots/
        └── <ts>_<label>_<uniq>.json       # auto every 15 beats; bounded to 50.
```

Repo-level config (optional):

```
<repo>/.claude/keeper.conf       # ini-style: default_family = ports
```

User-level config: none. By design — keeper has no global state, no `~/.config/keeper/`. The choice was deliberate (privacy, simplicity, repo-scoped truth).

---

## The hooks story

Three Claude Code hooks integrate keeper into the session lifecycle automatically. All three are guarded by `[ -n "$KEEPER_FAMILY" ]` so installing them is a no-op when keeper isn't being used.

| Hook | Behavior | Why |
|---|---|---|
| `SessionStart` | If `$KEEPER_FAMILY` is set, runs `keeper join --non-interactive`. | New shell → automatic resume. |
| `PreCompact` | Writes a `precompact.pending` marker. Does NOT call `keeper beat`. | The next `beat` consumes the marker. Avoids capturing mid-thought state when context compaction fires unexpectedly. |
| `SessionEnd` | Runs `keeper beat --auto --reason "session-end"` with one retry after 1s. | Best-effort final beat before shutdown. Does NOT call `complete` — that requires user intent. |

To install:

```bash
# Print-only first (review the JSON before writing).
keeper install-hooks

# When you're ready:
keeper install-hooks --auto

# Or user-scoped, applies to all your projects:
keeper install-hooks --auto --scope user
```

`install-hooks` is **idempotent**: re-running detects already-installed commands by exact string match and skips them. Existing settings.json is backed up to `settings.json.keeper-backup` before any write.

Now in any subsequent Claude session:

```bash
export KEEPER_FAMILY=ports
# SessionStart hook auto-runs `keeper join --family ports`.
# SessionEnd hook auto-beats on shutdown.
# PreCompact hook saves a marker before context compaction.
```


---

## Recovery scenarios

This is what `keeper` is actually for. Each scenario is a real failure mode with the recovery path.

### Scenario 1: Terminal closed mid-session (the common case)

You ran `keeper join`, did some `keeper beat` calls, then hit Cmd-Q or closed the laptop. **You never called `keeper complete`.**

```bash
# In a new shell:
keeper recover --family ports
```

Output:
```
=== keeper — family 'ports' ===

Goal:    wire up new health-check endpoint
Phase:   implementation

Working:
  • added /health route

Decisions:
  • use 200 OK — matches existing /ready

Files in play:
  • src/api.py

>>> NEXT STEP: add tests for the new route

---
session=sess-20260428T015432Z-ac3592 gen=1 beats=3
heartbeat=12.4min ago  ended_cleanly=False
branch=feature/health
```

To resume **as Claude**: feed `recover --family ports --json --brief` into the new conversation.

### Scenario 2: Rate limit, you'll resume later

Same shape as #1. Heartbeat is stale (>90 min) when you come back. `keeper join --family ports` prompts:

```
[keeper] family 'ports' is STALE (heartbeat 184min ago, holder=sess-...).
  Take over? [y/N] y
```

Generation bumps to 2, fresh `instance_token`, journal records `forced_takeover` with `reason: "stale-confirmed"`. The previous session's state is preserved in the takeover event for forensics, but the new session starts with empty arrays for working/broken/blocked.

**Want to keep the prior content and just claim the lease?** Read state with `--json` first, then re-supply via `keeper beat --action ...` after the takeover.

### Scenario 3: family.json is corrupt (rare — torn write on edge filesystems)

`family.json` exists but won't parse. **`keeper recover` automatically falls back to `family.json.backup`** with a stderr warning:

```
[keeper] WARNING: family.json unreadable; recovered from family.json.backup
```

`.backup` is the prior generation's state — written before each atomic update via rename. You lose the very last beat, not your whole context.

If both files are unreadable: read `journal.jsonl` directly. The linked log lets you reconstruct manually if needed.

### Scenario 4: Two sessions in the same family at once (race)

Stage 1 has soft-race semantics. `O_CREAT|O_EXCL` is NOT used on `family.json` (it's atomic-rename-overwritable). Practical outcome: in the rare window where two `keeper join` calls fire simultaneously on a fresh family, both succeed; last-writer-wins. In all other cases, the second `join` sees the first's state and exits 10 (held).

This is by design — Stage 1 assumes one human, one terminal. Multi-host coordination would require a CF Durable Object lease arbiter (deferred indefinitely; see `keeper-plan.md` § Stage 2).

### Scenario 5: PreCompact fired while Claude was thinking

The PreCompact hook writes a `precompact.pending` marker file in the family directory but does NOT call `keeper beat` directly. The next time **you** run `keeper beat`, the marker is consumed and a `snapshot` event is journaled. This means context compaction never captures mid-thought state — you decide when the next snapshot happens.

### Scenario 6: You forgot which family you were in

```bash
ls .claude/state/families/                 # all families in this repo
keeper status --family ports               # peek at one
keeper status --family ships
```

Or set the default for this repo so you don't have to remember:

```bash
echo 'default_family = ports' > .claude/keeper.conf
keeper status                              # uses ports automatically
```

---

## The quality gate

`keeper complete` won't let you finalize a session in a state Claude can't usefully resume from. Quality is scored against this rubric:

| Criterion | Points | Pass condition |
|---|---|---|
| `goal` | 20 | Set via `--goal` on join (or `beat --working-on`) |
| `next_step` | 20 | Set via `beat --next-step` |
| `decisions` | 15 | At least one logged via `beat --decision` |
| `status_arrays` | 15 | At least one of working/broken/blocked has content |
| `files_in_play` | 10 | Set via `beat --files` |
| `phase` | 10 | Set via `beat --phase` |
| `branch` | 10 | Auto-detected if you're in a git checkout |

Default complete-threshold is **60**. So a session with `goal + next_step + status_arrays = 55` will be rejected; add a decision (+15) or files (+10) to ship.

Each missing criterion comes with a **hint** in the validate output:

```
$ keeper validate --family ports

Quality: 35/100  (threshold 60)
  ✓ goal           (20)
  ✗ next_step      (20)  — set with `keeper beat --next-step "..."`
  ✗ decisions      (15)  — log one with `keeper beat --decision "what" "why"`
  ✓ status_arrays  (15)
  ...
```

**Bypass paths** (use when you really mean it; they're audited):

```bash
keeper complete --force                    # one-off bypass
keeper complete --threshold 30             # lower the bar this once
```

### Optional: gate `complete` on `keeper review` too

Add `--review` to also run the cognitive review (see next major section) before finalizing. Refuses to complete if any persona returns a critique with `aggregate_score >= --review-threshold` (default 7 — strong-confidence critiques only).

```bash
# Strict: validate + review must pass
keeper complete --review --summary "..."

# Tune the score that blocks (lower = stricter):
keeper complete --review --review-threshold 5

# Only consult specific personas during the gate:
keeper complete --review --review-persona skeptic --review-persona architect

# Skip noisy personas during the gate:
keeper complete --review --review-no-persona content-quality \
                          --review-no-persona user-experience

# Force still bypasses both gates:
keeper complete --force
```

When a persona blocks, the critique is shown inline so you know what to fix:

```
[keeper] refusing to complete: 1 persona(s) raised a strong critique (score >= 7).

  skeptic [9/10]
      I notice the `decisions` array commits to using '200 OK' for the
      new health endpoint because it matches the existing '/ready', but
      this decision doesn't account for the assumption that all clients
      interpret this status code as intended ...

  Address the critiques and beat the changes in, then re-run.
  Bypass with `keeper complete --force`.
```

Cost: same as a regular `keeper review --live` (~$0.10 default roster). If review can't run (no adapter SDKs / orchestrator missing), `complete --review` refuses rather than silently skipping the gate.

---

## Personas and `keeper review`

The cognitive companion to `keeper validate`. Where validate asks *"is this state structurally complete?"*, review asks *"is this state actually good — is anything important missing, ambiguous, or unexamined?"*

### Why this is separate from validate

Validate is **structural** and **deterministic**. It checks file paths exist, branches haven't drifted, the journal links cleanly. It runs in milliseconds for free, every time. It will never tell you that your `goal` is sloppy or your `decisions` lack rationale.

Review is **cognitive** and **probabilistic**. It runs a handful of LLM calls, each with a distinct point of view, and produces 1–3 sentence critiques anchored to the specific contents of your `family.json`. It costs roughly $0.10–$0.15 per invocation at default rosters. It catches the things only a thoughtful reader would catch.

The two are complementary:

| | `keeper validate` | `keeper review` |
|---|---|---|
| Type | Structural lint | Cognitive critique |
| Cost | Free | ~$0.012 / persona × roster size |
| Latency | <50 ms | 5–30 s (parallel calls) |
| Determinism | Yes | No (LLM) |
| Always-on | `complete` runs it strict-by-default | Opt-in only |
| Question | "Is the state internally consistent?" | "Is the state actually any good?" |

### How a single persona produces one comment

Each persona is one Claude call. The model is told to follow this protocol:

1. **Generate** 10 candidate critiques in the persona's voice, anchored to the family state and the last 10 journal events.
2. **Rate** each on the persona's three criteria, 10-point scale per criterion. Each persona has different criteria — Skeptic scores `assumption_examined` / `falsifiable` / `alternative_considered`; Architect scores `scope_clarity` / `abstraction_pulls_weight` / `testability`; etc.
3. **Apply −1 penalty** to candidates whose text contains the persona's blacklist of generic phrases ("consider best practices", "may want to think about", etc.).
4. **Aggregate** by `min(score_1, score_2, score_3)`. One weakness sinks a candidate.
5. **Select** the highest-aggregate candidate. If `aggregate < 4`, return `"no critique cleared threshold for <persona>"` instead of garbage.
6. **Return** as JSON: `{comment, aggregate_score, confidence}`.

This pattern is lifted from [`nickkeesG/Pantheon`](https://github.com/nickkeesG/Pantheon)'s daemon protocol. The min-aggregate (vs sum-of-points) is load-bearing — it forces critiques that are strong on every dimension, not just one.

### The persona library

31 personas drafted across 10 repositories. Every repo gets the 5 baseline personas; most also get repo-specific personas:

| Persona file | Scope | Looks for |
|---|---|---|
| `personas/skeptic.md` | baseline | Unexamined assumptions, missing alternatives |
| `personas/architect.md` | baseline | Design holes, scope creep, missing tests |
| `personas/future-self.md` | baseline | Gaps a returning author hits in 3 months |
| `personas/content-quality.md` | baseline | Prose clarity, coherence, engagement |
| `personas/user-experience.md` | baseline | Usability, accessibility, audience match |
| `personas/inthewake/*.md` | InTheWake (cruise planning) | weather realism, mechanical SPOFs, provisioning math, anchorage tactics, crew fatigue, customs (6 personas) |
| `personas/romans/*.md` | Romans (sermon content) | exegesis, pastoral attention, application bridge (3) |
| `personas/sermon-library/*.md` | sermon-library (production) | asset completeness, series coherence, archive findability, pipeline scalability, integration drift (5) |
| `personas/allrecipes/*.md` | Allrecipes | source attribution, dedupe curation, search findability (3) |
| `personas/heritage-cookbooks/*.md` | Grandmas/Grannys/Moms (shared) | voice fidelity, technique preservation, modernization marking (3) |
| `personas/flickersofmajesty/*.md` | flickersofmajesty | visual sacredness, spiritual resonance, subject respect (3) |
| `personas/manateecreeksheep/*.md` | manateecreeksheep | flock welfare, recordkeeping audit, environmental guardian (3, ⚠ thresholds need domain-expert review) |
| `personas/ken/*.md` | ken (this hub) | downstream impact, cost containment, cognitive-memory schema (3) |

Default roster sizes (baseline 5 + repo-specific) range from 8 (Allrecipes, flickersofmajesty, ken, manateecreeksheep, heritage cookbooks) to 11 (InTheWake — has 6 cruise-specific personas).

### Two modes: dry-run vs live

**Dry-run** is the default. It builds prompts but makes no API calls. Use this constantly — it's free, and it lets you check the roster and prompt shape before spending anything.

```bash
$ keeper review --family ports
=== keeper review — family 'ports' (repo: ken) ===

Roster: 8 personas
Estimated cost: ~$0.10

Personas:
  • architect                    (baseline)  6286ch
  • content-quality              (baseline)  3896ch
  • cognitive-memory-steward     (ken)  rank=3  3622ch
  • cost-containment-auditor     (ken)  rank=2  3654ch
  • downstream-impact-guardian   (ken)  rank=1  3711ch
  • future-self                  (baseline)  7111ch
  • skeptic                      (baseline)  6415ch
  • user-experience              (baseline)  4120ch

--- DRY RUN — no Claude calls made ---
```

**Live** (`--live`) actually fires the calls. By default it prompts for confirmation showing the cost estimate; pass `--yes`/`-y` to skip.

```bash
$ keeper review --family ports --live
[keeper] live review: 8 personas via 'gpt' (estimated ~$0.10)
[keeper] proceed? [y/N] y
[adapters] Loaded: gemini, gpt, grok, perplexity, youdotcom
=== keeper review — family 'ports' (repo: ken) ===

Roster: 8 personas
Actual cost: $0.0413

Comments:
  • skeptic [7/10]
      I notice the `decisions` array commits to using '200 OK' for the new
      health endpoint because it matches the existing '/ready', but this
      decision doesn't account for the assumption that all clients
      interpret this status code as intended. Without clarity on what
      happens during degraded service states, this could lead to
      confusion. A simple test of the endpoint's behavior under simulated
      failure conditions would reveal if this assumption holds.
  • architect [6/10]
      ...
  ...

--- LIVE — 8 personas invoked ---
```

### A worked example: review during a real session

Realistic flow, top to bottom:

```bash
# Begin a session.
keeper join --family ports --goal "wire up new health-check endpoint"

# Work for an hour, recording progress.
keeper beat --action "added /health route" --files src/api.py
keeper beat --decision "use 200 OK" "matches existing /ready"
keeper beat --action "wrote unit test for /health"
keeper beat --next-step "wire backoff into /api/calls"

# Quick structural check (free).
keeper validate
# → Quality: 80/100. all lints pass.

# Cognitive review BEFORE you complete (~$0.10, ~15 s).
keeper review --live
# → Skeptic catches that 200 OK was chosen for parity but you didn't
#   document what happens when the upstream check itself fails.
# → Architect flags that the test exists but isn't in files_in_play.
# → Future-self asks where "the upstream check" actually lives —
#   no file path attached to the decision.
# Three actionable items. Add them to next_step + decisions, then:
keeper beat --next-step "add fail-mode test for upstream-down case" \
            --files src/api.py tests/test_health.py

# Now finalize.
keeper complete --summary "endpoint shipping; CI green"
```

The review's cost (~$0.10) buys back work that would otherwise be discovered by a colleague code-reviewing your commit, or worse, in production. Use it when the session contained nontrivial decisions.

### Filtering the roster

The default roster is everything baseline + everything repo-specific. Often you want less.

**Skip personas you don't need this time:**

```bash
# In a non-content-heavy session, drop the prose-focused baselines:
keeper review --live \
  --no-persona content-quality \
  --no-persona user-experience
```

**Run a single persona:**

```bash
# Skeptic-only — quick second opinion at minimum cost (~$0.012).
# Drop everything else explicitly:
keeper review --live --yes \
  --no-persona architect \
  --no-persona future-self \
  --no-persona content-quality \
  --no-persona user-experience \
  --no-persona downstream-impact-guardian \
  --no-persona cost-containment-auditor \
  --no-persona cognitive-memory-steward
```

**Add a persona that isn't in the default roster** (e.g., for a domestic cruise normally `compliance-officer` is excluded; force it for an international leg):

```bash
keeper review --family ports --repo InTheWake --live \
  --persona compliance-officer
```

**Override the auto-detected repo** (e.g., you're working in `ken/` but reviewing a sermon entry):

```bash
keeper review --family draft-week3 --repo Romans --live
# → loads exegetical-guardian, pastoral-shepherd, application-bridge
#   instead of ken's downstream-impact-guardian etc.
```

**Skip the cost prompt:**

```bash
keeper review --live --yes              # already-confirmed
```

### Choosing a model

The `--model` flag selects which adapter handles the calls. Default is `gpt` (uses the orchestrator's GPT adapter):

```bash
keeper review --live --model gpt        # default
keeper review --live --model gemini
keeper review --live --model grok
keeper review --live --model perplexity
keeper review --live --model youdotcom
```

Different models will produce different critiques. If you have a specific persona that consistently underperforms on one model, run *just* that persona on a different model:

```bash
keeper review --live --yes --model grok \
  --no-persona architect --no-persona content-quality \
  --no-persona user-experience --no-persona future-self \
  --no-persona downstream-impact-guardian \
  --no-persona cost-containment-auditor \
  --no-persona cognitive-memory-steward
# → Skeptic-only on Grok
```

### Output shapes

**Default (text, no prompts):** human-readable, one block per persona with the comment and aggregate score. Best for reading.

**`--json`:** machine-readable. Good for piping into `jq` or feeding back into Claude:

```bash
keeper review --live --yes --json | jq '.results | to_entries | map({name: .key, comment: .value.comment})'
```

The JSON shape:

```json
{
  "family": "ports",
  "repo": "ken",
  "state_present": true,
  "live": true,
  "actual_cost_usd": 0.0413,
  "cost_estimate_usd": 0.10,
  "roster": [
    {
      "name": "skeptic",
      "repo": "baseline",
      "baseline": true,
      "criticality": null,
      "needs_domain_expert_review": false,
      "criteria": ["assumption_examined", "falsifiable", "alternative_considered"],
      "prompt_chars": 6415
    },
    ...
  ],
  "results": {
    "skeptic": {
      "comment": "I notice the `decisions` array commits to ...",
      "aggregate_score": 7,
      "confidence": 0.85,
      "usage": {"model": "gpt-4o", "input_tokens": 1542, "output_tokens": 87, "estimated_cost_usd": 0.0056}
    },
    ...
  },
  "notes": []
}
```

**`--show-prompts`:** print the full per-persona prompt that *would* be (or *was*) sent. Useful for:
- Debugging unexpected critiques ("why did the persona answer like that?")
- Sanity-checking a new repo-specific persona before going live
- Documenting the actual prompt for review by a domain expert (especially for `manateecreeksheep`, where domain thresholds need expert calibration)

```bash
keeper review --family ports --show-prompts > /tmp/review-prompts.txt
# 8 prompts, ~3K-7K chars each, fully renders the persona body + protocol +
# state JSON + journal — exactly what Claude sees.
```

### Cost planning

Per persona, ~$0.012 at typical model rates (1.5K input + 200 output tokens). Default rosters:

| Repo | Default roster size | Estimate per `--live` |
|---|---|---|
| ken | 8 | ~$0.10 |
| Allrecipes / flickersofmajesty / heritage-cookbooks / manateecreeksheep | 8 | ~$0.10 |
| Romans | 8 | ~$0.10 |
| sermon-library | 10 | ~$0.12 |
| InTheWake | 11 | ~$0.13 |

Strategies for keeping cost down:

- **Run dry-run first** (free) and confirm the roster before going live.
- **Drop personas not relevant** to the specific session — content-quality and user-experience are usually skippable for code-heavy sessions.
- **One-persona spot-checks**: when stuck, fire just Skeptic (`~$0.012`) for a quick outside view.
- **Don't auto-fire on every beat.** Review is for moments where you'd ask a colleague — typically right before `complete`, or when stuck.

### Custom personas

To add a persona for an existing repo, drop a markdown file in `keeper/personas/<repo>/<name>.md`:

```markdown
---
name: my-custom-persona
repo: ports
criticality: 4
description: One-line summary of what this catches.
criteria:
  - first_criterion        # what does a 10/10 look like?
  - second_criterion
  - third_criterion
penalty_phrases:
  - "specific phrase that signals lazy thinking"
  - "another phrase"
when_not_to_use: situations where this persona doesn't apply
---

# My Custom Persona

You are MyCustomPersona — [the role description]. Your job is to surface
[the specific blind spot].

## Voice
[How this persona speaks — what tone, what level of directness]

## Calibration example
> [A 1-3 sentence example critique in this persona's voice, citing a
> specific element of family.json with a concrete score]

## Notes
Tie-break: [what to prefer when two candidates tie on aggregate].
```

The loader picks it up automatically on the next review — no code changes needed. To make a persona apply to multiple repos, use `repos: [a, b, c]` instead of `repo: a`. To make it baseline (every repo), use `baseline: true` and put it directly under `personas/`.

### When NOT to use review

- **On every beat.** Review is for *moments*, not background noise. Three calls per beat × 100 beats × $0.012 = $3.60 you didn't need to spend.
- **For structural checks.** Use `keeper validate` for "is this state internally consistent" — it's instant and free.
- **For sterile work.** A 5-minute session with one trivial change doesn't need eight Claude critiques.
- **When the personas are wrong for the work.** The default `Architect` persona's "testability" criterion is meaningful for software but mostly noise for a recipe site. Use `--no-persona architect` or override with a repo-tuned persona.

---

## Troubleshooting

### "no family specified"
You called a command that needs a family but didn't supply one. Three ways to set it:
1. `--family ports` flag
2. `export KEEPER_FAMILY=ports` env var
3. Repo config: `echo 'default_family = ports' > .claude/keeper.conf`

### "family 'ports' is held by session ... (heartbeat 5s ago)"
Another session in this terminal owns the lease and it's fresh. Either:
- That's actually you in another tab — let it finish or use `keeper status` to see what it's doing.
- It's stuck — `keeper join --force` to take over (records a `forced_takeover` event).

### Validate keeps failing on "files_in_play exist"
The lint checks every file path in `files_in_play` actually resolves under the repo root. If you removed or renamed a file, drop it from the list:
```bash
keeper beat --files src/api.py     # replaces the whole list
```

### The PreCompact hook isn't firing my snapshot
That's by design — PreCompact only writes a marker. The actual snapshot fires on your next `keeper beat`. Check for the marker:
```bash
ls .claude/state/families/ports/precompact.pending
```

### `python -m keeper` complains about missing module
Set `PYTHONPATH` to the directory containing the `keeper/` package:
```bash
export PYTHONPATH=/home/user/ken
python3 -m keeper status --family ports
```
The installed hooks bake this path in automatically; CLI usage may need it set.

### My family is "stale" but I was just typing into Claude
Heartbeat threshold is 90 min by default. If you're idle longer than that (lunch, code review, doc reading), keeper will mark the session stale. The `Take over? [y/N]` prompt lets you reclaim it without losing the old state — `forced_takeover` events preserve the previous holder's id in the journal.

### journal/state synced lint fails
This means `family.json:last_event_id` doesn't match the actual last entry in `journal.jsonl`. Usually a sign someone wrote to one without the other (manual edits, partial recovery, etc.). Repair by running another `keeper beat` — it'll write a fresh entry that brings them back into sync.

### I want to wipe a family and start over
```bash
rm -rf .claude/state/families/<name>
keeper join --family <name>
```
Family state is just files; deletion is safe.

### `keeper review --live` errors with "could not import adapters"
Live mode loads the orchestrator's adapter package from `<repo>/orchestrator/`. If you're running keeper in a repo without that directory (or the SDKs the adapters need aren't installed), live mode can't fire calls. Two paths:

```bash
# 1. Run keeper from inside ken (which has orchestrator/):
cd /home/user/ken
keeper review --family ports --live

# 2. Or install the adapter SDKs (openai, google-genai, etc. — see
#    /home/user/ken/orchestrator/requirements.txt).
pip install -r /home/user/ken/orchestrator/requirements.txt
```

Dry-run mode works regardless — it never imports the adapters.

### `keeper review` returns "no critique cleared threshold for <persona>"
The persona generated 10 candidate critiques but every one scored below the floor on at least one criterion (post-penalty). This usually means the family state is sparse enough that there's nothing meaningful to say *from that persona's POV*. Either accept it (some personas legitimately have nothing to add) or enrich the state and re-run.

### A persona keeps generating critiques that miss the point
Three knobs:

1. **Read the persona file.** `keeper personas/<repo>/<name>.md` — the criteria and penalty phrases live in the frontmatter. Tweak them.
2. **Print the actual prompt.** `keeper review --family X --show-prompts` shows exactly what the model is seeing. If the persona body or criteria are off, they're visible there.
3. **Try a different model.** `keeper review --live --model gemini` — different models have different strengths. GPT tends to follow protocol structure tightly; Grok tends to be more adversarial; Gemini tends to be more elaborate.

### Cost is higher than expected
The estimate is ~$0.012/persona based on typical token usage. Reality varies:

- Larger family state (long `working` arrays, dense decisions) → larger input → higher cost.
- Verbose models (some Grok configurations) → higher output tokens.
- Failed JSON parsing → adapter retries (rare).

The actual cost is reported in the `actual_cost_usd` field of `--json` output and in the live-mode summary. Run `keeper review --live --json` once and check the per-persona `usage.estimated_cost_usd` to calibrate.

---

## Design notes

The full 9-round design history lives in `keeper-plan.md` at the repo root. Key decisions in brief:

**State-as-authority, not journal-replay.** `family.json` is the truth; the journal is an audit trail. Resume is a single file read, not an event-sourcing replay. Validated by SQLite/Redis/etcd which all use this shape (atomic state file + WAL).

**Heartbeat is mtime, not a JSON timestamp.** Eliminates clock-skew and parse-format bugs. Lifted from `AnastasiyaW/mclaude`.

**Composed staleness: wall-clock floor only (Stage 1).** 90 min wall-clock silence = stale. Stage 1.5 will add a sequence-unchanged second-scan check to handle laptop-sleep false positives more gracefully.

**Linked log via `prev_event_id`.** 16 bytes/entry buys partial-write detection, truncation detection, and tamper detection in one mechanism.

**Atomic write with `.backup` safety net.** Before each `family.json` rewrite, the prior generation is renamed to `.backup`. Reader falls back automatically if the primary won't parse. Defends against the rare torn-rename failure mode.

**Strict-by-default `complete`.** Forces meaningful handoffs. The quality rubric is a CONTINUITY pattern; the lint expansion is from the orchestra triad. Bypassable with `--force` for emergencies.

**Repo-local config only.** No `~/.config/keeper/`. Personal-data fields (name, tz, editor) were dropped per orchestra privacy concern. `default_family` is the only config; lives in `.claude/keeper.conf`.

**No CF / network coordination.** Stage 2 (Cloudflare Durable Objects for cross-host lease arbitration) is deferred indefinitely. The 5% phone-use case is solvable with cloudflared/tailscale tunnels onto a laptop-served read-only dashboard if/when needed.

**No SQLite.** Evaluated and rejected: zero binary deps, greppable JSONL, raw stdlib is enough. CONTINUITY uses SQLite for its MCP-tool surface; we have a CLI surface where files-on-disk is simpler.

**Review is a separate cognitive layer, not a replacement for validate.** The orchestra triad's "trim, don't enhance" verdict still applies to validate (deterministic structural checks stay structural). Review is opt-in and never gates `complete` by default — the cost-conscious choice is to run it explicitly, not have it ride along on every lifecycle action.

**Personas are markdown files, not code.** The frontmatter declares the rubric (`criteria`, `penalty_phrases`, `when_not_to_use`), and the markdown body becomes the system prompt. Adding a new persona is dropping a file, no code changes. Borrowed the daemon-with-rubric architecture from `nickkeesG/Pantheon` and the verifier-role concept from `PrometheanLink/pantheon`.

**Min-of-criteria aggregation, not sum-of-points.** A naive sum lets one strong dimension paper over weakness on others. The min forces every criterion to clear a bar. Sharp failure mode: if all candidates score 1 on at least one criterion, the "winner" is still bad — handled by the `aggregate < 4 → "no critique cleared threshold"` floor.

**Review uses the orchestrator's existing adapters, not its own model layer.** `keeper review --live` imports `orchestrator/adapters/__init__.py` and calls `adapter.query(prompt, system)` per persona in parallel. This means keeper's review surface stays small (~150 LOC in `review.py`) and inherits adapter improvements automatically. The price: review is a "live in ken" feature; using it in a repo without orchestrator next door requires installing the adapter SDKs locally.

---

## Limitations

- **Single-host only.** No cross-machine coordination. The 5% phone case isn't covered yet.
- **No O_EXCL on `join`.** Two simultaneous joins to a fresh family both succeed (last-writer-wins). Stage 1 assumes one human, one terminal.
- **No tamper-evident hashing on the journal.** Linked log catches truncation; cryptographic chains are deferred. If your threat model includes adversaries with FS write access, defense in depth lives elsewhere.
- **Quality rubric is opinionated.** The 7 criteria may not match your workflow. Override per-call with `--threshold N` or bypass with `--force`.
- **Family names are ASCII-only.** `[a-z0-9-]{1,32}`. Unicode names not supported.
- **Recovery brief is plaintext-bounded.** If your `working` array has 100 entries, the human-readable brief gets long. Use `--brief` for a tighter Claude prompt.
- **Review is single-model per invocation.** Each `--live` run uses one `--model`. Cross-model debate (one persona on Claude, one on GPT, one on Grok) would be a separate orchestration layer; for now, run two sequential `--live` invocations with different `--model` flags if you want both perspectives.
- **Personas score themselves; we trust the score.** The model returns its own `aggregate_score` per the protocol. We don't post-process or recompute it. If a model lies about its score, we won't notice — practical mitigation is the penalty phrases (which catch the most common laziness pattern).
- **Review can't see your code, only your state.** Each persona reads `family.json` + the last 10 journal events, not your actual git diff. A critique like "where's the test?" is anchored to whether `files_in_play` includes a test file, not whether the test exists in the working tree. If you want diff-aware review, that's future work.

---

## Credits

This module wouldn't exist without the prior art it learned from. Full attribution per concept lives in `CREDITS.md`. Highlights:

- **[AnastasiyaW/mclaude](https://github.com/AnastasiyaW/mclaude)** (MIT) — atomic-write pattern, heartbeat-as-mtime, structured handoff schema, worktree+branch detection, schema-version-with-migration.
- **[duke-of-beans/CONTINUITY](https://github.com/duke-of-beans/CONTINUITY)** (MIT) — auto-escalation, handoff quality scoring, state-accumulator merge semantics, `ended_cleanly` flag.
- **[nickkeesG/Pantheon](https://github.com/nickkeesG/Pantheon)** (MIT) — daemon-with-rubric protocol for `keeper review` (multi-persona, 3-criteria scoring, **minimum-of-criteria** aggregation, penalty-phrase post-processing).
- **[PrometheanLink/pantheon](https://github.com/PrometheanLink/pantheon)** (MIT) — Verifier role concept (one Claude instance whose job is to check the work of another); inspired the `keeper review` command shape.

Plus the 5-model review chain (Gemini → Perplexity → You.com → GPT → Grok), the orchestra triad (GPT → Gemini → Grok), four memory-tool spikes that surfaced Anthropic's official Auto Memory feature, and seven sequential per-repo orchestra runs that drafted the 26 repo-specific personas.

---

## License

MIT. See `LICENSE` (when added).

## Project layout

```
keeper/
├── README.md           # this file
├── CREDITS.md          # per-concept attribution
├── __init__.py         # public API re-exports
├── __main__.py         # python -m keeper entry point
├── checkpoint.py       # core: state, lease, journal, hooks, CLI
├── personas.py         # frontmatter parser + persona loader (no deps)
├── review.py           # build/run keeper review (dry-run + live)
├── personas/           # the 31-persona library
│   ├── README.md
│   ├── skeptic.md, architect.md, future-self.md,
│   ├── content-quality.md, user-experience.md          (5 baseline)
│   ├── allrecipes/<3 personas>
│   ├── flickersofmajesty/<3>
│   ├── heritage-cookbooks/<3 — shared by Grandmas/Grannys/Moms>
│   ├── inthewake/<6>
│   ├── ken/<3>
│   ├── manateecreeksheep/<3 — domain-expert review pending>
│   ├── romans/<3>
│   └── sermon-library/<5>
└── tests/
    ├── conftest.py     # tmp_repo fixture (gpg-disabled)
    ├── test_keeper.py  # core lifecycle (state/lease/journal/validate/snapshot/hooks)
    ├── test_personas.py  # frontmatter parser, roster, build_review, live mode (mocked)
    └── test_acceptance.py  # 3 end-to-end scenarios (kill-resume, corruption, race)
```

Total: ~1700 LOC core + ~1000 LOC tests, stdlib-only. Live `keeper review` additionally requires the orchestrator's adapter SDKs (`openai`, `google-genai`, etc. — see `/home/user/ken/orchestrator/requirements.txt`).
