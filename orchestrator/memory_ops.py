#!/usr/bin/env python3
"""
memory_ops.py — Cross-repository cognitive memory system (v3).

v3 upgrades (research-driven, zero external dependencies):
  1. Protected memories — foundational knowledge immune to decay
  2. Cross-domain recall — searches all domains by default, returns domain as metadata
  3. Graph centrality scoring — well-connected memories rank higher
  4. Memory summarization — consolidate merges high-similarity memories
  5. Tiered storage — active vs archive with automatic promotion/demotion

v3.1 instincts tier (continuous-learning-v2 Slice 1, opt-in via env var):
  6. Instinct candidates — extract_instinct_candidates() surfaces high-confidence
     frequently-recalled memories that look like reusable patterns. Read-only.
  7. Explicit promotion — promote_to_instinct() / demote_from_instinct() flip a
     single memory's is_instinct flag. No bulk, no auto-promotion. Requires
     MEMORY_LEARNING_ENABLED=true; otherwise both ops are no-ops returning
     {"enabled": false}. Memories stay in their original domain — no parallel
     namespace.
  Future slices (not in v3.1): session hooks, PreToolUse/PostToolUse capture,
  auto-promotion thresholds. Each its own decision.

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

MEMORY_ROOT_ENV = "MEMORY_ROOT"


def _resolve_memory_root() -> str:
    """Return the active MEMORY_ROOT path.

    Priority:
      1. ``MEMORY_ROOT`` env var (operator override; honored verbatim, with
         ``~`` expansion).
      2. ``<sibling>/open-claw-stuff/.memory/`` — when this module lives at
         ``<parent>/ken/orchestrator/memory_ops.py`` and a sibling
         ``open-claw-stuff/`` exists. This is the canonical persistent
         location: git-tracked, survives container teardown via clone/pull.
      3. ``~/.memory/`` — legacy fallback. **EPHEMERAL** in web containers
         (each session destroys it). Kept only so CLI/desktop installs that
         lack the sibling repo still work.

    The resolution is one-shot at module import; tests override via
    ``memory_ops.MEMORY_ROOT = "..."`` in setUp as before.
    """
    env = os.environ.get(MEMORY_ROOT_ENV)
    if env:
        return os.path.expanduser(env)
    here = os.path.dirname(os.path.abspath(__file__))      # .../orchestrator
    ken_repo = os.path.dirname(here)                        # .../ken
    parent = os.path.dirname(ken_repo)                      # ...
    sibling = os.path.join(parent, "open-claw-stuff", ".memory")
    if os.path.isdir(os.path.dirname(sibling)):
        # open-claw-stuff/ exists as a sibling repo. Use it.
        return sibling
    return os.path.expanduser("~/.memory")


MEMORY_ROOT = _resolve_memory_root()
ARCHIVE_DIR = os.path.join(MEMORY_ROOT, "_archive")
DOMAINS = [
    "romans", "sheep", "cruising", "recipes",
    "ken", "photography", "shared", "personal",
]

# v3.1 continuous-learning-v2 feature flag (Slice 1).
# Off by default — extract_instinct_candidates / promote_to_instinct /
# demote_from_instinct all return {"enabled": false} no-ops until this is
# set. Set MEMORY_LEARNING_ENABLED=true in the environment to enable.
# Read at call time (not at import) so tests can flip it via monkey-patch
# or os.environ without re-importing the module.
def _learning_enabled():
    return os.environ.get("MEMORY_LEARNING_ENABLED", "false").lower() == "true"


# ─────────────────────────────────────────────
# v5 Doctrine layer — profile, exception, invariants (Slice 0)
# ─────────────────────────────────────────────
# Slice 0 of the continuous-learning-v2 plan. See
# CONTINUOUS_LEARNING_PLAN.md + CONTINUOUS_LEARNING_DOCTRINE.md.
#
# 9 invariants shipped here are the doctrine made into code. Each
# raises CarefulNotCleverError (a discipline boundary, not a generic
# bug). They are called from EVERY public mutation function in
# subsequent slices; the CI gate test in tests/test_memory_ops.py
# enforces that contract via AST walk.
#
# Nothing in this block has external side effects; everything is
# feature-flag / profile gated and additive to the existing surface.

class CarefulNotCleverError(Exception):
    """Discipline boundary crossed, not a generic bug. Surface to
    operator; do not silently retry or downgrade. Catching this and
    swallowing it via `except: pass` is itself a doctrine violation —
    see CONTINUOUS_LEARNING_DOCTRINE.md."""


# Profile is read at call time (not import) so tests + emergency
# reconfiguration can flip via os.environ without re-importing.
def _learning_profile():
    """Return active operating profile. Valid values:
        'single-operator-local' (default) — sole-human household
        'multi-operator-shared'           — team/enterprise/shared FS
    Any other value falls back to single-operator-local with no warning;
    this field is operator-controlled configuration, not security policy."""
    return os.environ.get(
        "MEMORY_LEARNING_PROFILE", "single-operator-local"
    ).lower()


# Rate-limit state. Per (operation, key) tuple → list of recent timestamps.
# Cleared lazily by _assert_rate_limit. Per-process; sessions are short
# enough that this doesn't need persistence.
_rate_buckets = {}
_rate_baselines = {}  # historical 95th percentile per (operation, key)


def _dynamic_threshold(operation, key):
    """Per Grok R3: 95th percentile + 20% based on historical baseline.
    Falls back to 60/min during first session before baseline exists."""
    baseline = _rate_baselines.get((operation, key))
    if baseline is None:
        return 60
    return max(60, int(baseline * 1.20))


# Invariant 1: Panic check (MUST be first executable statement of every
# public learning function — CI gate will enforce position).
def _assert_panic_check():
    """Refuse to proceed if MEMORY_LEARNING_PANIC_DISABLE_ALL=true.
    Takes precedence over every other flag and profile."""
    if os.environ.get("MEMORY_LEARNING_PANIC_DISABLE_ALL",
                      "").lower() == "true":
        raise CarefulNotCleverError(
            "panic disable active — all learning operations halted"
        )


# Invariant 2: No silent skip. Surface as INFO finding, not silent drop.
def _assert_no_silent_skip(reason, count):
    """Refuse to silently skip > 0 items. Caller must surface as INFO
    findings instead. count == 0 is the success path (no-op)."""
    if count > 0:
        raise CarefulNotCleverError(
            f"silent skip of {count} items: {reason}. "
            f"Surface as INFO findings, not silent drop."
        )


# Invariant 3: Evidence present. No bare-pattern candidates.
def _assert_evidence_present(candidate):
    """Every candidate must carry observations + session_ids that
    produced it. Bare-pattern candidates cannot be audited and are
    forbidden."""
    evidence = candidate.get("evidence", {})
    if not evidence.get("observations"):
        raise CarefulNotCleverError(
            f"candidate {candidate.get('id', '?')} has no evidence trail"
        )


# Invariant 4: Single-id mutation contract.
def _assert_single_id(arg):
    """Refuse list/tuple/set arguments to single-id APIs. The structural
    block holds regardless of profile."""
    if isinstance(arg, (list, tuple, set)):
        raise CarefulNotCleverError(
            f"single-id API received {type(arg).__name__}; "
            f"bulk mutation forbidden by doctrine"
        )


# Invariant 5: Safety-guard compliance.
def _assert_safety_guard_compliant(operation, target, force=False):
    """Destructive operations (delete/forget/demote) on shielded
    targets (is_instinct or protected) require explicit force=True."""
    destructive = operation in ("delete", "forget", "demote")
    shielded = bool(target.get("is_instinct") or target.get("protected"))
    if destructive and shielded and not force:
        raise CarefulNotCleverError(
            f"{operation} on shielded target {target.get('id', '?')} "
            f"requires explicit force=True"
        )


# Invariant 6: Evidence integrity (STUB until Slice 3C).
def _assert_evidence_integrity(candidate):
    """Verify HMAC integrity of every observation log cited in the
    candidate's evidence trail. Activated by Slice 3C.

    Walks ``candidate['evidence']['observations']`` and, for any
    entry that is clearly Slice-3A-log-backed (carries BOTH a
    ``session_id`` str AND an integer ``index``), validates the
    corresponding ``<MEMORY_ROOT>/_observations/<session_id>.jsonl``
    file against its HMAC sidecar via ``_validate_file_integrity``.

    Observations without that pair are skipped — they describe a
    different evidence shape (Slice 2's blackboard session_id,
    Slice 2.5's transcript path, legacy bare ``line_hmac`` markers).
    The empty-evidence case (``{}``, ``{'id': ...}``,
    ``{'evidence': {}}``) is also a no-op so candidates that predate
    the observation log continue to pass.

    Raises ``CarefulNotCleverError`` on any sidecar mismatch, missing
    key when sidecar is present, missing-log when log is cited, or
    malformed session_id.
    """
    if not isinstance(candidate, dict):
        return
    evidence = candidate.get("evidence") or {}
    observations = evidence.get("observations") or []
    if not observations:
        return
    seen_sessions = set()
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        sid = obs.get("session_id")
        idx = obs.get("index")
        if not (isinstance(sid, str) and sid and isinstance(idx, int)):
            # Not a Slice-3A log reference — skip integrity check.
            continue
        if sid in seen_sessions:
            continue
        seen_sessions.add(sid)
        _validate_session_id(sid)
        log_path = os.path.join(
            MEMORY_ROOT, _OBSERVATIONS_SUBDIR, f"{sid}.jsonl"
        )
        if not os.path.exists(log_path):
            raise CarefulNotCleverError(
                f"evidence integrity: candidate "
                f"{candidate.get('id', '?')} cites observation log "
                f"session {sid!r} but no log exists at {log_path}"
            )
        _validate_file_integrity(log_path)


# Invariant 7: Rate limiting (dynamic per Grok R3).
def _assert_rate_limit(operation, key):
    """Bound call rate per (operation, key). Threshold is dynamic
    (95th %ile + 20%) once baseline exists; falls back to 60/min
    during first session. Mitigates DoS via repeated extraction or
    observation flooding."""
    now = time.time()
    bucket = _rate_buckets.setdefault((operation, key), [])
    bucket[:] = [t for t in bucket if now - t < 60]
    threshold = _dynamic_threshold(operation, key)
    if len(bucket) >= threshold:
        raise CarefulNotCleverError(
            f"rate limit: {operation} for {key} exceeded {threshold}/min"
        )
    bucket.append(now)


# Invariant 8: Temporal consistency (5min/5min per v4 tuning).
def _assert_temporal_consistency(ts, chain=None):
    """Reject timestamps > 5min in the future or > 5min before the
    chain head. Mitigates clock-skew and backdating attacks (T12).
    Tuned from v3's 60s/1h after NTP drift on consumer hardware was
    shown to exceed 60s (Grok R3)."""
    now = time.time()
    try:
        ts_epoch = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        raise CarefulNotCleverError(
            f"temporal consistency: unparseable timestamp {ts!r}"
        )
    if ts_epoch > now + 300:
        raise CarefulNotCleverError(
            f"temporal consistency: {ts} is future-dated >5min"
        )
    if chain:
        chain_ts = []
        for e in chain:
            if "at" in e:
                try:
                    chain_ts.append(time.mktime(
                        time.strptime(e["at"], "%Y-%m-%dT%H:%M:%SZ")))
                except (ValueError, TypeError):
                    continue
        if chain_ts:
            last = max(chain_ts)
            if ts_epoch < last - 300:
                raise CarefulNotCleverError(
                    f"temporal consistency: {ts} backdated >5min "
                    f"from chain head"
                )


# Invariant 9: Human attention (profile-aware per v5).
_AUTONOMOUS_KEYWORDS = (
    "auto", "every", "daily", "schedule", "automatically",
    "on its own", "without asking", "in the background",
    # T18 intent-laundering semantic coverage:
    "regularly", "routinely", "as a matter of course",
)


def _assert_human_attention(candidate, confirm=False):
    """Pre-promotion anomaly heuristic. Behavior depends on profile:

    single-operator-local (default): logs matched terms; non-blocking
      — there is no separate attacker mimicking operator habits.
    multi-operator-shared: blocks promotion on autonomous-action match
      unless caller passes confirm=True.

    Returns:
        {"matched_terms": [...], "blocking": bool}
    """
    content = candidate.get("content", "").lower()
    matched = [k for k in _AUTONOMOUS_KEYWORDS if k in content]
    profile = _learning_profile()
    if matched and profile == "multi-operator-shared" and not confirm:
        raise CarefulNotCleverError(
            f"candidate {candidate.get('id', '?')} matched autonomous-action "
            f"keywords {matched}; multi-operator-shared profile requires "
            f"explicit confirm=True"
        )
    return {"matched_terms": matched, "blocking": False}


# Slice 7.5 consensus auto-promotion eligibility criteria. Documented
# inline (audit-visible in PR diff). The doctrine forbids auto-promotion
# in multi-operator-shared profile entirely; in single-operator-local
# profile, all of these must be cryptographically verifiable.
_PROMOTION_ELIGIBILITY_MIN_RECALL = 10
_PROMOTION_ELIGIBILITY_MIN_AGE_DAYS = 30
_PROMOTION_ELIGIBILITY_MIN_CONFIDENCE = 0.9
_PROMOTION_ELIGIBILITY_MIN_SESSIONS = 5


def _assert_promotion_eligibility(candidate):
    """v5 Slice 7.5 invariant. Cryptographically validate consensus
    criteria before auto-promotion. Raises CarefulNotCleverError on
    ANY criterion fail; auto_promote_eligible() catches and routes
    the candidate to manual review instead of auto-promoting.

    Manual promote_to_instinct does NOT call this — manual promotion
    is the operator's explicit choice regardless of consensus.

    Criteria (all must hold):
      - recall_count >= 10
      - age (since `created`) >= 30 days
      - confidence >= 0.9
      - usage_history contains >= 5 distinct session_ids
      - No `demoted_at` in candidate's history (never demoted before)
      - Not archived, not superseded
      - _assert_evidence_integrity passes (stub until Slice 3C)
      - _validate_helper_integrity passes (Slice 0.5 mutation defense)
    """
    if candidate.get("superseded_by"):
        raise CarefulNotCleverError(
            f"eligibility: candidate {candidate.get('id', '?')} is superseded"
        )
    if candidate.get("archived"):
        raise CarefulNotCleverError(
            f"eligibility: candidate {candidate.get('id', '?')} is archived"
        )
    if candidate.get("demoted_at"):
        raise CarefulNotCleverError(
            f"eligibility: candidate {candidate.get('id', '?')} was "
            f"previously demoted (demoted_at={candidate['demoted_at']}). "
            f"Auto-promotion forbidden on demote-history."
        )

    recall = candidate.get("recall_count", 0)
    if recall < _PROMOTION_ELIGIBILITY_MIN_RECALL:
        raise CarefulNotCleverError(
            f"eligibility: recall_count {recall} < {_PROMOTION_ELIGIBILITY_MIN_RECALL}"
        )

    created = candidate.get("created")
    if not created:
        raise CarefulNotCleverError(
            f"eligibility: candidate {candidate.get('id', '?')} has no `created` timestamp"
        )
    try:
        created_epoch = time.mktime(
            time.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
        )
    except (ValueError, TypeError):
        raise CarefulNotCleverError(
            f"eligibility: unparseable created timestamp {created!r}"
        )
    age_days = (time.time() - created_epoch) / 86400
    if age_days < _PROMOTION_ELIGIBILITY_MIN_AGE_DAYS:
        raise CarefulNotCleverError(
            f"eligibility: age {age_days:.1f}d < "
            f"{_PROMOTION_ELIGIBILITY_MIN_AGE_DAYS}d minimum"
        )

    conf = candidate.get("confidence", 0.0)
    if conf < _PROMOTION_ELIGIBILITY_MIN_CONFIDENCE:
        raise CarefulNotCleverError(
            f"eligibility: confidence {conf} < {_PROMOTION_ELIGIBILITY_MIN_CONFIDENCE}"
        )

    history = candidate.get("usage_history", [])
    if not isinstance(history, list):
        raise CarefulNotCleverError(
            f"eligibility: usage_history corrupted (not a list)"
        )
    distinct_sessions = {
        h["session_id"] for h in history
        if isinstance(h, dict) and "session_id" in h
    }
    if len(distinct_sessions) < _PROMOTION_ELIGIBILITY_MIN_SESSIONS:
        raise CarefulNotCleverError(
            f"eligibility: {len(distinct_sessions)} distinct sessions in "
            f"usage_history < {_PROMOTION_ELIGIBILITY_MIN_SESSIONS} minimum"
        )

    # Cryptographic integrity checks. These are stubs/light today but
    # become real defenses when Slice 3C ships HMAC integrity and
    # Slice 0.5 helper-digest fires on monkey-patched invariants.
    _assert_evidence_integrity(candidate)  # stub until Slice 3C
    _validate_helper_integrity()  # mutation defense from Slice 0.5


# Read-only allowlist for the CI gate. Every addition is a doctrine
# decision visible in PR diff (the test in tests/ hashes this constant).
_INVARIANT_READ_ONLY_ALLOWLIST = frozenset({
    "recall", "extract", "tree", "stats", "neighbors",
    "extract_instinct_candidates",
    "main",  # CLI entry, not a mutation function per se
})


# ─────────────────────────────────────────────
# v5 Slice 0.5 — Mutation Defense Scaffolding
# ─────────────────────────────────────────────
# These helpers defend the defense layer ITSELF against silent
# weakening over time. Five vectors covered:
#   M2  runtime monkey-patching   →  _validate_helper_integrity + _seal_helpers
#   M3  direct disk write bypass  →  _validate_file_integrity (HMAC sidecar)
#   M5  config drift              →  _audit_config_integrity
#   M6  symbol shadowing          →  _seal_helpers (identity capture)
#   M9  HMAC key replacement      →  _validate_key_fingerprint
#
# All helpers ship as callables; wiring into existing read/write paths
# is the work of Slice 3A/3C (which introduces the HMAC key + observation
# log). Slice 0.5 ships the defenses ready for future wire-in.

import hashlib  # noqa — used by 0.5 helpers
import inspect  # noqa — used by _validate_helper_integrity

# Paths used by the integrity layer.
_INTEGRITY_KEY_PATH = os.path.expanduser("~/.memory/_integrity.key")
_INTEGRITY_FINGERPRINT_PATH = os.path.expanduser(
    "~/.memory/_integrity.fingerprint"
)
_CONFIG_FINGERPRINT_PATH = os.path.expanduser(
    "~/.memory/_config.fingerprint"
)

# At-import-time digests of the 9 invariant helpers. Captured once via
# _seal_helpers(); _validate_helper_integrity() re-validates on call.
# Uses bytecode (`__code__.co_code`) rather than source so the check
# is fast (no file I/O) and catches replacement of the function object,
# replacement of the code object, AND bytecode-level mutation.
_HELPER_DIGESTS = {}
_HELPER_NAMES = (
    "_assert_panic_check",
    "_assert_no_silent_skip",
    "_assert_evidence_present",
    "_assert_single_id",
    "_assert_safety_guard_compliant",
    "_assert_evidence_integrity",
    "_assert_rate_limit",
    "_assert_temporal_consistency",
    "_assert_human_attention",
    "_assert_promotion_eligibility",  # Slice 7.5
)


def _seal_helpers():
    """Capture at-import-time digests of every _assert_* helper plus their
    function-object identities. Called once at module load (see end of this
    block). Subsequent calls to _validate_helper_integrity compare against
    these snapshots. Mitigates M2 (monkey-patching) + M6 (symbol shadowing).

    Idempotent: calling again refreshes the snapshot, which a malicious
    actor would use to launder a patch. The CI gate must enforce that
    _seal_helpers is called EXACTLY ONCE at module init — see the
    test_seal_helpers_called_once_at_load meta-test."""
    for name in _HELPER_NAMES:
        fn = globals().get(name)
        if fn is None:
            raise CarefulNotCleverError(
                f"_seal_helpers: missing required helper {name}"
            )
        bytecode_digest = hashlib.sha256(fn.__code__.co_code).hexdigest()
        _HELPER_DIGESTS[name] = (id(fn), bytecode_digest)


def _validate_helper_integrity():
    """Verify all _assert_* helpers still match their at-import-time
    identity AND bytecode. Raises CarefulNotCleverError on any mismatch.

    Catches three mutation shapes:
      1. Function replaced in module namespace (globals()[name] = new_fn)
      2. Function's __code__ replaced (fn.__code__ = new_code)
      3. Bytecode-level mutation of the code object's co_code

    Does NOT catch monkey-patches via ctypes or PyObject manipulation;
    documented as out-of-scope (T20 supply-chain has a lower bound).
    Mitigates M2 + T20 within Python semantics.

    Cheap (~5 microseconds for 9 helpers); safe to call from every
    invariant entry point."""
    if not _HELPER_DIGESTS:
        # _seal_helpers hasn't been called yet — possible during import
        # or before module init completes. Silent no-op rather than
        # spurious raise during normal import.
        return
    for name, (expected_id, expected_digest) in _HELPER_DIGESTS.items():
        fn = globals().get(name)
        if fn is None:
            raise CarefulNotCleverError(
                f"helper integrity: {name} has been removed from module"
            )
        if id(fn) != expected_id:
            raise CarefulNotCleverError(
                f"helper integrity: {name} function object replaced "
                f"(monkey-patch detected)"
            )
        current_digest = hashlib.sha256(fn.__code__.co_code).hexdigest()
        if current_digest != expected_digest:
            raise CarefulNotCleverError(
                f"helper integrity: {name} bytecode mutated "
                f"(expected {expected_digest[:8]}, got {current_digest[:8]})"
            )


def _validate_file_integrity(path):
    """Validate a memory file against its HMAC sidecar (`<path>.hmac`).

    If a sidecar exists: computes HMAC-SHA256 of the file's contents
    using ~/.memory/_integrity.key; raises if mismatch (direct disk
    write detected without sidecar update).
    If no sidecar exists: returns silently. Legacy files (pre-Slice
    3C) are not retroactively protected; new files written via
    record_observation() and related slices get sidecars on write.

    Mitigates M3 (direct disk writes bypassing API). Slice 3A/3C
    wires this into observation log read paths; Slice 0.5 ships it
    as a callable ready for that wiring."""
    import hmac  # local to keep top-level imports stable
    sidecar = path + ".hmac"
    if not os.path.exists(sidecar):
        return  # legacy file; no enforcement
    if not os.path.exists(_INTEGRITY_KEY_PATH):
        # Sidecar exists but key is gone — that's an integrity failure
        raise CarefulNotCleverError(
            f"file integrity: sidecar present but key missing for {path}"
        )
    with open(_INTEGRITY_KEY_PATH, "rb") as f:
        key = f.read()
    with open(path, "rb") as f:
        content = f.read()
    expected = hmac.new(key, content, hashlib.sha256).hexdigest()
    with open(sidecar) as f:
        recorded = f.read().strip()
    if not hmac.compare_digest(expected, recorded):
        raise CarefulNotCleverError(
            f"file integrity: HMAC mismatch for {path} "
            f"(file content changed without sidecar update — "
            f"direct write detected)"
        )


def _ensure_integrity_key():
    """Generate the HMAC key on first use. 32 random bytes, mode 0o400.

    Lives at ``~/.memory/_integrity.key`` — outside any tracked repo
    even when MEMORY_ROOT points at a sibling git directory. Putting
    the signing key inside a private gitignored subdir is still
    one .gitignore edit away from accidental commit; keeping it
    outside the repo tree is the defense-in-depth posture per the
    doctrine note in ``open-claw-stuff/.memory/README.md``.

    Idempotent: returns silently when the key already exists. No-op
    when Slice 3C is not active in the caller's environment (the
    helper only ever gets invoked from log-integrity write paths).

    Also registers the key fingerprint immediately on creation so a
    subsequent key swap is detected even though the first
    ``_validate_key_fingerprint`` call (before key generation)
    no-opped. Without this atomic pairing, the very first post-
    generation call would register whatever key happens to be on
    disk — including an attacker-substituted one."""
    if os.path.exists(_INTEGRITY_KEY_PATH):
        return
    os.makedirs(os.path.dirname(_INTEGRITY_KEY_PATH), exist_ok=True)
    key_bytes = os.urandom(32)
    with open(_INTEGRITY_KEY_PATH, "wb") as f:
        f.write(key_bytes)
    os.chmod(_INTEGRITY_KEY_PATH, 0o400)
    # Atomic-with-creation fingerprint registration.
    digest = hashlib.sha256(key_bytes).hexdigest()
    with open(_INTEGRITY_FINGERPRINT_PATH, "w") as f:
        f.write(digest)
    os.chmod(_INTEGRITY_FINGERPRINT_PATH, 0o400)


def _compute_file_integrity(path):
    """Write the HMAC-SHA256 sidecar for ``path``.

    Mirror of ``_validate_file_integrity``: reads the file content,
    computes HMAC-SHA256 with ``~/.memory/_integrity.key``, writes to
    ``<path>.hmac``. Auto-generates the key on first use via
    ``_ensure_integrity_key``.

    Caller is responsible for serializing concurrent writes. In
    practice this is invoked from inside the flock held by
    ``record_observation`` so the sidecar is always consistent with
    the log's post-write state."""
    import hmac
    _ensure_integrity_key()
    with open(_INTEGRITY_KEY_PATH, "rb") as f:
        key = f.read()
    with open(path, "rb") as f:
        content = f.read()
    digest = hmac.new(key, content, hashlib.sha256).hexdigest()
    sidecar = path + ".hmac"
    with open(sidecar, "w") as f:
        f.write(digest)
    os.chmod(sidecar, 0o600)


def _validate_key_fingerprint():
    """Verify the HMAC integrity key hasn't been replaced.

    On first use (no fingerprint file): registers the current key's
    SHA256 at ~/.memory/_integrity.fingerprint with mode 0o400.
    On subsequent calls: compares current key's SHA256 against the
    stored fingerprint; raises on mismatch.

    Mitigates M9 + T23 (HMAC key replacement attack). Grok R3 flagged
    this as the highest-impact mutation gap: without it, an attacker
    could swap the key, sign forged data with the new key, and all
    integrity checks would pass against falsified data.

    No-op if no key file exists (Slice 3C ships the key)."""
    if not os.path.exists(_INTEGRITY_KEY_PATH):
        return  # Slice 3C hasn't shipped the key yet
    with open(_INTEGRITY_KEY_PATH, "rb") as f:
        current = hashlib.sha256(f.read()).hexdigest()
    if not os.path.exists(_INTEGRITY_FINGERPRINT_PATH):
        # First use — register the fingerprint
        with open(_INTEGRITY_FINGERPRINT_PATH, "w") as f:
            f.write(current)
        os.chmod(_INTEGRITY_FINGERPRINT_PATH, 0o400)
        return
    with open(_INTEGRITY_FINGERPRINT_PATH) as f:
        recorded = f.read().strip()
    if current != recorded:
        raise CarefulNotCleverError(
            f"key fingerprint: ~/.memory/_integrity.key has been replaced "
            f"(expected {recorded[:8]}, got {current[:8]}). Either rotate "
            f"deliberately by deleting _integrity.fingerprint first, OR "
            f"this is an attack."
        )


def _audit_config_integrity(config_path=None):
    """Audit .claude/settings.json (or any config file path) against a
    registered SHA256 fingerprint.

    Returns a structured result rather than raising — config edits are
    a normal operator action; the audit's job is to surface them, not
    block them. On first call (no fingerprint registered): records
    current SHA256. On subsequent calls: detects drift.

    Returns:
        {
          "config_path": str,
          "drift": bool,
          "current_sha256": str,
          "expected_sha256": str or None  (None on first registration)
        }

    Mitigates M5 (config drift via .claude/settings.json adding a hook
    that disables panic or weakens invariants). Operators who legitimately
    edit settings.json acknowledge by deleting _config.fingerprint;
    next call re-registers."""
    if config_path is None:
        config_path = ".claude/settings.json"
    if not os.path.exists(config_path):
        return {"config_path": config_path, "drift": False,
                "current_sha256": None, "expected_sha256": None}
    with open(config_path, "rb") as f:
        current = hashlib.sha256(f.read()).hexdigest()
    if not os.path.exists(_CONFIG_FINGERPRINT_PATH):
        # First call — register
        os.makedirs(os.path.dirname(_CONFIG_FINGERPRINT_PATH), exist_ok=True)
        with open(_CONFIG_FINGERPRINT_PATH, "w") as f:
            f.write(current)
        return {"config_path": config_path, "drift": False,
                "current_sha256": current, "expected_sha256": None}
    with open(_CONFIG_FINGERPRINT_PATH) as f:
        recorded = f.read().strip()
    return {"config_path": config_path,
            "drift": current != recorded,
            "current_sha256": current,
            "expected_sha256": recorded}


# Seal helpers at module load. Must be at the very end of the helper
# definitions so all 9 _assert_* functions are visible in globals().
_seal_helpers()


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
    """Update a memory by creating a new version. Preserves the original.

    v3.1 fix from edge-probe U1: refuses to update a memory that has
    `superseded_by` already set. Allowing it would branch the supersedes
    chain — the original m1 would point to a new m3, orphaning m2.
    Returns None on this guard (same shape as id-not-found, since both
    are "no update produced").
    """
    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if os.path.exists(path):
            with open(path) as f:
                old = json.load(f)

            # Refuse to branch an already-superseded chain.
            if old.get("superseded_by"):
                return None

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

        # Slice 5: usage history append (profile-aware, default-on).
        # Only timestamp + session_id are stored; query content is
        # never retained (privacy invariant). Capped at 20 entries
        # (FIFO). Per-entry temporal consistency validated against
        # the existing chain.
        if _usage_history_enabled():
            history = mem.get("usage_history", [])
            # Defensive: if corrupted to non-list, reinitialize
            if not isinstance(history, list):
                history = []
            new_entry = {
                "at": mem["last_recalled"],
                "session_id": _current_session_id(),
            }
            # _assert_temporal_consistency raises on future-dated or
            # backdated-from-chain; surfaces tampering visibly.
            try:
                _assert_temporal_consistency(new_entry["at"], chain=history)
            except CarefulNotCleverError:
                # Tampered chain: skip the append (don't add the new
                # entry) but DO surface to operator via _assert_no_silent_skip
                _assert_no_silent_skip(
                    f"usage_history append for {mem.get('id', '?')} "
                    f"failed temporal consistency",
                    1
                )
                # Unreachable: _assert_no_silent_skip raised above
            history.append(new_entry)
            # FIFO cap at the most recent _USAGE_HISTORY_CAP entries
            if len(history) > _USAGE_HISTORY_CAP:
                history = history[-_USAGE_HISTORY_CAP:]
            mem["usage_history"] = history

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
        "confidence_promoted": 0,
        "potential_duplicates": [],
    }

    # v3.1 fix from edge-probes AP1+AP2: auto-protect should count only
    # REAL edges — deduped + pointing at memories that actually exist on
    # disk in the same consolidate pass. Pre-compute the universe of ids
    # across all domains being processed so the centrality count below
    # can filter orphan and duplicate edges.
    valid_ids = set()
    for d in domains:
        for p in glob.glob(os.path.join(MEMORY_ROOT, d, "*.json")):
            try:
                with open(p) as f:
                    valid_ids.add(json.load(f)["id"])
            except (json.JSONDecodeError, IOError, KeyError):
                continue

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

            # Auto-protect well-connected memories: 3+ DEDUPED edges that
            # point at REAL memories. (v3.1 fix from edge-probes AP1+AP2:
            # raw len(related_to) counted orphan and duplicate edges,
            # producing false-positive auto-protection.)
            real_edges = len(set(mem.get("related_to", [])) & valid_ids)
            if real_edges >= 3 and not mem.get("protected"):
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

            # Slice 4: confidence promotion. Frequently-recalled memories
            # get a +0.05 bump, capped at 1.0. Profile-aware flag default-on
            # in single-operator-local; off in multi-operator-shared.
            # Fires once per consolidate pass (not per recall) so rapid-
            # fire recalls don't produce runaway promotion.
            if _confidence_promotion_enabled():
                now_epoch = time.time()
                if _should_bump_confidence(mem, now_epoch):
                    new_conf = min(
                        mem.get("confidence", 0.0) + _CONFIDENCE_PROMOTION_BUMP,
                        _CONFIDENCE_PROMOTION_CAP
                    )
                    if new_conf > mem.get("confidence", 0.0):
                        mem["confidence"] = new_conf
                        actions["confidence_promoted"] += 1
                        _save_mem(mem, path)

            # Auto-archive: old, low-confidence, unprotected, not an instinct.
            # is_instinct shields like `protected` does — an instinct that
            # was deliberately promoted should not be auto-archived just
            # because its raw confidence drifted under 0.3. (v3.1 fix from
            # edge-probe H1.)
            if (not mem.get("protected", False)
                    and not mem.get("is_instinct", False)
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
                        # Auto-merge with shield-aware role assignment.
                        # (v3.1 fix from edge-probes AM1+AM4+AM3):
                        #   * If both sides are shielded (protected OR
                        #     is_instinct), skip the merge entirely —
                        #     neither can be safely discarded.
                        #   * If exactly one side is shielded, force it
                        #     to be the keeper.
                        #   * Otherwise pick by confidence; on a tie,
                        #     break by id for determinism (no longer
                        #     filesystem-order dependent).
                        a = active_memories[i]
                        b = active_memories[j]

                        def _shielded(m):
                            return bool(m.get("protected", False)
                                        or m.get("is_instinct", False))

                        a_shield, b_shield = _shielded(a), _shielded(b)
                        if a_shield and b_shield:
                            # Both shielded: surface as potential duplicate
                            # but do NOT merge.
                            actions["potential_duplicates"].append({
                                "a": a["id"], "b": b["id"],
                                "similarity": round(sim, 3),
                                "domain": d,
                                "skipped_reason": "both shielded",
                            })
                            continue
                        if a_shield:
                            keep, discard = a, b
                        elif b_shield:
                            keep, discard = b, a
                        else:
                            a_conf = a.get("confidence", 0)
                            b_conf = b.get("confidence", 0)
                            if a_conf > b_conf:
                                keep, discard = a, b
                            elif a_conf < b_conf:
                                keep, discard = b, a
                            else:
                                # Tie: deterministic by id.
                                if a["id"] < b["id"]:
                                    keep, discard = a, b
                                else:
                                    keep, discard = b, a

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
# v3.1 Continuous Learning (Slice 1)
#
# Concept-lifted from ECC `skills/continuous-learning-v2/` (MIT) with
# intentional inversions:
#   - ECC uses PreToolUse/PostToolUse hooks + a background Haiku observer
#     to auto-capture instincts. Slice 1 has NO hooks and NO background
#     daemon — extract_instinct_candidates is a synchronous on-demand read.
#   - ECC auto-promotes at consensus thresholds across projects. Slice 1
#     requires explicit single-id promote_to_instinct calls — bulk
#     promotion is structurally impossible.
#   - ECC introduces a parallel project-scope namespace via git remote
#     hash. Slice 1 reuses the existing 7 domains + a flat is_instinct
#     flag — no parallel namespace.
#   - Feature flag default OFF — every call is a no-op until enabled.
#
# Future slices (NOT in v3.1): hook integration, auto-extraction,
# confidence-promotion rules, cross-session usage tracking. Each its own
# decision.
# ─────────────────────────────────────────────

# Memory types most likely to encode a reusable behavioral pattern.
# "insight" and "fact" are excluded: insights are often episodic; facts
# are too static. Patterns/preferences/decisions are the instinct-shaped
# memory types.
_INSTINCT_CANDIDATE_TYPES = ("pattern", "preference", "decision")

# Thresholds for candidate selection. Documented inline (auditable in
# this file's PR history); not read from runtime config.
_INSTINCT_MIN_CONFIDENCE = 0.8
_INSTINCT_MIN_RECALL_COUNT = 3
_INSTINCT_MIN_INTEGRATION = 1  # has tags OR >=1 graph edge


def extract_instinct_candidates(domain=None, limit=20):
    """Surface candidate instincts: high-confidence, frequently-recalled
    memories of pattern/preference/decision type that have been integrated
    into the graph (have tags or edges). Read-only — returns a ranked list
    of memories that *could* be promoted; never promotes.

    When MEMORY_LEARNING_ENABLED is unset/false, returns:
        {"enabled": false, "candidates": []}

    The candidate list is sorted by a composite signal score, but
    promotion still requires an explicit single-id promote_to_instinct
    call per item. There is no bulk-promote API.
    """
    _assert_panic_check()
    if not _learning_enabled():
        return {"enabled": False, "candidates": []}

    _ensure_dirs()
    memories = _load_all([domain] if domain else None)

    candidates = []
    for mem in memories:
        if mem.get("superseded_by"):
            continue
        if mem.get("archived", False):
            continue
        if mem.get("is_instinct", False):
            continue  # already promoted
        if mem.get("type") not in _INSTINCT_CANDIDATE_TYPES:
            continue
        if mem.get("confidence", 0.0) < _INSTINCT_MIN_CONFIDENCE:
            continue
        if mem.get("recall_count", 0) < _INSTINCT_MIN_RECALL_COUNT:
            continue
        integration = len(mem.get("tags", [])) + len(mem.get("related_to", []))
        if integration < _INSTINCT_MIN_INTEGRATION:
            continue

        # Composite signal: confidence × recall_count × (1 + integration)
        # — gives more weight to entries that are confident AND used AND
        # connected, without any single signal dominating.
        signal = (mem.get("confidence", 0.0)
                  * mem.get("recall_count", 0)
                  * (1 + integration))
        mem.pop("_path", None)
        candidates.append((signal, mem))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return {
        "enabled": True,
        "thresholds": {
            "min_confidence": _INSTINCT_MIN_CONFIDENCE,
            "min_recall_count": _INSTINCT_MIN_RECALL_COUNT,
            "min_integration": _INSTINCT_MIN_INTEGRATION,
            "candidate_types": list(_INSTINCT_CANDIDATE_TYPES),
        },
        "candidates": [
            {**mem, "_signal": round(signal, 3)}
            for signal, mem in candidates[:limit]
        ],
    }


def promote_to_instinct(memory_id, domain=None):
    """Mark a single memory as an instinct. Requires
    MEMORY_LEARNING_ENABLED=true; returns {"enabled": false} no-op
    otherwise. No bulk variant exists. Memory stays in its original
    domain — promotion is a flag flip plus a timestamp, not a move.

    Sets `is_instinct: true` and `promoted_at: <iso>` on the memory file.
    Idempotent: re-promoting an already-promoted memory returns success
    without changing the timestamp.
    """
    _assert_panic_check()
    if not _learning_enabled():
        return {"enabled": False, "promoted": False,
                "reason": "MEMORY_LEARNING_ENABLED is not set"}

    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                mem = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # v3.1 fix from edge-probe K1: don't crash on a corrupt
            # memory file; surface it as a structured not-found-style
            # response so callers can handle it. Matches the read
            # discipline in _load_all.
            return {"enabled": True, "promoted": False,
                    "id": memory_id, "domain": d,
                    "reason": f"Memory file unreadable: {type(e).__name__}"}
        if mem.get("is_instinct", False):
            return {"enabled": True, "promoted": True,
                    "id": memory_id, "domain": d,
                    "already_instinct": True,
                    "promoted_at": mem.get("promoted_at")}
        mem["is_instinct"] = True
        mem["promoted_at"] = _now()
        _save_mem(mem, path)
        return {"enabled": True, "promoted": True,
                "id": memory_id, "domain": d,
                "promoted_at": mem["promoted_at"]}

    return {"enabled": True, "promoted": False,
            "id": memory_id, "reason": "Not found in any domain"}


def demote_from_instinct(memory_id, domain=None):
    """Reverse of promote_to_instinct. Sets `is_instinct: false` and
    `demoted_at: <iso>`. Idempotent.
    """
    _assert_panic_check()
    if not _learning_enabled():
        return {"enabled": False, "demoted": False,
                "reason": "MEMORY_LEARNING_ENABLED is not set"}

    _ensure_dirs()
    domains = [domain] if domain else DOMAINS

    for d in domains:
        path = _memory_path(d, memory_id)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                mem = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return {"enabled": True, "demoted": False,
                    "id": memory_id, "domain": d,
                    "reason": f"Memory file unreadable: {type(e).__name__}"}
        if not mem.get("is_instinct", False):
            return {"enabled": True, "demoted": True,
                    "id": memory_id, "domain": d,
                    "already_not_instinct": True}
        mem["is_instinct"] = False
        mem["demoted_at"] = _now()
        _save_mem(mem, path)
        return {"enabled": True, "demoted": True,
                "id": memory_id, "domain": d,
                "demoted_at": mem["demoted_at"]}

    return {"enabled": True, "demoted": False,
            "id": memory_id, "reason": "Not found in any domain"}


# ─────────────────────────────────────────────
# v5 Slice 7.5 — Consensus auto-promotion eligibility
# ─────────────────────────────────────────────
# auto_promote_eligible() reads candidates from extract_instinct_candidates
# and auto-promotes those passing _assert_promotion_eligibility (cryptographic
# consensus criteria). The single-id contract is preserved internally:
# this function iterates per-id, calling promote_to_instinct(id) for each
# eligible candidate, then setting is_auto_promoted + auto_promoted_at
# audit flags on the promoted memory.
#
# Profile semantics (locked):
#   single-operator-local: auto-promotion permitted; flag defaults ON
#   multi-operator-shared: auto-promotion FORBIDDEN; returns disabled
#                         stub regardless of flag setting

def _auto_promote_enabled():
    """Profile-aware. Returns True only in single-operator-local profile
    (where the operator has confirmed sole human access). In
    multi-operator-shared profile, ALWAYS returns False regardless of
    env var — auto-promotion of cross-user memory is structurally
    forbidden by doctrine."""
    if _learning_profile() == "multi-operator-shared":
        return False
    env_val = os.environ.get("MEMORY_AUTO_PROMOTE_ELIGIBLE", "").lower()
    if env_val in ("false", "0", "no"):
        return False
    if env_val in ("true", "1", "yes"):
        return True
    # Default: ON in single-operator-local
    return True


def auto_promote_eligible(domain=None):
    """Promote every candidate that passes cryptographic consensus.

    Reads candidates from extract_instinct_candidates(); runs each
    through _assert_promotion_eligibility(); for passes, calls
    promote_to_instinct() then sets is_auto_promoted + auto_promoted_at
    audit flags. Single-id contract preserved internally (iteration
    over per-id promotion, not batch API).

    Returns:
      {
        "enabled": bool,
        "profile": str,
        "domain": str or None,
        "promoted": [{"id", "domain"}, ...],
        "skipped": [{"id", "reason"}, ...],
        "reason": str (only on early-return)
      }

    Profile behavior:
      single-operator-local: active by default; MEMORY_AUTO_PROMOTE_ELIGIBLE
                            env var can disable
      multi-operator-shared: returns disabled stub permanently;
                            structurally cannot run
    """
    _assert_panic_check()

    profile = _learning_profile()

    # Profile check FIRST: multi-operator-shared is permanently forbidden
    # regardless of any other flag. Surface the structural reason
    # before noting transient flag state.
    if profile == "multi-operator-shared":
        return {"enabled": False, "profile": profile, "domain": domain,
                "promoted": [], "skipped": [],
                "reason": "auto-promotion forbidden in multi-operator-shared profile"}

    if not _learning_enabled():
        return {"enabled": False, "profile": profile, "domain": domain,
                "promoted": [], "skipped": [],
                "reason": "MEMORY_LEARNING_ENABLED is not set"}

    if not _auto_promote_enabled():
        return {"enabled": False, "profile": profile, "domain": domain,
                "promoted": [], "skipped": [],
                "reason": "MEMORY_AUTO_PROMOTE_ELIGIBLE disabled"}

    _assert_rate_limit("auto_promote_eligible", domain or "all")

    # Defense in depth: validate the helper layer hasn't been
    # monkey-patched before iterating. If a single _assert_* has been
    # replaced, ALL eligibility checks below would be compromised;
    # better to halt the whole call than auto-promote against a
    # compromised invariant layer.
    _validate_helper_integrity()

    # Read candidates from the read-only extraction surface.
    extracted = extract_instinct_candidates(domain=domain, limit=100)
    if not extracted.get("enabled"):
        return {"enabled": False, "profile": profile, "domain": domain,
                "promoted": [], "skipped": [],
                "reason": "extract_instinct_candidates returned disabled"}

    promoted = []
    skipped = []
    for candidate in extracted.get("candidates", []):
        # Single-id contract: each candidate processed independently
        # via the per-id API. _assert_single_id fires inside
        # promote_to_instinct.
        try:
            _assert_promotion_eligibility(candidate)
        except CarefulNotCleverError as e:
            skipped.append({"id": candidate.get("id"),
                            "reason": str(e)})
            continue

        # Eligibility passed — promote via the existing single-id API.
        result = promote_to_instinct(candidate["id"])
        if not result.get("promoted"):
            skipped.append({"id": candidate["id"],
                            "reason": result.get("reason", "promotion failed")})
            continue

        # Mark the memory with audit flags. is_auto_promoted alongside
        # is_instinct distinguishes "operator chose this" from "consensus
        # auto-promoted this" in the audit trail.
        path = _memory_path(result["domain"], candidate["id"])
        try:
            with open(path) as f:
                mem = json.load(f)
            mem["is_auto_promoted"] = True
            mem["auto_promoted_at"] = _now()
            _save_mem(mem, path)
        except (json.JSONDecodeError, IOError) as e:
            skipped.append({"id": candidate["id"],
                            "reason": f"audit-flag write failed: {type(e).__name__}"})
            continue

        promoted.append({"id": candidate["id"], "domain": result["domain"]})

    return {
        "enabled": True,
        "profile": profile,
        "domain": domain,
        "promoted": promoted,
        "skipped": skipped,
    }


# ─────────────────────────────────────────────
# v5 Slice 2 — Pull-based session extraction
# ─────────────────────────────────────────────
# extract_candidates_from_session reads orchestrator state files
# (orchestrator/state/<session_id>.json) and surfaces candidate
# patterns / facts / preferences for operator review. Read-only;
# never promotes. Per v5 plan §3 Slice 2.
#
# Invariant call order (enforced by Slice 1 AST rule):
#   1. _assert_panic_check
#   2. _assert_rate_limit("extract_from_session", session_id)
#   3. per-candidate: _assert_evidence_present + _assert_evidence_integrity
#   4. _assert_no_silent_skip if any session-state file was unreadable

def _learning_from_sessions_enabled():
    """Profile-aware flag check. In single-operator-local profile:
    defaults ON. In multi-operator-shared: defaults OFF.
    Override via MEMORY_LEARNING_FROM_SESSIONS env var."""
    env_val = os.environ.get("MEMORY_LEARNING_FROM_SESSIONS", "").lower()
    if env_val in ("true", "1", "yes"):
        return True
    if env_val in ("false", "0", "no"):
        return False
    # Profile-driven default
    return _learning_profile() == "single-operator-local"


def _confidence_promotion_enabled():
    """Profile-aware flag for Slice 4 confidence promotion. Defaults ON
    in single-operator-local; OFF in multi-operator-shared.
    Override via MEMORY_CONFIDENCE_PROMOTION_ENABLED env var."""
    env_val = os.environ.get("MEMORY_CONFIDENCE_PROMOTION_ENABLED", "").lower()
    if env_val in ("true", "1", "yes"):
        return True
    if env_val in ("false", "0", "no"):
        return False
    return _learning_profile() == "single-operator-local"


def _usage_history_enabled():
    """Profile-aware flag for Slice 5 usage history. Defaults ON in
    single-operator-local; OFF in multi-operator-shared.
    Override via MEMORY_USAGE_HISTORY_ENABLED env var.

    When ON, every recall that bumps a memory appends an entry to
    that memory's usage_history list, capped at the most recent 20
    entries (FIFO). Privacy: only timestamp + session_id are stored;
    queries are not retained because queries can contain sensitive
    prose."""
    env_val = os.environ.get("MEMORY_USAGE_HISTORY_ENABLED", "").lower()
    if env_val in ("true", "1", "yes"):
        return True
    if env_val in ("false", "0", "no"):
        return False
    return _learning_profile() == "single-operator-local"


# Slice 5 cap. Documented inline (audit-visible in PR diff).
_USAGE_HISTORY_CAP = 20


_SESSION_STATE_SUBDIR = "_session"
_SESSION_STATE_FILENAME = "current"
_SESSION_STALE_SECONDS = 4 * 3600  # 4h idle = considered a new session


def _session_state_path():
    """Resolves to ``<MEMORY_ROOT>/_session/current``. Lazily created
    by ``_current_session_id`` so plain reads of the corpus never
    touch it."""
    return os.path.join(MEMORY_ROOT, _SESSION_STATE_SUBDIR,
                        _SESSION_STATE_FILENAME)


def _generate_session_id():
    """Short, sortable, no path separators: ``sess-YYYYMMDDTHHMMSSZ-<hex6>``."""
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    suffix = uuid.uuid4().hex[:6]
    return f"sess-{ts}-{suffix}"


def _is_safe_session_id(sid):
    """Bool wrapper around ``_validate_session_id``."""
    if not isinstance(sid, str) or not sid:
        return False
    try:
        _validate_session_id(sid)
    except CarefulNotCleverError:
        return False
    return True


def _resolve_or_create_session_state():
    """Read the session-state file, regenerating if stale or absent.

    Touches mtime on every read so an active session keeps the file
    fresh. After ``_SESSION_STALE_SECONDS`` of no calls, the next
    invocation generates a fresh id — matching the operator's
    intuition that "leaving the terminal idle overnight" starts a
    new session."""
    path = _session_state_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError:
        # Read-only FS or permission issue — return a generated id
        # without trying to persist. Better than crashing the caller.
        return _generate_session_id()

    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < _SESSION_STALE_SECONDS:
            try:
                with open(path) as f:
                    sid = f.read().strip()
                if _is_safe_session_id(sid):
                    # Bump mtime so active use keeps the session alive
                    try:
                        os.utime(path, None)
                    except OSError:
                        pass
                    return sid
            except IOError:
                pass  # fall through to regenerate

    sid = _generate_session_id()
    try:
        with open(path, "w") as f:
            f.write(sid)
    except IOError:
        pass  # couldn't persist; return id anyway
    return sid


def _current_session_id():
    """Resolve the current session_id from the most reliable source
    available, in order:

      1. ``MEMORY_SESSION_ID`` env var — explicit operator override.
      2. ``CLAUDE_SESSION_ID`` env var — picked up automatically if
         the Claude Code harness exports it; future-proofs the
         resolution if the harness ever propagates the transcript
         UUID via env.
      3. Session state file ``<MEMORY_ROOT>/_session/current`` —
         auto-managed; persists across subprocess invocations so two
         ``python3 -c`` calls in the same session get the same id.

    Fixes the v6 dogfood bug where ``MEMORY_SESSION_ID`` set inside
    one subprocess didn't inherit into the next, causing every recall
    bump to log ``session_id: "unknown"`` in usage_history.

    Slice 5 stores only timestamp + session_id in usage_history;
    never query content. The privacy invariant is preserved end-to-end
    regardless of which source resolved the id."""
    explicit = os.environ.get("MEMORY_SESSION_ID")
    if explicit and _is_safe_session_id(explicit):
        return explicit
    claude = os.environ.get("CLAUDE_SESSION_ID")
    if claude and _is_safe_session_id(claude):
        return claude
    return _resolve_or_create_session_state()


# Slice 4 thresholds. Documented inline (auditable in PR history).
_CONFIDENCE_PROMOTION_MIN_RECALL = 5
_CONFIDENCE_PROMOTION_RECENT_DAYS = 14
_CONFIDENCE_PROMOTION_BUMP = 0.05
_CONFIDENCE_PROMOTION_CAP = 1.0


def _should_bump_confidence(mem, now_epoch):
    """Pure predicate: does this memory qualify for a Slice 4 confidence
    bump? Returns False on missing/malformed fields (defensive)."""
    if mem.get("superseded_by"):
        return False
    if mem.get("archived"):
        return False
    if mem.get("recall_count", 0) < _CONFIDENCE_PROMOTION_MIN_RECALL:
        return False
    if mem.get("confidence", 0.0) >= _CONFIDENCE_PROMOTION_CAP:
        return False
    last_recalled = mem.get("last_recalled")
    if not last_recalled:
        return False  # corrupt: recall_count >= 5 but no last_recalled
    try:
        recalled_epoch = time.mktime(
            time.strptime(last_recalled, "%Y-%m-%dT%H:%M:%SZ")
        )
    except (ValueError, TypeError):
        return False  # malformed timestamp; skip silently per defensive default
    # Reject future-dated last_recalled (clock skew or attack)
    if recalled_epoch > now_epoch + 300:
        return False
    age_days = (now_epoch - recalled_epoch) / 86400
    return age_days <= _CONFIDENCE_PROMOTION_RECENT_DAYS


def _validate_session_id(session_id):
    """Defend against path traversal in session_id. Session IDs must be
    a basename with no path separators and no parent-directory or
    current-directory references.

    The raw-parts check below catches bare `"."` and embedded `"./"`
    segments that `os.path.basename` silently normalizes. Pattern
    lifted from OpenAgentd `validate_wiki_path` (their `wiki.py`)
    which documents the same Python behaviour: `Path("topics/./test.md")`
    becomes `("topics", "test.md")` — the dot is silently dropped before
    the parts check runs. We check the RAW string before any path
    operation."""
    if not session_id or not isinstance(session_id, str):
        raise CarefulNotCleverError(
            f"session_id must be a non-empty string, got {session_id!r}"
        )
    # Normalize backslash → slash for cross-platform consistency, then
    # check raw parts before Path/os.path touch the value.
    raw_parts = session_id.replace("\\", "/").split("/")
    if any(part in ("..", ".") for part in raw_parts):
        raise CarefulNotCleverError(
            f"session_id {session_id!r} contains '..' or '.' segment"
        )
    if os.path.basename(session_id) != session_id:
        raise CarefulNotCleverError(
            f"session_id {session_id!r} contains path separators"
        )


def _state_dir_default():
    """Return orchestrator/state/ relative to this module's location."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")


def _extract_candidates_from_blackboard(snapshot, session_id):
    """Pure function: given an immutable snapshot of the blackboard,
    return a list of candidate dicts. No I/O; testable in isolation.

    Three candidate kinds in v1:
      - 'fact' from verified_claims (high-confidence)
      - 'pattern' from repeated pipeline roles (3+ same role)
      - 'preference' from the task description itself

    Each candidate carries full provenance: source session_id, the
    observation references that produced it, and a 'delta' field
    describing what behavior would change if promoted (per v3 plan
    Perplexity R2 Differential Memory Review).
    """
    candidates = []

    # Kind 1: facts from verified_claims
    for i, claim in enumerate(snapshot.get("verified_claims", [])):
        if not isinstance(claim, dict):
            continue
        content = claim.get("claim") or claim.get("text") or ""
        if not content:
            continue
        candidates.append({
            "id": f"{session_id}:claim:{i}",
            "content": content,
            "type": "fact",
            "confidence": 0.95,
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id,
                     "kind": "verified_claim",
                     "ref": f"verified_claims[{i}]"}
                ],
                "observation_count": 1,
            },
            "delta": f"future recalls would return verified claim: "
                     f"'{content[:80]}'",
        })

    # Kind 2: patterns from repeated pipeline roles
    role_counts = {}
    role_refs = {}
    for i, step in enumerate(snapshot.get("pipeline", [])):
        if not isinstance(step, dict):
            continue
        role = step.get("role")
        if not role:
            continue
        role_counts[role] = role_counts.get(role, 0) + 1
        role_refs.setdefault(role, []).append(i)
    for role, count in role_counts.items():
        if count < 3:
            continue
        candidates.append({
            "id": f"{session_id}:pattern:{role}",
            "content": f"operator used '{role}' role {count} times in session",
            "type": "pattern",
            "confidence": min(0.5 + 0.1 * count, 0.85),
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id,
                     "kind": "pipeline_step",
                     "ref": f"pipeline[{i}]"}
                    for i in role_refs[role]
                ],
                "observation_count": count,
            },
            "delta": f"future sessions would weight '{role}' role higher "
                     f"in recall scoring",
        })

    # Kind 3: preference from task description
    task = snapshot.get("task", "")
    if task and len(task) > 20:
        candidates.append({
            "id": f"{session_id}:preference:task",
            "content": f"operator interested in: {task[:200]}",
            "type": "preference",
            "confidence": 0.7,
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id,
                     "kind": "task_description",
                     "ref": "task"}
                ],
                "observation_count": 1,
            },
            "delta": f"future recalls would prioritize content related "
                     f"to: {task[:80]}",
        })

    return candidates


def extract_candidates_from_session(session_id, dry_run=True, state_dir=None):
    """Read orchestrator state file at <state_dir>/<session_id>.json and
    surface candidate patterns/facts/preferences for operator review.

    Profile-aware default-on/off (MEMORY_LEARNING_FROM_SESSIONS);
    enforced read-only when dry_run=True (the v1 contract — never
    writes memory from this slice).

    Returns:
        {
          "enabled": bool,
          "session_id": str,
          "candidates": [...],
          "skipped": int,
          "reason": str (only present on early-return)
        }

    Mitigates T9 (TOCTOU) via single-read snapshot pattern: the entire
    state file is loaded into memory before any scanning, and the
    extraction operates on the immutable snapshot. Concurrent writes
    after the read are visible to subsequent calls but not this one.
    """
    _assert_panic_check()

    if not _learning_enabled():
        return {"enabled": False, "session_id": session_id,
                "candidates": [], "skipped": 0,
                "reason": "MEMORY_LEARNING_ENABLED is not set"}

    if not _learning_from_sessions_enabled():
        return {"enabled": False, "session_id": session_id,
                "candidates": [], "skipped": 0,
                "reason": "MEMORY_LEARNING_FROM_SESSIONS disabled"}

    # Defend against path traversal in session_id
    _validate_session_id(session_id)

    # Rate-limit per-session extraction
    _assert_rate_limit("extract_from_session", session_id)

    if state_dir is None:
        state_dir = _state_dir_default()
    state_path = os.path.join(state_dir, f"{session_id}.json")

    # Snapshot pattern: single read, then operate on immutable copy
    if not os.path.exists(state_path):
        return {"enabled": True, "session_id": session_id,
                "candidates": [], "skipped": 0,
                "reason": f"no state file at {state_path}"}
    try:
        with open(state_path) as f:
            snapshot = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        # Surface as INFO finding rather than crash
        _assert_no_silent_skip(
            f"state file unreadable for {session_id}: "
            f"{type(e).__name__}",
            1
        )
        # _assert_no_silent_skip raised; unreachable

    candidates = _extract_candidates_from_blackboard(snapshot, session_id)

    # Per-candidate invariant validation
    for candidate in candidates:
        _assert_evidence_present(candidate)
        _assert_evidence_integrity(candidate)  # stub until Slice 3C

    # If dry_run (always true in v1), do not write anything.
    # The caller decides what to do with the candidate list.
    return {
        "enabled": True,
        "session_id": session_id,
        "candidates": candidates,
        "skipped": 0,
        "dry_run": dry_run,
    }


# ─────────────────────────────────────────────
# v6 Slice 2.5 — Formalized transcript mining
# ─────────────────────────────────────────────
# Converts the cross-thread mining + relay pattern (emergent on
# 2026-05-13, used 4+ times across sibling threads) into stable
# callable surface. Three functions:
#
#   mine_transcripts()         read-only; parse jsonls → candidates
#   ingest_relayed_memories()  write relayer JSONs (with IDs) to disk
#   _dedup_against_corpus()    internal helper used by both
#
# Mining is read-only (no MEMORY_ROOT writes). Ingestion writes
# verbatim, preserving the relayer's chosen IDs — does NOT call
# memory_ops.encode (which generates fresh UUIDs and would lose
# origin trace).

# Auto-resume preamble + system-noise prefixes to skip during mining.
_MINE_SKIP_PREFIXES = (
    "This session is being continued",
    "<system-reminder>",
    "[Request interrupted",
    "Caveat:",
    "Stop hook feedback",
    "Tool loaded",  # ToolSearch acknowledgement
)


def _dedup_against_corpus(content, domain, tags=None):
    """Pure dedup helper. Returns (matched_memory_id, reason) or (None, None).

    Three signals (any one wins):
      1. Substring head-match: first 200 chars of new in existing,
         or vice versa.
      2. Word-overlap >65% within same-domain memories.
      3. Tag-overlap >60% paired with word-overlap >40% (soft signal).

    Reads from current MEMORY_ROOT/<domain>/*.json on every call —
    no caching, so dedup sees concurrent writes. Domain-scoped:
    a memory in domain=ken doesn't dedup against domain=sheep."""
    nc = content.lower()
    n_words = set(re.findall(r"\w{4,}", nc))
    n_tag_set = set(tags or [])

    for path in glob.glob(os.path.join(MEMORY_ROOT, domain, "*.json")):
        try:
            with open(path) as f:
                e = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        ec = e.get("content", "").lower()
        if not ec:
            continue
        # Substring head-match
        if nc[:200] in ec or ec[:200] in nc:
            return e.get("id"), "substring-head-match"
        # Word overlap
        if n_words:
            e_words = set(re.findall(r"\w{4,}", ec))
            overlap = len(n_words & e_words) / len(n_words)
            if overlap > 0.65:
                if n_tag_set:
                    e_tag_set = set(e.get("tags", []))
                    tag_overlap = (
                        len(n_tag_set & e_tag_set) / len(n_tag_set)
                        if e_tag_set else 0.0
                    )
                    return (
                        e.get("id"),
                        f"word-overlap-{overlap:.2f}+tag-overlap-{tag_overlap:.2f}",
                    )
                return e.get("id"), f"word-overlap-{overlap:.2f}"
    return None, None


def mine_transcripts(
    transcript_glob=None,
    min_content_chars=30,
    max_content_chars=500,
    source_tag=None,
):
    """Stream-mine transcript jsonl files for unique high-signal user
    prompts. Returns a structured report; read-only (no MEMORY_ROOT
    writes). Operator passes the returned candidates into
    ingest_relayed_memories or memory_ops.encode as desired.

    Each candidate carries an `evidence` sub-dict so it satisfies the
    _assert_evidence_present invariant when used in downstream
    extraction paths.

    Returns:
        {
            "candidates": [
                {
                    "content": str,
                    "timestamp": str (ISO),
                    "session_id": str (8-char prefix from filename),
                    "source": str,
                    "transcript_path": str,
                    "evidence": {"observations": [{"transcript", "session_id", "timestamp"}]},
                },
                ...
            ],
            "transcripts_scanned": int,
            "parse_failures": int,
            "skipped_too_short": int,
            "skipped_too_long": int,
            "skipped_preamble": int,
            "skipped_dup_text": int,
        }

    Counts are surfaced (not silent drops), so _assert_no_silent_skip
    is not triggered by normal filter activity. parse_failures is
    surfaced too — caller decides whether to investigate.
    """
    _assert_panic_check()

    if transcript_glob is None:
        transcript_glob = "/root/.claude/projects/-home-user/*.jsonl"

    # Defend against path traversal via the glob pattern itself.
    # Only allow alphanumeric, hyphen, slash, dot, asterisk, square brackets.
    if not re.match(r"^[a-zA-Z0-9_\-/.*\[\]?]+$", transcript_glob):
        raise CarefulNotCleverError(
            f"transcript_glob {transcript_glob!r} contains unsafe characters"
        )

    _assert_rate_limit("mine_transcripts", transcript_glob)

    source = source_tag or f"mined-from-transcripts:{_now()[:10]}"

    unique = {}  # text -> (timestamp, session_id, transcript_path)
    parse_failures = 0
    skipped_too_short = 0
    skipped_too_long = 0
    skipped_preamble = 0
    skipped_dup_text = 0
    scanned = 0

    for path in sorted(glob.glob(transcript_glob)):
        scanned += 1
        sess_id = os.path.basename(path)[:8]
        try:
            with open(path) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        parse_failures += 1
                        continue
                    msg = d.get("message", {})
                    if msg.get("role") != "user":
                        continue
                    content_block = msg.get("content", "")
                    # Text might be top-level string or list-of-blocks
                    texts = []
                    if isinstance(content_block, str):
                        texts.append(content_block)
                    elif isinstance(content_block, list):
                        for c in content_block:
                            if isinstance(c, dict) and c.get("type") == "text":
                                texts.append(c.get("text", ""))
                    for t in texts:
                        t = t.strip()
                        if not t:
                            continue
                        if any(t.startswith(p) for p in _MINE_SKIP_PREFIXES):
                            skipped_preamble += 1
                            continue
                        if len(t) < min_content_chars:
                            skipped_too_short += 1
                            continue
                        if len(t) > max_content_chars:
                            skipped_too_long += 1
                            continue
                        ts = d.get("timestamp", "")
                        if t in unique:
                            skipped_dup_text += 1
                            # Keep earliest timestamp
                            old_ts, _, _ = unique[t]
                            if ts and ts < old_ts:
                                unique[t] = (ts, sess_id, path)
                            continue
                        unique[t] = (ts, sess_id, path)
        except (IOError, OSError):
            parse_failures += 1
            continue

    candidates = []
    for text, (ts, sess, path) in unique.items():
        candidate = {
            "content": text,
            "timestamp": ts,
            "session_id": sess,
            "source": source,
            "transcript_path": path,
            "evidence": {
                "observations": [
                    {"transcript": path, "session_id": sess, "timestamp": ts}
                ]
            },
        }
        _assert_evidence_present(candidate)
        candidates.append(candidate)

    return {
        "candidates": candidates,
        "transcripts_scanned": scanned,
        "parse_failures": parse_failures,
        "skipped_too_short": skipped_too_short,
        "skipped_too_long": skipped_too_long,
        "skipped_preamble": skipped_preamble,
        "skipped_dup_text": skipped_dup_text,
    }


def ingest_relayed_memories(json_list, dedup=True):
    """Accept a list of complete memory dicts (with IDs already set by
    the relayer) and write the net-new ones verbatim to disk. Does NOT
    call memory_ops.encode — preserves the relayer's IDs for origin
    trace.

    Each dict must contain at minimum: id, created, domain, type,
    content. Other fields (version, source, confidence, tags,
    related_to, supersedes, protected, archived, summarizes,
    last_recalled, recall_count) are preserved verbatim if present;
    sensible defaults filled in otherwise.

    Args:
        json_list: list of memory dicts (or a single dict).
        dedup: if True (default), substring/word/tag overlap dedup
               against current MEMORY_ROOT corpus. Set False to write
               unconditionally (operator override).

    Returns:
        {
            "written": [{"id", "domain", "type"}, ...],
            "skipped": [{"id", "reason", "matched_id"}, ...],
            "errors": [{"id" or position, "reason"}, ...],
        }
    """
    _assert_panic_check()

    if isinstance(json_list, dict):
        json_list = [json_list]
    if not isinstance(json_list, list):
        raise CarefulNotCleverError(
            f"ingest_relayed_memories expects list or dict, got {type(json_list).__name__}"
        )

    _assert_rate_limit("ingest_relayed_memories", "default")

    required = {"id", "created", "domain", "type", "content"}
    defaults = {
        "version": 1,
        "updated": None,
        "source": "relayed",
        "confidence": 0.7,
        "tags": [],
        "related_to": [],
        "supersedes": None,
        "protected": False,
        "archived": False,
        "summarizes": [],
        "last_recalled": None,
        "recall_count": 0,
    }

    written, skipped, errors = [], [], []

    for idx, d in enumerate(json_list):
        if not isinstance(d, dict):
            errors.append({"position": idx, "reason": f"not a dict ({type(d).__name__})"})
            continue
        missing = required - set(d.keys())
        if missing:
            errors.append({
                "id": d.get("id", f"<position {idx}>"),
                "reason": f"missing required fields: {sorted(missing)}",
            })
            continue
        # Validate created timestamp
        try:
            _assert_temporal_consistency(d["created"])
        except CarefulNotCleverError as e:
            errors.append({"id": d["id"], "reason": str(e)})
            continue
        # Defend against id with path separators
        if os.path.basename(d["id"]) != d["id"] or any(
            seg in (".", "..") for seg in d["id"].replace("\\", "/").split("/")
        ):
            errors.append({"id": d["id"], "reason": "id contains path separators or traversal segments"})
            continue
        # Domain validation
        if d["domain"] not in DOMAINS:
            errors.append({"id": d["id"], "reason": f"unknown domain {d['domain']!r}"})
            continue

        # Dedup
        if dedup:
            dup_id, reason = _dedup_against_corpus(
                d["content"], d["domain"], d.get("tags", [])
            )
            if dup_id and dup_id != d["id"]:
                skipped.append({
                    "id": d["id"],
                    "matched_id": dup_id,
                    "reason": reason,
                })
                continue

        # File-exists check (idempotent — same id appearing twice in one call,
        # or already present on disk from a prior ingest).
        target_dir = os.path.join(MEMORY_ROOT, d["domain"])
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f"{d['id']}.json")
        if os.path.exists(target_path):
            skipped.append({"id": d["id"], "reason": "file already exists at target path"})
            continue

        # Fill in defaults for missing optional fields
        record = dict(defaults)
        record.update(d)

        with open(target_path, "w") as f:
            json.dump(record, f, indent=2)
        written.append({
            "id": d["id"],
            "domain": d["domain"],
            "type": d["type"],
        })

    return {"written": written, "skipped": skipped, "errors": errors}


# ─────────────────────────────────────────────
# v6 Slice 3A — Observation log infrastructure
# ─────────────────────────────────────────────
# OPTIONAL append-only log of tool invocations, keyed per session_id.
# Operator opts in via MEMORY_OBSERVATIONS_ENABLED=true. The log lives
# at <MEMORY_ROOT>/_observations/<session_id>.jsonl and stores only
# hashed args + a coarse result_class — no raw values (T4 sensitive
# data mitigation).
#
# Bounded: 10MB or 10,000 lines per session, whichever fires first.
# At cap, FIFO-evicts the oldest 10% (not a full truncate) and
# surfaces the eviction as an INFO finding via _assert_no_silent_skip
# (T3 disk exhaustion, T10 log-compaction attack).
#
# flock() held during every write, mitigating T6 (cross-session race)
# and T9 (TOCTOU during extraction). Hook integration is Slice 6;
# integrity sidecars are Slice 3C.

import fcntl  # POSIX advisory locking

_OBSERVATIONS_SUBDIR = "_observations"
_OBSERVATION_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_OBSERVATION_MAX_LINES = 10_000
_OBSERVATION_EVICTION_RATIO = 0.10
_OBSERVATION_RESULT_CLASSES = frozenset({
    "success", "error", "timeout", "truncated"
})
_OBSERVATION_TOOL_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_OBSERVATION_HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def _observations_enabled():
    """MEMORY_OBSERVATIONS_ENABLED=true to opt in. Default off."""
    return os.environ.get(
        "MEMORY_OBSERVATIONS_ENABLED", "false"
    ).lower() == "true"


def _observations_dir():
    """Return <MEMORY_ROOT>/_observations/, creating if needed."""
    path = os.path.join(MEMORY_ROOT, _OBSERVATIONS_SUBDIR)
    os.makedirs(path, exist_ok=True)
    return path


def _observation_log_path(session_id):
    """Return jsonl path for session_id. Caller must have already
    validated session_id via _validate_session_id."""
    return os.path.join(_observations_dir(), f"{session_id}.jsonl")


def _compute_args_hash(args):
    """Deterministic SHA256 over normalized args. Used by hook callers
    (Slice 6) to convert raw tool args into the hash that
    record_observation persists. Raw values never reach disk."""
    if isinstance(args, (dict, list)):
        serialized = json.dumps(args, sort_keys=True, separators=(",", ":"))
    else:
        serialized = str(args)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_observation_inputs(tool, hash_value, result_class):
    if not isinstance(tool, str) or not _OBSERVATION_TOOL_PATTERN.match(tool):
        raise CarefulNotCleverError(
            f"record_observation: invalid tool name {tool!r} "
            f"(expected /{_OBSERVATION_TOOL_PATTERN.pattern}/)"
        )
    if (not isinstance(hash_value, str)
            or not _OBSERVATION_HASH_PATTERN.match(hash_value)):
        raise CarefulNotCleverError(
            f"record_observation: args_hash must be 64-char lowercase hex "
            f"sha256, got {hash_value!r}"
        )
    if result_class not in _OBSERVATION_RESULT_CLASSES:
        raise CarefulNotCleverError(
            f"record_observation: result_class must be one of "
            f"{sorted(_OBSERVATION_RESULT_CLASSES)}, got {result_class!r}"
        )


def _rotate_observation_log(path):
    """FIFO-evict oldest 10% of the log if over size or line cap.
    Returns (evicted_count, reason) — (0, None) when no rotation needed.

    Caller must hold the flock on a separate handle. This function
    reads the file fresh and writes via os.replace, so concurrent
    readers see either the pre- or post-rotation contents — never
    a torn write."""
    if not os.path.exists(path):
        return 0, None
    size = os.path.getsize(path)
    over_bytes = size > _OBSERVATION_MAX_BYTES
    with open(path) as f:
        lines = f.readlines()
    over_lines = len(lines) > _OBSERVATION_MAX_LINES
    if not (over_bytes or over_lines):
        return 0, None
    reason_parts = []
    if over_bytes:
        reason_parts.append(f"byte cap {_OBSERVATION_MAX_BYTES}")
    if over_lines:
        reason_parts.append(f"line cap {_OBSERVATION_MAX_LINES}")
    reason = " + ".join(reason_parts)
    evict = max(1, int(len(lines) * _OBSERVATION_EVICTION_RATIO))
    kept = lines[evict:]
    tmp = path + ".rotating"
    with open(tmp, "w") as f:
        f.writelines(kept)
    os.replace(tmp, path)
    return evict, reason


def record_observation(tool, args_hash, result_class, session_id):
    """Append a single observation to <MEMORY_ROOT>/_observations/<session_id>.jsonl.

    Args:
        tool: short identifier of the tool invoked (e.g. "Bash", "Read");
            must match /[A-Za-z0-9_.-]{1,64}/
        args_hash: 64-char lowercase hex sha256 of normalized args;
            raw args MUST NOT be passed — the hash is the evidence
        result_class: one of {"success", "error", "timeout", "truncated"}
        session_id: opaque session identifier; path-traversal-checked

    Returns:
        {"enabled": False} when feature flag off, otherwise
        {
            "enabled": True,
            "path": str,
            "wrote": True,
            "rotation": None or {"evicted": int, "reason": str, "info": str}
        }

    Raises CarefulNotCleverError on panic flag, invalid input,
    rate-limit, or future-dated/temporal-inconsistent timestamp.
    """
    _assert_panic_check()
    if not _observations_enabled():
        return {"enabled": False}
    _validate_session_id(session_id)
    _validate_observation_inputs(tool, args_hash, result_class)
    _assert_rate_limit("record_observation", session_id)

    ts = _now()
    _assert_temporal_consistency(ts)

    path = _observation_log_path(session_id)
    record = {
        "ts": ts,
        "tool": tool,
        "args_hash": args_hash,
        "result_class": result_class,
    }
    line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"

    # Exclusive flock around append + rotation + sidecar write. Held
    # on the same fd so concurrent writers see a consistent
    # log+sidecar pair (Slice 3C T6/T9 mitigation).
    with open(path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
            evicted, reason = _rotate_observation_log(path)
            # Slice 3C: recompute HMAC sidecar to reflect post-write
            # state. Key fingerprint is validated on the way in.
            _validate_key_fingerprint()
            _compute_file_integrity(path)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    rotation = None
    if evicted > 0:
        rotation = {"evicted": evicted, "reason": reason}
        # _assert_no_silent_skip raises by design — capture as INFO
        # so the rotation surfaces in the return dict instead of being
        # a silent drop.
        try:
            _assert_no_silent_skip(
                reason=f"observation log rotation: {reason}",
                count=evicted,
            )
        except CarefulNotCleverError as e:
            rotation["info"] = str(e)

    return {
        "enabled": True,
        "path": path,
        "wrote": True,
        "rotation": rotation,
    }


def compute_log_checksum(session_id):
    """Explicitly (re)compute the HMAC sidecar for a session's log.
    Useful for migration / repair paths; normal writes through
    ``record_observation`` keep the sidecar fresh automatically.

    Returns ``{"enabled": False}`` when observations are off, else
    ``{"path": str, "hmac_path": str, "wrote": bool}``. Raises
    ``CarefulNotCleverError`` on missing log, panic, or invalid
    session_id."""
    _assert_panic_check()
    if not _observations_enabled():
        return {"enabled": False}
    _validate_session_id(session_id)
    _assert_rate_limit("compute_log_checksum", session_id)
    path = _observation_log_path(session_id)
    if not os.path.exists(path):
        raise CarefulNotCleverError(
            f"compute_log_checksum: no observation log for session "
            f"{session_id!r}"
        )
    _validate_key_fingerprint()
    _compute_file_integrity(path)
    return {
        "enabled": True,
        "path": path,
        "hmac_path": path + ".hmac",
        "wrote": True,
    }


def validate_log_checksum(session_id):
    """Validate a session's observation log against its HMAC sidecar.

    Returns ``{"enabled": False}`` when observations are off; else
    ``{"valid": bool, "reason": str or None, "path": str}``. Does NOT
    raise on integrity failure — wraps the underlying
    ``_validate_file_integrity`` exception into a structured result
    so callers can decide whether to treat the failure as fatal.
    Slice 3B's extraction path raises via ``_assert_evidence_integrity``;
    other callers may want to log + skip."""
    _assert_panic_check()
    if not _observations_enabled():
        return {"enabled": False}
    _validate_session_id(session_id)
    _assert_rate_limit("validate_log_checksum", session_id)
    path = _observation_log_path(session_id)
    if not os.path.exists(path):
        return {
            "enabled": True, "valid": False,
            "reason": "no observation log for this session",
            "path": path,
        }
    sidecar = path + ".hmac"
    if not os.path.exists(sidecar):
        return {
            "enabled": True, "valid": False,
            "reason": "sidecar missing — log was not written via "
                      "record_observation, or sidecar was deleted",
            "path": path,
        }
    try:
        _validate_file_integrity(path)
    except CarefulNotCleverError as e:
        return {
            "enabled": True, "valid": False,
            "reason": str(e), "path": path,
        }
    return {"enabled": True, "valid": True, "reason": None, "path": path}


def clear_observations(session_id):
    """Delete the observation log for session_id. Explicit cleanup;
    callers use this between sessions or to drop a corrupted log.

    Returns {"enabled": False} when feature off, else
    {"removed": bool, "path": str}.
    """
    _assert_panic_check()
    if not _observations_enabled():
        return {"enabled": False}
    _validate_session_id(session_id)
    _assert_rate_limit("clear_observations", session_id)
    path = _observation_log_path(session_id)
    if not os.path.exists(path):
        return {"removed": False, "path": path}
    os.remove(path)
    sidecar = path + ".hmac"
    if os.path.exists(sidecar):
        os.remove(sidecar)
    return {"removed": True, "path": path}


# ─────────────────────────────────────────────
# v6 Slice 3B — Observation extraction
# ─────────────────────────────────────────────
# Reads <MEMORY_ROOT>/_observations/<session_id>.jsonl produced by
# Slice 3A and surfaces candidate patterns. Every candidate's evidence
# carries (session_id, index) for each cited log line so Slice 3C's
# _assert_evidence_integrity cryptographically attests the chain.
#
# Three candidate kinds (mirror of Slice 2 with observation-log idioms):
#   pattern (success): tool+result_class="success" repeated >=3 times
#   pattern (repeat) : same args_hash repeated >=3 times (automation candidate)
#   fact   (failure) : tool+args_hash with result_class="error" repeated >=2 times
#
# Snapshot pattern: log read once in full under a shared flock, then
# extraction operates on the immutable copy. TOCTOU-safe against
# concurrent record_observation writers.

_OBS_SUCCESS_PATTERN_MIN = 3
_OBS_REPEAT_PATTERN_MIN = 3
_OBS_ERROR_PATTERN_MIN = 2


def _extract_candidates_from_observation_log(observations, session_id):
    """Pure function: input is a list of (index, obs_dict) tuples;
    output is a list of candidate dicts. No I/O. Testable in isolation."""
    candidates = []

    pair_counts = {}
    pair_indices = {}
    hash_counts = {}
    hash_indices = {}
    hash_tools = {}
    err_counts = {}
    err_indices = {}

    for idx, obs in observations:
        tool = obs["tool"]
        rc = obs["result_class"]
        h = obs["args_hash"]

        key = (tool, rc)
        pair_counts[key] = pair_counts.get(key, 0) + 1
        pair_indices.setdefault(key, []).append(idx)

        hash_counts[h] = hash_counts.get(h, 0) + 1
        hash_indices.setdefault(h, []).append(idx)
        hash_tools[h] = tool

        if rc == "error":
            ekey = (tool, h)
            err_counts[ekey] = err_counts.get(ekey, 0) + 1
            err_indices.setdefault(ekey, []).append(idx)

    for (tool, rc), count in sorted(pair_counts.items()):
        if rc != "success" or count < _OBS_SUCCESS_PATTERN_MIN:
            continue
        candidates.append({
            "id": f"{session_id}:obs:{tool}:{rc}",
            "content": (
                f"tool '{tool}' returned '{rc}' {count} times in session"
            ),
            "type": "pattern",
            "confidence": min(0.5 + 0.1 * count, 0.85),
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id, "index": i,
                     "tool": tool, "result_class": rc}
                    for i in pair_indices[(tool, rc)]
                ],
                "observation_count": count,
            },
            "delta": (
                f"frequent successful use of '{tool}' could become an "
                f"instinct after promotion"
            ),
        })

    for h, count in sorted(hash_counts.items()):
        if count < _OBS_REPEAT_PATTERN_MIN:
            continue
        candidates.append({
            "id": f"{session_id}:obs:hash:{h[:8]}",
            "content": (
                f"operator repeated identical-args call to "
                f"'{hash_tools[h]}' {count} times (args_hash {h[:12]}...)"
            ),
            "type": "pattern",
            "confidence": min(0.4 + 0.08 * count, 0.75),
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id, "index": i,
                     "tool": hash_tools[h], "args_hash": h}
                    for i in hash_indices[h]
                ],
                "observation_count": count,
            },
            "delta": (
                f"repeated identical call to '{hash_tools[h]}' is an "
                f"automation candidate"
            ),
        })

    for (tool, h), count in sorted(err_counts.items()):
        if count < _OBS_ERROR_PATTERN_MIN:
            continue
        candidates.append({
            "id": f"{session_id}:obs:err:{tool}:{h[:8]}",
            "content": (
                f"tool '{tool}' returned error for args_hash "
                f"{h[:12]}... {count} times — likely failure mode"
            ),
            "type": "fact",
            "confidence": min(0.5 + 0.1 * count, 0.85),
            "evidence": {
                "session_id": session_id,
                "observations": [
                    {"session_id": session_id, "index": i,
                     "tool": tool, "args_hash": h,
                     "result_class": "error"}
                    for i in err_indices[(tool, h)]
                ],
                "observation_count": count,
            },
            "delta": (
                f"future recalls warn operator about this failing pattern"
            ),
        })

    return candidates


def _is_well_formed_observation(obs):
    """Strict 4-key shape check. Mitigates T8 plan-injection: lines
    with extra keys or missing required keys are treated as malformed
    and counted, never fed to the extractor."""
    if not isinstance(obs, dict):
        return False
    required = {"ts", "tool", "args_hash", "result_class"}
    if set(obs.keys()) != required:
        return False
    if not (isinstance(obs["ts"], str)
            and isinstance(obs["tool"], str)
            and isinstance(obs["args_hash"], str)
            and isinstance(obs["result_class"], str)):
        return False
    if not _OBSERVATION_TOOL_PATTERN.match(obs["tool"]):
        return False
    if not _OBSERVATION_HASH_PATTERN.match(obs["args_hash"]):
        return False
    if obs["result_class"] not in _OBSERVATION_RESULT_CLASSES:
        return False
    return True


def extract_candidates_from_observations(session_id, dry_run=True):
    """Read <MEMORY_ROOT>/_observations/<session_id>.jsonl and surface
    candidate patterns from observed tool usage. Read-only;
    ``dry_run`` parameter is reserved for future write paths.

    Returns ``{"enabled": False}`` when observations are off, else::

        {
          "enabled": True,
          "session_id": str,
          "candidates": [...],
          "skipped": int,                  # malformed / injected lines
          "skipped_info": str or None,     # _assert_no_silent_skip msg
          "dry_run": bool,
          "reason": str (only on empty/missing-log return)
        }

    Snapshot pattern (T9 mitigation): the full log is read under a
    shared flock into an in-memory list of (index, obs) tuples. The
    extractor operates only on that snapshot — concurrent writes after
    the read are invisible to this call but visible to the next one.

    Each candidate's ``evidence.observations[]`` includes integer
    ``index`` alongside ``session_id`` so Slice 3C's
    ``_assert_evidence_integrity`` cryptographically attests the
    cited log file on every candidate.
    """
    _assert_panic_check()
    if not _observations_enabled():
        return {"enabled": False}
    _validate_session_id(session_id)
    _assert_rate_limit("extract_from_observations", session_id)

    path = _observation_log_path(session_id)
    if not os.path.exists(path):
        return {
            "enabled": True, "session_id": session_id,
            "candidates": [], "skipped": 0, "skipped_info": None,
            "dry_run": dry_run,
            "reason": f"no observation log at {path}",
        }

    # Snapshot under shared flock — blocks against concurrent
    # record_observation writes but does not block parallel readers.
    with open(path) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            raw_lines = f.readlines()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    observations = []
    malformed = 0
    for idx, raw in enumerate(raw_lines):
        line = raw.strip()
        if not line:
            continue
        try:
            obs = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not _is_well_formed_observation(obs):
            malformed += 1
            continue
        observations.append((idx, obs))

    candidates = _extract_candidates_from_observation_log(
        observations, session_id
    )

    # Per-candidate invariant validation — evidence shape + (Slice 3C)
    # cryptographic integrity of the cited log file.
    for c in candidates:
        _assert_evidence_present(c)
        _assert_evidence_integrity(c)

    skipped_info = None
    if malformed > 0:
        try:
            _assert_no_silent_skip(
                f"extraction skipped {malformed} malformed/injected "
                f"observation lines in session {session_id}",
                malformed,
            )
        except CarefulNotCleverError as e:
            # Surface as INFO in return rather than fail the extraction.
            skipped_info = str(e)

    return {
        "enabled": True,
        "session_id": session_id,
        "candidates": candidates,
        "skipped": malformed,
        "skipped_info": skipped_info,
        "dry_run": dry_run,
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
