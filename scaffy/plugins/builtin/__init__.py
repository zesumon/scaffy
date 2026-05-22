"""Built-in scaffy plugins — imported here so they self-register."""

from scaffy.plugins.builtin import (
    git_init,
    npm_init,
    venv_init,
    pip_install,
    prettier_init,
    eslint_init,
    editorconfig_init,
    license_init,
)

__all__ = [
    "git_init",
    "npm_init",
    "venv_init",
    "pip_install",
    "prettier_init",
    "eslint_init",
    "editorconfig_init",
    "license_init",
]
