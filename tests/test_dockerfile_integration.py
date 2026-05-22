"""Integration tests: dockerfile_init wired through run_plugins."""

from __future__ import annotations

import os
import pytest

from scaffy.plugins.registry import clear_registry
from scaffy.plugins.runner import run_plugins
import scaffy.plugins.builtin.dockerfile_init  # noqa: F401 — registers the plugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


def test_run_plugins_writes_dockerfile(tmp_path):
    context = {
        "project_type": "python",
        "project_name": "demo",
        "output_dir": str(tmp_path),
    }
    run_plugins(["dockerfile_init"], context)
    assert os.path.isfile(tmp_path / "Dockerfile")


def test_run_plugins_dockerfile_content_node(tmp_path):
    context = {
        "project_type": "node",
        "project_name": "demo",
        "output_dir": str(tmp_path),
    }
    run_plugins(["dockerfile_init"], context)
    content = (tmp_path / "Dockerfile").read_text()
    assert "node" in content


def test_run_plugins_skips_unknown_plugin(tmp_path):
    """run_plugins should not crash on an unregistered plugin name."""
    context = {
        "project_type": "python",
        "project_name": "demo",
        "output_dir": str(tmp_path),
    }
    # Should not raise — unknown plugins are skipped gracefully
    run_plugins(["nonexistent_plugin"], context)
