"""Validation schema for scaffy YAML templates."""

from typing import Any

REQUIRED_KEYS = {"name", "type", "structure"}
VALID_TYPES = {"python", "node"}


class SchemaValidationError(Exception):
    """Raised when a template does not conform to the expected schema."""


def validate_template(data: dict[str, Any]) -> None:
    """Validate the structure of a loaded template dictionary.

    Args:
        data: Parsed template data from a YAML file.

    Raises:
        SchemaValidationError: If required keys are missing or values are invalid.
    """
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise SchemaValidationError(
            f"Template is missing required keys: {', '.join(sorted(missing))}"
        )

    project_type = data["type"]
    if project_type not in VALID_TYPES:
        raise SchemaValidationError(
            f"Invalid project type '{project_type}'. Must be one of: {', '.join(VALID_TYPES)}"
        )

    structure = data["structure"]
    if not isinstance(structure, list) or not structure:
        raise SchemaValidationError(
            "'structure' must be a non-empty list of file/directory entries."
        )

    for i, entry in enumerate(structure):
        if not isinstance(entry, dict):
            raise SchemaValidationError(
                f"structure[{i}] must be a mapping, got {type(entry).__name__}"
            )
        if "path" not in entry:
            raise SchemaValidationError(
                f"structure[{i}] is missing required key 'path'."
            )
        if "type" in entry and entry["type"] not in ("file", "dir"):
            raise SchemaValidationError(
                f"structure[{i}].type must be 'file' or 'dir', got '{entry['type']}'"
            )
