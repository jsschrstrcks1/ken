---
name: cognitive-memory
description: "Cross-repository cognitive memory system with semantic search. Persists knowledge across sessions using TF-IDF recall, memory versioning, knowledge graph edges, and confidence decay. Memory is cognition, not storage."
trigger:
  - keyword: [memory, remember, recall, forget, "what do we know", "last session", "previous session", "what was", "do you remember"]
  - intent: ["recalling past context", "storing new knowledge", "resolving contradictions", "session continuity"]
  - event: session_start
priority: high
version: 2.0.0
---

# Cognitive Memory System v2

> Memory as stewardship: what we remember shapes how we serve.

## What's New in v2

- **Semantic search**: TF-IDF + cosine similarity replaces keyword matching. "deworming resistance" finds "FAMACHA scoring" and "parasite resistance" even without shared words.
- **Memory versioning**: `update` creates a new version, preserves the original with `supersedes` chain.
- **Knowledge graph**: `link` creates bidirectional edges between related memories.
- **Duplicate detection**: `consolidate` flags memories with >80% similarity.
- **Recency boost**: Recent memories score higher. Old unrecalled memories decay.

## Overview

This skill provides persistent cognitive memory across Claude Code sessions. It is NOT a database — it is a reasoning layer that encodes selectively, consolidates contradictions, recalls semantically, and forgets intentionally.

**Memory store:** `~/.memory/DOMAIN/`
**Operations script:** `/home/user/ken/orchestrator/memory_ops.py`

## Session Start Protocol

At the beginning of every session, recall relevant memories:

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "" --domain ken --limit 10
python3 /home/user/ken/orchestrator/memory_ops.py tree --domain ken
```

Present a brief summary to the user:
- Recent changes and current state
- Open questions or low-confidence memories
- Any contradictions flagged but not yet resolved

## Seven Cognitive Operations

### 1. REMEMBER — Encode new knowledge

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode ken <type> "content" \
  --tags tag1,tag2 --related id1,id2
```

**Types:** insight, decision, pattern, fact, preference

**Importance → confidence mapping:**
- 0.9: Critical decisions, corrections, structural changes
- 0.7: Important observations, verified facts
- 0.5: General notes, routine work
- 0.3: Temporary states, minor observations

### 2. RECALL — Semantic search

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "natural language query" --domain ken --limit 10
```

Recall now uses TF-IDF semantic matching. You don't need exact keywords — conceptually related memories surface automatically. Each result includes a `_score` field.

**Trust but verify:** If a recalled memory has low confidence or a low score, say so. Don't present uncertain memories as facts.

### 3. UPDATE — Version a memory

```bash
python3 /home/user/ken/orchestrator/memory_ops.py update <id> "corrected content" --domain ken
```

Creates a new version. The old memory is preserved with reduced confidence and a `superseded_by` pointer. Use this when facts change — don't forget and re-encode, update.

### 4. LINK — Connect related memories

```bash
python3 /home/user/ken/orchestrator/memory_ops.py link <id_a> <id_b>
```

Creates a bidirectional edge. Use when you discover two memories are related — a breeding decision connects to a flock validation insight, a recipe correction connects to a transcription note.

### 5. CONSOLIDATE — Maintain memory health

```bash
python3 /home/user/ken/orchestrator/memory_ops.py consolidate --domain ken
```

Decays unrecalled memories, removes dead ones, and reports potential duplicates (>80% similarity). Run periodically or at session end.

### 6. TREE — See what we know

```bash
python3 /home/user/ken/orchestrator/memory_ops.py tree --domain ken
```

Shows memory count, types, edge connections, and version chains per domain.

### 7. FORGET — Intentional removal

```bash
python3 /home/user/ken/orchestrator/memory_ops.py forget <id> --domain ken
```

## What Memory Is NOT

- Memory does NOT replace primary data files in this repository
- Memory does NOT override primary sources
- Memory does NOT store raw data — it stores *conclusions about* data
- Memory does NOT act autonomously — you decide when to remember and recall

## Soli Deo Gloria

Careful, not clever. What we remember matters. What we forget matters too.

## Domain-Specific: Hub / Orchestrator (Ken)

### What to Encode
- **Orchestrator decisions**: Configuration changes, mode adjustments, adapter tuning
- **Cross-repo observations**: Patterns that span multiple repositories
- **API behavior**: Model response quirks, rate limits hit, cost patterns
- **Skill development**: What worked when building skills, patterns to reuse
- **Infrastructure changes**: Environment setup issues, dependency conflicts resolved

### Encoding Patterns

```bash
# After an orchestrator configuration change
python3 /home/user/ken/orchestrator/memory_ops.py encode ken decision \
  "Switched Gemini adapter from free to paid tier for recipe mode. Free tier was hitting rate limits on batch operations." \
  --tags orchestrator,gemini,rate-limit,recipe

# After a cross-repo observation
python3 /home/user/ken/orchestrator/memory_ops.py encode shared pattern \
  "All 4 recipe repos need validation hooks. Deployed to Grandmasrecipes/Grannysrecipes first, then MomsRecipes/Allrecipes." \
  --tags hooks,recipes,deployment
```

### What NOT to Encode
- API keys (never encode secrets)
- Full model responses (encode conclusions, not raw output)
- Things already in CLAUDE.md files across repos
