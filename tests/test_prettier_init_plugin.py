"""Tests for the PrettierInitPlugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scaffy.plugins.builtin.prettier_init import PrettierInitPlugin, _DEFAULT_CONFIG
from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture
def plugin():
    return PrettierInitPlugin()


@pytest.fixture
def node_context(tmp_path):
    return {"project_type": "node", "output_dir": str(tmp_path)}


def test_prettier_skips_non_node_projects(plugin, tmp_path):
    ctx = {"project_type": "python", "output_dir": str(tmp_path)}
    plugin.run(ctx)
    assert not (tmp_path / ".prettierrc").exists()


def test_prettier_creates_prettierrc(plugin, node_context, tmp_path):
    plugin.run(node_context)
    assert (tmp_path / ".prettierrc").exists()


def test_prettier_default_config_content(plugin, node_context, tmp_path):
    plugin.run(node_context)
    data = json.loads((tmp_path / ".prettierrc").read_text())
    for key, value in _DEFAULT_CONFIG.items():
        assert data[key] == value


def test_prettier_merges_user_config(plugin, tmp_path):
    ctx = {
        "project_type": "node",
        "output_dir": str(tmp_path),
        "prettier": {"singleQuote": False, "printWidth": 80},
    }
    plugin.run(ctx)
    data = json.loads((tmp_path / ".prettierrc").read_text())
    assert data["singleQuote"] is False
    assert data["printWidth"] == 80
    assert data["semi"] is True  # default preserved


def test_prettier_raises_if_output_dir_missing(plugin):
    ctx = {"project_type": "node", "output_dir": "/nonexistent/path/xyz"}
    with pytest.raises(PluginError, match="does not exist"):
        plugin.run(ctx)


def test_prettier_install_calls_npm(plugin, node_context, tmp_path):
    node_context["prettier_install"] = True
    mock_result = MagicMock(returncode=0)
    with patch("scaffy.plugins.builtin.prettier_init.subprocess.run", return_value=mock_result) as mock_run:
        plugin.run(node_context)
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "prettier" in args


def test_prettier_install_failure_raises(plugin, node_context, tmp_path):
    node_context["prettier_install"] = True
    mock_result = MagicMock(returncode=1, stderr="some npm error")
    with patch("scaffy.plugins.builtin.prettier_init.subprocess.run", return_value=mock_result):
        with pytest.raises(PluginError, match="npm install failed"):
            plugin.run(node_context)


def test_plugin_repr(plugin):
    assert "prettier_init" in repr(plugin)
