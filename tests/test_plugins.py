"""Tests for the plugin registry, runner, and git_init built-in."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import (
    clear_registry,
    get_plugin,
    list_plugins,
    register,
)
from scaffy.plugins.runner import run_plugins


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_registry():
    """Isolate registry state between tests."""
    # Re-import to ensure built-ins are present, then yield, then restore.
    import scaffy.plugins.builtin.git_init  # noqa: F401  # ensure registered
    original = list_plugins()
    yield
    # Restore: clear and re-register only what was there before
    clear_registry()
    import importlib
    import scaffy.plugins.builtin.git_init as gi
    importlib.reload(gi)


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


def test_register_and_get():
    class DummyPlugin(BasePlugin):
        name = "dummy"

        def run(self, project_dir: Path, context: dict[str, Any]) -> None:
            pass

    register(DummyPlugin)
    assert get_plugin("dummy") is DummyPlugin


def test_register_missing_name_raises():
    class NoName(BasePlugin):
        name = ""

        def run(self, project_dir, context):
            pass

    with pytest.raises(PluginError, match="must define a non-empty"):
        register(NoName)


def test_get_unknown_plugin_raises():
    with pytest.raises(PluginError, match="Unknown plugin"):
        get_plugin("does_not_exist")


def test_list_plugins_returns_sorted():
    names = list_plugins()
    assert names == sorted(names)
    assert "git_init" in names


# ---------------------------------------------------------------------------
# Runner tests
# ---------------------------------------------------------------------------


def test_run_plugins_string_spec(tmp_path):
    calls = []

    class TrackPlugin(BasePlugin):
        name = "tracker"

        def run(self, project_dir, context):
            calls.append((project_dir, context))

    register(TrackPlugin)
    run_plugins(["tracker"], tmp_path, {"key": "val"})
    assert calls == [(tmp_path, {"key": "val"})]


def test_run_plugins_dict_spec(tmp_path):
    received_cfg = {}

    class CfgPlugin(BasePlugin):
        name = "cfg_plugin"

        def run(self, project_dir, context):
            received_cfg.update(self.config)

    register(CfgPlugin)
    run_plugins([{"name": "cfg_plugin", "config": {"foo": 42}}], tmp_path, {})
    assert received_cfg == {"foo": 42}


def test_run_plugins_invalid_spec_raises(tmp_path):
    with pytest.raises(PluginError, match="Invalid plugin spec"):
        run_plugins([123], tmp_path, {})


# ---------------------------------------------------------------------------
# git_init plugin tests
# ---------------------------------------------------------------------------


def test_git_init_calls_subprocess(tmp_path):
    from scaffy.plugins.builtin.git_init import GitInitPlugin

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        plugin = GitInitPlugin()
        plugin.run(tmp_path, {})
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[:2] == ["git", "init"]


def test_git_init_missing_git_raises(tmp_path):
    from scaffy.plugins.builtin.git_init import GitInitPlugin
    import subprocess

    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(PluginError, match="git executable not found"):
            GitInitPlugin().run(tmp_path, {})
