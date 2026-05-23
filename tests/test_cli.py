"""Tests for the scaffy CLI entry point."""

import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from scaffy.cli import build_parser, parse_variables, main


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_returns_parser(self):
        parser = build_parser()
        assert parser is not None

    def test_new_subcommand_exists(self):
        parser = build_parser()
        args = parser.parse_args(["new", "myproject", "--template", "python"])
        assert args.command == "new"
        assert args.name == "myproject"
        assert args.template == "python"

    def test_new_requires_name(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["new"])

    def test_new_output_dir_default(self):
        parser = build_parser()
        args = parser.parse_args(["new", "myproject", "--template", "python"])
        assert args.output is None

    def test_new_output_dir_custom(self):
        parser = build_parser()
        args = parser.parse_args(
            ["new", "myproject", "--template", "python", "--output", "/tmp/out"]
        )
        assert args.output == "/tmp/out"

    def test_list_subcommand_exists(self):
        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"

    def test_var_flag_accepts_multiple(self):
        parser = build_parser()
        args = parser.parse_args(
            ["new", "proj", "--template", "python", "--var", "author=Alice", "--var", "version=1.0"]
        )
        assert args.var == ["author=Alice", "version=1.0"]

    def test_no_subcommand_prints_help(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])


# ---------------------------------------------------------------------------
# parse_variables
# ---------------------------------------------------------------------------

class TestParseVariables:
    def test_empty_list(self):
        assert parse_variables([]) == {}

    def test_none_returns_empty(self):
        assert parse_variables(None) == {}

    def test_single_pair(self):
        assert parse_variables(["author=Alice"]) == {"author": "Alice"}

    def test_multiple_pairs(self):
        result = parse_variables(["author=Alice", "version=1.0"])
        assert result == {"author": "Alice", "version": "1.0"}

    def test_value_with_equals_sign(self):
        # Only the first '=' is used as separator
        result = parse_variables(["url=http://example.com/a=b"])
        assert result == {"url": "http://example.com/a=b"}

    def test_malformed_entry_raises(self):
        with pytest.raises((ValueError, SystemExit)):
            parse_variables(["no-equals-sign"])


# ---------------------------------------------------------------------------
# main — integration-style, heavily mocked
# ---------------------------------------------------------------------------

class TestMain:
    def _make_new_args(self, name="myproject", template="python", output=None, var=None):
        return Namespace(
            command="new",
            name=name,
            template=template,
            output=output,
            var=var or [],
        )

    @patch("scaffy.cli.run_plugins")
    @patch("scaffy.cli.render_project")
    @patch("scaffy.cli.apply_defaults")
    @patch("scaffy.cli.validate_template")
    @patch("scaffy.cli.resolve_template")
    @patch("scaffy.cli.load_template")
    @patch("scaffy.cli.build_parser")
    def test_main_new_calls_pipeline(
        self, mock_bp, mock_load, mock_resolve, mock_validate,
        mock_defaults, mock_render, mock_plugins
    ):
        mock_parser = MagicMock()
        mock_bp.return_value = mock_parser
        mock_parser.parse_args.return_value = self._make_new_args()

        mock_load.return_value = {"name": "myproject", "type": "python", "structure": []}
        mock_resolve.return_value = "/some/path/python.yaml"
        mock_validate.return_value = None
        mock_defaults.return_value = {"name": "myproject", "type": "python", "structure": [], "variables": {}}
        mock_render.return_value = None
        mock_plugins.return_value = None

        main()

        mock_load.assert_called_once()
        mock_validate.assert_called_once()
        mock_defaults.assert_called_once()
        mock_render.assert_called_once()
        mock_plugins.assert_called_once()

    @patch("scaffy.cli.list_templates")
    @patch("scaffy.cli.build_parser")
    def test_main_list_calls_list_templates(self, mock_bp, mock_list):
        mock_parser = MagicMock()
        mock_bp.return_value = mock_parser
        mock_parser.parse_args.return_value = Namespace(command="list")
        mock_list.return_value = ["python", "node"]

        main()  # should not raise

        mock_list.assert_called_once()
