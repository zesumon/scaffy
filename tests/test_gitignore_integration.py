"""Integration test: gitignore_init runs through run_plugins end-to-end."""

from __future__ import annotations

import os
import pytest

from scaffy.plugins.registry import clear_registry
from scaffy.plugins.runner import run_plugins
import scaffy.plugins.builtin.gitignore_init  # noqa: F401


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


def test_run_plugins_writes_gitignore(tmp_path):
    context = {
        "output_dir": str(tmp_path),
        "project_type": "python",
    }
    run_plugins(["gitignore_init"], context)
    assert os.path.isfile(tmp_path / ".gitignore")


def test_run_plugins_gitignore_content_python(tmp_path):
    context = {
        "output_dir": str(tmp_path),
        "project_type": "python",
    }
    run_plugins(["gitignore_init"], context)
    content = (tmp_path / ".gitignore").read_text()
    assert ".venv/" in content
    assert "__pycache__/" in content


def test_run_plugins_gitignore_content_node(tmp_path):
    context = {
        "output_dir": str(tmp_path),
        "project_type": "node",
    }
    run_plugins(["gitignore_init"], context)
    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content


def test_run_plugins_skips_unknown_plugin(tmp_path):
    """run_plugins should not crash when an unknown plugin name is given."""
    context = {"output_dir": str(tmp_path), "project_type": "python"}
    # Should not raise; unknown plugins are silently skipped by runner
    run_plugins(["does_not_exist"], context)
