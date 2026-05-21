"""Tests for the npm_init built-in plugin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scaffy.plugins.base import PluginError
from scaffy.plugins.builtin.npm_init import NpmInitPlugin
from scaffy.plugins.registry import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return NpmInitPlugin()


@pytest.fixture()
def node_context(tmp_path):
    return {
        "output_dir": str(tmp_path),
        "project_type": "node",
        "variables": {
            "project_name": "my-app",
            "version": "1.2.3",
            "description": "A test app",
            "author": "Ada",
            "license": "Apache-2.0",
        },
    }


def test_npm_init_creates_package_json(plugin, node_context, tmp_path):
    plugin.run(node_context)
    assert (tmp_path / "package.json").exists()


def test_npm_init_package_json_content(plugin, node_context, tmp_path):
    plugin.run(node_context)
    data = json.loads((tmp_path / "package.json").read_text())
    assert data["name"] == "my-app"
    assert data["version"] == "1.2.3"
    assert data["description"] == "A test app"
    assert data["author"] == "Ada"
    assert data["license"] == "Apache-2.0"
    assert data["main"] == "index.js"


def test_npm_init_skips_non_node_project(plugin, tmp_path):
    context = {
        "output_dir": str(tmp_path),
        "project_type": "python",
        "variables": {},
    }
    plugin.run(context)
    assert not (tmp_path / "package.json").exists()


def test_npm_init_missing_output_dir_raises(plugin):
    with pytest.raises(PluginError, match="output_dir"):
        plugin.run({"project_type": "node"})


def test_npm_init_defaults_when_variables_empty(plugin, tmp_path):
    context = {
        "output_dir": str(tmp_path),
        "project_type": "nodejs",
        "variables": {},
    }
    plugin.run(context)
    data = json.loads((tmp_path / "package.json").read_text())
    assert data["version"] == "0.1.0"
    assert data["license"] == "MIT"
    assert data["name"] == tmp_path.name


def test_npm_init_repr(plugin):
    assert "npm_init" in repr(plugin)
