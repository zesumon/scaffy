"""Built-in plugin: initialise a Python virtual environment."""

import subprocess
import sys
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


class VenvInitPlugin(BasePlugin):
    """Create a Python virtual environment inside the generated project."""

    name = "venv_init"

    def run(self, context: dict) -> None:
        """Run ``python -m venv .venv`` in the project output directory.

        Args:
            context: Scaffold context dict.  Must contain ``output_dir``.

        Raises:
            PluginError: If the venv creation command fails or the project
                type is not ``python``.
        """
        project_type = context.get("project_type", "python")
        if project_type != "python":
            return

        output_dir = context.get("output_dir")
        if not output_dir:
            raise PluginError("venv_init: 'output_dir' missing from context")

        target = Path(output_dir)
        if not target.is_dir():
            raise PluginError(
                f"venv_init: output directory does not exist: {target}"
            )

        venv_dir = target / ".venv"
        cmd = [sys.executable, "-m", "venv", str(venv_dir)]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(target),
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            raise PluginError(f"venv_init: failed to run venv command: {exc}") from exc

        if result.returncode != 0:
            raise PluginError(
                f"venv_init: venv creation failed:\n{result.stderr.strip()}"
            )


register(VenvInitPlugin)
