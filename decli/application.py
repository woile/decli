import argparse
import logging
from typing import Optional, Callable, Union
from copy import deepcopy


config = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def init_config():
    return {"prefix_chars": "-"}


def ensure_list(name: Union[str, list]) -> list:
    if isinstance(name, str):
        name = [name]
    return name


def has_many_and_is_optional(names: list) -> list:
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


def is_exclusive_group_or_not(arg: dict):
    if "exclusive_group" in arg and "group" in arg:
        msg = "choose group or exclusive_group not both."
        raise ValueError(msg)


def validate_args(args: list):
    for arg in args:
        arg["name"] = ensure_list(arg["name"])
        has_many_and_is_optional(arg["name"])
        is_exclusive_group_or_not(arg)
        yield arg


def get_or_create_group(
    parser,
    groups: dict,
    title: Optional[str] = None,
    description: Optional[str] = None,
):
    group_parser = groups.get(title)
    if group_parser is None:
        group_parser = parser.add_argument_group(title, description)
        groups.update({title: group_parser})
    return group_parser


def get_or_create_exclusive_group(
    parser, groups: dict, title: str = None, required=False
):
    group_parser = groups.get(title)
    if group_parser is None:
        group_parser = parser.add_mutually_exclusive_group(required=required)
        groups.update({title: group_parser})

    return group_parser


def add_arguments(parser, args: list):
    groups = {}
    exclusive_groups = {}

    for arg in validate_args(args):
        logger.debug("arg: %s", arg)

        name: list = arg.pop("name")
        group_title: Optional[str] = arg.pop("group", None)
        exclusive_group_title: Optional[str] = arg.pop("exclusive_group", None)

        _parser = parser
        if exclusive_group_title:
            logger.debug("Exclusive group: %s", exclusive_group_title)
            _parser = get_or_create_exclusive_group(
                parser, exclusive_groups, exclusive_group_title
            )
        elif group_title:
            logger.debug("Group: %s", group_title)
            _parser = get_or_create_group(parser, groups, group_title)

        _parser.add_argument(*name, **arg)


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


def add_subparser(parser, subcommand: dict):
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
        logger.debug("Adding arguments...")
        add_arguments(parser, args)

    if subcommands:
        logger.debug("Adding subcommands...")
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
    global config
    config = init_config()
    data = deepcopy(data)

    if data.get("prefix_chars"):
        config.update({"prefix_chars": data.get("prefix_chars")})

    parser = add_parser(data, parser_class, parents)
    return parser
