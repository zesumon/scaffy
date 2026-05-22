"""Tests for the LicenseInitPlugin."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from scaffy.plugins.builtin.license_init import LicenseInitPlugin, LICENSE_TEMPLATES
from scaffy.plugins.base import PluginError
from scaffy.plugins.registry import clear_registry, get_plugin


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    clear_registry()


@pytest.fixture
def plugin():
    return LicenseInitPlugin()


@pytest.fixture
def base_context(tmp_path):
    return {
        "output_dir": str(tmp_path),
        "variables": {"author": "Jane Doe", "license": "mit"},
    }


def test_license_creates_file(plugin, base_context, tmp_path):
    plugin.run(base_context)
    assert (tmp_path / "LICENSE").exists()


def test_license_mit_content(plugin, base_context, tmp_path):
    plugin.run(base_context)
    content = (tmp_path / "LICENSE").read_text()
    assert "MIT License" in content
    assert "Jane Doe" in content
    assert str(datetime.date.today().year) in content


def test_license_apache2(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "variables": {"author": "Acme Corp", "license": "apache2"}}
    plugin.run(ctx)
    content = (tmp_path / "LICENSE").read_text()
    assert "Apache License" in content
    assert "Acme Corp" in content


def test_license_gpl3(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "variables": {"author": "Bob", "license": "gpl3"}}
    plugin.run(ctx)
    content = (tmp_path / "LICENSE").read_text()
    assert "GNU GENERAL PUBLIC LICENSE" in content


def test_license_defaults_to_mit_when_not_specified(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "variables": {"author": "Someone"}}
    plugin.run(ctx)
    content = (tmp_path / "LICENSE").read_text()
    assert "MIT License" in content


def test_license_unknown_type_raises(plugin, tmp_path):
    ctx = {"output_dir": str(tmp_path), "variables": {"license": "bsd999"}}
    with pytest.raises(PluginError, match="Unknown license type"):
        plugin.run(ctx)


def test_license_registered():
    from scaffy.plugins.builtin.license_init import LicenseInitPlugin  # re-import triggers register
    found = get_plugin("license_init")
    assert found is LicenseInitPlugin


def test_license_repr(plugin):
    assert "license_init" in repr(plugin)


def test_all_templates_have_year_and_author_placeholders():
    for name, tmpl in LICENSE_TEMPLATES.items():
        assert "{year}" in tmpl, f"{name} missing {{year}}"
        assert "{author}" in tmpl, f"{name} missing {{author}}"
