"""Most of argparse examples rebuilt with climp."""
import pytest
import argparse
from . import examples
from decli import cli
import unittest


class Test(unittest.TestCase):
    def test_main_example_ok(self):
        parser = examples.main_example()
        args = parser.parse_args("1 2 3 4".split())

        assert args.accumulate(args.integers) == 4

    def test_main_example_sums_ok(self):
        parser = examples.main_example()
        args = parser.parse_args("1 2 3 4 --sum".split())

        assert args.accumulate(args.integers) == 10

    def test_main_example_fails(self):
        parser = examples.main_example()

        with pytest.raises(SystemExit):
            args = parser.parse_args("a b c".split())
            args.accumulate(args.integers)

    def test_complete_example(self):
        parser = examples.complete_example()
        args = parser.parse_args("sum 1 2 3".split())

        assert args.func(args.integers) == 6

    def test_compose_clis_using_parents(self):
        data = {"prog": "daddy", "arguments": [{"name": "something"}]}
        parents = examples.compose_clis_using_parents()
        parser = cli(data, parents=parents)
        args = parser.parse_args(["--foo-parent", "2", "XXX"])

        assert args.something == "XXX"
        assert args.foo_parent == 2

    def test_compose_clis_using_parents_and_arguments(self):
        data = {"prog": "daddy", "arguments": [{"name": "--something"}]}
        parents = examples.compose_clis_using_parents()
        parser = cli(data, parents=parents)
        args = parser.parse_args(["--something", "XXX"])

        assert args.something == "XXX"

    def test_prefix_chars(self):
        data = examples.prefix_chars()
        parser = cli(data)
        args = parser.parse_args("+f X ++bar Y".split())

        assert args.foo == "X"
        assert args.bar == "Y"

    def test_name_or_flags(self):
        data = examples.name_or_flags()
        parser = cli(data)

        args = parser.parse_args(["HELLO"])
        assert args.bar == "HELLO"

        args = parser.parse_args(["BAR", "--foo", "FOO"])
        assert args.bar == "BAR"
        assert args.foo == "FOO"

    def test_name_or_flags_fail(self):
        data = examples.name_or_flags()
        parser = cli(data)
        with pytest.raises(SystemExit):
            parser.parse_args(["--foo", "FOO"])

    def test_cli_no_args(self):
        data = {"prog": "daddy", "description": "helloo"}
        parser = cli(data)
        args = parser.parse_args([])

        assert args.__dict__ == {}

    def test_groups(self):
        data = examples.grouping_arguments()
        parser = cli(data)
        help_result = parser.format_help()

        assert "app" in help_result
        assert "package" in help_result

    def test_not_optional_arg_name_validation_fails(self):
        data = {"arguments": [{"name": ["f", "foo"]}]}
        with pytest.raises(ValueError):
            cli(data)

    def test_exclusive_group_ok(self):
        data = {
            "prog": "app",
            "arguments": [
                {
                    "name": "--install",
                    "action": "store_true",
                    "exclusive_group": "ops",
                },
                {
                    "name": "--purge",
                    "action": "store_true",
                    "exclusive_group": "ops",
                },
            ],
        }
        parser = cli(data)
        args = parser.parse_args(["--install"])
        assert args.install is True
        assert args.purge is False

    def test_exclusive_group_fails_when_same_group_called(self):
        data = {
            "prog": "app",
            "arguments": [
                {
                    "name": "--install",
                    "action": "store_true",
                    "exclusive_group": "opas",
                },
                {
                    "name": "--purge",
                    "action": "store_true",
                    "exclusive_group": "opas",
                },
            ],
        }

        parser = cli(data)
        with pytest.raises(SystemExit):
            parser.parse_args("--install --purge".split())

    def test_exclusive_group_and_group_together_fail(self):
        """
        Note:

        Exclusive group requires at least one arg before adding groups
        """
        data = {
            "prog": "app",
            "arguments": [
                {
                    "name": "--install",
                    "action": "store_true",
                    "exclusive_group": "ops",
                    "group": "cmd",
                },
                {
                    "name": "--purge",
                    "action": "store_true",
                    "exclusive_group": "ops",
                    "group": "cmd",
                },
                {"name": "--fear", "exclusive_group": "ops"},
            ],
        }

        with pytest.raises(ValueError):
            cli(data)

    def test_subcommand_required(self):
        data = {
            "prog": "cz",
            "description": (
                "Commitizen is a cli tool to generate conventional commits.\n"
                "For more information about the topic go to "
                "https://conventionalcommits.org/"
            ),
            "formatter_class": argparse.RawDescriptionHelpFormatter,
            "arguments": [
                {"name": "--debug", "action": "store_true", "help": "use debug mode"},
                {
                    "name": ["-n", "--name"],
                    "help": "use the given commitizen (default: cz_conventional_commits)",
                },
            ],
            "subcommands": {
                "title": "commands",
                "required": True,
                "commands": [
                    {
                        "name": ["init"],
                        "help": "init commitizen configuration",
                    }
                ],
            },
        }

        parser = cli(data)
        args = parser.parse_args(["-n", "cz_jira", "init"])
        assert args.debug is False
        assert args.name == "cz_jira"
