"""Tests for DockerfileInitPlugin."""

from __future__ import annotations

import os
import pytest

from scaffy.plugins.registry import clear_registry
from scaffy.plugins.builtin.dockerfile_init import DockerfileInitPlugin
from scaffy.plugins.base import PluginError


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture()
def plugin():
    return DockerfileInitPlugin()


@pytest.fixture()
def python_context(tmp_path):
    return {
        "project_type": "python",
        "project_name": "myapp",
        "output_dir": str(tmp_path),
    }


@pytest.fixture()
def node_context(tmp_path):
    return {
        "project_type": "node",
        "project_name": "myapp",
        "output_dir": str(tmp_path),
    }


def test_dockerfile_creates_files_python(plugin, python_context, tmp_path):
    plugin.run(python_context)
    assert os.path.isfile(tmp_path / "Dockerfile")
    assert os.path.isfile(tmp_path / ".dockerignore")


def test_dockerfile_python_references_project_name(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / "Dockerfile").read_text()
    assert "myapp" in content
    assert "python:3.11-slim" in content


def test_dockerfile_node_uses_node_image(plugin, node_context, tmp_path):
    plugin.run(node_context)
    content = (tmp_path / "Dockerfile").read_text()
    assert "node:20-alpine" in content
    assert "npm ci" in content


def test_dockerignore_contains_common_entries(plugin, python_context, tmp_path):
    plugin.run(python_context)
    content = (tmp_path / ".dockerignore").read_text()
    assert "node_modules" in content
    assert ".venv" in content
    assert ".git" in content


def test_unsupported_project_type_raises(plugin, tmp_path):
    ctx = {"project_type": "rust", "project_name": "proj", "output_dir": str(tmp_path)}
    with pytest.raises(PluginError, match="unsupported project_type"):
        plugin.run(ctx)


def test_plugin_repr(plugin):
    assert "dockerfile_init" in repr(plugin)


def test_write_error_raises_plugin_error(plugin, python_context, monkeypatch):
    def _bad_open(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("builtins.open", _bad_open)
    with pytest.raises(PluginError, match="could not write files"):
        plugin.run(python_context)
