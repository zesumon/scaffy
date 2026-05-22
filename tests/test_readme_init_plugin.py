"""Tests for the ReadmeInitPlugin."""

from __future__ import annotations

import pytest
from pathlib import Path

from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry, get_plugin
from scaffy.plugins.builtin.readme_init import ReadmeInitPlugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return ReadmeInitPlugin()


@pytest.fixture()
def base_context(tmp_path):
    return {
        "project_path": tmp_path,
        "project_name": "my-project",
        "description": "A test project",
        "author": "Jane Doe",
        "license": "MIT",
        "project_type": "python",
    }


def test_readme_creates_file(plugin, base_context, tmp_path):
    plugin.run(base_context)
    assert (tmp_path / "README.md").exists()


def test_readme_contains_project_name(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "# my-project" in content


def test_readme_contains_description(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "A test project" in content


def test_readme_python_getting_started(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "pip install" in content
    assert "npm install" not in content


def test_readme_node_getting_started(plugin, base_context, tmp_path):
    base_context["project_type"] = "node"
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "npm install" in content
    assert "pip install" not in content


def test_readme_contains_license(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "MIT" in content


def test_readme_contains_author(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "README.md").read_text()
    assert "Jane Doe" in content


def test_readme_missing_project_path_raises(plugin):
    with pytest.raises(PluginError, match="project_path"):
        plugin.run({})


def test_readme_registered():
    from scaffy.plugins.builtin.readme_init import ReadmeInitPlugin  # noqa: F401 re-import triggers register
    assert get_plugin("readme_init") is ReadmeInitPlugin


def test_readme_repr(plugin):
    assert "readme_init" in repr(plugin)
