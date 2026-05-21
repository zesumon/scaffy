"""Tests for the VenvInitPlugin built-in plugin."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry, get_plugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin(tmp_path):
    # Re-import to trigger registration after registry was cleared.
    import importlib
    import scaffy.plugins.builtin.venv_init as mod

    importlib.reload(mod)
    return get_plugin("venv_init")()


@pytest.fixture()
def python_context(tmp_path):
    return {"project_type": "python", "output_dir": str(tmp_path)}


def _make_ok_result():
    result = MagicMock()
    result.returncode = 0
    result.stderr = ""
    return result


def _make_fail_result():
    result = MagicMock()
    result.returncode = 1
    result.stderr = "some error"
    return result


def test_venv_init_skips_non_python(plugin, tmp_path):
    ctx = {"project_type": "node", "output_dir": str(tmp_path)}
    with patch("subprocess.run") as mock_run:
        plugin.run(ctx)
        mock_run.assert_not_called()


def test_venv_init_missing_output_dir_raises(plugin):
    ctx = {"project_type": "python"}
    with pytest.raises(PluginError, match="output_dir"):
        plugin.run(ctx)


def test_venv_init_nonexistent_dir_raises(plugin, tmp_path):
    ctx = {"project_type": "python", "output_dir": str(tmp_path / "ghost")}
    with pytest.raises(PluginError, match="does not exist"):
        plugin.run(ctx)


def test_venv_init_calls_subprocess(plugin, python_context):
    with patch("subprocess.run", return_value=_make_ok_result()) as mock_run:
        plugin.run(python_context)
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[-2] == "-m"
        assert cmd[-1] == "venv" or ".venv" in cmd[-1]


def test_venv_init_subprocess_failure_raises(plugin, python_context):
    with patch("subprocess.run", return_value=_make_fail_result()):
        with pytest.raises(PluginError, match="venv creation failed"):
            plugin.run(python_context)


def test_venv_init_oserror_raises(plugin, python_context):
    with patch("subprocess.run", side_effect=OSError("not found")):
        with pytest.raises(PluginError, match="failed to run venv command"):
            plugin.run(python_context)


def test_venv_init_repr(plugin):
    assert "venv_init" in repr(plugin)
