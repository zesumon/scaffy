"""Built-in plugin: write a sensible .editorconfig into the project root."""

from __future__ import annotations

from pathlib import Path

from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


EDITORCONFIG_TEMPLATE = """\
# EditorConfig — https://editorconfig.org
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{{py}}]
indent_style = space
indent_size = 4

[*.{{js,ts,json,yaml,yml}}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
"""


@register(name="editorconfig_init")
class EditorconfigInitPlugin(BasePlugin):
    """Write a .editorconfig file suited to the project type."""

    name = "editorconfig_init"

    def run(self, context: dict) -> None:  # noqa: D102
        output_dir = Path(context.get("output_dir", "."))
        if not output_dir.exists():
            raise PluginError(
                f"editorconfig_init: output directory does not exist: {output_dir}"
            )

        editorconfig = output_dir / ".editorconfig"
        try:
            editorconfig.write_text(EDITORCONFIG_TEMPLATE, encoding="utf-8")
        except OSError as exc:
            raise PluginError(
                f"editorconfig_init: failed to write .editorconfig: {exc}"
            ) from exc
