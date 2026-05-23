"""Tests for MakefileInitPlugin."""

from __future__ import annotations

import pytest

from scaffy.plugins.builtin.makefile_init import MakefileInitPlugin
from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture
def plugin():
    return MakefileInitPlugin()


@pytest.fixture
def python_context(tmp_path):
    return {"output_dir": str(tmp_path), "project_type": "python"}


@pytest.fixture
def node_context(tmp_path):
    return {"output_dir": str(tmp_path), "project_type": "node"}


def test_makefile_creates_file_python(plugin, python_context, tmp_path):
    plugin.run(python_context)
    assert (tmp_path / "Makefile").exists()


def test_makefile_python_content(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "Makefile").read_text()
    assert "pip install" in content
    assert "pytest" in content
    assert "black" in content


def test_makefile_creates_file_node(plugin, node_context, tmp_path):
    plugin.run(node_context)
    assert (tmp_path / "Makefile").exists()


def test_makefile_node_content(plugin, node_context, tmp_path):
    plugin.run(node_context)
    content = (tmp_path / "Makefile").read_text()
    assert "npm install" in content
    assert "npx eslint" in content
    assert "node_modules" in content


def test_makefile_unknown_project_type_writes_stub(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "project_type": "rust"}
    plugin.run(ctx)
    content = (tmp_path / "Makefile").read_text()
    assert "help" in content


def test_makefile_raises_if_already_exists(plugin, python_context, tmp_path):
    (tmp_path / "Makefile").write_text("existing")
    with pytest.raises(PluginError, match="already exists"):
        plugin.run(python_context)


def test_makefile_plugin_name():
    assert MakefileInitPlugin.name == "makefile_init"


def test_makefile_repr():
    p = MakefileInitPlugin()
    assert "makefile_init" in repr(p)
