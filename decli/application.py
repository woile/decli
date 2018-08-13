import argparse
from typing import Optional, Callable, Union


config = {"prefix_chars": "-", "groups": {}}


def validate_arg_names(names: list) -> list:
    """The arguments can have aliases only when they are optional.

    If this is not the case, then it raises an error.
    """
    prefix_chars = config["prefix_chars"]
    is_optional = all(name.startswith(tuple(prefix_chars)) for name in names)

    if not is_optional and len(names) > 1:
        msg = (
            f"Only optional arguments (starting with {prefix_chars}) "
            "can have aliases"
        )
        raise ValueError(msg)
    return names


def ensure_list(name: Union[str, list]) -> list:
    if isinstance(name, str):
        name = [name]
    return name


def add_arguments(parser, args: list):
    for arg in args:
        name: list = validate_arg_names(ensure_list(arg.pop("name")))
        group: str = arg.pop("group", None)
        if group:
            groups = config["groups"]
            group_parser = groups.setdefault(
                group, parser.add_argument_group(group)
            )
            group_parser.add_argument(*name, **arg)
        else:
            parser.add_argument(*name, **arg)


def add_subcommand(parser, command: dict):
    args: list = command.pop("arguments", None)
    func: Optional[Callable] = command.pop("func", None)

    names: list = ensure_list(command.pop("name"))
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
    if data.get("prefix_chars"):
        config.update({"prefix_chars": data.get("prefix_chars")})

    parser = add_parser(data, parser_class, parents)
    return parser
