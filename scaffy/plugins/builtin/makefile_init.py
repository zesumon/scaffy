"""Built-in plugin: generate a basic Makefile for Python or Node projects."""

from __future__ import annotations

from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register

_PYTHON_MAKEFILE = """\
.PHONY: install test lint format clean

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	flake8 .

format:
	black .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -delete
"""

_NODE_MAKEFILE = """\
.PHONY: install test lint format clean

install:
	npm install

test:
	npm test

lint:
	npx eslint .

format:
	npx prettier --write .

clean:
	rm -rf node_modules dist build
"""


@register
class MakefileInitPlugin(BasePlugin):
    name = "makefile_init"

    def run(self, context: dict) -> None:
        output_dir = Path(context.get("output_dir", "."))
        project_type = context.get("project_type", "python")

        makefile_path = output_dir / "Makefile"

        if makefile_path.exists():
            raise PluginError(
                f"makefile_init: Makefile already exists at {makefile_path}"
            )

        if project_type == "python":
            content = _PYTHON_MAKEFILE
        elif project_type == "node":
            content = _NODE_MAKEFILE
        else:
            # Generic fallback — just write an empty Makefile stub
            content = ".PHONY: help\n\nhelp:\n\t@echo 'No targets defined yet.'\n"

        makefile_path.write_text(content)
