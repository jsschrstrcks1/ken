# HEARTBEAT.md — Periodic Check-in Tasks

## Cognitive Memory — Session Startup Recall

On the FIRST heartbeat of each session (or when the session feels fresh/new),
run memory recall to restore cross-session continuity:

```bash
HOME=/Users/kenbaker python3 "/Volumes/1TB External/openclaw/workspace-main/tools/memory_ops.py" recall "" --domain ken --limit 10
HOME=/Users/kenbaker python3 "/Volumes/1TB External/openclaw/workspace-main/tools/memory_ops.py" tree --domain ken
```

Then briefly summarize: open threads, recent decisions, low-confidence items.

## Rotating Periodic Checks (2-4x/day)

Track in `memory/heartbeat-state.json`:
- email — any urgent unread?
- calendar — upcoming events <24-48h?
- weather — relevant if Ken might go out?

## When to Reach Out

- Important email arrived
- Calendar event coming up (<2h)
- Something interesting found
- >8h since last contact

## When to Stay Quiet (HEARTBEAT_OK)

- Late night (23:00-08:00) unless urgent
- Human clearly busy
- Nothing new since last check
- Checked <30 min ago
