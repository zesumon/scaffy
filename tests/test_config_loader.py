"""Tests for the YAML template loader and schema validator."""

import textwrap
from pathlib import Path

import pytest

from scaffy.config.loader import ConfigLoadError, load_template
from scaffy.config.schema import SchemaValidationError, validate_template


@pytest.fixture()
def valid_yaml(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        name: my-lib
        type: python
        structure:
          - path: src/my_lib/__init__.py
            type: file
          - path: tests/
            type: dir
    """)
    p = tmp_path / "template.yaml"
    p.write_text(content)
    return p


def test_load_template_success(valid_yaml: Path):
    data = load_template(valid_yaml)
    assert data["name"] == "my-lib"
    assert data["type"] == "python"
    assert isinstance(data["structure"], list)


def test_load_template_missing_file(tmp_path: Path):
    with pytest.raises(ConfigLoadError, match="not found"):
        load_template(tmp_path / "ghost.yaml")


def test_load_template_wrong_extension(tmp_path: Path):
    p = tmp_path / "template.json"
    p.write_text("{}")
    with pytest.raises(ConfigLoadError, match="Expected a .yaml"):
        load_template(p)


def test_load_template_invalid_yaml(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("key: [unclosed")
    with pytest.raises(ConfigLoadError, match="Failed to parse"):
        load_template(p)


def test_validate_template_success(valid_yaml: Path):
    data = load_template(valid_yaml)
    validate_template(data)  # should not raise


def test_validate_template_missing_keys():
    with pytest.raises(SchemaValidationError, match="missing required keys"):
        validate_template({"name": "x"})


def test_validate_template_invalid_type():
    with pytest.raises(SchemaValidationError, match="Invalid project type"):
        validate_template({"name": "x", "type": "rust", "structure": [{"path": "src/"}]})


def test_validate_template_empty_structure():
    with pytest.raises(SchemaValidationError, match="non-empty list"):
        validate_template({"name": "x", "type": "node", "structure": []})


def test_validate_template_entry_missing_path():
    with pytest.raises(SchemaValidationError, match="missing required key 'path'"):
        validate_template({"name": "x", "type": "python", "structure": [{"type": "file"}]})
