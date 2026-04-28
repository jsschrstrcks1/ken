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
    complete("ports", summary="done", root=tmp_repo)
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
    s = complete("ports", summary="done", root=tmp_repo)
    assert s["ended_cleanly"] is True
    assert "completed_at" in s


def test_complete_archives_markdown(tmp_repo):
    join("ports", root=tmp_repo)
    complete("ports", summary="finished work", root=tmp_repo)
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
    assert "NEXT STEP: ship it" in out


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
    assert main(["complete", "--family", "ports", "--summary", "fin"]) == 0
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
