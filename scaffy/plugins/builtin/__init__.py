"""Built-in plugins shipped with scaffy.

Importing this package registers all built-in plugins so they are available
via :func:`scaffy.plugins.registry.get_plugin` without the caller needing to
import each module individually.
"""

from scaffy.plugins.builtin import git_init, npm_init  # noqa: F401  — side-effect imports

__all__ = ["git_init", "npm_init"]
