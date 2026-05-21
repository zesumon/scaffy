"""Built-in scaffy plugins — imported here so they self-register."""

from scaffy.plugins.builtin import git_init  # noqa: F401
from scaffy.plugins.builtin import npm_init  # noqa: F401
from scaffy.plugins.builtin import venv_init  # noqa: F401
from scaffy.plugins.builtin import pip_install  # noqa: F401

__all__ = ["git_init", "npm_init", "venv_init", "pip_install"]
