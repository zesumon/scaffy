"""Built-in plugin: initialise ESLint config for Node.js projects."""

from __future__ import annotations

import json
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


DEFAULT_ESLINT_CONFIG = {
    "env": {
        "browser": True,
        "es2021": True,
        "node": True,
    },
    "extends": ["eslint:recommended"],
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module",
    },
    "rules": {},
}


@register(name="eslint_init")
class EslintInitPlugin(BasePlugin):
    """Write a default .eslintrc.json into the project root.

    Skipped automatically for non-Node.js projects.
    """

    name = "eslint_init"

    def run(self, context: dict) -> None:  # noqa: D102
        project_type = context.get("project_type", "")
        if project_type != "node":
            return

        output_dir = Path(context.get("output_dir", "."))
        if not output_dir.exists():
            raise PluginError(
                f"eslint_init: output directory does not exist: {output_dir}"
            )

        config = dict(DEFAULT_ESLINT_CONFIG)
        # Allow template-level overrides via variables
        variables = context.get("variables", {})
        if "eslint_extends" in variables:
            extends = variables["eslint_extends"]
            config["extends"] = (
                extends if isinstance(extends, list) else [extends]
            )

        eslintrc = output_dir / ".eslintrc.json"
        try:
            eslintrc.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            raise PluginError(f"eslint_init: failed to write .eslintrc.json: {exc}") from exc
