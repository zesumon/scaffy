"""Built-in plugin: initialise a git repository in the new project."""

import subprocess
from pathlib import Path
from typing import Any

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


@register
class GitInitPlugin(BasePlugin):
    """Runs ``git init`` (and optionally ``git add -A``) in the project dir."""

    name = "git_init"

    def run(self, project_dir: Path, context: dict[str, Any]) -> None:  # noqa: ARG002
        """Initialise a git repo.  Optionally stage all files."""
        try:
            subprocess.run(
                ["git", "init", str(project_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise PluginError("git executable not found on PATH.") from exc
        except subprocess.CalledProcessError as exc:
            raise PluginError(f"git init failed: {exc.stderr.strip()}") from exc

        if self.config.get("initial_commit", False):
            try:
                subprocess.run(
                    ["git", "-C", str(project_dir), "add", "-A"],
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(project_dir),
                        "commit",
                        "-m",
                        "chore: initial scaffold",
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as exc:
                raise PluginError(
                    f"git commit failed: {exc.stderr.strip()}"
                ) from exc
