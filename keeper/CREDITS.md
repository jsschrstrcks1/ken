# Credits

`keeper` learned from prior art. This file attributes every lifted concept to its source. Both upstream projects are MIT-licensed; we're not forking either, but the ideas they pioneered are baked into our design and we want to be loud about that.

## From [`AnastasiyaW/mclaude`](https://github.com/AnastasiyaW/mclaude) (MIT)

mclaude is a multi-session collaboration layer for Claude Code: atomic locks, handoffs, memory graph, hub server, voice I/O. We don't share the per-task lock granularity (we use per-family) or the hub-server transport, but ten of mclaude's patterns are in our code:

| # | Concept | Where it lives |
|---|---|---|
| 1 | Atomic write with unique tmp suffix (`f".tmp.{uuid.uuid4().hex[:8]}"`) — survives same-session multi-thread races | `checkpoint.py: atomic_write()` |
| 2 | Heartbeat-as-file-mtime via `Path.touch()` — no JSON timestamp | `checkpoint.py: touch_heartbeat()` |
| 3 | Worktree detection via `git rev-parse --git-common-dir != --git-dir` | `checkpoint.py: detect_worktree()` |
| 4 | Branch detection via `git rev-parse --abbrev-ref HEAD` | `checkpoint.py: detect_branch()` |
| 5 | Schema-version-with-migration hook | `checkpoint.py: _migrate_schema()` |
| 6 | Append-only audit semantics — status changes are new rows, never edits | `checkpoint.py: journal_append()` |
| 7 | Structured handoff schema (`done`/`not_worked`/`working`/`broken`/`blocked`/`decisions`/`next_step`/`refs`) | `family.json` content |
| 8 | Slug validation regex (kebab-case, length-bounded) | `checkpoint.py: FAMILY_NAME_RE` |
| 9 | Force-takeover with explicit reason + audit entry | `checkpoint.py: join()` |
| 10 | Env-var identity pattern (`MCLAUDE_IDENTITY` → `KEEPER_FAMILY`) | `checkpoint.py: _resolve_family()` |

## From [`duke-of-beans/CONTINUITY`](https://github.com/duke-of-beans/CONTINUITY) (MIT)

CONTINUITY is a TypeScript MCP server: SQLite + JSONL + JSON snapshots, single-session-at-a-time. We took a different storage path (greppable JSON-on-disk, no SQLite) and a different surface (CLI, not MCP), but six of CONTINUITY's patterns are in our code:

| # | Concept | Where it lives |
|---|---|---|
| 11 | Auto-escalation — every Nth beat triggers a full snapshot, so crash recovery is bounded | `checkpoint.py: beat()` (the `% AUTO_ESCALATION_INTERVAL` check) |
| 12 | Handoff quality scoring — 0-100 against a rubric, with hints when fields are missing | `checkpoint.py: _score_quality()`, `QUALITY_RUBRIC` |
| 13 | State accumulator merge semantics — latest-wins for scalars, append-with-dedup for arrays | `checkpoint.py: _merge_state()` |
| 14 | Explicit `ended_cleanly` flag for cheap crash detection | `family.json: ended_cleanly` |
| 15 | Richer decision schema (object with `what`/`why`/`category`/`impact`/`alternatives`/`revisit_trigger` instead of just a tuple) | `family.json: decisions[]` |
| 16 | Per-family snapshot pruning bounded to a fixed ring | `checkpoint.py: _prune_snapshots()`, `SNAPSHOT_KEEP_COUNT` |

## From the memory-tool spike

A focused investigation across five memory-related projects clarified what keeper *isn't* and contributed three concrete patterns:

| # | Concept | Source |
|---|---|---|
| 17 | Hook integration with exact event names (`SessionStart` / `PreCompact` / `SessionEnd`) | [`coleam00/claude-memory-compiler`](https://github.com/coleam00/claude-memory-compiler) (MIT) |
| 18 | Repo-local config (replacing global `~/.config/keeper/profile.json` after orchestra critique) | Inspired by [`hanfang/claude-memory-skill`](https://github.com/hanfang/claude-memory-skill) (MIT) `me.md` pattern |
| 19 | Strategic frame: keeper is *session-continuity*, NOT *knowledge-accumulation* (the latter is owned by [Anthropic Auto Memory](https://code.claude.com/docs/en/memory)) | Anthropic Auto Memory docs (Claude Code v2.1.59+) |

## From the orchestra triad (Round 9)

The 9th review round produced an unusually unified verdict (trim, don't enhance) and surfaced three new concepts we hadn't lifted from elsewhere:

| # | Concept | Where it lives |
|---|---|---|
| 20 | `family.json.backup` safety net — atomic-rename of prior generation before each update; reader falls back automatically | `checkpoint.py: atomic_write_state()`, `read_state()` |
| 21 | Debounced PreCompact — write a marker, defer the actual snapshot to next beat | `checkpoint.py: beat()` (precompact.pending consume), `_hook_commands()` |
| 22 | Inline stale-takeover prompt in `keeper join` (no separate "recover then join" flow) | `checkpoint.py: join()` |

## What we explicitly chose NOT to lift

| Thing | Source | Why |
|---|---|---|
| Per-task lock granularity | mclaude | Wrong abstraction for our use case (we want per-family, not per-task) |
| FastAPI hub server | mclaude | Self-hosted infra burden; defer cross-host until concrete need |
| Identity registry as separate concept | mclaude | Adds complexity without value for a solo user |
| Memory graph / mail / messaging / MCP server | mclaude | Out of scope; cognitive-memory handles knowledge |
| 180-second stale threshold | mclaude | Way too aggressive for Claude's thinking pauses; we use 90 min |
| SQLite (better-sqlite3 / WAL mode) | CONTINUITY | Zero binary deps + greppable JSONL is simpler for our CLI surface |
| MCP server architecture | CONTINUITY | Different deployment model; we're terminal-first |
| Token-budget context compression | CONTINUITY | Heuristic line-based filter is rough; let Claude summarize on demand if needed |
| `ORDER BY timestamp DESC` | CONTINUITY | Clock-skew unsafe; our generation counter is correct |

## Review process

The full review history (5-model linear chain → mclaude code spike → CONTINUITY code spike → memory-tool spike across 5 sources → orchestra triad) is documented in `keeper-plan.md` at the repo root. 22 concepts ultimately landed in code; many more were considered and rejected with documented rationale.

## License

`keeper` itself is MIT-licensed (see `LICENSE`). Both upstream projects we lifted from are also MIT, so the ideas flow freely. Where we copied patterns rather than literal code, we've still attributed them here for honesty about lineage.
