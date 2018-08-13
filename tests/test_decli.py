"""Most of argparse examples rebuilt with climp."""
import pytest
from . import examples
from decli import cli


def test_main_example_ok():
    parser = examples.main_example()
    args = parser.parse_args("1 2 3 4".split())

    assert args.accumulate(args.integers) == 4


def test_main_example_sums_ok():
    parser = examples.main_example()
    args = parser.parse_args("1 2 3 4 --sum".split())
    assert args.accumulate(args.integers) == 10


def test_main_example_fails():
    parser = examples.main_example()
    with pytest.raises(SystemExit):
        args = parser.parse_args("a b c".split())
        args.accumulate(args.integers)


def test_complete_example():
    parser = examples.complete_example()
    args = parser.parse_args("sum 1 2 3".split())
    assert args.func(args.integers) == 6


def test_compose_clis_using_parents():
    data = {"prog": "daddy", "arguments": [{"name": "something"}]}
    parents = examples.compose_clis_using_parents()
    parser = cli(data, parents=parents)

    args = parser.parse_args(["--foo-parent", "2", "XXX"])
    assert args.something == "XXX"
    assert args.foo_parent == 2


def test_compose_clis_using_parents_and_arguments():
    data = {"prog": "daddy", "arguments": [{"name": "--something"}]}
    parents = examples.compose_clis_using_parents()
    parser = cli(data, parents=parents)

    args = parser.parse_args(["--something", "XXX"])
    assert args.something == "XXX"


def test_prefix_chars():
    parser = examples.prefix_chars()
    args = parser.parse_args("+f X ++bar Y".split())

    assert args.f == "X"
    assert args.bar == "Y"


def test_name_or_flags():
    parser = examples.name_or_flags()

    args = parser.parse_args(["HELLO"])
    assert args.bar == "HELLO"

    args = parser.parse_args(["BAR", "--foo", "FOO"])
    assert args.bar == "BAR"
    assert args.foo == "FOO"


def test_name_or_flags_fail():
    parser = examples.name_or_flags()
    with pytest.raises(SystemExit):
        parser.parse_args(["--foo", "FOO"])


def test_cli_no_args():
    data = {"prog": "daddy", "description": "helloo"}
    parser = cli(data)

    args = parser.parse_args([])

    assert args.__dict__ == {}
