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
```

That's it. `keeper recover` is the hook that re-bootstraps a new Claude session against the prior one's state with zero manual handoff.

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
3. Append a `complete` event to journal.
4. Set `ended_cleanly=true` and `completed_at` in state.
5. Atomic-write state.
6. Render a markdown summary to `completed/<family>_<YYYY-MM-DD_HH-MM-SS>_complete.md` with done/working/broken/blocked/decisions sections.

Skip the gate with `keeper complete --force` (audit trail is preserved; you just bypass the quality check).

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

---

## Limitations

- **Single-host only.** No cross-machine coordination. The 5% phone case isn't covered yet.
- **No O_EXCL on `join`.** Two simultaneous joins to a fresh family both succeed (last-writer-wins). Stage 1 assumes one human, one terminal.
- **No tamper-evident hashing on the journal.** Linked log catches truncation; cryptographic chains are deferred. If your threat model includes adversaries with FS write access, defense in depth lives elsewhere.
- **Quality rubric is opinionated.** The 7 criteria may not match your workflow. Override per-call with `--threshold N` or bypass with `--force`.
- **Family names are ASCII-only.** `[a-z0-9-]{1,32}`. Unicode names not supported.
- **Recovery brief is plaintext-bounded.** If your `working` array has 100 entries, the human-readable brief gets long. Use `--brief` for a tighter Claude prompt.

---

## Credits

This module wouldn't exist without the prior art it learned from. Full attribution per concept lives in `CREDITS.md`. The two biggest contributors:

- **[AnastasiyaW/mclaude](https://github.com/AnastasiyaW/mclaude)** (MIT) — atomic-write pattern, heartbeat-as-mtime, structured handoff schema, worktree+branch detection, schema-version-with-migration.
- **[duke-of-beans/CONTINUITY](https://github.com/duke-of-beans/CONTINUITY)** (MIT) — auto-escalation, handoff quality scoring, state-accumulator merge semantics, `ended_cleanly` flag.

Plus the 5-model review chain (Gemini → Perplexity → You.com → GPT → Grok), the orchestra triad (GPT → Gemini → Grok), and four memory-tool spikes that surfaced Anthropic's official Auto Memory feature and clarified that keeper's scope is *session-continuity*, not *knowledge-accumulation*.

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
└── tests/
    ├── conftest.py     # tmp_repo fixture
    ├── test_keeper.py  # 90+ unit tests
    └── test_acceptance.py  # 3 end-to-end scenarios
```

Total: ~1100 LOC core + ~700 LOC tests, stdlib-only.
