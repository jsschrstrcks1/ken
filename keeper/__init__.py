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
    install_hooks,
    new_id,
)
from keeper.personas import (
    Persona,
    load_all_personas,
    load_persona,
    parse_frontmatter,
    roster_for_repo,
    filter_roster,
)
from keeper.review import (
    build_review,
    build_persona_prompt,
    render_review_text,
    detect_repo_name,
)
# Re-export the rest of the keeper.checkpoint top-level names so the
# original __all__ list still works:
from keeper.checkpoint import (
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
    # core
    "join", "beat", "complete", "recover", "status", "validate",
    "snapshot", "install_hooks", "new_id",
    # state helpers
    "family_dir", "family_json_path", "snapshots_dir", "read_state",
    # constants
    "AUTO_ESCALATION_INTERVAL", "BRIEF_KEYS", "QUALITY_RUBRIC",
    "QUALITY_THRESHOLD_DEFAULT", "SCHEMA_VERSION", "SNAPSHOT_KEEP_COUNT",
    "FAMILY_NAME_RE",
    # personas + review (Stage 2 — review is dry-run only for now)
    "Persona", "load_all_personas", "load_persona", "parse_frontmatter",
    "roster_for_repo", "filter_roster",
    "build_review", "build_persona_prompt", "render_review_text",
    "detect_repo_name",
]
