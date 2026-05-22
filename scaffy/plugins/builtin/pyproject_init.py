"""Plugin that generates a pyproject.toml for Python projects."""

from __future__ import annotations

import textwrap
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


@register
class PyprojectInitPlugin(BasePlugin):
    name = "pyproject_init"

    def run(self, context: dict) -> None:
        project_type = context.get("project_type", "")
        if project_type != "python":
            return

        output_dir = Path(context.get("output_dir", "."))
        project_name = context.get("project_name", "my-project")
        author = context.get("author", "")
        description = context.get("description", "")
        python_version = context.get("python_version", "3.11")
        dependencies = context.get("dependencies", [])

        deps_lines = ""
        if dependencies:
            joined = ", ".join(f'"{d}"' for d in dependencies)
            deps_lines = f"dependencies = [{joined}]\n"
        else:
            deps_lines = "dependencies = []\n"

        content = textwrap.dedent(f"""\
            [build-system]
            requires = ["setuptools>=68", "wheel"]
            build-backend = "setuptools.backends.legacy:build"

            [project]
            name = "{project_name}"
            version = "0.1.0"
            description = "{description}"
            authors = [{{name = "{author}"}}]
            requires-python = ">={python_version}"
            {deps_lines}
            [tool.setuptools.packages.find]
            where = ["src"]
        """)

        target = output_dir / "pyproject.toml"
        if target.exists():
            raise PluginError(
                f"pyproject_init: {target} already exists"
            )

        try:
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise PluginError(f"pyproject_init: failed to write file: {exc}") from exc
