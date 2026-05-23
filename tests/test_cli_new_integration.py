"""End-to-end integration tests for the `scaffy new` CLI command.

These tests exercise the full pipeline: CLI argument parsing → template
loading → defaults resolution → file rendering → plugin execution.
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from scaffy.plugins.registry import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure the plugin registry is reset between tests."""
    clear_registry()
    from scaffy.plugins.builtin import register_all
    register_all()
    yield
    clear_registry()


@pytest.fixture()
def tmp_output(tmp_path):
    """Return a temporary output directory that does NOT yet exist."""
    out = tmp_path / "output"
    return out


@pytest.fixture()
def python_tmpl(tmp_path):
    """Write a minimal Python template YAML and return its path."""
    data = {
        "name": "my_python_app",
        "type": "python",
        "variables": {"author": "Test Author", "version": "0.1.0"},
        "structure": [
            {"my_python_app": [{"__init__.py": ""}, {"main.py": "# entry point\n"}]},
            {"tests": [{"__init__.py": ""}]},
        ],
        "plugins": ["gitignore_init", "readme_init"],
    }
    tmpl = tmp_path / "python_tmpl.yaml"
    tmpl.write_text(yaml.dump(data))
    return tmpl


@pytest.fixture()
def node_tmpl(tmp_path):
    """Write a minimal Node.js template YAML and return its path."""
    data = {
        "name": "my_node_app",
        "type": "node",
        "variables": {"author": "Test Author", "version": "1.0.0"},
        "structure": [
            {"src": [{"index.js": "// entry\n"}]},
        ],
        "plugins": ["gitignore_init", "readme_init"],
    }
    tmpl = tmp_path / "node_tmpl.yaml"
    tmpl.write_text(yaml.dump(data))
    return tmpl


def _run_scaffy(args, *, cwd=None):
    """Run `scaffy` via its CLI entry-point in a subprocess.

    Returns a ``subprocess.CompletedProcess`` with captured stdout/stderr.
    """
    return subprocess.run(
        [sys.executable, "-m", "scaffy.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_new_python_creates_output_dir(python_tmpl, tmp_output):
    result = _run_scaffy(["new", "my_python_app", "--template", str(python_tmpl), "--output", str(tmp_output)])
    assert result.returncode == 0, result.stderr
    assert tmp_output.is_dir()


def test_new_python_renders_source_files(python_tmpl, tmp_output):
    _run_scaffy(["new", "my_python_app", "--template", str(python_tmpl), "--output", str(tmp_output)])
    assert (tmp_output / "my_python_app" / "__init__.py").exists()
    assert (tmp_output / "my_python_app" / "main.py").exists()
    assert (tmp_output / "tests" / "__init__.py").exists()


def test_new_python_readme_plugin_runs(python_tmpl, tmp_output):
    _run_scaffy(["new", "my_python_app", "--template", str(python_tmpl), "--output", str(tmp_output)])
    readme = tmp_output / "README.md"
    assert readme.exists(), "readme_init plugin should create README.md"
    assert "my_python_app" in readme.read_text()


def test_new_python_gitignore_plugin_runs(python_tmpl, tmp_output):
    _run_scaffy(["new", "my_python_app", "--template", str(python_tmpl), "--output", str(tmp_output)])
    gitignore = tmp_output / ".gitignore"
    assert gitignore.exists(), "gitignore_init plugin should create .gitignore"
    content = gitignore.read_text()
    assert "__pycache__" in content or ".venv" in content


def test_new_node_renders_source_files(node_tmpl, tmp_output):
    _run_scaffy(["new", "my_node_app", "--template", str(node_tmpl), "--output", str(tmp_output)])
    assert (tmp_output / "src" / "index.js").exists()


def test_new_node_gitignore_contains_node_modules(node_tmpl, tmp_output):
    _run_scaffy(["new", "my_node_app", "--template", str(node_tmpl), "--output", str(tmp_output)])
    gitignore = tmp_output / ".gitignore"
    assert gitignore.exists()
    assert "node_modules" in gitignore.read_text()


def test_new_with_variable_override(python_tmpl, tmp_output):
    result = _run_scaffy([
        "new", "my_python_app",
        "--template", str(python_tmpl),
        "--output", str(tmp_output),
        "--var", "author=Override Author",
    ])
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# Error / edge-case tests
# ---------------------------------------------------------------------------


def test_new_missing_template_exits_nonzero(tmp_output):
    result = _run_scaffy(["new", "proj", "--template", "/nonexistent/tmpl.yaml", "--output", str(tmp_output)])
    assert result.returncode != 0


def test_new_existing_output_dir_exits_nonzero(python_tmpl, tmp_output):
    tmp_output.mkdir(parents=True)
    result = _run_scaffy(["new", "my_python_app", "--template", str(python_tmpl), "--output", str(tmp_output)])
    assert result.returncode != 0
    assert "exist" in result.stderr.lower() or "exist" in result.stdout.lower()


def test_new_bad_yaml_exits_nonzero(tmp_path, tmp_output):
    bad = tmp_path / "bad.yaml"
    bad.write_text(": : : invalid yaml :::")
    result = _run_scaffy(["new", "proj", "--template", str(bad), "--output", str(tmp_output)])
    assert result.returncode != 0
