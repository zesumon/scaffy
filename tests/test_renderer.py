"""Tests for scaffy.generator.renderer."""

import pytest
from pathlib import Path

from scaffy.generator.renderer import render_project, RenderError


@pytest.fixture
def simple_template():
    return {
        "name": "my-project",
        "structure": [
            "README.md",
            {"name": "setup.py", "content": "# setup\n"},
            {
                "name": "src",
                "type": "dir",
                "children": [
                    "__init__.py",
                    {"name": "main.py", "content": "def main(): pass\n"},
                ],
            },
        ],
    }


def test_render_project_creates_files(simple_template, tmp_path):
    dest = str(tmp_path / "my-project")
    created = render_project(simple_template, dest)

    assert Path(dest).is_dir()
    assert Path(dest, "README.md").exists()
    assert Path(dest, "setup.py").exists()
    assert Path(dest, "src").is_dir()
    assert Path(dest, "src", "__init__.py").exists()
    assert Path(dest, "src", "main.py").exists()
    assert len(created) == 6  # dest + README + setup + src/ + __init__ + main


def test_render_project_file_content(simple_template, tmp_path):
    dest = str(tmp_path / "my-project")
    render_project(simple_template, dest)

    assert Path(dest, "setup.py").read_text() == "# setup\n"
    assert Path(dest, "src", "main.py").read_text() == "def main(): pass\n"


def test_render_project_empty_structure(tmp_path):
    template = {"name": "empty", "structure": []}
    dest = str(tmp_path / "empty")
    created = render_project(template, dest)

    assert Path(dest).is_dir()
    assert created == [dest]


def test_render_project_existing_dir_raises(simple_template, tmp_path):
    dest = str(tmp_path / "existing")
    Path(dest).mkdir()

    with pytest.raises(RenderError, match="already exists"):
        render_project(simple_template, dest)


def test_render_project_invalid_entry_raises(tmp_path):
    template = {"name": "bad", "structure": [42]}
    dest = str(tmp_path / "bad")

    with pytest.raises(RenderError, match="Invalid structure entry"):
        render_project(template, dest)


def test_render_project_missing_name_raises(tmp_path):
    template = {"name": "bad", "structure": [{"type": "dir"}]}
    dest = str(tmp_path / "bad")

    with pytest.raises(RenderError, match="missing 'name'"):
        render_project(template, dest)
