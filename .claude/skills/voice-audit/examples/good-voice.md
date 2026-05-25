# Good Voice — example passage

Excerpted from a hypothetical ken `HANDOFF.md`. Utility-prose voice: terse, specific, command-and-path exact, no marketing or sermon overlay.

---

## What Was Done

- Migrated 26 manatee tabs to the new sheet structure. Sheet ID `1AbC...XyZ`. Apps Script timed out on tab 18; resumed via `keeper checkpoint manatee --tab 19`.
- Patched `orchestrator/adapters/gemini.py:84` to use `google-genai` (was `google-generativeai`). Tests pass.

## What Still Needs Doing

- Tabs 22–26 are blocked on a column-name disagreement between `flock-manager-schema.md` and the live source. Pick one. The schema doc is older; the live source has the column names actually in use.

## How to Resume

```
cd /home/user/ken && python -m keeper status manatee
```

---

Why this passes voice-audit:

- Every claim has a file path, command, sheet ID, or line number.
- No mantra phrases ("we're building," "the right way," "memory is infrastructure").
- The blocker is named and the resolution path is concrete.
- No hedging stack ("might possibly potentially").
- Reads cold — a session that opens this file with no prior context can act.
