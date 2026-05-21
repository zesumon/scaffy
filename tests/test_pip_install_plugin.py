"""Tests for the PipInstallPlugin."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scaffy.plugins.builtin.pip_install import PipInstallPlugin
from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return PipInstallPlugin()


@pytest.fixture()
def python_context(tmp_path):
    return {"output_dir": str(tmp_path)}


def _make_ok_result():
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.returncode = 0
    r.stderr = ""
    return r


def _make_fail_result(code: int = 1, stderr: str = "error"):
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.returncode = code
    r.stderr = stderr
    return r


def test_pip_install_skipped_without_requirements(plugin, python_context, tmp_path):
    """Plugin should do nothing when requirements.txt is absent."""
    with patch("subprocess.run") as mock_run:
        plugin.run(python_context)
        mock_run.assert_not_called()


def test_pip_install_runs_when_requirements_present(plugin, python_context, tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests\n")

    with patch("subprocess.run", return_value=_make_ok_result()) as mock_run:
        plugin.run(python_context)
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "-r" in cmd
        assert str(req) in cmd


def test_pip_install_uses_venv_python(plugin, python_context, tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("flask\n")
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()

    with patch("subprocess.run", return_value=_make_ok_result()) as mock_run:
        plugin.run(python_context)
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == str(venv_python)


def test_pip_install_raises_on_nonzero_exit(plugin, python_context, tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("nonexistent-pkg\n")

    with patch("subprocess.run", return_value=_make_fail_result(1, "No matching dist")):
        with pytest.raises(PluginError, match="pip exited with code 1"):
            plugin.run(python_context)


def test_pip_install_raises_on_missing_executable(plugin, python_context, tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests\n")

    with patch("subprocess.run", side_effect=FileNotFoundError("python not found")):
        with pytest.raises(PluginError, match="python executable not found"):
            plugin.run(python_context)


def test_pip_install_error_includes_stderr(plugin, python_context, tmp_path):
    """PluginError message should include stderr output from pip for easier debugging."""
    req = tmp_path / "requirements.txt"
    req.write_text("badpackage\n")
    stderr_msg = "ERROR: Could not find a version that satisfies the requirement badpackage"

    with patch("subprocess.run", return_value=_make_fail_result(1, stderr_msg)):
        with pytest.raises(PluginError) as exc_info:
            plugin.run(python_context)
        assert stderr_msg in str(exc_info.value)


def test_pip_install_repr(plugin):
    assert "pip_install" in repr(plugin)
