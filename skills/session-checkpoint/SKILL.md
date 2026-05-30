---
name: session-checkpoint
description: "Enforces atomic commits, checkpoint summaries, rate-limit recovery, and safe resume patterns. Writes session pulses + cognitive memory so interrupted sessions can restart cleanly."
version: 3.0.0
---

# Session Checkpoint

*Soli Deo Gloria — we work carefully, in small steps, offering each commit as honest labor.*

## Why This Skill Exists

Claude Code makes many API calls per step. Large edits can exhaust per-minute token budgets, and a rate-limit kill in the middle of a multi-file change loses uncommitted work silently. This skill prevents that with two complementary mechanisms:

1. **Cognitive memory checkpoints** — narrative state for the next session.
2. **Session pulse** — a heartbeat that captures the list of git-uncommitted files. If a session dies before writing a HANDOFF, the next session can scan for stale pulses and see exactly what work was in flight.

## Two layers, one workflow

The pulse module exists in two forms:

- **`keeper`** (modern, recommended) — full per-family lease/instance-token semantics, atomic state with `.backup` safety net, structured handoff schema, optional cognitive review. State at `<repo>/.claude/state/families/<name>/`. See `keeper/README.md`.
- **`orchestrator/checkpoint.py`** (legacy CLI, now a shim) — preserves the v1 command shape (`checkpoint.py beat / scan / complete / new-id`) and routes calls into keeper under family `default`. Existing scripts and the SessionStart hook keep working unchanged. On first call in a repo with a legacy `session-pulse.json`, the shim auto-migrates the file into `families/default/family.json`.

**For new work, prefer keeper directly.** The protocols below show the keeper commands first, with the legacy `checkpoint.py` form below for reference.

## Session Startup Protocol

### 1. Scan for an abandoned previous session

**Modern (keeper):**
```bash
PYTHONPATH=/Volumes/1TB External/openclaw/workspace-main python3 -m keeper status --family default
```
If a session's heartbeat is older than 90 min, `keeper join --family default` will prompt to take it over.

**Legacy (still works, routes through the shim):**
```bash
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py scan
```
If output is `{"ok": true, "stale": false}` you're clean. If a stale pulse is found you'll get a recovery summary listing the abandoned session's last action, last beat time, and the files that were uncommitted when it died. The stale pulse is archived to `.claude/state/session-pulse-stale/`.

### 2. Open a new pulse

**Modern (keeper):**
```bash
PYTHONPATH=/Volumes/1TB External/openclaw/workspace-main python3 -m keeper join --family <name> \
  --goal "<short summary>"
# Example: keeper join --family ports --goal "wire up new health-check endpoint"
```
Pick a family name that scopes the work (`ports`, `ships`, `cruising`, etc.). Multiple families can run in parallel without colliding.

**Legacy:**
```bash
SID=$(python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py new-id)
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py beat \
  --session "$SID" --action "starting <task>" --context "<short summary>"
```
Keep `$SID` for the rest of the session. Every later beat must use the same id so `beat_count` increments instead of resetting. (The shim now warns on stderr if the session id changes mid-flight.)

### 3. Identify the single target file

Do not load all files simultaneously. Load only what the task requires.

### 4. Write a session intent to cognitive memory

```bash
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/memory_ops.py encode ken insight \
  "Session intent: [task]. Target: [files]. Expected: [outcome]." \
  --tags session,intent,checkpoint
```

### 5. Recall prior session state

```bash
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/memory_ops.py recall "session checkpoint" --domain ken --limit 5
```

## Checkpoint Protocol (During Work)

After every logical unit of work do **both**:

**A. Beat the pulse** — refreshes state + heartbeat.

**Modern (keeper):**
```bash
PYTHONPATH=/Volumes/1TB External/openclaw/workspace-main python3 -m keeper beat \
  --family <name> --action "edited foo.py: added retry logic" \
  --files foo.py
```

**Legacy (still works):**
```bash
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py beat \
  --session "$SID" --action "edited foo.py: added retry logic"
```

**B. Encode to cognitive memory** — narrative for resume.

```bash
python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/memory_ops.py encode ken insight \
  "Checkpoint [N]: Edited [file]. Changed [what]. Still needs [remaining]. Risks: [any]." \
  --tags session,checkpoint
```

### When to checkpoint

- After completing a function or block edit
- Before switching to a second file
- Before any find-and-replace touching multiple locations
- Before modifying critical data structures

## Rate Limit Recovery

When you see `Rate limit reached` or HTTP 429:

1. **Stop.** Do not retry immediately.
2. **Beat one final time** with the recovery state in `--action`:

   ```bash
   python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py beat --session "$SID" \
     --action "RATE LIMIT: paused at <step> in <file>; resume with <next>"
   ```

3. **Encode recovery memory:**

   ```bash
   python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/memory_ops.py encode ken decision \
     "RATE LIMIT RECOVERY: Interrupted at [step]. File: [name]. Last clean: [state]. Next step: [action]. Do NOT: [incomplete work]." \
     --tags session,recovery,rate-limit --protected
   ```

4. **Wait 60 seconds** for per-minute limits to reset.
5. **On resume**, run `checkpoint.py scan` first, then recall the recovery memory:

   ```bash
   python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/memory_ops.py recall "rate limit recovery" --domain ken --limit 3
   ```

## Atomic Commit Rules

- **Single file** per commit
- **Passing state** — file must be valid at commit time
- **Described** — commit message matches checkpoint summary
- **Never commit** half-edited functions or inconsistent state

## Token Conservation

1. Read a file once per session — store what you need in checkpoints
2. Edit precisely — targeted str_replace, not full-file rewrites
3. Don't verify by re-reading — reason about the change
4. One concern per session — log discovered issues for next session
5. Keep responses short — the context window is shared with skills

## End of Session

1. Write/update `HANDOFF.md` if work is incomplete (per the format in CLAUDE.md).
2. Encode the final checkpoint to cognitive memory (use `--protected` if it's foundational).
3. **Mark the session complete** so the next session doesn't flag it as abandoned:

   **Modern (keeper, with quality gate):**
   ```bash
   PYTHONPATH=/Volumes/1TB External/openclaw/workspace-main python3 -m keeper complete --family <name> \
     --summary "what shipped"
   ```
   The keeper `complete` runs validate strict-by-default — refuses if the state is too sparse for a useful resume. Add `--review` to also run the cognitive-review gate (see `keeper/README.md`). Bypass with `--force` for emergencies.

   **Legacy:**
   ```bash
   python3 /Volumes/1TB External/openclaw/workspace-main/tools/orchestrator/checkpoint.py complete --session "$SID"
   ```

4. Confirm all touched files are consistent.

## Pulse File Reference

**Modern (keeper):** state at `<repo>/.claude/state/families/<name>/family.json`. See `keeper/README.md` for the full schema.

**Legacy** (now a path that gets auto-migrated on first read):

Path: `<repo>/.claude/state/session-pulse.json` (read-only after migration; `session-pulse.json.migrated` archive).

```json
{
  "session_id": "sess-20260428T015432Z-ac3592",
  "started_at": "2026-04-28T01:54:32+00:00",
  "last_beat":  "2026-04-28T01:54:41+00:00",
  "beat_count": 2,
  "status":     "active",        // "active" | "complete"
  "last_action": "edited foo.py",
  "context":     "refactoring retry logic",
  "files_in_play": ["foo.py"],
  "at_risk":     ["foo.py", "bar.py"]
}
```

Stale threshold: **90 minutes** since `last_beat` with `status != "complete"` (was 30 — increased per orchestra critique to handle long lunches / code reviews / doc reads without false ghosts).
Stale archive: `<repo>/.claude/state/session-pulse-stale/<session-id>_<utc-timestamp>.json`.

## CLI Reference

**Modern (keeper):**

| Command | Purpose |
|---|---|
| `python -m keeper join --family X --goal "..."` | Acquire family lease + open state. |
| `python -m keeper beat --family X --action "..." [--files ...]` | Heartbeat + merge state. |
| `python -m keeper status [--family X]` | At-a-glance view. |
| `python -m keeper recover [--family X] [--json] [--brief]` | Resume oracle for a new shell. |
| `python -m keeper validate [--family X] [--strict]` | Quality score + 7 lint checks. |
| `python -m keeper review [--family X] [--live]` | Multi-persona cognitive critique. |
| `python -m keeper complete [--family X] [--review]` | Graceful end (strict by default). |
| `python -m keeper help` | Full usage. |

**Legacy shim** (preserved for backward compat; routes to keeper internally):

| Command | Purpose |
|---|---|
| `checkpoint.py new-id` | Generate a fresh session id. |
| `checkpoint.py beat --session ID --action TEXT [--context TEXT] [--files A B] [--json]` | Record a heartbeat; refreshes at-risk file list. |
| `checkpoint.py status [--json]` | Show current pulse + at-risk files. |
| `checkpoint.py scan [--stale-minutes N] [--json]` | If pulse is stale-and-not-complete, archive it and print recovery summary. |
| `checkpoint.py recover [--json]` | Print recovery summary for the latest pulse. |
| `checkpoint.py complete [--session ID] [--json]` | Mark current pulse complete. |
| `checkpoint.py migrate` | Idempotent one-shot of the auto-migration. |
