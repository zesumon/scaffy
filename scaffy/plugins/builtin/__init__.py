"""Auto-import all built-in plugins so their @register decorators fire."""

from scaffy.plugins.builtin import (
    git_init,
    npm_init,
    venv_init,
    pip_install,
    prettier_init,
    eslint_init,
    editorconfig_init,
    license_init,
    readme_init,
    gitignore_init,
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
    "readme_init",
    "gitignore_init",
]
