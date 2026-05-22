"""Tests for PyprojectInitPlugin."""

from __future__ import annotations

import pytest

from scaffy.plugins.registry import clear_registry
from scaffy.plugins.builtin.pyproject_init import PyprojectInitPlugin
from scaffy.plugins.base import PluginError


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture
def plugin():
    return PyprojectInitPlugin()


@pytest.fixture
def python_context(tmp_path):
    return {
        "project_type": "python",
        "output_dir": str(tmp_path),
        "project_name": "awesome-lib",
        "author": "Ada Lovelace",
        "description": "An awesome library",
        "python_version": "3.11",
        "dependencies": ["requests", "click"],
    }


def test_pyproject_creates_file(plugin, python_context, tmp_path):
    plugin.run(python_context)
    assert (tmp_path / "pyproject.toml").exists()


def test_pyproject_contains_project_name(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "pyproject.toml").read_text()
    assert 'name = "awesome-lib"' in content


def test_pyproject_contains_author(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "pyproject.toml").read_text()
    assert "Ada Lovelace" in content


def test_pyproject_contains_dependencies(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "pyproject.toml").read_text()
    assert '"requests"' in content
    assert '"click"' in content


def test_pyproject_contains_python_version(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "pyproject.toml").read_text()
    assert "requires-python" in content
    assert "3.11" in content


def test_pyproject_skips_non_python(plugin, tmp_path):
    context = {"project_type": "node", "output_dir": str(tmp_path)}
    plugin.run(context)
    assert not (tmp_path / "pyproject.toml").exists()


def test_pyproject_raises_if_file_exists(plugin, python_context, tmp_path):
    (tmp_path / "pyproject.toml").write_text("existing", encoding="utf-8")
    with pytest.raises(PluginError, match="already exists"):
        plugin.run(python_context)


def test_pyproject_empty_dependencies(plugin, tmp_path):
    context = {
        "project_type": "python",
        "output_dir": str(tmp_path),
        "project_name": "bare-project",
        "dependencies": [],
    }
    plugin.run(context)
    content = (tmp_path / "pyproject.toml").read_text()
    assert "dependencies = []" in content
