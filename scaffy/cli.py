"""Command-line interface for scaffy.

Entry point for the scaffy CLI tool. Handles argument parsing and
orchestrates config loading, validation, and project generation.
"""

import argparse
import sys
from pathlib import Path

from scaffy.config.loader import ConfigLoadError, load_template, resolve_template
from scaffy.config.schema import SchemaValidationError, validate_template
from scaffy.generator.renderer import RenderError, render_project


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="scaffy",
        description="Generate boilerplate for Python and Node.js projects from YAML templates.",
    )

    parser.add_argument(
        "template",
        type=str,
        help="Path to a YAML template file, or a built-in template name (e.g. 'python-lib').",
    )

    parser.add_argument(
        "output",
        type=str,
        nargs="?",
        default=".",
        help="Directory where the project will be generated (default: current directory).",
    )

    parser.add_argument(
        "--var",
        metavar="KEY=VALUE",
        action="append",
        default=[],
        dest="variables",
        help="Template variable in KEY=VALUE format. Can be specified multiple times.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing any files.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    return parser


def parse_variables(raw: list[str]) -> dict[str, str]:
    """Parse a list of 'KEY=VALUE' strings into a dictionary.

    Args:
        raw: List of strings in 'KEY=VALUE' format.

    Returns:
        Dictionary of variable name to value.

    Raises:
        SystemExit: If any entry is malformed.
    """
    variables: dict[str, str] = {}
    for entry in raw:
        if "=" not in entry:
            print(f"error: invalid variable format '{entry}' — expected KEY=VALUE", file=sys.stderr)
            sys.exit(1)
        key, _, value = entry.partition("=")
        key = key.strip()
        if not key:
            print(f"error: empty key in variable '{entry}'", file=sys.stderr)
            sys.exit(1)
        variables[key] = value
    return variables


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the scaffy CLI.

    Args:
        argv: Argument list (defaults to sys.argv when None).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    variables = parse_variables(args.variables)
    output_dir = Path(args.output)

    # Resolve built-in template names or file paths
    try:
        template_path = resolve_template(args.template)
    except ConfigLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Load and validate the template
    try:
        template = load_template(template_path)
        validate_template(template)
    except (ConfigLoadError, SchemaValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"[dry-run] would generate project in: {output_dir.resolve()}")
        print(f"[dry-run] template: {template_path}")
        if variables:
            print(f"[dry-run] variables: {variables}")
        return 0

    # Generate the project
    try:
        render_project(template, output_dir, variables=variables)
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Project generated in {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
