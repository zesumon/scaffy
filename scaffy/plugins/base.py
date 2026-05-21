"""Base plugin interface for scaffy post-generation hooks."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class PluginError(Exception):
    """Raised when a plugin fails during execution."""


class BasePlugin(ABC):
    """Abstract base class for all scaffy plugins.

    Plugins are executed after the project structure has been rendered.
    They receive the output directory and the resolved template context.
    """

    #: Short identifier used in template YAML to reference this plugin.
    name: str = ""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config: dict[str, Any] = config or {}

    @abstractmethod
    def run(self, project_dir: Path, context: dict[str, Any]) -> None:
        """Execute the plugin against the generated project directory.

        Args:
            project_dir: Root directory of the newly scaffolded project.
            context: Resolved template variables passed by the renderer.

        Raises:
            PluginError: If the plugin cannot complete its task.
        """

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(name={self.name!r})"
