"""Resolve and run plugins declared in a template's 'plugins' section."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import get_plugin

# Ensure built-ins are registered when this module is imported.
import scaffy.plugins.builtin.git_init  # noqa: F401


def run_plugins(
    plugin_specs: list[dict[str, Any] | str],
    project_dir: Path,
    context: dict[str, Any],
) -> None:
    """Instantiate and run each plugin listed in *plugin_specs*.

    Each spec is either:
    - a plain string  → plugin name with no config
    - a dict          → ``{name: str, config: dict}``

    Args:
        plugin_specs: Raw plugin list from the resolved template.
        project_dir: Root of the scaffolded project.
        context: Resolved template variables.

    Raises:
        PluginError: Propagated from any failing plugin.
    """
    for spec in plugin_specs:
        if isinstance(spec, str):
            name, cfg = spec, {}
        elif isinstance(spec, dict):
            name = spec.get("name", "")
            cfg = spec.get("config", {})
        else:
            raise PluginError(f"Invalid plugin spec: {spec!r}")

        plugin_cls = get_plugin(name)
        plugin = plugin_cls(config=cfg)
        plugin.run(project_dir, context)
