"""Shared fixtures for keeper tests."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path, monkeypatch) -> Path:
    """Make tmp_path a git repo and chdir into it. Returns the repo root."""
    subprocess.run(
        ["git", "init", "-q", "-b", "main"],
        cwd=tmp_path, check=True,
    )
    for k, v in (
        ("user.email", "t@t"),
        ("user.name", "t"),
        ("commit.gpgsign", "false"),
        ("tag.gpgsign", "false"),
    ):
        subprocess.run(
            ["git", "-C", str(tmp_path), "config", k, v], check=True,
        )
    # Empty initial commit so HEAD resolves
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "--allow-empty",
         "-m", "init", "-q", "--no-gpg-sign"],
        check=True,
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path
