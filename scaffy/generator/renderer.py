"""Template renderer for scaffy project generation."""

import os
from pathlib import Path
from typing import Any


class RenderError(Exception):
    """Raised when project rendering fails."""
    pass


def render_project(template: dict[str, Any], output_dir: str) -> list[str]:
    """Render a validated template into a directory structure.

    Args:
        template: Validated template dict from load_template/validate_template.
        output_dir: Path to the directory where the project will be created.

    Returns:
        List of created file/directory paths.

    Raises:
        RenderError: If output_dir already exists or rendering fails.
    """
    dest = Path(output_dir)

    if dest.exists():
        raise RenderError(f"Output directory already exists: {output_dir}")

    created: list[str] = []

    try:
        dest.mkdir(parents=True)
        created.append(str(dest))

        for entry in template.get("structure", []):
            created.extend(_render_entry(entry, dest))

    except OSError as exc:
        raise RenderError(f"Failed to create project structure: {exc}") from exc

    return created


def _render_entry(entry: dict[str, Any] | str, base: Path) -> list[str]:
    """Recursively render a single structure entry."""
    created: list[str] = []

    if isinstance(entry, str):
        file_path = base / entry
        file_path.touch()
        created.append(str(file_path))
        return created

    if not isinstance(entry, dict):
        raise RenderError(f"Invalid structure entry: {entry!r}")

    name = entry.get("name")
    if not name:
        raise RenderError("Structure entry missing 'name' field.")

    path = base / name

    if entry.get("type") == "dir":
        path.mkdir(parents=True, exist_ok=True)
        created.append(str(path))
        for child in entry.get("children", []):
            created.extend(_render_entry(child, path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = entry.get("content", "")
        path.write_text(content, encoding="utf-8")
        created.append(str(path))

    return created
