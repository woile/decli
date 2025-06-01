from __future__ import annotations

import logging
from argparse import (
    ArgumentParser,
    _ArgumentGroup,
    _MutuallyExclusiveGroup,
    _SubParsersAction,
)
from collections.abc import Generator, Iterable
from copy import deepcopy
from typing import Any, Callable

config: dict = {}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def init_config() -> dict[str, Any]:
    return {"prefix_chars": "-"}


def ensure_list(name: str | list[str]) -> list[str]:
    if isinstance(name, str):
        return [name]
    return name


def has_many_and_is_optional(names: list[str]) -> list[str]:
    """The arguments can have aliases only when they are optional.

    If this is not the case, then it raises an error.
    """
    prefix_chars = config["prefix_chars"]
    is_optional = all(name.startswith(tuple(prefix_chars)) for name in names)

    if not is_optional and len(names) > 1:
        raise ValueError(
            f"Only optional arguments (starting with {prefix_chars}) can have aliases"
        )
    return names


def is_exclusive_group_or_not(arg: dict) -> None:
    if "exclusive_group" in arg and "group" in arg:
        raise ValueError("choose group or exclusive_group not both.")


def validate_args(args: Iterable[dict]) -> Generator[dict, Any, None]:
    for arg in args:
        arg["name"] = ensure_list(arg["name"])
        has_many_and_is_optional(arg["name"])
        is_exclusive_group_or_not(arg)
        yield arg


def get_or_create_group(
    parser: ArgumentParser,
    groups: dict,
    title: str | None = None,
    description: str | None = None,
) -> _ArgumentGroup | Any:
    group_parser = groups.get(title)
    if group_parser is None:
        group_parser = parser.add_argument_group(title, description)
        groups.update({title: group_parser})
    return group_parser


def get_or_create_exclusive_group(
    parser: ArgumentParser,
    groups: dict,
    title: str | None = None,
    required: bool = False,
) -> _MutuallyExclusiveGroup | Any:
    group_parser = groups.get(title)
    if group_parser is None:
        group_parser = parser.add_mutually_exclusive_group(required=required)
        groups.update({title: group_parser})

    return group_parser


def add_arguments(parser: ArgumentParser, args: list) -> None:
    groups: dict = {}
    exclusive_groups: dict = {}

    for arg in validate_args(args):
        logger.debug("arg: %s", arg)

        name: list = arg.pop("name")
        group_title: str | None = arg.pop("group", None)
        exclusive_group_title: str | None = arg.pop("exclusive_group", None)

        _parser: Any = parser
        if exclusive_group_title:
            logger.debug("Exclusive group: %s", exclusive_group_title)
            _parser = get_or_create_exclusive_group(
                parser, exclusive_groups, exclusive_group_title
            )
        elif group_title:
            logger.debug("Group: %s", group_title)
            _parser = get_or_create_group(parser, groups, group_title)

        _parser.add_argument(*name, **arg)


def add_subcommand(parser: _SubParsersAction[ArgumentParser], command: dict) -> None:
    args: list = command.pop("arguments", None)
    func: Callable | None = command.pop("func", None)

    names: list = ensure_list(command.pop("name"))
    name: str = names.pop(0)

    if names:
        command.update({"aliases": names})

    command_parser = parser.add_parser(name, **command)

    if func:
        command_parser.set_defaults(func=func)
    if args:
        add_arguments(command_parser, args)


def add_subparser(parser: ArgumentParser, subcommand: dict) -> None:
    commands: list = subcommand.pop("commands")

    # This design is for python 3.6 compatibility
    if "required" in subcommand:
        required = subcommand.pop("required")
        subparser = parser.add_subparsers(**subcommand)
        subparser.required = required
    else:
        subparser = parser.add_subparsers(**subcommand)

    for command in commands:
        add_subcommand(subparser, command)


def add_parser(
    data: dict, parser_class: Callable[..., ArgumentParser], parents: list | None
) -> ArgumentParser:
    if parents is None:
        parents = []

    args: list | None = data.pop("arguments", None)
    subcommands: dict | None = data.pop("subcommands", None)

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
    parser_class: Callable[..., ArgumentParser] = ArgumentParser,
    parents: list | None = None,
) -> ArgumentParser:
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
