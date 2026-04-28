# keeper — design doc

**Status:** design frozen pending CONTINUITY spike. No code yet.
**Goal:** survive seamless thread handoff across Claude Code sessions; family-scoped, primarily local FS, optional remote later.

---

## Why we're building this

Three Anthropic GitHub issues confirm the user's pain is widespread:
- [#24798](https://github.com/anthropics/claude-code/issues/24798) — inter-session communication for multi-Claude workflows
- [#15776](https://github.com/anthropics/claude-code/issues/15776) — session state should persist across git worktrees
- [#11455](https://github.com/anthropics/claude-code/issues/11455) — session handoff / continuity support

User's specific shape: ~95% laptop, ~5% phone. Sessions group into named families (`ports`, `ships`); families are isolated, threads within share continuity.

---

## How we got here (review process)

5-model chain (Gemini → Perplexity → You.com → GPT → Grok) + mclaude code spike. Everything below survived all six rounds.

---

## Architecture (final)

**Single source of truth:** one `family.json` per family, atomic-rewritten under heartbeat-gated lease. Inspired by ZFS TXG+ZIL, Git refs+reflog, Restic snapshots. Validated as canonical by SQLite/Redis/etcd prior art.

### File layout

```
.claude/state/families/<name>/
├── family.json          # consolidated lease + state — atomic tmp+rename
├── heartbeat            # 0-byte file; mtime IS the heartbeat (no JSON timestamp)
├── journal.jsonl        # optional audit trail; linked log via prev_event_id
└── completed/           # archive of finished/force-released sessions
    └── <name>_<ts>_<status>.md
```

### `family.json` schema

```json
{
  "schema": 1,
  "family": "ports",
  "session_id": "sess-20260428T015432Z-ac3592",
  "instance_token": "uuid-per-join",
  "generation": 3,
  "host": "user-laptop",
  "pid": 12345,
  "boot_id": "from /proc/sys/kernel/random/boot_id",
  "started_at": "...",
  "worktree": "/path/to/worktree",
  "branch": "feature/x",
  "git_hash": "abc123",
  "goal": "what this thread is doing",
  "done":       ["completed steps"],
  "not_worked": ["dead ends"],
  "working":    ["verified working"],
  "broken":     ["currently broken"],
  "blocked":    ["external blockers"],
  "decisions":  [["what", "why"]],
  "next_step":  "first action for resume",
  "files_in_play": ["list of files touched"],
  "refs":       ["gh:42", "linear:ENG-1"]
}
```

The `done` / `not_worked` / `working` / `broken` / `blocked` / `decisions` / `next_step` field set is **lifted from mclaude's Handoff dataclass** — credit in CREDITS.md.

### `journal.jsonl` schema (linked log)

```json
{
  "ts": "...",
  "event_id": "uuid",
  "prev_event_id": "uuid or null",
  "session_id": "...",
  "instance_token": "...",
  "git_hash": "abc123",
  "type": "join | beat | complete | forced_takeover | branch_change | note",
  "payload": {...}
}
```

### Invariants

1. **Lease gates writes.** `instance_token` validates ownership at the data layer; bypass attempts are rejected on read.
2. **Atomic state.** `family.json` always written via tmp+rename with unique tmp suffix (`f".tmp.{uuid.uuid4().hex[:8]}"`) to survive same-session-multi-thread races. Lifted from mclaude.
3. **Journal-before-state ordering.** Append journal first, then update `family.json`. Crash leaves either old or new generation, never half (Restic pattern).
4. **Heartbeat = mtime.** No JSON timestamp; `Path.touch()` on heartbeat file is the canonical liveness signal. Lifted from mclaude.
5. **Composed staleness.** `(wall_clock_silent > 90 min) AND (heartbeat_seq_unchanged across two scans)`. Survives laptop sleep without false-positive eviction.
6. **Linked log integrity.** Each journal entry references `prev_event_id`. On replay (debug only), break in chain → stop at last valid entry.
7. **One writer per family.** `O_CREAT|O_EXCL` on initial family.json creation; `generation` counter on takeover.
8. **Force takeover requires `--reason`.** Audit entry in journal + archived markdown in `completed/`. No cooldown (Grok-cut).

---

## Concepts lifted from `AnastasiyaW/mclaude` (with credit)

| # | Concept | Where in our code |
|---|---|---|
| 1 | Heartbeat-as-mtime via `Path.touch()` | `keeper/checkpoint.py: _beat()` |
| 2 | Structured handoff schema (`done`/`not_worked`/`working`/`broken`/`blocked`/`decisions`/`next_step`/`refs`) | `family.json` content |
| 3 | `_atomic_write` with unique tmp suffix | `keeper/_fs.py: atomic_write()` |
| 4 | Worktree detection via `git rev-parse --git-common-dir != --git-dir` | `keeper/_git.py: detect_worktree()` |
| 5 | Branch detection via `git rev-parse --abbrev-ref HEAD` | `keeper/_git.py: detect_branch()` |
| 6 | Schema-version with explicit migration hook | `keeper/checkpoint.py: _load_state()` |
| 7 | `KEEPER_FAMILY` env var pattern (mclaude has `MCLAUDE_IDENTITY`) | `keeper/cli.py` |
| 8 | `slugify()` with stopwords | `keeper/_text.py` |
| 9 | Append-only audit semantics — status transitions are new rows | `journal.jsonl` (validates our linked-log) |
| 10 | Refs section for opaque external IDs | `family.json: refs[]` |

CREDITS.md will reference mclaude (MIT) by name with a one-line explanation per concept.

---

## What we explicitly did NOT lift

| Thing | Why |
|---|---|
| Per-task lock granularity (`<slug>.lock`) | Wrong abstraction; we want per-family, not per-task |
| Hub server (FastAPI) | Self-hosted infra burden; we have CF available if needed |
| Identity registry as separate concept | Solo-user-friendly; family already encodes "what" |
| Memory graph / mail / messaging | Out of scope; cognitive memory handles this |
| MCP server integration in v1 | Premature; can add later as adapter |
| 180-second stale threshold | Way too aggressive for Claude's thinking pauses; we use 90 min |

---

## What we rejected from external suggestions

| Suggestion | Source | Why rejected |
|---|---|---|
| `sqlitedict` for state | Perplexity R2 | CVE-2024-35515 pickle RCE; #108/#24/#63 commit hangs |
| `portalocker` for locks | Perplexity R2 | Debian #1058077 NFS failure; Linux 5.15 advisory-only |
| `fasteners` for locks | Perplexity R2 | pyfakefs failures; reader/writer deadlocks |
| Periodic NFS recheck | Gemini R1 | Initial check sufficient; periodic cost > rare benefit |
| Force-takeover cooldown | ChatGPT critique | `--reason` + audit log is enough friction |
| Debug-info bundle command | Gemini R1 | Premature; add when first user reports a bug |
| Build-order C abstraction over our design + mclaude | GPT R4 | Fence-sit; pick one (Grok rightly attacked) |
| Tunnel-only for phone (no CF DO ever) | You.com R3 | User already pays for CF; defer the decision until Stage 1 ships |
| SQLite WAL backend | ChatGPT critique | Strong case when journal was authoritative; weak now that state is |

---

## Stage 1 — FS foundation (~3-4 hours)

**New repo** name TBD (candidates: `keeper`, `claude-keeper`, `pulse-keeper`, `tether`, `relay`). Pip-installable. License MIT. Stdlib-only core.

### CLI

| Command | Purpose |
|---|---|
| `keeper join --family <name> [--goal "..."]` | Acquire lease, write family.json, log to journal, touch heartbeat. Auto-suggests family from branch/cwd if not provided (prompt, never silent). |
| `keeper beat [--action "..."] [--working-on "..."] [--decision "what" "why"]` | Touch heartbeat, update family.json fields, append journal. Read-modify-write transaction (Android DataStore shape). |
| `keeper complete [--summary "..."]` | Graceful end; archive to completed/, release lease. |
| `keeper status [--family <name>]` | Current state, files in play, time since last beat. |
| `keeper scan` | Detect stale families in current repo via composed criterion. |
| `keeper recover [--family <name>] [--json]` | Print recovery brief; `--json` emits machine-parseable form for Claude client priming. |
| `keeper families [--all-repos]` | Registry of active families. |
| `keeper clean-locks` | Orphan-lock cleanup (Git index.lock style; explicit, no `--force` ambiguity). |
| `keeper validate-journal --family <name>` | Linked-log integrity check. |
| `keeper new-id` | Fresh session id. |

### Reused from existing `orchestrator/checkpoint.py`

`_now()`, `repo_root()`, `_git()` helpers. Migrate the existing 365-line checkpoint.py to the new repo via a thin shim that imports from `keeper`.

### Hard caps

- 100 families per repo.
- `family.json` size: 2 KB warn, 8 KB fail.
- Journal entry size: <PIPE_BUF (4 KB) for atomic append.

### Tests (~50 total)

| Suite | Coverage |
|---|---|
| `test_lease.py` | acquisition, takeover, generation monotonicity, instance_token validation |
| `test_state.py` | atomic write, schema migration, field validation |
| `test_journal.py` | linked-log integrity, append-only semantics, replay correctness |
| `test_heartbeat.py` | mtime-based liveness, composed staleness, sleep-survival |
| `test_concurrency.py` | two-process subprocess.Popen race; **crash-mid-write** via SIGKILL between journal append and state write (Grok-flagged failure mode) |
| `test_filesystem.py` | NFS refusal, boot_id detection, atomic-rename guarantees |
| `test_family.py` | isolation, auto-suggest prompt, worktree-aware identity |
| `test_cli.py` | recover --json shape, status output, error codes |

---

## Stage 2 — DEFERRED

CF Durable Object sync vs. tunnel for phone. **Do not decide until Stage 1 ships and there is real usage signal.** You.com argued tunnel is sufficient (matches HAPI/claude-relay); Grok argued tunnel adds friction. Both have merit. The user already pays for InTheWake on CF, so the $5/mo argument is moot — but cold-start latency (100-500ms) and lease-thrashing on sleep/wake (Figma + GitHub Codespaces both see this) are real concerns.

When Stage 2 happens, decision criteria:
- If multiple devices need to **write** → CF DO (lease arbitration)
- If phone only needs to **read** state → tunnel + dashboard

## Stage 3 — DEFERRED

Read-only HTML dashboard. Not started until Stage 2 transport is decided.

---

## Mental models worth pinning

| Pattern | What it teaches us |
|---|---|
| ZFS TXG + ZIL | Authoritative state at TXG boundaries; ZIL is intent log. Maps to family.json + journal.jsonl. Generation counter mirrors TXG number. |
| Git refs + reflog | Lightweight ref pointer (lease) + chronological log (journal). Reflog can expire without losing state. |
| Restic write order | Data → index → snapshot. Crash leaves either old or new, never half. Maps to journal-append → state-write → lease-bump. |
| Android DataStore `updateData()` | Read-modify-write transactional update with verification. Right shape for `keeper beat`. |
| Chrome IndexedDB recovery journal | Tiny "pending operations" list for crash recovery between journal append and state rewrite. Optional refinement. |
| SQLite + WAL | Main DB authoritative, WAL supplemental. Same shape; validates we're not novel. |

---

## Calibration data (not building toward, just useful)

- mclaude is ~140 KB Python, MIT, alpha (v0.6.0). Stdlib-only core. Per-task locks, hub server, mail, memory graph, MCP server. Closest existing tool; granularity differs.
- CF DO cold-start under contention: 100-500ms. Per-object soft limit ~1,000 req/s. $5/mo minimum on paid Workers.
- portalocker NFS Debian #1058077; Linux 5.15 removed mandatory locking.
- sqlitedict CVE-2024-35515 pickle RCE.
- Existing tools (8 found by You.com): `mclaude`, `mohshomis/ckpt`, `varie-ai/workstation`, `Sonovore/claude-code-handoff`, `thepushkarp/handoff`, `nielsgroen/claude-tmux`, `TerminalGravity/cld-tmux`, `markx3/nexus-tui`. None match our family abstraction.

---

## Acceptance test (real-world, not unit)

> Start session A on laptop in `ports` family. Edit two files, write a `decisions` entry, kill the terminal abruptly (Cmd-Q, no `complete`). Open new terminal. Run `keeper recover --family ports`. The output must include: last action, current `working`/`broken`/`blocked` state, `next_step`, files_in_play, and the decision history. Zero manual handoff. Claude can resume by reading the JSON output without re-asking the human.

---

## Open questions deferred to implementation

- Repo name (lean: `keeper`, short and search-friendly).
- Migration of existing `.claude/state/session-pulse.json` in `ken/` → `families/default/`.
- SessionStart hook integration: detect `KEEPER_FAMILY`, auto-call `keeper join` if family exists else prompt.

---

---

## CONTINUITY spike findings (`duke-of-beans/CONTINUITY` v1.3.0)

TypeScript MCP server, MIT, ~2,160 LOC. Storage: SQLite (state.db, WAL mode) for checkpoints + sessions + indexes; JSONL for decisions; JSON+markdown for session snapshots. **8 MCP tools** invoked from Claude Desktop, not a CLI.

### Architectural divergences from us

| Dimension | CONTINUITY | keeper |
|---|---|---|
| Concurrency model | Single-session-at-a-time, no locks/leases | Multi-session via lease + instance_token |
| Storage | SQLite (state.db) authoritative + JSONL audit | Single `family.json` authoritative + JSONL audit |
| Workspace identity | `workspace` string (free-form) | `family` string (validated kebab-case) |
| Crash detection | `ended_cleanly: bool` flag in DB; query unclean sessions on start | Heartbeat mtime + composed staleness |
| Latest-record ordering | `ORDER BY timestamp DESC` | `generation` counter (clock-skew safe) |
| Distribution | Local-only; one Claude Desktop instance assumed | Designed for many concurrent threads in named families |
| Surface | MCP tools (Claude calls them) | CLI (human + hooks call it) |

Their model is simpler because their problem is smaller. Our concurrency apparatus exists for a problem they don't have.

### Concepts worth lifting (with credit)

| # | Concept | Why it's strong | How we adopt it |
|---|---|---|---|
| 11 | **Auto-escalation** — checkpoint counter triggers automatic full snapshot every N beats (default 15) | Means crash recovery is always within N-beats of a full snapshot, even without explicit `complete` | Add `--escalation-threshold` to `keeper join`; every Nth `keeper beat` writes `completed/snapshots/<ts>_auto.json`. Default 15. |
| 12 | **Handoff quality scoring** — 0-100 completeness score with missing_elements + warnings + suggestions | Forces meaningful handoffs; users get feedback if state is too sparse | New `keeper validate [--strict]` command. `keeper complete` blocks if score < 60 (configurable). Rubric: workspace+phase=20, next_step=20, files_in_play=10, decisions=15, working/broken/blocked=15, etc. |
| 13 | **State accumulator semantics for beats** — latest-wins for scalars, append-with-dedup for arrays | Each beat carries running context; any beat can serve as recovery point | `keeper beat` merges in this exact pattern. Already roughly planned; CONTINUITY validates the rules. |
| 14 | **Explicit `ended_cleanly` flag** on session record | Cheap crash detection regardless of heartbeat state | Add to `family.json`. On `complete`, set true. On `join` of new generation, log unclean ending in journal. |
| 15 | **Richer decision schema** — category / impact / alternatives / revisit_trigger | Decisions become searchable artifacts, not just `[what, why]` tuples | Enrich `family.json: decisions[]` to objects: `{what, why, category, impact, alternatives[], revisit_trigger}`. Backward-compat: tuple form still accepted. |
| 16 | **Per-workspace checkpoint pruning** (`keepCount: 50`) | Bounds disk usage automatically | `keeper beat` prunes `completed/snapshots/` to last 50 per family. |

### Concepts considered but rejected

| Thing | Why we don't lift |
|---|---|
| SQLite (better-sqlite3 / WAL mode) for state | We already evaluated and rejected: zero binary deps + greppable JSONL stays. Theirs is fine for their MCP-tool surface; ours is fine for our CLI surface. |
| MCP server architecture | Different deployment model. We're terminal-first; MCP is Claude-Desktop-first. Both valid; ours is simpler for our use. |
| Token-budget context compression heuristic | Their `estimateTokens(text) = ceil(len/4)` line-based filter is rough. If we ever need this, let Claude itself summarize on-demand. |
| Brain signal extraction (`writeSignalObservation`) coupling | Coupled to their separate analytics DB. We have cognitive-memory for that, plumbed differently. |
| `ORDER BY timestamp DESC` for "latest" | Clock-skew unsafe under concurrent writers. Our `generation` counter is correct for our case. |
| Free-form workspace strings | We validate with `[a-z0-9][a-z0-9-]{1,31}` (mclaude pattern) to prevent typos like `port` vs `ports`. |

### What CONTINUITY's existence tells us

1. **Two independent designs converged on the same content shape:** workspace+phase+completed_operations+active_files+next_steps+decisions+warnings. mclaude's Handoff and CONTINUITY's SessionState are basically the same dataclass written by different people. This is strong evidence the field set is right.

2. **Single-writer designs are common; multi-writer is rare.** Both mclaude and CONTINUITY assume one writer at a time. Our lease/instance_token apparatus is the differentiator. Worth keeping; it's the actual reason we're building rather than adopting.

3. **Auto-escalation is the missing piece in mclaude AND in our original plan.** Without it, a user who forgets to call `complete` loses everything between last manual save and crash. Lifting this is the highest-value find from CONTINUITY.

4. **Handoff quality scoring is a UX feature with real value.** "Your handoff is 35/100 — missing next_step, no decisions logged, only 1 active file" is useful feedback that mclaude doesn't provide.

### Updated `family.json` schema (post-CONTINUITY)

```json
{
  "schema": 1,
  "family": "ports",
  "session_id": "...",
  "instance_token": "...",
  "generation": 3,
  "ended_cleanly": false,
  "host": "user-laptop",
  "pid": 12345,
  "boot_id": "...",
  "started_at": "...",
  "worktree": "/path/to/worktree",
  "branch": "feature/x",
  "git_hash": "abc123",
  "phase": "implementation",
  "goal": "...",
  "done":       ["..."],
  "not_worked": ["..."],
  "working":    ["..."],
  "broken":     ["..."],
  "blocked":    ["..."],
  "decisions":  [
    {
      "what": "use SQLite WAL",
      "why": "atomic writes",
      "category": "architectural",
      "impact": "high",
      "alternatives": ["JSONL", "raw FS"],
      "revisit_trigger": "if write contention > 1k/s"
    }
  ],
  "next_step":  "...",
  "files_in_play": ["..."],
  "warnings":   ["..."],
  "refs":       ["gh:42"]
}
```

Two new fields vs. mclaude-derived schema: `ended_cleanly` (CONTINUITY) and `phase` (CONTINUITY). Decisions become objects, not tuples (CONTINUITY).

### Updated CLI (post-CONTINUITY)

Two new commands:

| Command | Purpose |
|---|---|
| `keeper validate [--family <name>] [--strict]` | Score current state against handoff-completeness rubric (0-100). Suggests improvements. `--strict` makes `complete` block if score < threshold. |
| `keeper snapshot [--family <name>] [--label "..."]` | Manually write a full snapshot to `completed/snapshots/`. Auto-fired every N beats (default 15). |

### Updated invariants (post-CONTINUITY)

9. **Auto-escalation guarantee.** A full snapshot is written to `completed/snapshots/` every N beats (default 15), so crash recovery is bounded.
10. **Handoff completeness gate.** `keeper complete` checks score; refuses if below threshold unless `--force`.
11. **`ended_cleanly` flag.** Set true on `complete`; checked on next `join` to log "previous session ended uncleanly" in journal.

---

## Status of this document

- 7 review rounds applied (5-model chain + mclaude spike + CONTINUITY spike).
- CREDITS.md will reference both `AnastasiyaW/mclaude` (10 concepts) and `duke-of-beans/CONTINUITY` (6 concepts) by name with one-line attribution per concept.
- Ready to scaffold `keeper/` locally on user signal.
