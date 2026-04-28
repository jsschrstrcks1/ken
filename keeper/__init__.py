"""keeper — session-continuity for Claude Code threads.

Stage 1: minimum-viable thread handoff. `join`, `beat`, `complete`,
`recover`, `help`, `new-id`. State is a single atomic `family.json` per
named family; heartbeat is the mtime of a 0-byte file; journal is an
optional linked-log audit trail.

See keeper-plan.md (repo root) for the full design rationale and the
9-round review history.
"""
from keeper.checkpoint import (
    join,
    beat,
    complete,
    recover,
    status,
    validate,
    snapshot,
    new_id,
    family_dir,
    family_json_path,
    snapshots_dir,
    read_state,
    AUTO_ESCALATION_INTERVAL,
    BRIEF_KEYS,
    QUALITY_RUBRIC,
    QUALITY_THRESHOLD_DEFAULT,
    SCHEMA_VERSION,
    SNAPSHOT_KEEP_COUNT,
    FAMILY_NAME_RE,
)

__all__ = [
    "join",
    "beat",
    "complete",
    "recover",
    "status",
    "validate",
    "snapshot",
    "new_id",
    "family_dir",
    "family_json_path",
    "snapshots_dir",
    "read_state",
    "AUTO_ESCALATION_INTERVAL",
    "BRIEF_KEYS",
    "QUALITY_RUBRIC",
    "QUALITY_THRESHOLD_DEFAULT",
    "SCHEMA_VERSION",
    "SNAPSHOT_KEEP_COUNT",
    "FAMILY_NAME_RE",
]
