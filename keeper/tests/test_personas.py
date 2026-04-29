"""Tests for keeper.personas + keeper.review (dry-run mode).

Coverage:
  - frontmatter parser handles scalars, block lists, inline lists,
    booleans, integers, comments, blank lines
  - persona loading from disk
  - roster composition (baseline + repo + repos[])
  - filter_roster (include adds, exclude removes)
  - build_review respects filtering, surfaces domain-expert notes
  - dry-run prompt structure (state included, journal included,
    protocol footer present)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from keeper import checkpoint as kc
from keeper.checkpoint import join, beat
from keeper.personas import (
    Persona,
    PERSONAS_DIR,
    filter_roster,
    load_all_personas,
    load_persona,
    parse_frontmatter,
    roster_for_repo,
)
from keeper.review import (
    build_persona_prompt,
    build_review,
    detect_repo_name,
    render_review_text,
)


# ─── Frontmatter parser ─────────────────────────────────────────────────

def test_parse_frontmatter_scalars():
    text = """---
name: skeptic
description: looks for assumptions
baseline: true
criticality: 1
---

# Body
"""
    fm, body = parse_frontmatter(text)
    assert fm["name"] == "skeptic"
    assert fm["description"] == "looks for assumptions"
    assert fm["baseline"] is True
    assert fm["criticality"] == 1
    assert body.strip() == "# Body"


def test_parse_frontmatter_block_list():
    text = """---
criteria:
  - one
  - two
  - three
---

body
"""
    fm, _ = parse_frontmatter(text)
    assert fm["criteria"] == ["one", "two", "three"]


def test_parse_frontmatter_inline_list():
    text = """---
repos: [a, b, c]
---

body
"""
    fm, _ = parse_frontmatter(text)
    assert fm["repos"] == ["a", "b", "c"]


def test_parse_frontmatter_quoted_strings():
    text = """---
penalty_phrases:
  - "quoted phrase"
  - 'single quoted'
  - unquoted
---

body
"""
    fm, _ = parse_frontmatter(text)
    assert fm["penalty_phrases"] == ["quoted phrase", "single quoted", "unquoted"]


def test_parse_frontmatter_no_frontmatter():
    text = "# Just a body\n\nNo frontmatter here.\n"
    fm, body = parse_frontmatter(text)
    assert fm == {}
    assert body == text


def test_parse_frontmatter_empty():
    fm, body = parse_frontmatter("")
    assert fm == {}
    assert body == ""


def test_parse_frontmatter_comments_and_blanks():
    text = """---
# this is a comment
name: skeptic

# another comment
baseline: true
---

body
"""
    fm, _ = parse_frontmatter(text)
    assert fm == {"name": "skeptic", "baseline": True}


def test_parse_frontmatter_negative_int():
    text = """---
score: -5
---

body
"""
    fm, _ = parse_frontmatter(text)
    assert fm["score"] == -5


# ─── Loading from disk ─────────────────────────────────────────────────

def test_load_persona_skeptic():
    p = load_persona(PERSONAS_DIR / "skeptic.md")
    assert p.name == "skeptic"
    assert "assumption_examined" in p.criteria
    assert any("best practices" in pp for pp in p.penalty_phrases)
    assert "Skeptic" in p.body
    assert p.source_path.name == "skeptic.md"


def test_load_persona_inthewake_weather_realist():
    p = load_persona(PERSONAS_DIR / "inthewake" / "weather-realist.md")
    assert p.name == "weather-realist"
    assert p.repo == "InTheWake"
    assert p.criticality == 1
    assert p.baseline is False


def test_load_persona_heritage_shared_repos():
    p = load_persona(PERSONAS_DIR / "heritage-cookbooks" / "voice-keeper.md")
    assert p.repos == ["Grandmasrecipes", "Grannysrecipes", "MomsRecipes"]
    assert p.repo is None


def test_load_persona_domain_expert_caveat():
    p = load_persona(PERSONAS_DIR / "manateecreeksheep" / "flock-guardian.md")
    assert p.needs_domain_expert_review is True


def test_load_all_personas_skips_readme():
    personas = load_all_personas()
    names = [p.name for p in personas]
    assert "README" not in names
    assert "readme" not in names
    # We have 31 personas drafted (3 baseline + content-quality + UX + 26 repo-specific)
    assert len(personas) >= 30


# ─── Roster composition ────────────────────────────────────────────────

def _make_persona(name, **kw):
    return Persona(name=name, body="", **kw)


def test_roster_baseline_only_when_no_repo():
    personas = [
        _make_persona("skeptic", baseline=True),
        _make_persona("weather-realist", repo="InTheWake"),
        _make_persona("voice-keeper", repos=["X", "Y"]),
    ]
    r = roster_for_repo(personas, None)
    assert [p.name for p in r] == ["skeptic"]


def test_roster_baseline_plus_repo_match():
    personas = [
        _make_persona("skeptic", baseline=True),
        _make_persona("weather-realist", repo="InTheWake"),
        _make_persona("anchorage-tactician", repo="InTheWake"),
        _make_persona("source-integrity", repo="Allrecipes"),
    ]
    r = roster_for_repo(personas, "InTheWake")
    names = sorted([p.name for p in r])
    assert names == ["anchorage-tactician", "skeptic", "weather-realist"]


def test_roster_baseline_plus_repos_list_match():
    personas = [
        _make_persona("skeptic", baseline=True),
        _make_persona("voice-keeper", repos=["Grandmasrecipes", "MomsRecipes"]),
        _make_persona("weather-realist", repo="InTheWake"),
    ]
    r = roster_for_repo(personas, "Grandmasrecipes")
    assert sorted([p.name for p in r]) == ["skeptic", "voice-keeper"]


def test_roster_no_match_returns_baseline_only():
    personas = [
        _make_persona("skeptic", baseline=True),
        _make_persona("weather-realist", repo="InTheWake"),
    ]
    r = roster_for_repo(personas, "unknown-repo")
    assert [p.name for p in r] == ["skeptic"]


# ─── Filter ─────────────────────────────────────────────────────────────

def test_filter_exclude_drops_persona():
    roster = [
        _make_persona("skeptic", baseline=True),
        _make_persona("architect", baseline=True),
        _make_persona("weather-realist", repo="InTheWake"),
    ]
    out = filter_roster(roster, exclude=["architect"])
    names = [p.name for p in out]
    assert "architect" not in names
    assert "skeptic" in names
    assert "weather-realist" in names


def test_filter_include_adds_from_outside_roster():
    roster = [_make_persona("skeptic", baseline=True)]
    all_personas = roster + [
        _make_persona("compliance-officer", repo="InTheWake"),
    ]
    out = filter_roster(roster, include=["compliance-officer"], all_personas=all_personas)
    assert sorted([p.name for p in out]) == ["compliance-officer", "skeptic"]


def test_filter_include_idempotent():
    roster = [_make_persona("skeptic", baseline=True)]
    out = filter_roster(roster, include=["skeptic"], all_personas=roster)
    assert [p.name for p in out] == ["skeptic"]
    assert len(out) == 1


# ─── Review (dry-run) ───────────────────────────────────────────────────

def test_build_review_no_family_returns_state_present_false(tmp_repo):
    review = build_review("nope", root=tmp_repo)
    assert review["state_present"] is False
    assert review["roster"] == []
    assert review["prompts"] == {}


def test_build_review_includes_state_in_prompt(tmp_repo):
    join("ports", goal="ship the thing", root=tmp_repo)
    beat("ports", action="step 1", root=tmp_repo)
    review = build_review("ports", repo_name="ken", root=tmp_repo)
    assert review["state_present"] is True
    # baseline + ken-specific personas should both appear
    persona_names = {r["name"] for r in review["roster"]}
    assert "skeptic" in persona_names
    assert "downstream-impact-guardian" in persona_names
    # Each prompt should embed the state and the protocol
    for name, prompt in review["prompts"].items():
        assert "ship the thing" in prompt        # goal in state
        assert "Follow this protocol exactly" in prompt
        assert "MIN of the 3 scores" in prompt
        # Operator metadata stripped
        assert "instance_token" not in prompt


def test_build_review_filters_apply(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    review = build_review(
        "ports", repo_name="ken", exclude=["skeptic"], root=tmp_repo
    )
    persona_names = {r["name"] for r in review["roster"]}
    assert "skeptic" not in persona_names


def test_build_review_includes_outside_repo(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    review = build_review(
        "ports",
        repo_name="ken",
        include=["weather-realist"],   # would normally be InTheWake-only
        root=tmp_repo,
    )
    persona_names = {r["name"] for r in review["roster"]}
    assert "weather-realist" in persona_names


def test_build_review_surfaces_domain_expert_note(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    review = build_review(
        "ports", repo_name="manateecreeksheep", root=tmp_repo
    )
    assert any("domain-expert" in n for n in review["notes"])


def test_build_review_cost_estimate_scales_with_roster(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    r1 = build_review("ports", repo_name="ken", root=tmp_repo)
    r2 = build_review(
        "ports",
        repo_name="ken",
        exclude=[p["name"] for p in r1["roster"][:-1]],
        root=tmp_repo,
    )
    assert r2["cost_estimate_usd"] < r1["cost_estimate_usd"]
    assert len(r2["roster"]) < len(r1["roster"])


def test_render_review_text_structure(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    review = build_review("ports", repo_name="ken", root=tmp_repo)
    out = render_review_text(review, show_prompts=False)
    assert "keeper review" in out
    assert "Roster:" in out
    assert "Estimated cost:" in out
    assert "DRY RUN" in out
    # Without --show-prompts, the prompt body shouldn't appear
    assert "Follow this protocol exactly" not in out


def test_render_review_text_with_prompts(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    review = build_review("ports", repo_name="ken", root=tmp_repo)
    out = render_review_text(review, show_prompts=True)
    assert "Follow this protocol exactly" in out


def test_detect_repo_name_uses_root_basename(tmp_repo):
    # tmp_repo is a Path under /tmp/.../<random-name>; its basename is the repo name
    name = detect_repo_name(tmp_repo)
    assert name == tmp_repo.name


# ─── Persona prompt assembly ────────────────────────────────────────────

def test_build_persona_prompt_has_required_sections():
    p = Persona(
        name="test-p",
        body="You are TestP.",
        criteria=["a", "b", "c"],
        penalty_phrases=["bad", "worse"],
    )
    state = {"family": "demo", "goal": "test goal", "instance_token": "secret"}
    journal = [{"type": "join", "ts": "2026-01-01"}]
    prompt = build_persona_prompt(p, state, journal)
    assert "[PERSONA — test-p]" in prompt
    assert "You are TestP." in prompt
    assert '"family": "demo"' in prompt
    assert '"goal": "test goal"' in prompt
    assert "instance_token" not in prompt   # operator metadata stripped
    assert "RECENT JOURNAL EVENTS" in prompt
    assert '"type": "join"' in prompt
    assert "10 candidate critiques" in prompt
    assert "MIN of the 3 scores" in prompt
    assert "no critique cleared threshold for test-p" in prompt


def test_build_persona_prompt_handles_empty_journal():
    p = Persona(name="test-p", body="x", criteria=["a"])
    state = {"family": "demo"}
    prompt = build_persona_prompt(p, state, [])
    assert "(none)" in prompt


# ─── CLI ────────────────────────────────────────────────────────────────

def test_cli_review_text_output(tmp_repo, capsys):
    from keeper.checkpoint import main
    main(["join", "--family", "ports", "--goal", "g"])
    main(["beat", "--family", "ports", "--action", "step 1"])
    capsys.readouterr()
    rc = main(["review", "--family", "ports", "--repo", "ken"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "keeper review" in out
    assert "Roster:" in out
    assert "DRY RUN" in out


def test_cli_review_json_output(tmp_repo, capsys):
    from keeper.checkpoint import main
    main(["join", "--family", "ports", "--goal", "g"])
    capsys.readouterr()
    rc = main(["review", "--family", "ports", "--repo", "ken", "--json"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["family"] == "ports"
    assert parsed["repo"] == "ken"
    assert parsed["state_present"] is True
    assert "roster" in parsed
    assert "prompts" in parsed


def test_cli_review_persona_filter(tmp_repo, capsys):
    from keeper.checkpoint import main
    main(["join", "--family", "ports", "--goal", "g"])
    capsys.readouterr()
    rc = main(["review", "--family", "ports", "--repo", "ken",
               "--no-persona", "skeptic", "--json"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    names = {r["name"] for r in parsed["roster"]}
    assert "skeptic" not in names


def test_cli_review_missing_family(tmp_repo, capsys):
    from keeper.checkpoint import main
    rc = main(["review", "--family", "nope"])
    assert rc != 0
