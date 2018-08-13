import argparse
from typing import Optional, Callable, Union


def handle_name(name: Union[str, list]) -> list:
    if isinstance(name, str):
        name = [name]
    return name


def add_arguments(parser, args: list):
    for arg in args:
        name = handle_name(arg.pop("name"))
        parser.add_argument(*name, **arg)


def add_subcommand(parser, command: dict):
    args: list = command.pop("arguments", None)
    func: Optional[Callable] = command.pop("func", None)

    names: list = handle_name(command.pop("name"))
    name: str = names.pop(0)

    if names:
        command.update({"aliases": names})

    command_parser = parser.add_parser(name, **command)

    if func:
        command_parser.set_defaults(func=func)
    if args:
        add_arguments(command_parser, args)


def add_subparser(parser, subcommand):
    commands: list = subcommand.pop("commands")
    subparser = parser.add_subparsers(**subcommand)

    for command in commands:
        add_subcommand(subparser, command)


def add_parser(data: dict, parser_class: Callable, parents: Optional[list]):
    if parents is None:
        parents = []

    args: Optional[list] = data.pop("arguments", None)
    subcommands: Optional[dict] = data.pop("subcommands", None)

    parser = parser_class(**data, parents=parents)

    if args:
        add_arguments(parser, args)

    if subcommands:
        add_subparser(parser, subcommands)

    return parser


def cli(
    data: dict,
    parser_class: Callable = argparse.ArgumentParser,
    parents: Optional[list] = None,
):
    """Create a cli application.

    This is the entrypoint.
    """
    parser = add_parser(data, parser_class, parents)
    return parser
