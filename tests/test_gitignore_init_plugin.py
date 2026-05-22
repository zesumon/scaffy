"""Tests for the GitignoreInitPlugin."""

from __future__ import annotations

import os
import pytest

from scaffy.plugins.registry import clear_registry, get_plugin
from scaffy.plugins.base import PluginError


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    import scaffy.plugins.builtin.gitignore_init  # noqa: F401 — triggers @register
    return get_plugin("gitignore_init")()


@pytest.fixture()
def base_context(tmp_path):
    return {"output_dir": str(tmp_path), "project_type": ""}


def test_gitignore_creates_file(plugin, base_context, tmp_path):
    plugin.run(base_context)
    assert os.path.isfile(tmp_path / ".gitignore")


def test_gitignore_python_contains_venv(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "project_type": "python"}
    plugin.run(ctx)
    content = (tmp_path / ".gitignore").read_text()
    assert ".venv/" in content
    assert "__pycache__/" in content


def test_gitignore_node_contains_node_modules(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "project_type": "node"}
    plugin.run(ctx)
    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content


def test_gitignore_unknown_type_uses_common(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / ".gitignore").read_text()
    assert ".DS_Store" in content
    assert "node_modules/" not in content
    assert ".venv/" not in content


def test_gitignore_python_does_not_include_node_modules(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "project_type": "python"}
    plugin.run(ctx)
    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" not in content


def test_gitignore_raises_on_bad_path(plugin):
    ctx = {"output_dir": "/nonexistent/path/that/does/not/exist", "project_type": "python"}
    with pytest.raises(PluginError, match="gitignore_init"):
        plugin.run(ctx)


def test_gitignore_repr(plugin):
    assert "gitignore_init" in repr(plugin)
