"""Built-in plugin: install Python dependencies via pip."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


class PipInstallPlugin(BasePlugin):
    """Runs `pip install -r requirements.txt` inside the project directory.

    Skipped silently when no *requirements.txt* is present.
    """

    name = "pip_install"

    def run(self, context: dict) -> None:  # noqa: D102
        project_dir = Path(context.get("output_dir", "."))
        requirements = project_dir / "requirements.txt"

        if not requirements.exists():
            return

        venv_python = project_dir / ".venv" / "bin" / "python"
        python_bin = str(venv_python) if venv_python.exists() else "python"

        cmd = [python_bin, "-m", "pip", "install", "-r", str(requirements)]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise PluginError(
                f"pip_install: python executable not found — {exc}"
            ) from exc

        if result.returncode != 0:
            raise PluginError(
                f"pip_install: pip exited with code {result.returncode}\n"
                f"{result.stderr.strip()}"
            )


register(PipInstallPlugin)
