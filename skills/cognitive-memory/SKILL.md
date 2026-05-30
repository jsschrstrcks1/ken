---
name: cognitive-memory
description: "Cross-session cognitive memory system with semantic search. Persists knowledge across sessions using TF-IDF recall, memory versioning, knowledge graph edges, and confidence decay. Use when the user says 'remember this', 'what do you know about X', 'last session', 'previous session', 'do you remember', 'don't forget', or when starting a new session (session startup). Also fires when storing insights, decisions, patterns, facts, or preferences worth keeping across sessions."
---

# Cognitive Memory System v3

Memory as stewardship: what we remember shapes how we serve. *Soli Deo Gloria.*

## Session Startup — Do This Every Time

At the start of every session, recall recent memories to restore continuity:

```bash
python3 ~/workspace/tools/memory_ops.py recall "" --domain ken --limit 10
python3 ~/workspace/tools/memory_ops.py tree --domain ken
```

Briefly summarize to Ken:
- What's in active memory (open threads, recent decisions)
- Any low-confidence items that need verification
- Any contradictions flagged but unresolved

**If nothing comes back:** memory is empty or this is a fresh domain. That's fine — start encoding now.

## The Script

All operations go through:
```
python3 ~/workspace/tools/memory_ops.py <operation> [args]
```

Or using the full absolute path:
```
python3 /Volumes/1TB External/openclaw/workspace-main/tools/memory_ops.py <operation> [args]
```

Memory store: `~/.memory/<domain>/`

## The Seven Operations

### 1. REMEMBER — Encode new knowledge

```bash
python3 ~/workspace/tools/memory_ops.py encode ken <type> "content" \
  --tags tag1,tag2
```

Types: `insight`, `decision`, `pattern`, `fact`, `preference`

Confidence guide:
- `0.9` — Critical decisions, corrections, structural changes
- `0.7` — Important observations, verified facts  
- `0.5` — General notes, routine work
- `0.3` — Temporary states, minor observations

When Ken says "remember this" or "don't forget" → encode immediately.

### 2. RECALL — Semantic search (TF-IDF, not exact match)

```bash
python3 ~/workspace/tools/memory_ops.py recall "natural language query" --domain ken --limit 10
```

Cross-domain search (searches all domains by default — omit `--domain` to cast wide):
```bash
python3 ~/workspace/tools/memory_ops.py recall "sheep breeding"
```

Each result has a `_score`. Low score or low confidence → say so. Don't present uncertain memories as facts.

### 3. UPDATE — Version a memory when facts change

```bash
python3 ~/workspace/tools/memory_ops.py update <id> "corrected content" --domain ken
```

Old version preserved with `superseded_by` pointer. Never re-encode from scratch — update.

### 4. LINK — Connect related memories

```bash
python3 ~/workspace/tools/memory_ops.py link <id_a> <id_b>
```

Bidirectional. Use when two memories are causally or contextually related.

### 5. CONSOLIDATE — Memory health (run periodically, e.g. end of session)

```bash
python3 ~/workspace/tools/memory_ops.py consolidate --domain ken
```

Decays unrecalled memories, auto-merges near-duplicates (>85% similarity), auto-archives old/cold items, auto-protects well-connected nodes (3+ edges).

### 6. TREE — Quick status view

```bash
python3 ~/workspace/tools/memory_ops.py tree --domain ken
```

### 7. FORGET — Intentional removal

```bash
python3 ~/workspace/tools/memory_ops.py forget <id> --domain ken
```

## Protected Memories

Use `--protected` to mark memories immune to decay:

```bash
python3 ~/workspace/tools/memory_ops.py encode ken fact "content" --protected
```

Protect an existing memory:
```bash
python3 ~/workspace/tools/memory_ops.py protect <id> --domain ken
```

Use for: vocabulary conventions, architectural decisions downstream work assumes, core identity facts.

## Domains

| Domain | Use for |
|--------|---------|
| `ken` | Hub / orchestrator / cross-project knowledge |
| `romans` | Sermon writing, theology, pastoral work |
| `sheep` | Manatee Creek flock management, breeding, records |
| `cruising` | InTheWake website content, protocols |
| `recipes` | Recipe content, transcription notes |
| `photography` | Flickers of Majesty, photo metadata |
| `shared` | Cross-domain patterns |

## What Memory Is NOT

- Not a replacement for primary data files (sheep records, sermon manuscripts, etc.)
- Not a secret store (never encode API keys, passwords, congregation PII)
- Not raw data — encode *conclusions* about data, not the data itself
- Not autonomous — you decide when to encode and recall

## Encoding Patterns

```bash
# After a project decision
python3 ~/workspace/tools/memory_ops.py encode ken decision \
  "Switched InTheWake ship pages to ICP-2 protocol. Old ITW-Lite deprecated as of 2026-05." \
  --tags inthewave,protocol,icp2

# After a flock observation
python3 ~/workspace/tools/memory_ops.py encode sheep fact \
  "Angus (new ram, 50% Katahdin/25% Dorper/25% Awassi) replaced NoriSon/Eclipse sold 2026-04-26." \
  --tags ram,acquisition,breeding

# Session intent at start
python3 ~/workspace/tools/memory_ops.py encode ken insight \
  "Session intent: fixing P9 Carnival ship pages. Target: InTheWake/ships/carnival/. Expected: head images updated." \
  --tags session,intent
```

## End of Session

Encode a summary of what happened:
```bash
python3 ~/workspace/tools/memory_ops.py encode ken insight \
  "Session [date]: [what was accomplished]. Open: [what's left]. Risks: [any]." \
  --tags session,summary
```

Then consolidate:
```bash
python3 ~/workspace/tools/memory_ops.py consolidate --domain ken
```
