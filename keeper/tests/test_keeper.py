"""Stage 1 unit tests for keeper.

Coverage:
  - state read/write with .backup safety net
  - fresh join, takeover (force + stale-confirmed), held rejection
  - beat: merge semantics, journal append, beat_count, decision
  - complete: ended_cleanly, archive markdown
  - recover: text + json output, .backup fallback
  - journal: linked log via prev_event_id, partial-write tolerance,
    PIPE_BUF size limit
  - schema migration: version mismatch errors
  - CLI: help, new-id, family resolution precedence
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from keeper import checkpoint as kc
from keeper.checkpoint import (
    BRIEF_KEYS,
    SCHEMA_VERSION,
    atomic_write_state,
    beat,
    complete,
    family_dir,
    family_json_backup_path,
    family_json_path,
    heartbeat_path,
    is_stale,
    join,
    journal_append,
    journal_path,
    journal_tail,
    new_id,
    read_state,
    recover,
    status,
    main,
)


# ─── Path / identity ────────────────────────────────────────────────────

def test_new_id_format():
    sid = new_id()
    assert sid.startswith("sess-")
    assert len(sid) == len("sess-20260428T015432Z-ac3592")


def test_new_id_unique():
    assert len({new_id() for _ in range(100)}) == 100


def test_family_name_validation_accepts(tmp_repo):
    join("ports", root=tmp_repo)
    assert family_json_path("ports", tmp_repo).exists()


def test_family_name_validation_rejects_uppercase(tmp_repo):
    with pytest.raises(ValueError):
        join("PORTS", root=tmp_repo)


def test_family_name_validation_rejects_underscore(tmp_repo):
    with pytest.raises(ValueError):
        join("port_s", root=tmp_repo)


def test_family_name_validation_rejects_too_long(tmp_repo):
    with pytest.raises(ValueError):
        join("a" * 33, root=tmp_repo)


# ─── Fresh join ─────────────────────────────────────────────────────────

def test_fresh_join_creates_state(tmp_repo):
    state = join("ports", goal="hello", root=tmp_repo)
    assert state["family"] == "ports"
    assert state["generation"] == 1
    assert state["goal"] == "hello"
    assert state["instance_token"]
    assert state["session_id"].startswith("sess-")
    assert family_json_path("ports", tmp_repo).exists()
    assert heartbeat_path("ports", tmp_repo).exists()
    assert state["ended_cleanly"] is False
    assert state["beat_count"] == 0


def test_fresh_join_writes_journal(tmp_repo):
    join("ports", goal="hello", root=tmp_repo)
    entries = journal_tail("ports", root=tmp_repo)
    assert len(entries) == 1
    assert entries[0]["type"] == "join"
    assert entries[0]["prev_event_id"] is None
    assert entries[0]["payload"]["first"] is True


# ─── Held / takeover ────────────────────────────────────────────────────

def test_join_rejects_when_held_fresh(tmp_repo):
    join("ports", root=tmp_repo)
    with pytest.raises(SystemExit):
        join("ports", root=tmp_repo, interactive=False)


def test_join_force_takes_over(tmp_repo):
    s1 = join("ports", root=tmp_repo)
    s2 = join("ports", force=True, reason="testing", root=tmp_repo)
    assert s2["generation"] == 2
    assert s2["session_id"] != s1["session_id"]
    assert s2["instance_token"] != s1["instance_token"]
    # Journal records the takeover
    entries = journal_tail("ports", root=tmp_repo)
    types = [e["type"] for e in entries]
    assert "forced_takeover" in types


def test_takeover_warns_about_unclean_previous(tmp_repo):
    join("ports", root=tmp_repo)
    s2 = join("ports", force=True, root=tmp_repo)
    assert any("uncleanly" in w for w in s2["warnings"])


def test_takeover_no_warning_after_complete(tmp_repo):
    join("ports", root=tmp_repo)
    # Bypass the quality gate; we're testing takeover semantics, not handoff quality.
    complete("ports", summary="done", force=True, root=tmp_repo)
    s2 = join("ports", force=True, root=tmp_repo)
    assert not any("uncleanly" in w for w in s2["warnings"])


# ─── Beat ───────────────────────────────────────────────────────────────

def test_beat_increments_count(tmp_repo):
    join("ports", root=tmp_repo)
    s1 = beat("ports", action="step 1", root=tmp_repo)
    assert s1["beat_count"] == 1
    s2 = beat("ports", action="step 2", root=tmp_repo)
    assert s2["beat_count"] == 2


def test_beat_appends_to_working(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", action="step 1", root=tmp_repo)
    beat("ports", action="step 2", root=tmp_repo)
    state = read_state("ports", tmp_repo)
    assert "step 1" in state["working"]
    assert "step 2" in state["working"]


def test_beat_dedupes_arrays(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", action="same", root=tmp_repo)
    beat("ports", action="same", root=tmp_repo)
    state = read_state("ports", tmp_repo)
    assert state["working"].count("same") == 1


def test_beat_decision_appends_object(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", decision=("use vim", "muscle memory"), root=tmp_repo)
    state = read_state("ports", tmp_repo)
    assert state["decisions"] == [{"what": "use vim", "why": "muscle memory"}]


def test_beat_files_replaces(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", files=["a.py", "b.py"], root=tmp_repo)
    beat("ports", files=["c.py"], root=tmp_repo)
    state = read_state("ports", tmp_repo)
    assert state["files_in_play"] == ["c.py"]


def test_beat_without_join_errors(tmp_repo):
    with pytest.raises(SystemExit):
        beat("nope", action="x", root=tmp_repo)


def test_beat_links_journal_entries(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", action="a", root=tmp_repo)
    beat("ports", action="b", root=tmp_repo)
    entries = journal_tail("ports", root=tmp_repo)
    assert entries[0]["prev_event_id"] is None  # join
    assert entries[1]["prev_event_id"] == entries[0]["event_id"]  # beat 1
    assert entries[2]["prev_event_id"] == entries[1]["event_id"]  # beat 2


def test_beat_consumes_precompact_marker(tmp_repo):
    join("ports", root=tmp_repo)
    pending = family_dir("ports", tmp_repo) / "precompact.pending"
    pending.touch()
    beat("ports", action="x", root=tmp_repo)
    assert not pending.exists()
    types = [e["type"] for e in journal_tail("ports", root=tmp_repo)]
    assert "snapshot" in types


# ─── Complete ───────────────────────────────────────────────────────────

def test_complete_sets_ended_cleanly(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)
    # Bypass quality gate; this test is about the cycle, not the gate.
    s = complete("ports", summary="done", force=True, root=tmp_repo)
    assert s["ended_cleanly"] is True
    assert "completed_at" in s


def test_complete_archives_markdown(tmp_repo):
    join("ports", root=tmp_repo)
    complete("ports", summary="finished work", force=True, root=tmp_repo)
    cdir = family_dir("ports", tmp_repo) / "completed"
    archives = list(cdir.glob("ports_*_complete.md"))
    assert len(archives) == 1
    body = archives[0].read_text()
    assert "finished work" in body


def test_complete_without_join_errors(tmp_repo):
    with pytest.raises(SystemExit):
        complete("nope", root=tmp_repo)


# ─── Recover ────────────────────────────────────────────────────────────

def test_recover_returns_state_dict(tmp_repo, capsys):
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", next_step="ship it", root=tmp_repo)
    state = recover("ports", json_output=True, root=tmp_repo)
    assert state is not None
    assert state["family"] == "ports"
    assert state["next_step"] == "ship it"


def test_recover_text_output(tmp_repo, capsys):
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", next_step="ship it", root=tmp_repo)
    recover("ports", root=tmp_repo)
    out = capsys.readouterr().out
    assert "ports" in out
    assert ">>> NEXT STEP: ship it" in out


def test_recover_text_content_first(tmp_repo, capsys):
    """Goal/Working/Next Step must appear BEFORE the metadata footer."""
    join("ports", goal="my-goal", root=tmp_repo)
    beat("ports", action="my-action", next_step="my-next", root=tmp_repo)
    recover("ports", root=tmp_repo)
    out = capsys.readouterr().out
    goal_idx = out.index("my-goal")
    action_idx = out.index("my-action")
    next_idx = out.index("my-next")
    sep_idx = out.index("---")
    session_idx = out.index("session=")
    # Content before separator
    assert goal_idx < sep_idx
    assert action_idx < sep_idx
    assert next_idx < sep_idx
    # Metadata after separator
    assert sep_idx < session_idx


def test_recover_brief_returns_essentials_only(tmp_repo, capsys):
    """--brief drops operator metadata (session_id, instance_token, etc.)
    and the journal_tail. Keeps resume-essentials."""
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", next_step="ship it",
         files=["a.py"], root=tmp_repo)
    capsys.readouterr()
    recover("ports", json_output=True, brief=True, root=tmp_repo)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    # Has resume-essentials
    assert set(parsed.keys()) == set(BRIEF_KEYS)
    assert parsed["family"] == "ports"
    assert parsed["goal"] == "g"
    assert parsed["next_step"] == "ship it"
    assert "x" in parsed["working"]
    assert parsed["files_in_play"] == ["a.py"]
    # Doesn't have operator metadata
    assert "session_id" not in parsed
    assert "instance_token" not in parsed
    assert "generation" not in parsed
    assert "host" not in parsed
    assert "_recovery_meta" not in parsed
    assert "schema" not in parsed


def test_recover_full_json_keeps_everything(tmp_repo, capsys):
    """Without --brief, the full state dump remains intact."""
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)
    capsys.readouterr()
    recover("ports", json_output=True, brief=False, root=tmp_repo)
    parsed = json.loads(capsys.readouterr().out)
    assert "session_id" in parsed
    assert "instance_token" in parsed
    assert "_recovery_meta" in parsed


def test_recover_missing_family_returns_none(tmp_repo, capsys):
    r = recover("nope", root=tmp_repo)
    assert r is None


def test_recover_falls_back_to_backup(tmp_repo, capsys):
    join("ports", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)
    # Beat triggered: prior generation moved to .backup, new written.
    primary = family_json_path("ports", tmp_repo)
    backup = family_json_backup_path("ports", tmp_repo)
    assert backup.exists()
    # Corrupt the primary
    primary.write_text("{not valid json", encoding="utf-8")
    # recover should succeed via backup
    state = recover("ports", json_output=True, root=tmp_repo)
    assert state is not None
    err = capsys.readouterr().err
    assert "WARNING" in err
    assert "recovered from family.json.backup" in err


def test_recover_no_backup_returns_none(tmp_repo, capsys):
    join("ports", root=tmp_repo)
    primary = family_json_path("ports", tmp_repo)
    primary.write_text("{not valid", encoding="utf-8")
    # No backup yet because only one generation has been written
    backup = family_json_backup_path("ports", tmp_repo)
    if backup.exists():
        backup.unlink()
    r = recover("ports", root=tmp_repo)
    assert r is None


# ─── State write invariants ─────────────────────────────────────────────

def test_atomic_write_creates_backup_on_subsequent_write(tmp_repo):
    join("ports", root=tmp_repo)
    backup = family_json_backup_path("ports", tmp_repo)
    assert not backup.exists()  # first write, no prior generation
    beat("ports", action="x", root=tmp_repo)
    assert backup.exists()  # second write — prior moved to backup


def test_state_size_hard_cap(tmp_repo):
    join("ports", root=tmp_repo)
    huge = "x" * 9000
    with pytest.raises(ValueError, match="exceeds"):
        beat("ports", action=huge, root=tmp_repo)


# ─── Journal ────────────────────────────────────────────────────────────

def test_journal_partial_write_tolerated(tmp_repo):
    join("ports", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)
    j = journal_path("ports", tmp_repo)
    # Append a half-written line
    with j.open("a", encoding="utf-8") as f:
        f.write('{"ts":"2026-04-28T00:00:00+00:00","event_id":"abc","prev_e')
    entries = journal_tail("ports", root=tmp_repo)
    # Two valid entries (join + beat), partial line skipped
    assert len(entries) == 2


def test_journal_entry_size_limit(tmp_repo):
    join("ports", root=tmp_repo)
    state = read_state("ports", tmp_repo)
    huge = "x" * 5000
    with pytest.raises(ValueError, match="atomic-append limit"):
        journal_append(
            "ports", "note", {"big": huge},
            state["session_id"], state["instance_token"], tmp_repo,
        )


# ─── Schema migration ──────────────────────────────────────────────────

def test_schema_newer_rejected(tmp_repo):
    join("ports", root=tmp_repo)
    p = family_json_path("ports", tmp_repo)
    data = json.loads(p.read_text())
    data["schema"] = SCHEMA_VERSION + 1
    p.write_text(json.dumps(data))
    with pytest.raises(RuntimeError, match="newer"):
        read_state("ports", tmp_repo)


# ─── Stale detection ────────────────────────────────────────────────────

def test_fresh_family_not_stale(tmp_repo):
    join("ports", root=tmp_repo)
    assert not is_stale("ports", tmp_repo)


def test_old_heartbeat_marked_stale(tmp_repo):
    join("ports", root=tmp_repo)
    hb = heartbeat_path("ports", tmp_repo)
    # Backdate heartbeat by 2 hours
    old = (Path(hb).stat().st_mtime) - (2 * 3600)
    os.utime(hb, (old, old))
    assert is_stale("ports", tmp_repo)


# ─── CLI ────────────────────────────────────────────────────────────────

def test_cli_help_exits_ok(capsys):
    rc = main(["help"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "USAGE" in out
    assert "join" in out


def test_cli_no_args_shows_help(capsys):
    rc = main([])
    assert rc == 0
    assert "USAGE" in capsys.readouterr().out


def test_cli_new_id(capsys):
    rc = main(["new-id"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("sess-")


def test_cli_join_then_beat_then_complete(tmp_repo, capsys):
    assert main(["join", "--family", "ports", "--goal", "hi"]) == 0
    assert main(["beat", "--family", "ports", "--action", "did stuff"]) == 0
    # --force bypasses the quality gate (this test exercises the cycle,
    # not the gate; see test_complete_blocks_on_low_quality below).
    assert main(["complete", "--family", "ports", "--summary", "fin",
                 "--force"]) == 0
    state = read_state("ports", tmp_repo)
    assert state["ended_cleanly"] is True


def test_cli_recover_json(tmp_repo, capsys):
    main(["join", "--family", "ports"])
    main(["beat", "--family", "ports", "--next-step", "do X"])
    capsys.readouterr()  # drain
    rc = main(["recover", "--family", "ports", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["next_step"] == "do X"


def test_cli_resolve_family_from_env(tmp_repo, monkeypatch, capsys):
    monkeypatch.setenv("KEEPER_FAMILY", "ports")
    rc = main(["join"])
    assert rc == 0


def test_cli_resolve_family_from_conf(tmp_repo, capsys):
    conf = tmp_repo / ".claude" / "keeper.conf"
    conf.parent.mkdir(parents=True, exist_ok=True)
    conf.write_text("default_family = ports\n")
    rc = main(["join"])
    assert rc == 0


def test_cli_unspecified_family_errors(tmp_repo, monkeypatch, capsys):
    monkeypatch.delenv("KEEPER_FAMILY", raising=False)
    rc = main(["join"])
    assert rc != 0


def test_cli_invalid_family_name(tmp_repo, capsys):
    rc = main(["join", "--family", "BAD_NAME"])
    assert rc != 0


# ─── Status (Stage 1.5) ─────────────────────────────────────────────────

def test_status_returns_state(tmp_repo, capsys):
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="working on x",
         files=["a.py", "b.py"], next_step="ship",
         root=tmp_repo)
    capsys.readouterr()
    s = status("ports", root=tmp_repo)
    assert s is not None
    assert s["family"] == "ports"


def test_status_text_output_contains_essentials(tmp_repo, capsys):
    join("ports", goal="my-goal", root=tmp_repo)
    beat("ports", action="my-action", files=["x.py"],
         next_step="my-next", root=tmp_repo)
    capsys.readouterr()
    status("ports", root=tmp_repo)
    out = capsys.readouterr().out
    assert "ports" in out
    assert "my-goal" in out
    assert "my-action" in out
    assert "x.py" in out
    assert "my-next" in out
    assert "beats=1" in out


def test_status_missing_family_returns_none(tmp_repo, capsys):
    s = status("nope", root=tmp_repo)
    assert s is None
    assert "no family" in capsys.readouterr().err


def test_status_marks_stale(tmp_repo, capsys):
    join("ports", root=tmp_repo)
    hb = heartbeat_path("ports", tmp_repo)
    old = hb.stat().st_mtime - (2 * 3600)
    os.utime(hb, (old, old))
    capsys.readouterr()
    status("ports", root=tmp_repo)
    out = capsys.readouterr().out
    assert "[STALE]" in out


def test_cli_status(tmp_repo, capsys):
    main(["join", "--family", "ports"])
    main(["beat", "--family", "ports", "--action", "did stuff"])
    capsys.readouterr()
    rc = main(["status", "--family", "ports"])
    assert rc == 0
    assert "did stuff" in capsys.readouterr().out


def test_cli_recover_brief_flag(tmp_repo, capsys):
    main(["join", "--family", "ports", "--goal", "g"])
    main(["beat", "--family", "ports", "--next-step", "do X"])
    capsys.readouterr()
    rc = main(["recover", "--family", "ports", "--json", "--brief"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert "session_id" not in parsed
    assert parsed["next_step"] == "do X"


# ─── Validate (Stage 1.5) ───────────────────────────────────────────────

from keeper.checkpoint import validate


def _populate_quality_state(family: str, root: Path) -> None:
    """Bring quality from ~25 to ~100 for tests that need a passing state.

    Creates a real file inside tmp_repo so the files_in_play lint passes.
    """
    real_file = root / "fake_module.py"
    real_file.write_text("# placeholder for tests\n")
    join(family, goal="ship Stage 1.5", root=root)
    beat(family,
         action="implemented validate",
         phase="implementation",
         next_step="run tests",
         files=["fake_module.py"],
         decision=("rubric matches CONTINUITY", "validated by orchestra"),
         root=root)


def test_validate_empty_state_low_score(tmp_repo):
    join("ports", root=tmp_repo)  # only goal=""; no beats
    r = validate("ports", root=tmp_repo)
    # Branch likely auto-set by git; everything else missing.
    assert r["score"] <= 25
    assert r["ok"] is False


def test_validate_full_state_passes(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    r = validate("ports", root=tmp_repo)
    assert r["score"] >= 90
    assert r["ok"] is True
    assert all(l["ok"] for l in r["lints"])


def test_validate_missing_family(tmp_repo):
    r = validate("nope", root=tmp_repo)
    assert r["missing"] is True
    assert r["ok"] is False


def test_validate_threshold_configurable(tmp_repo):
    join("ports", root=tmp_repo)  # low quality
    r_low = validate("ports", threshold=20, root=tmp_repo)
    r_high = validate("ports", threshold=80, root=tmp_repo)
    # All lints should pass (fresh state); score difference matters
    assert r_low["score"] == r_high["score"]
    # Lower threshold may pass; higher will fail
    assert r_high["ok"] is False


def test_validate_lint_branch_drift(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    # Tamper: change the branch in family.json
    p = family_json_path("ports", tmp_repo)
    state = json.loads(p.read_text())
    state["branch"] = "definitely-not-the-current-branch"
    p.write_text(json.dumps(state))
    r = validate("ports", root=tmp_repo)
    drift = next(l for l in r["lints"] if l["name"] == "branch drift")
    assert drift["ok"] is False
    assert "definitely-not-the-current-branch" in drift["detail"]


def test_validate_lint_files_missing(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    beat("ports", files=["does-not-exist.py"], root=tmp_repo)
    r = validate("ports", root=tmp_repo)
    f = next(l for l in r["lints"] if l["name"] == "files_in_play exist")
    assert f["ok"] is False
    assert "does-not-exist.py" in f["detail"]


def test_validate_lint_journal_state_synced(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    r = validate("ports", root=tmp_repo)
    j = next(l for l in r["lints"] if l["name"] == "journal/state synced")
    assert j["ok"] is True
    # Tamper: write the wrong last_event_id
    p = family_json_path("ports", tmp_repo)
    state = json.loads(p.read_text())
    state["last_event_id"] = "deadbeef"
    p.write_text(json.dumps(state))
    r2 = validate("ports", root=tmp_repo)
    j2 = next(l for l in r2["lints"] if l["name"] == "journal/state synced")
    assert j2["ok"] is False


def test_validate_lint_heartbeat_stale(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    hb = heartbeat_path("ports", tmp_repo)
    old = hb.stat().st_mtime - (2 * 3600)
    os.utime(hb, (old, old))
    r = validate("ports", root=tmp_repo)
    h = next(l for l in r["lints"] if l["name"] == "heartbeat fresh")
    assert h["ok"] is False


def test_validate_lint_completed_archive_integrity(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    # Drop a malformed file in completed/
    cdir = family_dir("ports", tmp_repo) / "completed"
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "junk.md").write_text("no header here at all", encoding="utf-8")
    r = validate("ports", root=tmp_repo)
    a = next(l for l in r["lints"] if l["name"] == "completed/ archives")
    assert a["ok"] is False
    assert "junk.md" in a["detail"]


def test_validate_breakdown_includes_hints(tmp_repo):
    join("ports", root=tmp_repo)
    r = validate("ports", root=tmp_repo)
    next_step = next(b for b in r["breakdown"] if b["key"] == "next_step")
    assert next_step["ok"] is False
    assert "next-step" in next_step["hint"]


# ─── Complete strict-by-default gate ────────────────────────────────────

def test_complete_blocks_on_low_quality(tmp_repo, capsys):
    join("ports", root=tmp_repo)  # too sparse
    with pytest.raises(SystemExit) as exc_info:
        complete("ports", root=tmp_repo)
    assert exc_info.value.code != 0
    err = capsys.readouterr().err
    assert "refusing to complete" in err


def test_complete_passes_when_quality_high(tmp_repo):
    _populate_quality_state("ports", tmp_repo)
    s = complete("ports", summary="done", root=tmp_repo)
    assert s["ended_cleanly"] is True


def test_complete_force_bypasses_gate(tmp_repo):
    join("ports", root=tmp_repo)  # too sparse
    s = complete("ports", summary="emergency", force=True, root=tmp_repo)
    assert s["ended_cleanly"] is True


def test_complete_threshold_lowering_passes(tmp_repo):
    join("ports", goal="g", root=tmp_repo)
    beat("ports", action="x", root=tmp_repo)
    # Default threshold (60) would fail; lower it to 25 to pass
    s = complete("ports", summary="ok", threshold=25, root=tmp_repo)
    assert s["ended_cleanly"] is True


# ─── CLI for validate ───────────────────────────────────────────────────

def test_cli_validate_text_output(tmp_repo, capsys):
    _populate_quality_state("ports", tmp_repo)
    capsys.readouterr()
    rc = main(["validate", "--family", "ports"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Quality:" in out
    assert "Lint:" in out
    assert "OK" in out


def test_cli_validate_json_output(tmp_repo, capsys):
    _populate_quality_state("ports", tmp_repo)
    capsys.readouterr()
    rc = main(["validate", "--family", "ports", "--json"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert "score" in parsed
    assert "lints" in parsed
    assert parsed["ok"] is True


def test_cli_validate_strict_exits_nonzero_on_fail(tmp_repo, capsys):
    join("ports", root=tmp_repo)  # too sparse
    rc = main(["validate", "--family", "ports", "--strict"])
    assert rc != 0


def test_cli_validate_strict_exits_zero_on_pass(tmp_repo, capsys):
    _populate_quality_state("ports", tmp_repo)
    rc = main(["validate", "--family", "ports", "--strict"])
    assert rc == 0


def test_cli_complete_strict_blocks(tmp_repo, capsys):
    main(["join", "--family", "ports"])
    main(["beat", "--family", "ports", "--action", "x"])
    capsys.readouterr()
    rc = main(["complete", "--family", "ports", "--summary", "fin"])
    assert rc != 0
    err = capsys.readouterr().err
    assert "refusing to complete" in err


def test_cli_complete_force_bypasses(tmp_repo, capsys):
    main(["join", "--family", "ports"])
    main(["beat", "--family", "ports", "--action", "x"])
    rc = main(["complete", "--family", "ports", "--summary", "fin", "--force"])
    assert rc == 0
