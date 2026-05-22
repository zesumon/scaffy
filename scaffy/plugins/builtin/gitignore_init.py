"""Built-in plugin: write a .gitignore file based on project type."""

from __future__ import annotations

import os
from typing import Any, Dict

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register

_PYTHON_PATTERNS = [
    "__pycache__/",
    "*.py[cod]",
    "*.egg-info/",
    "dist/",
    "build/",
    ".venv/",
    "venv/",
    ".env",
    ".pytest_cache/",
    ".mypy_cache/",
    "*.so",
]

_NODE_PATTERNS = [
    "node_modules/",
    "dist/",
    "build/",
    ".env",
    "*.log",
    ".DS_Store",
    "coverage/",
    ".next/",
]

_COMMON_PATTERNS = [
    ".DS_Store",
    "Thumbs.db",
    "*.swp",
    "*.swo",
]


@register
class GitignoreInitPlugin(BasePlugin):
    name = "gitignore_init"

    def run(self, context: Dict[str, Any]) -> None:
        output_dir: str = context.get("output_dir", ".")
        project_type: str = context.get("project_type", "")

        if project_type == "python":
            patterns = _PYTHON_PATTERNS + _COMMON_PATTERNS
        elif project_type == "node":
            patterns = _NODE_PATTERNS + _COMMON_PATTERNS
        else:
            patterns = _COMMON_PATTERNS

        gitignore_path = os.path.join(output_dir, ".gitignore")
        try:
            with open(gitignore_path, "w") as fh:
                fh.write("\n".join(patterns) + "\n")
        except OSError as exc:
            raise PluginError(f"gitignore_init: could not write .gitignore: {exc}") from exc
