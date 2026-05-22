"""Built-in plugin: initialise Prettier config for Node.js projects."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register

_DEFAULT_CONFIG: dict = {
    "semi": True,
    "singleQuote": True,
    "tabWidth": 2,
    "trailingComma": "es5",
    "printWidth": 100,
}


class PrettierInitPlugin(BasePlugin):
    """Write a .prettierrc file and optionally install prettier as a dev dependency."""

    name = "prettier_init"

    def run(self, context: dict) -> None:
        project_type = context.get("project_type", "")
        if project_type != "node":
            return

        output_dir = Path(context.get("output_dir", "."))
        if not output_dir.exists():
            raise PluginError(f"prettier_init: output directory does not exist: {output_dir}")

        prettier_rc = output_dir / ".prettierrc"
        user_config: dict = context.get("prettier", {})
        merged = {**_DEFAULT_CONFIG, **user_config}

        try:
            prettier_rc.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            raise PluginError(f"prettier_init: could not write .prettierrc: {exc}") from exc

        if context.get("prettier_install", False):
            result = subprocess.run(
                ["npm", "install", "--save-dev", "prettier"],
                cwd=str(output_dir),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise PluginError(
                    f"prettier_init: npm install failed:\n{result.stderr.strip()}"
                )


register(PrettierInitPlugin)
