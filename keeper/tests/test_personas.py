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


# ─── Live mode (mocked adapter; no real API calls) ──────────────────────

def test_build_persona_messages_split():
    """build_persona_messages returns (system, user) split correctly."""
    from keeper.review import build_persona_messages
    p = Persona(
        name="test-p",
        body="You are TestP.",
        criteria=["a", "b", "c"],
        penalty_phrases=["x", "y"],
    )
    state = {"family": "demo", "goal": "g"}
    sys_p, user_p = build_persona_messages(p, state, [])
    # System prompt should have persona body + protocol + JSON requirement
    assert "[PERSONA — test-p]" in sys_p
    assert "You are TestP." in sys_p
    assert "Respond in JSON" in sys_p
    assert "comment" in sys_p
    # User prompt should have data only, not protocol
    assert "CURRENT FAMILY STATE" in user_p
    assert '"goal": "g"' in user_p
    assert "Follow this protocol" not in user_p


def test_run_review_live_with_mocked_adapter(tmp_repo, monkeypatch):
    """Live mode invokes adapter.query per persona and aggregates results."""
    from keeper.checkpoint import join, beat
    from keeper.review import run_review_live
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)

    # Build a fake adapter that returns a deterministic response.
    invoked = []
    class FakeAdapter:
        def query(self, prompt, system):
            invoked.append({"prompt_chars": len(prompt), "system_chars": len(system)})
            return {
                "response": {
                    "comment": "mock critique",
                    "aggregate_score": 7,
                    "confidence": 0.8,
                },
                "usage": {
                    "model": "fake",
                    "input_tokens": 1000,
                    "output_tokens": 50,
                    "estimated_cost_usd": 0.01,
                },
            }

    # Monkeypatch the adapter loader to return our fake.
    import keeper.review
    monkeypatch.setattr(
        keeper.review, "_import_adapters",
        lambda: {"fake": FakeAdapter()},
    )

    review = run_review_live(
        "ports",
        repo_name="ken",
        model="fake",
        max_parallel=2,
        root=tmp_repo,
    )
    assert review["live"] is True
    assert "results" in review
    assert review["actual_cost_usd"] > 0
    # Every roster member produced a result
    for r in review["roster"]:
        assert r["name"] in review["results"]
        entry = review["results"][r["name"]]
        assert entry.get("comment") == "mock critique"
        assert entry.get("aggregate_score") == 7
    # Adapter was called once per persona
    assert len(invoked) == len(review["roster"])


def test_run_review_live_handles_adapter_error(tmp_repo, monkeypatch):
    """If the adapter raises, the persona's result records the error
    but other personas still run."""
    from keeper.checkpoint import join
    from keeper.review import run_review_live
    join("ports", goal="g", root=tmp_repo)

    call_count = [0]
    class FlakyAdapter:
        def query(self, prompt, system):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("simulated network failure")
            return {
                "response": {"comment": "ok", "aggregate_score": 5},
                "usage": {"estimated_cost_usd": 0.005},
            }

    import keeper.review
    monkeypatch.setattr(
        keeper.review, "_import_adapters",
        lambda: {"fake": FlakyAdapter()},
    )
    review = run_review_live(
        "ports", repo_name="ken", model="fake", max_parallel=1, root=tmp_repo,
    )
    # At least one error and at least one success
    has_error = any("error" in r for r in review["results"].values())
    has_success = any(r.get("comment") == "ok" for r in review["results"].values())
    assert has_error and has_success


def test_run_review_live_handles_non_dict_response(tmp_repo, monkeypatch):
    """Adapter returns plain text — fallback comment extraction should work."""
    from keeper.checkpoint import join
    from keeper.review import run_review_live
    join("ports", goal="g", root=tmp_repo)

    class TextAdapter:
        def query(self, prompt, system):
            return {
                "response": "just a plain string critique",
                "usage": {"estimated_cost_usd": 0.005},
            }

    import keeper.review
    monkeypatch.setattr(
        keeper.review, "_import_adapters",
        lambda: {"fake": TextAdapter()},
    )
    review = run_review_live(
        "ports", repo_name="ken", model="fake", root=tmp_repo,
    )
    # Every result should have SOME comment, even if not the JSON shape we asked for
    for entry in review["results"].values():
        assert "comment" in entry
        assert entry["comment"]


def test_run_review_live_unknown_model_errors(tmp_repo, monkeypatch):
    from keeper.checkpoint import join
    from keeper.review import run_review_live, LiveReviewError
    join("ports", goal="g", root=tmp_repo)

    import keeper.review
    monkeypatch.setattr(
        keeper.review, "_import_adapters", lambda: {"gpt": object()},
    )
    with pytest.raises(LiveReviewError, match="unknown model"):
        run_review_live("ports", repo_name="ken", model="nonexistent", root=tmp_repo)


def test_render_review_text_with_results(tmp_repo, monkeypatch):
    """Live-mode render shows comments inline, replaces dry-run footer."""
    from keeper.checkpoint import join
    from keeper.review import run_review_live, render_review_text
    join("ports", goal="g", root=tmp_repo)

    class FakeAdapter:
        def query(self, prompt, system):
            return {
                "response": {"comment": "fake critique", "aggregate_score": 6},
                "usage": {"estimated_cost_usd": 0.01},
            }
    import keeper.review
    monkeypatch.setattr(
        keeper.review, "_import_adapters", lambda: {"fake": FakeAdapter()},
    )
    review = run_review_live(
        "ports", repo_name="ken", model="fake", root=tmp_repo,
    )
    out = render_review_text(review)
    assert "Comments:" in out
    assert "fake critique" in out
    assert "[6/10]" in out
    assert "LIVE —" in out
    assert "DRY RUN" not in out
    assert "Actual cost:" in out


def test_cli_review_live_aborts_on_no_confirmation(tmp_repo, capsys, monkeypatch):
    """CLI live mode without --yes prompts; declining aborts."""
    from keeper.checkpoint import main
    main(["join", "--family", "ports", "--goal", "g"])
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda *a, **kw: "n")
    rc = main(["review", "--family", "ports", "--repo", "ken", "--live"])
    assert rc != 0
    assert "aborted" in capsys.readouterr().err


# ─── keeper complete --review (gate) ────────────────────────────────────

def _populate_complete_state(family: str, root: Path) -> None:
    """Populate enough state that validate passes; isolates the review gate."""
    from keeper.checkpoint import join, beat
    real_file = root / "fake_module.py"
    real_file.write_text("# placeholder\n")
    join(family, goal="ship Stage 2", root=root)
    beat(family,
         action="implemented review gate",
         phase="implementation",
         next_step="run tests",
         files=["fake_module.py"],
         decision=("review-threshold default 7", "stricter blocks more"),
         root=root)


def _mock_adapters(monkeypatch, scores: dict[str, int]):
    """Patch _import_adapters to return a fake adapter that returns
    canned aggregate_scores per persona."""
    import keeper.review

    class ScoreByPersonaAdapter:
        def query(self, prompt, system):
            # Crude: detect the persona name from the system prompt header.
            persona_name = None
            for line in system.splitlines():
                if line.startswith("[PERSONA — "):
                    persona_name = line.split("—", 1)[1].rstrip("]").strip()
                    break
            score = scores.get(persona_name, 5)
            return {
                "response": {
                    "comment": f"mock critique from {persona_name} at score {score}",
                    "aggregate_score": score,
                    "confidence": 0.8,
                },
                "usage": {"estimated_cost_usd": 0.01},
            }
    monkeypatch.setattr(
        keeper.review, "_import_adapters",
        lambda: {"gpt": ScoreByPersonaAdapter(), "fake": ScoreByPersonaAdapter()},
    )


def test_complete_review_passes_when_all_low(tmp_repo, monkeypatch, capsys):
    """If every persona returns aggregate_score < threshold, review gate passes."""
    from keeper.checkpoint import complete, read_state
    _populate_complete_state("ports", tmp_repo)
    _mock_adapters(monkeypatch, scores={})  # default 5/10 across the board
    s = complete(
        "ports", summary="ok", review=True,
        review_threshold=7, root=tmp_repo,
    )
    assert s["ended_cleanly"] is True


def test_complete_review_blocks_on_strong_critique(tmp_repo, monkeypatch, capsys):
    """If any persona returns aggregate_score >= threshold, refuses."""
    from keeper.checkpoint import complete
    _populate_complete_state("ports", tmp_repo)
    _mock_adapters(monkeypatch, scores={"skeptic": 9})  # one strong critique
    with pytest.raises(SystemExit) as exc:
        complete(
            "ports", summary="x", review=True,
            review_threshold=7, root=tmp_repo,
        )
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "strong critique" in err
    assert "skeptic" in err
    assert "9/10" in err


def test_complete_review_threshold_configurable(tmp_repo, monkeypatch, capsys):
    """Lowering threshold catches medium-confidence critiques too."""
    from keeper.checkpoint import complete
    _mock_adapters(monkeypatch, scores={"skeptic": 6})
    # Two separate families so the second isn't re-joining a completed one.
    _populate_complete_state("ports-a", tmp_repo)
    _populate_complete_state("ports-b", tmp_repo)
    # Threshold 7 → 6 passes
    s = complete(
        "ports-a", summary="ok", review=True,
        review_threshold=7, root=tmp_repo,
    )
    assert s["ended_cleanly"] is True
    # Threshold 5 → 6 now blocks
    with pytest.raises(SystemExit):
        complete(
            "ports-b", summary="x", review=True,
            review_threshold=5, root=tmp_repo,
        )


def test_complete_review_force_bypasses_gate(tmp_repo, monkeypatch):
    """--force skips both validate AND review gates."""
    from keeper.checkpoint import complete
    _populate_complete_state("ports", tmp_repo)
    _mock_adapters(monkeypatch, scores={"skeptic": 10})  # would block normally
    s = complete(
        "ports", summary="emergency", force=True,
        review=True, root=tmp_repo,
    )
    assert s["ended_cleanly"] is True


def test_complete_review_errors_if_adapters_unavailable(tmp_repo, monkeypatch, capsys):
    """If review can't run (no adapters), refuse rather than skip silently."""
    from keeper.checkpoint import complete
    from keeper.review import LiveReviewError
    import keeper.review
    _populate_complete_state("ports", tmp_repo)

    def boom():
        raise LiveReviewError("simulated: no adapters available")
    monkeypatch.setattr(keeper.review, "_import_adapters", boom)

    with pytest.raises(SystemExit):
        complete(
            "ports", summary="x", review=True, root=tmp_repo,
        )
    err = capsys.readouterr().err
    assert "review failed to run" in err
    assert "no adapters available" in err


def test_complete_review_filters_propagate(tmp_repo, monkeypatch):
    """--review-persona / --review-no-persona reach the review call."""
    from keeper.checkpoint import complete
    import keeper.review

    seen_includes = []
    seen_excludes = []
    real_run = keeper.review.run_review_live

    def capture(*args, **kwargs):
        seen_includes.append(kwargs.get("include"))
        seen_excludes.append(kwargs.get("exclude"))
        return {
            "state_present": True,
            "live": True,
            "results": {},
            "roster": [],
            "actual_cost_usd": 0,
        }
    monkeypatch.setattr(keeper.review, "run_review_live", capture)

    _populate_complete_state("ports", tmp_repo)
    complete(
        "ports", summary="x", review=True,
        review_include=["skeptic"],
        review_exclude=["architect"],
        root=tmp_repo,
    )
    assert seen_includes == [["skeptic"]]
    assert seen_excludes == [["architect"]]


def test_complete_review_non_dict_response_doesnt_block(tmp_repo, monkeypatch):
    """If a persona returns plain text (no aggregate_score), it can't
    block — there's nothing to compare to the threshold."""
    from keeper.checkpoint import complete
    _populate_complete_state("ports", tmp_repo)
    import keeper.review
    class TextAdapter:
        def query(self, prompt, system):
            return {
                "response": "just some text, not JSON",
                "usage": {"estimated_cost_usd": 0.01},
            }
    monkeypatch.setattr(
        keeper.review, "_import_adapters",
        lambda: {"gpt": TextAdapter()},
    )
    # Should not block — no aggregate_score, no comparison possible
    s = complete(
        "ports", summary="ok", review=True, root=tmp_repo,
    )
    assert s["ended_cleanly"] is True


def test_cli_complete_review_blocks(tmp_repo, monkeypatch, capsys):
    """CLI: keeper complete --review with a strong critique returns non-zero."""
    from keeper.checkpoint import main
    main(["join", "--family", "ports", "--goal", "g"])
    main(["beat", "--family", "ports", "--action", "did stuff",
          "--decision", "x", "y", "--next-step", "next",
          "--phase", "phase", "--files",
          str(tmp_repo / "fake_module.py")])
    (tmp_repo / "fake_module.py").write_text("# placeholder\n")
    _mock_adapters(monkeypatch, scores={"skeptic": 9})
    capsys.readouterr()
    rc = main(["complete", "--family", "ports", "--summary", "x",
               "--review", "--review-threshold", "7"])
    assert rc != 0
    err = capsys.readouterr().err
    assert "strong critique" in err
