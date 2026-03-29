#!/usr/bin/env python3
"""
memory_ops.py — Cross-repository cognitive memory system (v3).

v3 upgrades (research-driven, zero external dependencies):
  1. Protected memories — foundational knowledge immune to decay
  2. Cross-domain recall — searches all domains by default, returns domain as metadata
  3. Graph centrality scoring — well-connected memories rank higher
  4. Memory summarization — consolidate merges high-similarity memories
  5. Tiered storage — active vs archive with automatic promotion/demotion

v2 features retained:
  - TF-IDF + cosine similarity semantic search (pure Python)
  - Memory versioning (update preserves history)
  - Bidirectional knowledge graph edges
  - Confidence decay for unrecalled memories
  - Backward compatible with v1/v2 memory files

Operations: encode, recall, update, link, protect, consolidate, archive,
            promote, extract, forget, tree, stats, neighbors

Memory is cognition, not storage — we keep what matters and let the rest go.

Directory structure:
    ~/.memory/
    ├── romans/        # Sermon writing, theology
    ├── sheep/         # Flock management, breeding
    ├── cruising/      # InTheWake website
    ├── recipes/       # Recipe content
    ├── ken/           # Hub / orchestrator knowledge
    ├── photography/   # Flickers of Majesty
    ├── shared/        # Cross-domain knowledge
    └── _archive/      # Tiered: summarized old memories

Each memory is a JSON file with:
    {
        "id": "unique-id",
        "created": "ISO timestamp",
        "updated": "ISO timestamp or null",
        "version": 1,
        "domain": "domain-name",
        "type": "insight|decision|pattern|fact|preference|summary",
        "content": "The actual memory",
        "source": "Where this came from",
        "confidence": 0.0-1.0,
        "tags": [],
        "related_to": [],         # Memory IDs this connects to
        "supersedes": null,       # ID of the memory this replaced
        "protected": false,       # v3: immune to decay
        "archived": false,        # v3: in archive tier
        "summarizes": [],         # v3: IDs of memories this summarizes
        "last_recalled": "ISO timestamp or null",
        "recall_count": 0
    }
"""

import glob
import json
import math
import os
import re
import time
import uuid

MEMORY_ROOT = os.path.expanduser("~/.memory")
ARCHIVE_DIR = os.path.join(MEMORY_ROOT, "_archive")
DOMAINS = [
    "romans", "sheep", "cruising", "recipes",
    "ken", "photography", "shared",
]

# ─────────────────────────────────────────────
# Infrastructure
# ─────────────────────────────────────────────

def _ensure_dirs():
    """Create the memory directory structure if it doesn't exist."""
    for domain in DOMAINS:
        os.makedirs(os.path.join(MEMORY_ROOT, domain), exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)


def _memory_path(domain, memory_id):
    return os.path.join(MEMORY_ROOT, domain, f"{memory_id}.json")


def _archive_path(memory_id):
    return os.path.join(ARCHIVE_DIR, f"{memory_id}.json")


def _load_all(domains=None, include_archive=False):
    """Load all memories from specified domains (or all)."""
    _ensure_dirs()
    domains = domains or DOMAINS
    memories = []
    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    mem = json.load(f)
                mem["_path"] = path
                memories.append(mem)
            except (json.JSONDecodeError, IOError):
                continue
    if include_archive:
        pattern = os.path.join(ARCHIVE_DIR, "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    mem = json.load(f)
                mem["_path"] = path
                memories.append(mem)
            except (json.JSONDecodeError, IOError):
                continue
    return memories


def _save_mem(mem, path):
    """Save memory to disk, stripping internal fields."""
    clean = {k: v for k, v in mem.items() if not k.startswith("_")}
    with open(path, "w") as f:
        json.dump(clean, f, indent=2)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _age_days(timestamp_str):
    """Return age in days from an ISO timestamp string."""
    try:
        created = time.mktime(time.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ"))
        return (time.time() - created) / 86400
    except (ValueError, TypeError):
        return 0


# ─────────────────────────────────────────────
# TF-IDF Semantic Search (pure Python)
# ─────────────────────────────────────────────

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "that", "this",
    "it", "its", "i", "me", "my", "we", "our", "you", "your", "he", "him",
    "his", "she", "her", "they", "them", "their", "what", "which", "who",
}


def _tokenize(text):
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _build_tfidf(documents):
    n_docs = len(documents)
    if n_docs == 0:
        return {}, []

    doc_tokens = [_tokenize(doc) for doc in documents]
    df = {}
    for tokens in doc_tokens:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    tfidf_matrix = []
    for tokens in doc_tokens:
        if not tokens:
            tfidf_matrix.append({})
            continue
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        max_tf = max(tf.values())
        tfidf = {}
        for t, count in tf.items():
            tf_norm = 0.5 + 0.5 * (count / max_tf)
            idf = math.log((n_docs + 1) / (df.get(t, 0) + 1)) + 1
            tfidf[t] = tf_norm * idf
        tfidf_matrix.append(tfidf)

    return df, tfidf_matrix


def _cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in vec_a if k in vec_b)
    if dot == 0:
        return 0.0
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _recency_boost(created_str, half_life_days=90):
    try:
        age = _age_days(created_str)
        return math.pow(0.5, age / half_life_days)
    except (ValueError, TypeError):
        return 0.5


def _graph_centrality(mem, all_memories):
    """
    Simple degree centrality: how many edges does this memory have?
    Normalized to [0, 1] relative to the most-connected memory.
    """
    edges = len(mem.get("related_to", []))
    if edges == 0:
        return 0.0
    max_edges = max(len(m.get("related_to", [])) for m in all_memories) if all_memories else 1
    return edges / max(max_edges, 1)


# ─────────────────────────────────────────────
# Core Operations
# ─────────────────────────────────────────────

def encode(content, domain="shared", memory_type="insight", source="",
           confidence=0.8, tags=None, related_to=None, protected=False):
    """
    Encode a new memory.

    Args:
        content: The thing worth remembering
        domain: Which scope
        memory_type: insight, decision, pattern, fact, preference
        source: Where this came from (session, user, notebook, document)
        confidence: How confident we are (0.0-1.0)
        tags: List of tags for recall
        related_to: List of memory IDs this connects to
        protected: If True, this memory is immune to decay (foundational knowledge)
    """
    _ensure_dirs()
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain '{domain}'. Use: {', '.join(DOMAINS)}")

    memory = {
        "id": str(uuid.uuid4())[:8],
        "created": _now(),
        "updated": None,
        "version": 1,
        "domain": domain,
        "type": memory_type,
        "content": content,
        "source": source,
        "confidence": confidence,
        "tags": tags or [],
        "related_to": related_to or [],
        "supersedes": None,
        "protected": protected,
        "archived": False,
        "summarizes": [],
        "last_recalled": None,
        "recall_count": 0,
    }

    path = _memory_path(domain, memory["id"])
    _save_mem(memory, path)
    return memory


def update(memory_id, new_content, domain=None, confidence=None):
    """Update a memory by creating a new version. Preserves the original."""
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            with open(path) as f:
                old = json.load(f)

            old["superseded_by"] = None
            old["confidence"] = max(0.1, old.get("confidence", 0.5) * 0.5)

            new_mem = {
                "id": str(uuid.uuid4())[:8],
                "created": old["created"],
                "updated": _now(),
                "version": old.get("version", 1) + 1,
                "domain": d,
                "type": old.get("type", "insight"),
                "content": new_content,
                "source": old.get("source", ""),
                "confidence": confidence if confidence is not None else 0.8,
                "tags": old.get("tags", []),
                "related_to": old.get("related_to", []),
                "supersedes": memory_id,
                "protected": old.get("protected", False),
                "archived": False,
                "summarizes": old.get("summarizes", []),
                "last_recalled": None,
                "recall_count": 0,
            }

            old["superseded_by"] = new_mem["id"]
            _save_mem(old, path)

            new_path = _memory_path(d, new_mem["id"])
            _save_mem(new_mem, new_path)
            return new_mem

    return None


def protect(memory_id, domain=None):
    """Mark a memory as protected — immune to decay. For foundational knowledge."""
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            with open(path) as f:
                mem = json.load(f)
            mem["protected"] = True
            _save_mem(mem, path)
            return {"protected": True, "id": memory_id, "domain": d}

    return {"protected": False, "id": memory_id, "reason": "Not found"}


def recall(query, domain=None, limit=10, min_score=0.05, include_archive=False):
    """
    Recall memories using TF-IDF semantic search.

    v3 changes:
      - Searches ALL domains by default (cross-domain recall)
      - Graph centrality boosts well-connected memories
      - Domain returned as metadata for context
      - Archive tier searchable with --include-archive

    Scoring:
      score = similarity * confidence * (0.7 + 0.15*recency + 0.15*centrality)
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    memories = _load_all(domains, include_archive=include_archive)

    if not memories:
        return []

    # Skip superseded memories (show only latest versions)
    active = [m for m in memories if not m.get("superseded_by")]
    if not active:
        active = memories

    # Build corpus: query + all memory contents
    corpus = [query]
    for m in active:
        text = m.get("content", "") + " " + " ".join(m.get("tags", []))
        if m.get("domain"):
            text += " " + m["domain"]  # domain name boosts domain-relevant queries
        corpus.append(text)

    _, tfidf_matrix = _build_tfidf(corpus)
    if not tfidf_matrix:
        return []

    query_vec = tfidf_matrix[0]
    scored = []

    for i, mem in enumerate(active):
        mem_vec = tfidf_matrix[i + 1]
        similarity = _cosine_similarity(query_vec, mem_vec)

        if similarity <= 0:
            # Fallback: keyword matching
            query_terms = set(query.lower().split())
            searchable = (mem.get("content", "") + " " + " ".join(mem.get("tags", []))).lower()
            kw_matches = sum(1 for t in query_terms if t in searchable)
            if kw_matches > 0:
                similarity = 0.1 * kw_matches
            else:
                continue

        confidence = mem.get("confidence", 0.5)
        recency = _recency_boost(mem.get("updated") or mem.get("created", ""))
        centrality = _graph_centrality(mem, active)

        # Composite score: similarity * confidence * (recency + centrality blend)
        score = similarity * confidence * (0.70 + 0.15 * recency + 0.15 * centrality)

        if score >= min_score:
            scored.append((score, mem))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, mem in scored[:limit]:
        mem["last_recalled"] = _now()
        mem["recall_count"] = mem.get("recall_count", 0) + 1
        mem["_score"] = round(score, 4)
        mem["_domain"] = mem.get("domain", "unknown")
        path = mem.get("_path")
        if path:
            _save_mem(mem, path)
        mem.pop("_path", None)
        results.append(mem)

    return results


def link(id_a, id_b, domain=None):
    """Create a bidirectional edge between two memories."""
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    mem_a = mem_b = None
    path_a = path_b = None

    for d in domains:
        pa = _memory_path(d, id_a)
        pb = _memory_path(d, id_b)
        if os.path.exists(pa) and mem_a is None:
            with open(pa) as f:
                mem_a = json.load(f)
            path_a = pa
        if os.path.exists(pb) and mem_b is None:
            with open(pb) as f:
                mem_b = json.load(f)
            path_b = pb

    if not mem_a:
        return {"linked": False, "reason": f"Memory {id_a} not found"}
    if not mem_b:
        return {"linked": False, "reason": f"Memory {id_b} not found"}

    related_a = mem_a.get("related_to", [])
    related_b = mem_b.get("related_to", [])

    if id_b not in related_a:
        related_a.append(id_b)
        mem_a["related_to"] = related_a
        _save_mem(mem_a, path_a)

    if id_a not in related_b:
        related_b.append(id_a)
        mem_b["related_to"] = related_b
        _save_mem(mem_b, path_b)

    return {"linked": True, "a": id_a, "b": id_b,
            "a_edges": len(related_a), "b_edges": len(related_b)}


def neighbors(memory_id, domain=None, depth=1):
    """
    Get all memories connected to a given memory (graph traversal).
    depth=1: direct neighbors. depth=2: neighbors of neighbors.
    """
    _ensure_dirs()
    all_mems = _load_all([domain] if domain else None)
    by_id = {}
    for m in all_mems:
        by_id[m["id"]] = m

    if memory_id not in by_id:
        return {"error": f"Memory {memory_id} not found"}

    visited = {memory_id}
    found = set()

    frontier = set()
    source_mem = by_id.get(memory_id)
    if source_mem:
        for rel_id in source_mem.get("related_to", []):
            frontier.add(rel_id)
            found.add(rel_id)

    for _ in range(depth - 1):
        next_frontier = set()
        for mid in frontier:
            if mid in visited:
                continue
            visited.add(mid)
            mem = by_id.get(mid)
            if mem:
                for rel_id in mem.get("related_to", []):
                    if rel_id not in visited and rel_id not in found:
                        next_frontier.add(rel_id)
                        found.add(rel_id)
        frontier = next_frontier
    result = []
    for mid in found:
        mem = by_id.get(mid)
        if mem:
            clean = {k: v for k, v in mem.items() if not k.startswith("_")}
            result.append(clean)

    return {"source": memory_id, "depth": depth, "neighbors": result}


def archive(memory_id, domain=None):
    """
    Move a memory to the archive tier. Archived memories are:
    - Excluded from default recall (unless --include-archive)
    - Preserved for history and graph integrity
    - Never decayed further
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            with open(path) as f:
                mem = json.load(f)
            mem["archived"] = True
            mem["archived_from"] = d
            mem["archived_at"] = _now()

            # Move to archive directory
            dest = _archive_path(memory_id)
            _save_mem(mem, dest)
            os.remove(path)
            return {"archived": True, "id": memory_id, "from": d}

    return {"archived": False, "id": memory_id, "reason": "Not found"}


def promote(memory_id):
    """
    Promote an archived memory back to its original domain.
    """
    _ensure_dirs()
    path = _archive_path(memory_id)
    if not os.path.exists(path):
        return {"promoted": False, "id": memory_id, "reason": "Not in archive"}

    with open(path) as f:
        mem = json.load(f)

    domain = mem.pop("archived_from", "shared")
    mem.pop("archived_at", None)
    mem["archived"] = False

    dest = _memory_path(domain, memory_id)
    _save_mem(mem, dest)
    os.remove(path)
    return {"promoted": True, "id": memory_id, "to": domain}


def consolidate(domain=None):
    """
    Consolidate memories — v3 enhanced:

    1. Decay: reduce confidence of unrecalled, unprotected memories (>7 days old)
    2. Remove: delete memories decayed to zero
    3. Protect connected: auto-protect memories with 3+ edges (high centrality)
    4. Summarize: merge memories with >80% similarity into a summary
    5. Auto-archive: move old (>180 days), low-confidence (<0.3), unprotected memories
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    actions = {
        "decayed": 0, "removed": 0, "kept": 0,
        "auto_protected": 0, "summarized": 0, "auto_archived": 0,
        "potential_duplicates": [],
    }

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        paths = glob.glob(pattern)
        active_memories = []

        for path in paths:
            try:
                with open(path) as f:
                    mem = json.load(f)
                mem["_path"] = path
            except (json.JSONDecodeError, IOError):
                continue

            if mem.get("superseded_by"):
                continue

            # Auto-protect well-connected memories (3+ edges)
            if len(mem.get("related_to", [])) >= 3 and not mem.get("protected"):
                mem["protected"] = True
                _save_mem(mem, path)
                actions["auto_protected"] += 1

            # Decay: only unrecalled, unprotected, >7 days old
            if (mem.get("recall_count", 0) == 0
                    and not mem.get("protected", False)
                    and _age_days(mem.get("created", "")) > 7):

                mem["confidence"] = max(0.0, mem.get("confidence", 0.5) - 0.05)
                actions["decayed"] += 1

                if mem["confidence"] <= 0.0:
                    os.remove(path)
                    actions["removed"] += 1
                    continue

                _save_mem(mem, path)
            else:
                actions["kept"] += 1

            # Auto-archive: old, low-confidence, unprotected
            if (not mem.get("protected", False)
                    and mem.get("confidence", 1.0) < 0.3
                    and _age_days(mem.get("created", "")) > 180):
                mem_id = mem["id"]
                mem["archived"] = True
                mem["archived_from"] = d
                mem["archived_at"] = _now()
                dest = _archive_path(mem_id)
                _save_mem(mem, dest)
                os.remove(path)
                actions["auto_archived"] += 1
                continue

            active_memories.append(mem)

        # Duplicate detection + summarization
        if len(active_memories) >= 2:
            contents = [m.get("content", "") for m in active_memories]
            _, tfidf_matrix = _build_tfidf(contents)
            merged = set()

            for i in range(len(active_memories)):
                if active_memories[i]["id"] in merged:
                    continue
                for j in range(i + 1, len(active_memories)):
                    if active_memories[j]["id"] in merged:
                        continue
                    sim = _cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])
                    if sim > 0.85:
                        # Auto-merge: keep the higher-confidence one, archive the other
                        a = active_memories[i]
                        b = active_memories[j]
                        keep = a if a.get("confidence", 0) >= b.get("confidence", 0) else b
                        discard = b if keep is a else a

                        # Add tags from discarded to kept
                        merged_tags = list(set(keep.get("tags", []) + discard.get("tags", [])))
                        keep["tags"] = merged_tags
                        keep["related_to"] = list(set(
                            keep.get("related_to", []) + discard.get("related_to", [])
                        ))
                        keep["summarizes"] = keep.get("summarizes", []) + [discard["id"]]
                        _save_mem(keep, keep["_path"])

                        # Archive the discarded one
                        discard["archived"] = True
                        discard["archived_from"] = d
                        discard["archived_at"] = _now()
                        discard["merged_into"] = keep["id"]
                        _save_mem(discard, _archive_path(discard["id"]))
                        if os.path.exists(discard["_path"]):
                            os.remove(discard["_path"])

                        merged.add(discard["id"])
                        actions["summarized"] += 1

                    elif sim > 0.70:
                        actions["potential_duplicates"].append({
                            "a": active_memories[i]["id"],
                            "b": active_memories[j]["id"],
                            "similarity": round(sim, 3),
                            "domain": d,
                        })

    return actions


def extract(domain=None, memory_type=None, min_confidence=0.0):
    """Extract all active memories matching criteria."""
    memories = _load_all([domain] if domain else None)
    results = []
    for mem in memories:
        if mem.get("superseded_by"):
            continue
        if memory_type and mem.get("type") != memory_type:
            continue
        if mem.get("confidence", 0) < min_confidence:
            continue
        mem.pop("_path", None)
        results.append(mem)
    results.sort(key=lambda m: (m.get("confidence", 0), m.get("recall_count", 0)), reverse=True)
    return results


def forget(memory_id, domain=None):
    """Explicitly forget a memory by ID."""
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            os.remove(path)
            return {"forgotten": True, "id": memory_id, "domain": d}

    # Also check archive
    path = _archive_path(memory_id)
    if os.path.exists(path):
        os.remove(path)
        return {"forgotten": True, "id": memory_id, "domain": "_archive"}

    return {"forgotten": False, "id": memory_id, "reason": "Not found"}


def tree(domain=None):
    """Show memory tree — count, types, connections, and tier info per domain."""
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    result = {}

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        paths = glob.glob(pattern)
        types = {}
        total = 0
        linked = 0
        superseded = 0
        protected_count = 0

        for path in paths:
            try:
                with open(path) as f:
                    mem = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            total += 1
            t = mem.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
            if mem.get("related_to"):
                linked += 1
            if mem.get("superseded_by"):
                superseded += 1
            if mem.get("protected"):
                protected_count += 1

        if total > 0:
            result[d] = {
                "total": total,
                "active": total - superseded,
                "superseded": superseded,
                "linked": linked,
                "protected": protected_count,
                "types": types,
            }

    # Archive stats
    archive_count = len(glob.glob(os.path.join(ARCHIVE_DIR, "*.json")))
    if archive_count > 0:
        result["_archive"] = {"total": archive_count}

    return result


def stats():
    """Global memory statistics."""
    t = tree()
    archive_total = t.pop("_archive", {}).get("total", 0)
    total = sum(d["total"] for d in t.values())
    active = sum(d["active"] for d in t.values())
    linked = sum(d["linked"] for d in t.values())
    protected_total = sum(d.get("protected", 0) for d in t.values())
    return {
        "total_memories": total,
        "active_memories": active,
        "superseded": total - active,
        "with_edges": linked,
        "protected": protected_total,
        "archived": archive_total,
        "domains": len(t),
        "per_domain": t,
    }


# ─────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────

def main():
    import sys

    usage = """memory_ops.py v3 — Cognitive memory with semantic search, protection, and tiered storage

Usage:
    python3 memory_ops.py encode <domain> <type> "content" [--tags t1,t2] [--related id1,id2] [--protected]
    python3 memory_ops.py recall "query" [--domain <d>] [--limit N] [--include-archive]
    python3 memory_ops.py update <id> "new content" [--domain <d>]
    python3 memory_ops.py link <id_a> <id_b> [--domain <d>]
    python3 memory_ops.py protect <id> [--domain <d>]
    python3 memory_ops.py neighbors <id> [--domain <d>] [--depth N]
    python3 memory_ops.py archive <id> [--domain <d>]
    python3 memory_ops.py promote <id>
    python3 memory_ops.py extract [--domain <d>] [--type <t>] [--min-confidence 0.5]
    python3 memory_ops.py consolidate [--domain <d>]
    python3 memory_ops.py forget <id> [--domain <d>]
    python3 memory_ops.py tree [--domain <d>]
    python3 memory_ops.py stats
"""

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    cmd = sys.argv[1]

    def _get_flag(flag, default=None):
        if flag in sys.argv:
            idx = sys.argv.index(flag)
            if idx + 1 < len(sys.argv):
                return sys.argv[idx + 1]
        return default

    def _has_flag(flag):
        return flag in sys.argv

    if cmd == "encode":
        if len(sys.argv) < 5:
            print("Usage: encode <domain> <type> \"content\"")
            sys.exit(1)
        tags_str = _get_flag("--tags", "")
        tags = tags_str.split(",") if tags_str else []
        related_str = _get_flag("--related", "")
        related = related_str.split(",") if related_str else []
        is_protected = _has_flag("--protected")
        mem = encode(
            sys.argv[4], domain=sys.argv[2], memory_type=sys.argv[3],
            tags=tags, related_to=related, protected=is_protected,
        )
        print(json.dumps(mem, indent=2))

    elif cmd == "recall":
        if len(sys.argv) < 3:
            print("Usage: recall \"query\"")
            sys.exit(1)
        domain = _get_flag("--domain")
        limit = int(_get_flag("--limit", "10"))
        inc_archive = _has_flag("--include-archive")
        results = recall(sys.argv[2], domain=domain, limit=limit, include_archive=inc_archive)
        print(json.dumps(results, indent=2))

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: update <id> \"new content\"")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = update(sys.argv[2], sys.argv[3], domain=domain)
        print(json.dumps(result or {"error": "Memory not found"}, indent=2))

    elif cmd == "link":
        if len(sys.argv) < 4:
            print("Usage: link <id_a> <id_b>")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = link(sys.argv[2], sys.argv[3], domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "protect":
        if len(sys.argv) < 3:
            print("Usage: protect <id>")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = protect(sys.argv[2], domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "neighbors":
        if len(sys.argv) < 3:
            print("Usage: neighbors <id>")
            sys.exit(1)
        domain = _get_flag("--domain")
        depth = int(_get_flag("--depth", "1"))
        result = neighbors(sys.argv[2], domain=domain, depth=depth)
        print(json.dumps(result, indent=2))

    elif cmd == "archive":
        if len(sys.argv) < 3:
            print("Usage: archive <id>")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = archive(sys.argv[2], domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "promote":
        if len(sys.argv) < 3:
            print("Usage: promote <id>")
            sys.exit(1)
        result = promote(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "extract":
        domain = _get_flag("--domain")
        mtype = _get_flag("--type")
        min_conf = float(_get_flag("--min-confidence", "0.0"))
        results = extract(domain=domain, memory_type=mtype, min_confidence=min_conf)
        print(json.dumps(results, indent=2))

    elif cmd == "consolidate":
        domain = _get_flag("--domain")
        result = consolidate(domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "forget":
        if len(sys.argv) < 3:
            print("Usage: forget <id>")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = forget(sys.argv[2], domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "tree":
        domain = _get_flag("--domain")
        result = tree(domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "stats":
        result = stats()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(usage)
        sys.exit(1)


if __name__ == "__main__":
    main()
