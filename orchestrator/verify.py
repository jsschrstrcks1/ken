#!/usr/bin/env python3
"""
verify.py — Hallucination defense layer.

Extracts claims from model responses and routes them to the appropriate
verification backend based on claim type.

Claim types and routing:
  scripture   → ESV text verification (local or API)
  quote       → quote-map.md lookup
  theological → theological-map.md lookup
  livestock   → flock data lookup
  standards   → web standards doc lookup
  factual     → flagged for human review (no auto-verify)
"""

import os
import re

# Paths to verification sources (relative to Romans repo)
# These are resolved at runtime based on mode
ROMANS_CLAUDE_DIR = None  # Set by _find_romans_dir()
QUOTE_MAP = None
THEOLOGICAL_MAP = None


def _find_romans_dir():
    """Try to locate the Romans repo's .claude/ directory."""
    candidates = [
        os.path.expanduser("~/Romans/.claude"),
        os.path.expanduser("~/romans/.claude"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Romans", ".claude"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


def _load_map(filename):
    """Load a markdown map file and return its contents as a string."""
    romans_dir = _find_romans_dir()
    if not romans_dir:
        return None
    path = os.path.join(romans_dir, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def verify_claims(claims, mode="sermon"):
    """
    Verify a list of claims. Each claim is a dict with:
      {"type": "scripture|quote|theological|livestock|standards|factual",
       "claim": "the claim text",
       "source": "where it allegedly comes from"}

    Returns:
      {"verified": [...], "unverified": [...], "failed": [...]}
    """
    result = {"verified": [], "unverified": [], "failed": []}

    for claim in claims:
        claim_type = claim.get("type", "factual").lower()
        claim_text = claim.get("claim", "")
        source = claim.get("source", "")

        if claim_type == "scripture":
            status = _verify_scripture(claim_text, source)
        elif claim_type == "quote":
            status = _verify_quote(claim_text, source)
        elif claim_type == "theological":
            status = _verify_theological(claim_text, source)
        elif claim_type == "livestock":
            status = _verify_livestock(claim_text, source)
        elif claim_type == "standards":
            status = _verify_standards(claim_text, source)
        else:
            # Factual claims and unknown types → flag for human review
            status = "unverified"
            claim["verification_note"] = "Requires human review"

        result[status].append(claim)

    return result


def _verify_scripture(claim_text, source):
    """
    Verify a Scripture reference claim.

    Checks if the reference pattern is valid and looks up the claim
    in known verified sources. Full ESV API integration is Phase 4+.
    """
    # Basic reference pattern validation
    ref_pattern = r"(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|" \
                  r"1\s*Samuel|2\s*Samuel|1\s*Kings|2\s*Kings|1\s*Chronicles|2\s*Chronicles|" \
                  r"Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|" \
                  r"Song\s*of\s*Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|" \
                  r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|" \
                  r"Haggai|Zechariah|Malachi|" \
                  r"Matthew|Mark|Luke|John|Acts|Romans|1\s*Corinthians|2\s*Corinthians|" \
                  r"Galatians|Ephesians|Philippians|Colossians|" \
                  r"1\s*Thessalonians|2\s*Thessalonians|1\s*Timothy|2\s*Timothy|" \
                  r"Titus|Philemon|Hebrews|James|1\s*Peter|2\s*Peter|" \
                  r"1\s*John|2\s*John|3\s*John|Jude|Revelation)" \
                  r"\s+\d+[:\d\-,;\s]*"

    if not re.search(ref_pattern, source, re.IGNORECASE):
        return "failed"

    # Check theological-map for known verified references
    theo_map = _load_map("theological-map.md")
    if theo_map and source.lower() in theo_map.lower():
        return "verified"

    # Valid reference format but not locally verified
    return "unverified"


def _verify_quote(claim_text, source):
    """Verify an attributed quote against quote-map.md."""
    quote_map = _load_map("quote-map.md")
    if not quote_map:
        return "unverified"

    # Check if the source or a significant portion of the claim appears in quote-map
    if source and source.lower() in quote_map.lower():
        # Source found — check if claim text roughly matches
        claim_words = set(claim_text.lower().split())
        # If 60%+ of claim words appear near the source in the map, consider verified
        source_idx = quote_map.lower().find(source.lower())
        if source_idx >= 0:
            context = quote_map[max(0, source_idx - 500):source_idx + 500].lower()
            matches = sum(1 for w in claim_words if len(w) > 3 and w in context)
            if claim_words and matches / max(len(claim_words), 1) >= 0.6:
                return "verified"

    return "unverified"


def _verify_theological(claim_text, source):
    """Verify a theological claim against theological-map.md."""
    theo_map = _load_map("theological-map.md")
    if not theo_map:
        return "unverified"

    # Check if key terms from the claim appear in the theological map
    claim_lower = claim_text.lower()
    theo_lower = theo_map.lower()

    # Extract significant theological terms (4+ chars)
    terms = [w for w in claim_lower.split() if len(w) >= 4]
    if not terms:
        return "unverified"

    matches = sum(1 for t in terms if t in theo_lower)
    ratio = matches / len(terms)

    if ratio >= 0.7:
        return "verified"
    elif ratio >= 0.4:
        return "unverified"
    else:
        return "failed"


def _verify_livestock(claim_text, source):
    """
    Verify a livestock/flock data claim.
    Currently flags for review — full integration pending flock data format decision.
    """
    return "unverified"


def _verify_standards(claim_text, source):
    """
    Verify a web standards claim against InTheWake repo standards.
    Currently flags for review — full integration pending standards format.
    """
    return "unverified"
