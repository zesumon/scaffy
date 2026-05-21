"""Tests for scaffy/config/defaults.py"""

import pytest
from scaffy.config.defaults import (
    apply_defaults,
    resolve_variables,
    get_project_type,
    TEMPLATE_DEFAULTS,
    SUPPORTED_TYPES,
)


# ---------------------------------------------------------------------------
# apply_defaults
# ---------------------------------------------------------------------------

def test_apply_defaults_fills_missing_keys():
    result = apply_defaults({"name": "my-project", "type": "python"})
    for key, value in TEMPLATE_DEFAULTS.items():
        assert key in result
        # Keys not supplied by the template should equal the default
        if key not in {"name", "type"}:
            assert result[key] == value


def test_apply_defaults_does_not_overwrite_existing():
    template = {"version": "2.5", "description": "custom desc", "type": "node"}
    result = apply_defaults(template)
    assert result["version"] == "2.5"
    assert result["description"] == "custom desc"


def test_apply_defaults_returns_new_dict():
    original = {"type": "python"}
    result = apply_defaults(original)
    assert result is not original


def test_apply_defaults_empty_template():
    result = apply_defaults({})
    assert result == TEMPLATE_DEFAULTS


# ---------------------------------------------------------------------------
# resolve_variables
# ---------------------------------------------------------------------------

def test_resolve_variables_merges_overrides():
    template = {"variables": {"author": "Alice", "license": "MIT"}}
    result = resolve_variables(template, {"author": "Bob"})
    assert result["variables"]["author"] == "Bob"
    assert result["variables"]["license"] == "MIT"


def test_resolve_variables_adds_new_keys():
    template = {"variables": {}}
    result = resolve_variables(template, {"project_name": "scaffy"})
    assert result["variables"]["project_name"] == "scaffy"


def test_resolve_variables_no_overrides():
    template = {"variables": {"x": "1"}}
    result = resolve_variables(template, {})
    assert result["variables"] == {"x": "1"}


def test_resolve_variables_does_not_mutate_original():
    template = {"variables": {"a": "original"}}
    resolve_variables(template, {"a": "changed"})
    assert template["variables"]["a"] == "original"


# ---------------------------------------------------------------------------
# get_project_type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ptype", list(SUPPORTED_TYPES))
def test_get_project_type_valid(ptype):
    assert get_project_type({"type": ptype}) == ptype


def test_get_project_type_case_insensitive():
    assert get_project_type({"type": "Python"}) == "python"
    assert get_project_type({"type": "NODE"}) == "node"


def test_get_project_type_invalid_raises():
    with pytest.raises(ValueError, match="Unsupported project type"):
        get_project_type({"type": "ruby"})


def test_get_project_type_missing_raises():
    with pytest.raises(ValueError):
        get_project_type({})
