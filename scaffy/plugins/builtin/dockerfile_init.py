"""Plugin that generates a basic Dockerfile for the project."""

from __future__ import annotations

import os
from scaffy.plugins.base import BasePlugin, PluginError
from scaffy.plugins.registry import register


PYTHON_DOCKERFILE = """\
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "{name}"]
"""

NODE_DOCKERFILE = """\
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

CMD ["node", "index.js"]
"""

DOCKERIGNORE_CONTENT = """\
.git
.env
*.pyc
__pycache__
.venv
node_modules
dist
"""


@register("dockerfile_init")
class DockerfileInitPlugin(BasePlugin):
    """Writes a Dockerfile and .dockerignore suited to the project type."""

    name = "dockerfile_init"

    def run(self, context: dict) -> None:
        project_type = context.get("project_type", "python")
        output_dir = context.get("output_dir", ".")
        project_name = context.get("project_name", "app")

        if project_type == "python":
            dockerfile_content = PYTHON_DOCKERFILE.format(name=project_name)
        elif project_type == "node":
            dockerfile_content = NODE_DOCKERFILE
        else:
            raise PluginError(
                f"dockerfile_init: unsupported project_type '{project_type}'"
            )

        dockerfile_path = os.path.join(output_dir, "Dockerfile")
        dockerignore_path = os.path.join(output_dir, ".dockerignore")

        try:
            with open(dockerfile_path, "w", encoding="utf-8") as fh:
                fh.write(dockerfile_content.lstrip("\n"))
            with open(dockerignore_path, "w", encoding="utf-8") as fh:
                fh.write(DOCKERIGNORE_CONTENT.lstrip("\n"))
        except OSError as exc:
            raise PluginError(f"dockerfile_init: could not write files: {exc}") from exc
