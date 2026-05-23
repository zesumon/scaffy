"""Integration tests for the CLI — exercises the full new-project flow."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scaffy.cli import main
from scaffy.plugins import registry


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure the plugin registry is reset between tests."""
    registry.clear_registry()
    from scaffy.plugins.builtin import register_builtin_plugins  # noqa: F401
    yield
    registry.clear_registry()


@pytest.fixture()
def tmp_output(tmp_path):
    """Return a fresh temporary directory for project output."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture()
def python_template(tmp_path):
    """Write a minimal Python project YAML template and return its path."""
    content = """
name: my-py-app
project_type: python
variables:
  author: Test Author
plugins:
  - editorconfig
  - gitignore
structure:
  - src/:
    - __init__.py: ""
  - tests/:
    - __init__.py: ""
"""
    tpl = tmp_path / "python_template.yaml"
    tpl.write_text(content)
    return str(tpl)


@pytest.fixture()
def node_template(tmp_path):
    """Write a minimal Node.js project YAML template and return its path."""
    content = """
name: my-node-app
project_type: node
variables:
  author: Test Author
plugins:
  - editorconfig
  - gitignore
structure:
  - src/:
    - index.js: "console.log('hello');"
"""
    tpl = tmp_path / "node_template.yaml"
    tpl.write_text(content)
    return str(tpl)


# ---------------------------------------------------------------------------
# Happy-path: python project
# ---------------------------------------------------------------------------

def test_new_python_project_creates_output_dir(python_template, tmp_output):
    """Running `scaffy new` with a python template creates the output directory."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()
    assert (tmp_output / "my-py-app").is_dir()


def test_new_python_project_creates_src_package(python_template, tmp_output):
    """The rendered python project contains src/__init__.py."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()
    assert (tmp_output / "my-py-app" / "src" / "__init__.py").exists()


def test_new_python_project_creates_editorconfig(python_template, tmp_output):
    """The editorconfig plugin fires and creates .editorconfig."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()
    assert (tmp_output / "my-py-app" / ".editorconfig").exists()


def test_new_python_project_creates_gitignore(python_template, tmp_output):
    """The gitignore plugin fires and creates .gitignore."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()
    assert (tmp_output / "my-py-app" / ".gitignore").exists()


# ---------------------------------------------------------------------------
# Happy-path: node project
# ---------------------------------------------------------------------------

def test_new_node_project_creates_src_index(node_template, tmp_output):
    """The rendered node project contains src/index.js."""
    argv = ["scaffy", "new", "my-node-app", "--template", node_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()
    assert (tmp_output / "my-node-app" / "src" / "index.js").exists()


# ---------------------------------------------------------------------------
# Variable override via --var
# ---------------------------------------------------------------------------

def test_variable_override_is_applied(python_template, tmp_output):
    """--var flags override template variables without breaking the run."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output), "--var", "author=Override Author"]
    with patch("sys.argv", argv):
        main()  # should not raise
    assert (tmp_output / "my-py-app").is_dir()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_missing_template_exits_nonzero(tmp_output, capsys):
    """A missing template file should cause a non-zero SystemExit."""
    argv = ["scaffy", "new", "my-proj", "--template", "/nonexistent/template.yaml",
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code != 0


def test_existing_project_dir_exits_nonzero(python_template, tmp_output):
    """Re-running with the same output dir should fail because the dir exists."""
    argv = ["scaffy", "new", "my-py-app", "--template", python_template,
            "--output-dir", str(tmp_output)]
    with patch("sys.argv", argv):
        main()  # first run — should succeed
    with patch("sys.argv", argv):
        with pytest.raises(SystemExit) as exc_info:
            main()  # second run — directory already exists
    assert exc_info.value.code != 0
