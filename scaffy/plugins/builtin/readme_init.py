"""Built-in plugin: generate a README.md for the scaffolded project."""

from __future__ import annotations

import textwrap
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


class ReadmeInitPlugin(BasePlugin):
    """Writes a minimal README.md into the project root."""

    name = "readme_init"

    def run(self, context: dict) -> None:  # noqa: D102
        project_path: Path = context.get("project_path")
        if project_path is None:
            raise PluginError("readme_init: 'project_path' missing from context")

        project_name: str = context.get("project_name", project_path.name)
        description: str = context.get("description", "")
        author: str = context.get("author", "")
        license_name: str = context.get("license", "MIT")
        project_type: str = context.get("project_type", "")

        lines = [f"# {project_name}", ""]

        if description:
            lines += [description, ""]

        if project_type == "python":
            lines += [
                "## Getting Started",
                "",
                "```bash",
                "python -m venv .venv",
                "source .venv/bin/activate",
                "pip install -r requirements.txt",
                "```",
                "",
            ]
        elif project_type == "node":
            lines += [
                "## Getting Started",
                "",
                "```bash",
                "npm install",
                "npm start",
                "```",
                "",
            ]

        if author:
            lines += [f"## Author", "", author, ""]

        lines += [f"## License", "", license_name, ""]

        readme_path = project_path / "README.md"
        try:
            readme_path.write_text("\n".join(lines), encoding="utf-8")
        except OSError as exc:
            raise PluginError(f"readme_init: could not write README.md: {exc}") from exc


register(ReadmeInitPlugin)
