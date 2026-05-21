# scaffy

An opinionated project scaffolding tool that generates boilerplate for common Python and Node.js project structures from YAML templates.

---

## Installation

```bash
pip install scaffy
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install scaffy
```

---

## Usage

Initialize a new project using a built-in template:

```bash
scaffy init my-project --template python-package
```

Use a custom YAML template:

```bash
scaffy init my-app --template ./my-template.yaml
```

List available built-in templates:

```bash
scaffy list
```

**Example template (`python-package.yaml`):**

```yaml
name: python-package
structure:
  - src/{{ project_name }}/__init__.py
  - tests/test_main.py
  - README.md
  - pyproject.toml
  - .gitignore
```

Scaffy will prompt for any variables defined in the template and generate the full project structure in seconds.

---

## Supported Templates

| Template | Description |
|---|---|
| `python-package` | Src-layout Python package with pyproject.toml |
| `python-cli` | Click-based CLI application |
| `node-express` | Minimal Express.js REST API |
| `node-cli` | Node.js CLI with commander.js |

---

## License

[MIT](LICENSE)