---
name: orchestrator-monitor
description: "Tracks API costs, response quality, and failure rates per model across the multi-LLM orchestrator. Makes usage data queryable."
version: 1.0.0
---

# Orchestrator Monitor

> Know what you're spending and what you're getting.

## Purpose

Tracks and reports on orchestrator usage: costs per model, costs per mode, failure rates, and quality patterns. Turns the cost_log in state/current.json into actionable intelligence.

## When to Fire

- On `/monitor` or `/costs` command
- When asking about API usage, spending, or model performance
- At session end (summarize session costs)

## Data Source

**State file:** `/home/user/ken/orchestrator/state/current.json`

Contains per-run:
- `consultations` — each model's response
- `cost_log` — per-model token usage and estimated cost
- `total_cost_usd` — total pipeline cost

## Reports

### Cost Report
```
## Orchestrator Costs — [period]

| Model | Calls | Tokens In | Tokens Out | Cost |
|-------|-------|-----------|------------|------|
| GPT-4o | [N] | [N] | [N] | $[X.XX] |
| Gemini | [N] | [N] | [N] | $[X.XX] |
| Grok-3 | [N] | [N] | [N] | $[X.XX] |
| **Total** | | | | **$[X.XX]** |

### By Mode
| Mode | Runs | Total Cost | Avg Cost/Run |
|------|------|-----------|-------------|
| sermon | [N] | $[X.XX] | $[X.XX] |
| sheep | [N] | $[X.XX] | $[X.XX] |
| cruising | [N] | $[X.XX] | $[X.XX] |
| recipe | [N] | $[X.XX] | $[X.XX] |
```

### Failure Report
```
## Model Failures — [period]
| Model | Failures | Last Failure | Error |
|-------|----------|-------------|-------|
```

### Quality Patterns
- Which model's suggestions get integrated most often?
- Which model's suggestions get discarded most often?
- Track via cognitive-memory: encode integration decisions

## Integration

- **cognitive-memory** — store cost trends and quality observations
- **consult** — individual consultation costs also tracked
- **orchestrate** — pipeline costs are the primary data source

---

*Soli Deo Gloria* — Steward resources wisely.
