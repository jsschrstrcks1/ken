#!/usr/bin/env python3
"""
memory_ops.py — Cross-repository cognitive memory system (v2).

Upgrades from v1:
  - Semantic recall via TF-IDF + cosine similarity (pure Python, zero dependencies)
  - Memory versioning (update creates new version, preserves history)
  - Memory edges (link related memories into a knowledge graph)
  - Hybrid scoring: TF-IDF similarity * confidence * recency boost
  - Backward compatible with v1 memory files

Operations: encode, recall, consolidate, extract, forget, link, update, tree, stats
Memory is cognition, not storage — we keep what matters and let the rest go.

Directory structure:
    ~/.memory/
    ├── romans/        # Sermon writing, theology
    ├── sheep/         # Flock management, breeding
    ├── cruising/      # InTheWake website
    ├── recipes/       # Recipe content
    ├── ken/           # Hub / orchestrator knowledge
    ├── photography/   # Flickers of Majesty
    └── shared/        # Cross-domain knowledge

Each memory is a JSON file with:
    {
        "id": "unique-id",
        "created": "ISO timestamp",
        "updated": "ISO timestamp or null",
        "version": 1,
        "domain": "domain-name",
        "type": "insight|decision|pattern|fact|preference",
        "content": "The actual memory",
        "source": "Where this came from",
        "confidence": 0.0-1.0,
        "tags": [],
        "related_to": [],         # Memory IDs this connects to
        "supersedes": null,       # ID of the memory this replaced
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


def _memory_path(domain, memory_id):
    """Get the file path for a memory."""
    return os.path.join(MEMORY_ROOT, domain, f"{memory_id}.json")


def _load_all(domains=None):
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
    return memories


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ─────────────────────────────────────────────
# TF-IDF Semantic Search (pure Python)
# ─────────────────────────────────────────────

def _tokenize(text):
    """Simple tokenizer: lowercase, split on non-alpha, remove stopwords."""
    STOPWORDS = {
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
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def _build_tfidf(documents):
    """
    Build TF-IDF vectors for a list of documents.
    Returns (vocab, tfidf_matrix) where tfidf_matrix[i] is a dict {term: score}.
    """
    n_docs = len(documents)
    if n_docs == 0:
        return {}, []

    # Tokenize all documents
    doc_tokens = [_tokenize(doc) for doc in documents]

    # Build vocabulary and document frequency
    df = {}  # term -> number of documents containing it
    for tokens in doc_tokens:
        seen = set(tokens)
        for t in seen:
            df[t] = df.get(t, 0) + 1

    # Build TF-IDF for each document
    tfidf_matrix = []
    for tokens in doc_tokens:
        if not tokens:
            tfidf_matrix.append({})
            continue

        # Term frequency (normalized)
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        max_tf = max(tf.values())

        # TF-IDF
        tfidf = {}
        for t, count in tf.items():
            tf_norm = 0.5 + 0.5 * (count / max_tf)  # augmented TF
            idf = math.log((n_docs + 1) / (df.get(t, 0) + 1)) + 1  # smoothed IDF
            tfidf[t] = tf_norm * idf
        tfidf_matrix.append(tfidf)

    return df, tfidf_matrix


def _cosine_similarity(vec_a, vec_b):
    """Cosine similarity between two sparse vectors (dicts)."""
    if not vec_a or not vec_b:
        return 0.0

    # Dot product
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in vec_a if k in vec_b)
    if dot == 0:
        return 0.0

    # Magnitudes
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def _recency_boost(created_str, half_life_days=90):
    """
    Boost score based on recency. Memories decay over time.
    Half-life: score halves every `half_life_days` days.
    """
    try:
        created = time.mktime(time.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ"))
        age_days = (time.time() - created) / 86400
        return math.pow(0.5, age_days / half_life_days)
    except (ValueError, TypeError):
        return 0.5  # default for unparseable dates


# ─────────────────────────────────────────────
# Core Operations
# ─────────────────────────────────────────────

def encode(content, domain="shared", memory_type="insight", source="",
           confidence=0.8, tags=None, related_to=None):
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

    Returns:
        The memory dict with its assigned ID
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
        "last_recalled": None,
        "recall_count": 0,
    }

    path = _memory_path(domain, memory["id"])
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

    return memory


def update(memory_id, new_content, domain=None, confidence=None):
    """
    Update a memory by creating a new version. Preserves the original.

    The old memory gets a 'superseded_by' field and reduced confidence.
    The new memory gets a 'supersedes' field pointing to the original.

    Returns the new memory, or None if original not found.
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            with open(path) as f:
                old = json.load(f)

            # Mark old as superseded
            old["superseded_by"] = None  # will fill after creating new
            old["confidence"] = max(0.1, old.get("confidence", 0.5) * 0.5)

            # Create new version
            new_mem = {
                "id": str(uuid.uuid4())[:8],
                "created": old["created"],
                "updated": _now(),
                "version": old.get("version", 1) + 1,
                "domain": d,
                "type": old.get("type", "insight"),
                "content": new_content,
                "source": old.get("source", ""),
                "confidence": confidence if confidence is not None else old.get("confidence", 0.8),
                "tags": old.get("tags", []),
                "related_to": old.get("related_to", []),
                "supersedes": memory_id,
                "last_recalled": None,
                "recall_count": 0,
            }

            # Link old → new
            old["superseded_by"] = new_mem["id"]

            # Save both
            with open(path, "w") as f:
                json.dump(old, f, indent=2)

            new_path = _memory_path(d, new_mem["id"])
            with open(new_path, "w") as f:
                json.dump(new_mem, f, indent=2)

            return new_mem

    return None


def recall(query, domain=None, limit=10, min_score=0.05):
    """
    Recall memories using TF-IDF semantic search.

    Scores each memory by:
      similarity = cosine_similarity(query_tfidf, memory_tfidf)
      score = similarity * confidence * recency_boost

    Falls back to keyword matching for very short queries (1-2 words).

    Args:
        query: Natural language search
        domain: Restrict to domain (None = search all)
        limit: Max results
        min_score: Minimum score threshold
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    memories = _load_all(domains)

    if not memories:
        return []

    # Skip superseded memories (show only latest versions)
    active = [m for m in memories if "superseded_by" not in m or m.get("superseded_by") is None]
    if not active:
        active = memories  # fallback if all superseded somehow

    # Build corpus: query + all memory contents
    corpus = [query]
    for m in active:
        text = m.get("content", "") + " " + " ".join(m.get("tags", []))
        corpus.append(text)

    # Build TF-IDF
    _, tfidf_matrix = _build_tfidf(corpus)

    if not tfidf_matrix:
        return []

    query_vec = tfidf_matrix[0]
    scored = []

    for i, mem in enumerate(active):
        mem_vec = tfidf_matrix[i + 1]  # +1 because query is index 0
        similarity = _cosine_similarity(query_vec, mem_vec)

        if similarity <= 0:
            # Fallback: keyword matching for short queries
            query_terms = set(query.lower().split())
            searchable = (mem.get("content", "") + " " + " ".join(mem.get("tags", []))).lower()
            kw_matches = sum(1 for t in query_terms if t in searchable)
            if kw_matches > 0:
                similarity = 0.1 * kw_matches  # small boost for keyword hits
            else:
                continue

        confidence = mem.get("confidence", 0.5)
        recency = _recency_boost(mem.get("created", ""))
        score = similarity * confidence * (0.7 + 0.3 * recency)  # recency is 30% of weight

        if score >= min_score:
            scored.append((score, mem))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, mem in scored[:limit]:
        # Update recall metadata
        mem["last_recalled"] = _now()
        mem["recall_count"] = mem.get("recall_count", 0) + 1
        mem["_score"] = round(score, 4)
        path = mem.pop("_path", None)
        if path:
            with open(path, "w") as f:
                json.dump({k: v for k, v in mem.items() if k != "_score"}, f, indent=2)
        results.append(mem)

    return results


def link(id_a, id_b, domain=None):
    """
    Create a bidirectional edge between two memories.

    Args:
        id_a: First memory ID
        id_b: Second memory ID
        domain: If known, speeds up lookup

    Returns:
        dict with link status
    """
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

    # Add bidirectional links
    related_a = mem_a.get("related_to", [])
    related_b = mem_b.get("related_to", [])

    if id_b not in related_a:
        related_a.append(id_b)
        mem_a["related_to"] = related_a
        with open(path_a, "w") as f:
            json.dump(mem_a, f, indent=2)

    if id_a not in related_b:
        related_b.append(id_a)
        mem_b["related_to"] = related_b
        with open(path_b, "w") as f:
            json.dump(mem_b, f, indent=2)

    return {"linked": True, "a": id_a, "b": id_b}


def consolidate(domain=None):
    """
    Consolidate memories — decay unused, remove dead, report duplicates.

    Decay: reduce confidence of never-recalled memories by 0.05.
    Remove: delete memories that have decayed to zero.
    Duplicate detection: flag memories with >80% TF-IDF similarity.

    Returns summary of actions taken.
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    actions = {"decayed": 0, "removed": 0, "kept": 0, "potential_duplicates": []}

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        paths = glob.glob(pattern)
        active_memories = []

        for path in paths:
            try:
                with open(path) as f:
                    mem = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            # Skip superseded
            if mem.get("superseded_by"):
                continue

            # Decay never-recalled memories
            if mem.get("recall_count", 0) == 0:
                age_days = 0
                try:
                    created = time.mktime(time.strptime(mem.get("created", ""), "%Y-%m-%dT%H:%M:%SZ"))
                    age_days = (time.time() - created) / 86400
                except (ValueError, TypeError):
                    pass

                # Only decay if older than 7 days (give new memories a chance)
                if age_days > 7:
                    mem["confidence"] = max(0.0, mem.get("confidence", 0.5) - 0.05)
                    actions["decayed"] += 1

                    if mem["confidence"] <= 0.0:
                        os.remove(path)
                        actions["removed"] += 1
                        continue

                    with open(path, "w") as f:
                        json.dump(mem, f, indent=2)
            else:
                actions["kept"] += 1

            active_memories.append(mem)

        # Duplicate detection via TF-IDF
        if len(active_memories) >= 2:
            contents = [m.get("content", "") for m in active_memories]
            _, tfidf_matrix = _build_tfidf(contents)
            for i in range(len(active_memories)):
                for j in range(i + 1, len(active_memories)):
                    sim = _cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])
                    if sim > 0.80:
                        actions["potential_duplicates"].append({
                            "a": active_memories[i]["id"],
                            "b": active_memories[j]["id"],
                            "similarity": round(sim, 3),
                            "domain": d,
                        })

    return actions


def extract(domain=None, memory_type=None, min_confidence=0.0):
    """
    Extract all memories matching criteria. Used for building context.
    """
    memories = _load_all([domain] if domain else None)
    results = []

    for mem in memories:
        # Skip superseded
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

    return {"forgotten": False, "id": memory_id, "reason": "Not found"}


def tree(domain=None):
    """
    Show memory tree — count, types, and connections per domain.
    """
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

        if total > 0:
            result[d] = {
                "total": total,
                "active": total - superseded,
                "superseded": superseded,
                "linked": linked,
                "types": types,
            }

    return result


def stats():
    """Global memory statistics."""
    t = tree()
    total = sum(d["total"] for d in t.values())
    active = sum(d["active"] for d in t.values())
    linked = sum(d["linked"] for d in t.values())
    return {
        "total_memories": total,
        "active_memories": active,
        "superseded": total - active,
        "with_edges": linked,
        "domains": len(t),
        "per_domain": t,
    }


# ─────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────

def main():
    import sys

    usage = """memory_ops.py v2 — Cognitive memory with semantic search

Usage:
    python3 memory_ops.py encode <domain> <type> "content" [--tags t1,t2] [--related id1,id2]
    python3 memory_ops.py recall "query" [--domain <d>] [--limit N]
    python3 memory_ops.py update <id> "new content" [--domain <d>]
    python3 memory_ops.py link <id_a> <id_b> [--domain <d>]
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

    if cmd == "encode":
        if len(sys.argv) < 5:
            print("Usage: encode <domain> <type> \"content\"")
            sys.exit(1)
        tags_str = _get_flag("--tags", "")
        tags = tags_str.split(",") if tags_str else []
        related_str = _get_flag("--related", "")
        related = related_str.split(",") if related_str else []
        mem = encode(
            sys.argv[4], domain=sys.argv[2], memory_type=sys.argv[3],
            tags=tags, related_to=related,
        )
        print(json.dumps(mem, indent=2))

    elif cmd == "recall":
        if len(sys.argv) < 3:
            print("Usage: recall \"query\"")
            sys.exit(1)
        domain = _get_flag("--domain")
        limit = int(_get_flag("--limit", "10"))
        results = recall(sys.argv[2], domain=domain, limit=limit)
        print(json.dumps(results, indent=2))

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: update <id> \"new content\"")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = update(sys.argv[2], sys.argv[3], domain=domain)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({"error": "Memory not found"}, indent=2))

    elif cmd == "link":
        if len(sys.argv) < 4:
            print("Usage: link <id_a> <id_b>")
            sys.exit(1)
        domain = _get_flag("--domain")
        result = link(sys.argv[2], sys.argv[3], domain=domain)
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
