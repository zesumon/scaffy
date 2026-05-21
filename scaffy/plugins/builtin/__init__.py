"""Built-in scaffy plugins.

Importing this package registers all bundled plugins automatically.
"""

from scaffy.plugins.builtin import git_init  # noqa: F401
from scaffy.plugins.builtin import npm_init  # noqa: F401
from scaffy.plugins.builtin import venv_init  # noqa: F401

__all__ = ["git_init", "npm_init", "venv_init"]
