#!/usr/bin/env python3
"""
memory_ops.py — Cross-repository cognitive memory system.

Operations: encode, consolidate, recall, extract, forget.
Memory is cognition, not storage — we keep what matters and let the rest go.

Directory structure:
    ~/.memory/
    ├── romans/        # Sermon writing, theology
    ├── sheep/         # Flock management, breeding
    ├── cruising/      # InTheWake website
    ├── recipes/       # Recipe content
    └── shared/        # Cross-domain knowledge

Each memory is a JSON file with:
    {
        "id": "unique-id",
        "created": "ISO timestamp",
        "domain": "romans|sheep|cruising|recipes|shared",
        "type": "insight|decision|pattern|fact|preference",
        "content": "The actual memory",
        "source": "Where this came from",
        "confidence": 0.0-1.0,
        "tags": [],
        "last_recalled": "ISO timestamp or null",
        "recall_count": 0
    }
"""

import glob
import json
import os
import time
import uuid

MEMORY_ROOT = os.path.expanduser("~/.memory")
DOMAINS = ["romans", "sheep", "cruising", "recipes", "shared"]


def _ensure_dirs():
    """Create the memory directory structure if it doesn't exist."""
    for domain in DOMAINS:
        os.makedirs(os.path.join(MEMORY_ROOT, domain), exist_ok=True)


def _memory_path(domain, memory_id):
    """Get the file path for a memory."""
    return os.path.join(MEMORY_ROOT, domain, f"{memory_id}.json")


def encode(content, domain="shared", memory_type="insight", source="", confidence=0.8, tags=None):
    """
    Encode a new memory. This is the 'write' operation.

    Args:
        content: The thing worth remembering
        domain: Which scope (romans, sheep, cruising, recipes, shared)
        memory_type: insight, decision, pattern, fact, preference
        source: Where this came from (session, model, document)
        confidence: How confident we are (0.0-1.0)
        tags: List of tags for recall

    Returns:
        The memory dict with its assigned ID
    """
    _ensure_dirs()

    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain '{domain}'. Use: {', '.join(DOMAINS)}")

    memory = {
        "id": str(uuid.uuid4())[:8],
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "domain": domain,
        "type": memory_type,
        "content": content,
        "source": source,
        "confidence": confidence,
        "tags": tags or [],
        "last_recalled": None,
        "recall_count": 0,
    }

    path = _memory_path(domain, memory["id"])
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

    return memory


def recall(query, domain=None, limit=10):
    """
    Recall memories matching a query string.

    Simple keyword matching against content and tags.
    Returns memories sorted by relevance (match count * confidence).

    Args:
        query: Search terms
        domain: Restrict to domain (None = search all)
        limit: Max results
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    query_terms = set(query.lower().split())
    scored = []

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    mem = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            # Score by keyword matches in content + tags
            searchable = (mem.get("content", "") + " " + " ".join(mem.get("tags", []))).lower()
            matches = sum(1 for t in query_terms if t in searchable)

            if matches > 0:
                score = matches * mem.get("confidence", 0.5)
                scored.append((score, mem, path))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, mem, path in scored[:limit]:
        # Update recall metadata
        mem["last_recalled"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        mem["recall_count"] = mem.get("recall_count", 0) + 1
        with open(path, "w") as f:
            json.dump(mem, f, indent=2)
        results.append(mem)

    return results


def consolidate(domain=None):
    """
    Consolidate memories — merge duplicates, decay low-confidence unused memories.

    This is the 'sleep' operation. Run periodically to keep memory clean.

    Returns summary of actions taken.
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    actions = {"decayed": 0, "removed": 0, "kept": 0}

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    mem = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            # Decay: reduce confidence of never-recalled memories over time
            if mem.get("recall_count", 0) == 0:
                mem["confidence"] = max(0.0, mem.get("confidence", 0.5) - 0.05)
                actions["decayed"] += 1

                # Remove memories that have decayed to zero
                if mem["confidence"] <= 0.0:
                    os.remove(path)
                    actions["removed"] += 1
                    continue

                with open(path, "w") as f:
                    json.dump(mem, f, indent=2)
            else:
                actions["kept"] += 1

    return actions


def extract(domain=None, memory_type=None, min_confidence=0.0):
    """
    Extract all memories matching criteria. Used for building context.

    Args:
        domain: Filter by domain
        memory_type: Filter by type (insight, decision, pattern, fact, preference)
        min_confidence: Minimum confidence threshold
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS
    results = []

    for d in domains:
        pattern = os.path.join(MEMORY_ROOT, d, "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    mem = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            if memory_type and mem.get("type") != memory_type:
                continue
            if mem.get("confidence", 0) < min_confidence:
                continue

            results.append(mem)

    # Sort by confidence descending, then by recall_count
    results.sort(key=lambda m: (m.get("confidence", 0), m.get("recall_count", 0)), reverse=True)
    return results


def forget(memory_id, domain=None):
    """
    Explicitly forget a memory by ID.

    Args:
        memory_id: The memory's ID
        domain: If known, speeds up lookup
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            os.remove(path)
            return {"forgotten": True, "id": memory_id, "domain": d}

    return {"forgotten": False, "id": memory_id, "reason": "Not found"}


# --- CLI interface ---

def main():
    """Simple CLI for testing memory operations."""
    import sys

    usage = """memory_ops.py — Cognitive memory system

Usage:
    python3 memory_ops.py encode <domain> <type> "content" [--tags tag1,tag2]
    python3 memory_ops.py recall "query" [--domain <domain>]
    python3 memory_ops.py extract [--domain <domain>] [--type <type>]
    python3 memory_ops.py consolidate [--domain <domain>]
    python3 memory_ops.py forget <id> [--domain <domain>]
"""

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "encode":
        if len(sys.argv) < 5:
            print("Usage: encode <domain> <type> \"content\"")
            sys.exit(1)
        domain = sys.argv[2]
        mtype = sys.argv[3]
        content = sys.argv[4]
        tags = []
        if "--tags" in sys.argv:
            idx = sys.argv.index("--tags")
            if idx + 1 < len(sys.argv):
                tags = sys.argv[idx + 1].split(",")
        mem = encode(content, domain=domain, memory_type=mtype, tags=tags)
        print(json.dumps(mem, indent=2))

    elif cmd == "recall":
        if len(sys.argv) < 3:
            print("Usage: recall \"query\"")
            sys.exit(1)
        query_str = sys.argv[2]
        domain = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            if idx + 1 < len(sys.argv):
                domain = sys.argv[idx + 1]
        results = recall(query_str, domain=domain)
        print(json.dumps(results, indent=2))

    elif cmd == "extract":
        domain = None
        mtype = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            if idx + 1 < len(sys.argv):
                domain = sys.argv[idx + 1]
        if "--type" in sys.argv:
            idx = sys.argv.index("--type")
            if idx + 1 < len(sys.argv):
                mtype = sys.argv[idx + 1]
        results = extract(domain=domain, memory_type=mtype)
        print(json.dumps(results, indent=2))

    elif cmd == "consolidate":
        domain = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            if idx + 1 < len(sys.argv):
                domain = sys.argv[idx + 1]
        result = consolidate(domain=domain)
        print(json.dumps(result, indent=2))

    elif cmd == "forget":
        if len(sys.argv) < 3:
            print("Usage: forget <id>")
            sys.exit(1)
        mid = sys.argv[2]
        domain = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            if idx + 1 < len(sys.argv):
                domain = sys.argv[idx + 1]
        result = forget(mid, domain=domain)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(usage)
        sys.exit(1)


if __name__ == "__main__":
    main()
