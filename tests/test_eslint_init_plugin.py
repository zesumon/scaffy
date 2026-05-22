"""Tests for the EslintInitPlugin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scaffy.plugins.builtin.eslint_init import EslintInitPlugin
from scaffy.plugins.registry import clear_registry, get_plugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return EslintInitPlugin()


@pytest.fixture()
def node_context(tmp_path):
    return {
        "project_type": "node",
        "output_dir": str(tmp_path),
        "variables": {},
    }


def test_eslint_skips_non_node_projects(plugin, tmp_path):
    ctx = {"project_type": "python", "output_dir": str(tmp_path), "variables": {}}
    plugin.run(ctx)
    assert not (tmp_path / ".eslintrc.json").exists()


def test_eslint_creates_eslintrc(plugin, node_context, tmp_path):
    plugin.run(node_context)
    assert (tmp_path / ".eslintrc.json").exists()


def test_eslint_default_content(plugin, node_context, tmp_path):
    plugin.run(node_context)
    data = json.loads((tmp_path / ".eslintrc.json").read_text())
    assert "eslint:recommended" in data["extends"]
    assert data["env"]["node"] is True


def test_eslint_custom_extends(plugin, tmp_path):
    ctx = {
        "project_type": "node",
        "output_dir": str(tmp_path),
        "variables": {"eslint_extends": "airbnb"},
    }
    plugin.run(ctx)
    data = json.loads((tmp_path / ".eslintrc.json").read_text())
    assert data["extends"] == ["airbnb"]


def test_eslint_custom_extends_list(plugin, tmp_path):
    ctx = {
        "project_type": "node",
        "output_dir": str(tmp_path),
        "variables": {"eslint_extends": ["airbnb", "prettier"]},
    }
    plugin.run(ctx)
    data = json.loads((tmp_path / ".eslintrc.json").read_text())
    assert data["extends"] == ["airbnb", "prettier"]


def test_eslint_missing_output_dir_raises(plugin):
    from scaffy.plugins.base import PluginError

    ctx = {
        "project_type": "node",
        "output_dir": "/nonexistent/path/xyz",
        "variables": {},
    }
    with pytest.raises(PluginError, match="output directory does not exist"):
        plugin.run(ctx)


def test_eslint_registered():
    p = get_plugin("eslint_init")
    assert p is EslintInitPlugin
