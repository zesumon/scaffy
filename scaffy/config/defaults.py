"""Default values and fallback resolution for template configs."""

from typing import Any

# Default structure applied when optional keys are missing from a template
TEMPLATE_DEFAULTS: dict[str, Any] = {
    "version": "1.0",
    "description": "",
    "variables": {},
    "plugins": [],
    "structure": [],
}

# Allowed project types
SUPPORTED_TYPES = {"python", "node"}


def apply_defaults(template: dict[str, Any]) -> dict[str, Any]:
    """Return a new template dict with missing keys filled from TEMPLATE_DEFAULTS.

    Only top-level keys are defaulted; existing values are never overwritten.

    Args:
        template: A raw parsed template dictionary.

    Returns:
        A new dictionary with defaults merged in.
    """
    result = dict(TEMPLATE_DEFAULTS)
    result.update(template)
    return result


def resolve_variables(template: dict[str, Any], overrides: dict[str, str]) -> dict[str, Any]:
    """Merge CLI-supplied variable overrides into the template's variable map.

    Values provided via *overrides* take precedence over the defaults declared
    inside the template file.

    Args:
        template:  Template dict (should already have defaults applied).
        overrides: Key/value pairs supplied by the user at runtime.

    Returns:
        A shallow copy of *template* whose ``variables`` key reflects the
        merged values.
    """
    merged_vars = dict(template.get("variables", {}))
    merged_vars.update(overrides)
    return {**template, "variables": merged_vars}


def get_project_type(template: dict[str, Any]) -> str:
    """Return the normalised project type string.

    Raises:
        ValueError: If the type is absent or not in SUPPORTED_TYPES.
    """
    raw = template.get("type", "").strip().lower()
    if raw not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported project type {raw!r}. Must be one of: {sorted(SUPPORTED_TYPES)}"
        )
    return raw
