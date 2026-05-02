"""Persona loader for `keeper review`.

Each persona lives as a markdown file under keeper/personas/ with simple
YAML-ish frontmatter. We hand-roll a small parser to keep keeper stdlib-only.

Layout:
    personas/
    ├── skeptic.md, architect.md, ...      # baseline (frontmatter: baseline: true)
    └── <repo>/<name>.md                   # repo-specific (frontmatter: repo: <repo>)

Frontmatter format (subset of YAML — what our files actually use):
    ---
    name: skeptic
    baseline: true
    description: ...
    criteria:
      - assumption_examined
      - falsifiable
      - alternative_considered
    penalty_phrases:
      - "consider best practices"
      - "may want to think about"
    when_not_to_use: ...
    ---

    # Markdown body — used as the persona's system prompt
    ...
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PERSONAS_DIR = Path(__file__).parent / "personas"


@dataclass
class Persona:
    name: str
    body: str                              # markdown body, used as system prompt
    criteria: list[str] = field(default_factory=list)
    penalty_phrases: list[str] = field(default_factory=list)
    when_not_to_use: str | None = None
    description: str | None = None
    repo: str | None = None                # single-repo scope
    repos: list[str] | None = None         # multi-repo scope (heritage cookbooks)
    baseline: bool = False                 # applies to every repo
    criticality: int | None = None
    needs_domain_expert_review: bool = False
    source_path: Path | None = None


# ─── Frontmatter parser (no external deps) ──────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file into (frontmatter_dict, body).
    Returns ({}, text) if no frontmatter is present.
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]   # skip the closing ---\n
    return _parse_simple_yaml(fm_text), body


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the subset of YAML our persona files use:
      key: scalar           → string / int / bool
      key: [a, b, c]        → list (inline)
      key:                  → list (block, items "  - x" on following lines)
        - item
    """
    out: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()

        if val == "":
            # Block list: collect "- item" lines that follow
            items: list[Any] = []
            i += 1
            while i < len(lines):
                sub = lines[i]
                sub_stripped = sub.strip()
                if sub_stripped.startswith("- "):
                    items.append(_coerce(sub_stripped[2:].strip()))
                    i += 1
                elif sub_stripped == "":
                    i += 1
                else:
                    break
            out[key] = items
            continue

        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1]
            out[key] = [_coerce(x.strip()) for x in inner.split(",") if x.strip()]
        else:
            out[key] = _coerce(val)
        i += 1
    return out


def _coerce(s: str) -> Any:
    """Strip inline '#'-comments + surrounding quotes, coerce bool/int,
    leave everything else as a string."""
    s = _strip_inline_comment(s).strip()
    if s == "":
        return ""
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s == "null" or s == "None":
        return None
    if s.lstrip("-").isdigit():
        try:
            return int(s)
        except ValueError:
            pass
    return s


def _strip_inline_comment(s: str) -> str:
    """Strip a '#'-comment that follows whitespace, but keep '#' inside
    quotes and at start of line (those are caller's problem). Conservative:
    only strips when '#' is preceded by whitespace AND we're not inside a
    quoted string."""
    in_q: str | None = None  # tracks quote char if we're inside one
    for i, ch in enumerate(s):
        if in_q is None:
            if ch in ('"', "'"):
                in_q = ch
            elif ch == "#" and i > 0 and s[i - 1].isspace():
                return s[:i].rstrip()
        else:
            if ch == in_q and (i == 0 or s[i - 1] != "\\"):
                in_q = None
    return s


# ─── Loading ────────────────────────────────────────────────────────────

def load_persona(path: Path) -> Persona:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    return Persona(
        name=fm.get("name", path.stem),
        body=body.strip(),
        criteria=list(fm.get("criteria") or []),
        penalty_phrases=list(fm.get("penalty_phrases") or []),
        when_not_to_use=fm.get("when_not_to_use"),
        description=fm.get("description"),
        repo=fm.get("repo"),
        repos=fm.get("repos"),
        baseline=bool(fm.get("baseline", False)),
        criticality=fm.get("criticality"),
        needs_domain_expert_review=bool(fm.get("needs_domain_expert_review", False)),
        source_path=path,
    )


def load_all_personas(personas_dir: Path | None = None) -> list[Persona]:
    """Load every persona under personas_dir. Skips README.md and
    silently skips anything that fails to parse (with a stderr warning)."""
    pdir = personas_dir or PERSONAS_DIR
    out: list[Persona] = []
    for path in sorted(pdir.rglob("*.md")):
        if path.name.upper() == "README.MD":
            continue
        try:
            out.append(load_persona(path))
        except Exception as e:
            sys.stderr.write(f"[keeper] failed to load persona {path}: {e}\n")
    return out


# ─── Roster composition ─────────────────────────────────────────────────

def roster_for_repo(
    personas: list[Persona],
    repo_name: str | None,
) -> list[Persona]:
    """Return personas applicable to a repo:
       all baseline + any matching `repo:` + any with `repo_name in repos[]`.

    If repo_name is None, returns baseline only."""
    out = []
    for p in personas:
        if p.baseline:
            out.append(p)
        elif repo_name and p.repo == repo_name:
            out.append(p)
        elif repo_name and p.repos and repo_name in p.repos:
            out.append(p)
    return out


def filter_roster(
    roster: list[Persona],
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    all_personas: list[Persona] | None = None,
) -> list[Persona]:
    """Apply --persona / --no-persona filtering.

    `include` ADDS a persona to the roster (even if it wasn't in the
    repo-scoped roster — useful for one-off invocations).
    `exclude` REMOVES a persona from the roster.
    """
    out = list(roster)
    if include:
        present = {p.name for p in out}
        if all_personas:
            for p in all_personas:
                if p.name in include and p.name not in present:
                    out.append(p)
                    present.add(p.name)
    if exclude:
        out = [p for p in out if p.name not in exclude]
    return out
