"""Built-in plugin: initializes a package.json for Node.js projects."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register

logger = logging.getLogger(__name__)


class NpmInitPlugin(BasePlugin):
    """Generates a minimal package.json in the project output directory."""

    name = "npm_init"

    def run(self, context: dict) -> None:  # noqa: D401
        """Write package.json based on template variables."""
        output_dir: str | None = context.get("output_dir")
        if not output_dir:
            raise PluginError("npm_init: 'output_dir' missing from context")

        project_type = context.get("project_type", "")
        if project_type not in ("node", "nodejs"):
            logger.debug(
                "npm_init: skipping — project_type is %r, not node/nodejs", project_type
            )
            return

        variables = context.get("variables", {})
        package = {
            "name": variables.get("project_name", Path(output_dir).name),
            "version": variables.get("version", "0.1.0"),
            "description": variables.get("description", ""),
            "main": "index.js",
            "scripts": {
                "test": 'echo "Error: no test specified" && exit 1'
            },
            "keywords": [],
            "author": variables.get("author", ""),
            "license": variables.get("license", "MIT"),
        }

        package_path = Path(output_dir) / "package.json"
        try:
            package_path.write_text(
                json.dumps(package, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as exc:
            raise PluginError(f"npm_init: could not write package.json — {exc}") from exc

        logger.info("npm_init: wrote %s", package_path)


register(NpmInitPlugin)
