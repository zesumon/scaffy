"""YAML template loader for scaffy project configurations."""

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TEMPLATE_DIRS = [
    Path.home() / ".scaffy" / "templates",
    Path(__file__).parent.parent / "templates",
]


class ConfigLoadError(Exception):
    """Raised when a template config cannot be loaded or parsed."""


def load_template(path: str | Path) -> dict[str, Any]:
    """Load and parse a YAML template file.

    Args:
        path: Absolute or relative path to the YAML template.

    Returns:
        Parsed template as a dictionary.

    Raises:
        ConfigLoadError: If the file is missing or contains invalid YAML.
    """
    path = Path(path)
    if not path.exists():
        raise ConfigLoadError(f"Template file not found: {path}")
    if path.suffix not in (".yaml", ".yml"):
        raise ConfigLoadError(f"Expected a .yaml/.yml file, got: {path.suffix}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ConfigLoadError(f"Failed to parse YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigLoadError(f"Template root must be a mapping, got {type(data).__name__}")

    return data


def resolve_template(name: str) -> Path:
    """Search default template directories for a named template.

    Args:
        name: Template name without extension (e.g. 'python-lib').

    Returns:
        Path to the first matching template file.

    Raises:
        ConfigLoadError: If no matching template is found.
    """
    for directory in DEFAULT_TEMPLATE_DIRS:
        for ext in (".yaml", ".yml"):
            candidate = directory / f"{name}{ext}"
            if candidate.exists():
                return candidate

    searched = ", ".join(str(d) for d in DEFAULT_TEMPLATE_DIRS)
    raise ConfigLoadError(
        f"Template '{name}' not found. Searched in: {searched}"
    )


def list_templates() -> list[str]:
    """Return the names of all available templates across default directories.

    Templates are deduplicated by name; directories earlier in
    ``DEFAULT_TEMPLATE_DIRS`` take precedence (their names appear first).

    Returns:
        Sorted list of template names without file extensions.
    """
    seen: set[str] = set()
    names: list[str] = []
    for directory in DEFAULT_TEMPLATE_DIRS:
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir()):
            if entry.suffix in (".yaml", ".yml") and entry.stem not in seen:
                seen.add(entry.stem)
                names.append(entry.stem)
    return names
