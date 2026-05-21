"""Plugin registry — maps plugin names to their classes and manages loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

from scaffy.plugins.base import BasePlugin, PluginError

if TYPE_CHECKING:
    pass

_REGISTRY: dict[str, Type[BasePlugin]] = {}


def register(cls: Type[BasePlugin]) -> Type[BasePlugin]:
    """Class decorator that registers a plugin by its *name* attribute."""
    if not cls.name:
        raise PluginError(f"Plugin {cls.__name__} must define a non-empty 'name'.")
    if cls.name in _REGISTRY:
        raise PluginError(f"Plugin name '{cls.name}' is already registered.")
    _REGISTRY[cls.name] = cls
    return cls


def get_plugin(name: str) -> Type[BasePlugin]:
    """Return the plugin class for *name*.

    Raises:
        PluginError: If no plugin with that name is registered.
    """
    try:
        return _REGISTRY[name]
    except KeyError:
        available = ", ".join(sorted(_REGISTRY)) or "<none>"
        raise PluginError(
            f"Unknown plugin '{name}'. Available plugins: {available}"
        ) from None


def list_plugins() -> list[str]:
    """Return sorted list of all registered plugin names."""
    return sorted(_REGISTRY.keys())


def clear_registry() -> None:  # used in tests
    """Remove all registered plugins (test helper)."""
    _REGISTRY.clear()
