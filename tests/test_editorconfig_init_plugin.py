"""Tests for the EditorconfigInitPlugin."""

from __future__ import annotations

from pathlib import Path

import pytest

from scaffy.plugins.builtin.editorconfig_init import EditorconfigInitPlugin
from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry, get_plugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return EditorconfigInitPlugin()


@pytest.fixture()
def base_context(tmp_path):
    return {"output_dir": str(tmp_path), "project_type": "python", "variables": {}}


def test_editorconfig_creates_file(plugin, base_context, tmp_path):
    plugin.run(base_context)
    assert (tmp_path / ".editorconfig").exists()


def test_editorconfig_content_has_root_true(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / ".editorconfig").read_text()
    assert "root = true" in content


def test_editorconfig_content_has_utf8(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / ".editorconfig").read_text()
    assert "charset = utf-8" in content


def test_editorconfig_runs_for_node_project(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "project_type": "node", "variables": {}}
    plugin.run(ctx)
    assert (tmp_path / ".editorconfig").exists()


def test_editorconfig_missing_output_dir_raises(plugin):
    ctx = {"output_dir": "/no/such/dir", "project_type": "python", "variables": {}}
    with pytest.raises(PluginError, match="output directory does not exist"):
        plugin.run(ctx)


def test_editorconfig_registered():
    p = get_plugin("editorconfig_init")
    assert p is EditorconfigInitPlugin


def test_editorconfig_repr(plugin):
    assert "editorconfig_init" in repr(plugin)
