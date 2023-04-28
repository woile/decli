======
Decli
======

Minimal declarative cli tool.

.. image:: https://img.shields.io/codecov/c/github/Woile/decli.svg?style=flat-square
    :alt: Codecov
    :target: https://codecov.io/gh/Woile/decli

.. image:: https://img.shields.io/pypi/v/decli.svg?style=flat-square
    :alt: PyPI
    :target: https://pypi.org/project/decli/

.. image:: https://img.shields.io/pypi/pyversions/decli.svg?style=flat-square
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/decli/


.. code-block:: python

    from decli import cli

    data = {
        "prog": "myapp",
        "description": "Process some integers.",
        "arguments": [
            {
                "name": "integers",
                "metavar": "N",
                "type": int,
                "nargs": "+",
                "help": "an integer for the accumulator",
            },
            {
                "name": "--sum",
                "dest": "accumulate",
                "action": "store_const",
                "const": sum,
                "default": max,
                "help": "sum the integers (default: find the max)",
            },
        ],
    }
    parser = cli(data)
    parser.parse_args()


::

    >> parser.print_help()
    usage: myapp [-h] [--sum] N [N ...]

    Process some integers.

    positional arguments:
    N           an integer for the accumulator

    optional arguments:
    -h, --help  show this help message and exit
    --sum       sum the integers (default: find the max)


::

    In [4]: args = parser.parse_args("--sum 3 2 1".split())

    In [5]: args.accumulate(args.integers)
    Out[5]: 6


.. contents::
    :depth: 2


About
=====

Decli is minimal wrapper around **argparse**.

It's useful when writing big applications that have many arguments and subcommands, this way it'll be more clear.

It's a minimal library to rapidly create an interface separated from your app.

It's possible to use any argument from **argparse** and it works really well with it.

Forget about copy pasting the argparse functions, if you are lazy like me, this library should be really handy!

Many cases were tested, but it's possible that not everything was covered, so if you find anything, please report it.


Installation
============

::

    pip install -U decli

or alternatively:

::

    poetry add decli


Usage
======

Main cli
--------

Create the dictionary in which the cli tool is declared.

The same arguments argparse use are accepted, except parents, which is ignored.

- prog - The name of the program (default: sys.argv[0])
- usage - The string describing the program usage (default: generated from arguments added to parser)
- description - Text to display before the argument help (default: none)
- epilog - Text to display after the argument help (default: none)
- formatter_class - A class for customizing the help output
- prefix_chars - The set of characters that prefix optional arguments (default: ‘-‘)
- fromfile_prefix_chars - The set of characters that prefix files from which additional arguments should be read (default: None)
- argument_default - The global default value for arguments (default: None)
- conflict_handler - The strategy for resolving conflicting optionals (usually unnecessary)
- add_help - Add a -h/--help option to the parser (default: True)
- allow_abbrev - Allows long options to be abbreviated if the abbreviation is unambiguous. (default: True)

More info in the `argparse page <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_

Example:

.. code-block:: python

    data = {
        "prog": "myapp",
        "description": "This app does something cool",
        "epilog": "And that's it"
    }


Arguments
---------

It's just a list with dictionaries. To add aliases just use a list instead of a string.

Accepted values:


- name: - Either a name or a list of option strings, e.g. foo or -f, --foo.
- action - The basic type of action to be taken when this argument is encountered at the command line.
- nargs - The number of command-line arguments that should be consumed.
- const - A constant value required by some action and nargs selections.
- default - The value produced if the argument is absent from the command line.
- type - The type to which the command-line argument should be converted.
- choices - A container of the allowable values for the argument.
- required - Whether or not the command-line option may be omitted (optionals only).
- help - A brief description of what the argument does.
- metavar - A name for the argument in usage messages.
- dest - The name of the attribute to be added to the object returned by parse_args().


More info about `arguments <https://docs.python.org/3/library/argparse.html#the-add-argument-method>`_

Example:

.. code-block:: python

    data = {
        "prog": "myapp",
        "description": "This app does something cool",
        "epilog": "And that's it",
        "arguments": [
            {
                "name": "--foo"
            },
            {
                "name": ["-b", "--bar"]
            }
        ]
    }


Subcommands
-----------

Just a dictionary where the most important key is **commands** which is a list of the commands.


Accepted values:


- title - title for the sub-parser group in help output; by default “subcommands” if description is provided, otherwise uses title for positional arguments
- description - description for the sub-parser group in help output, by default None
- commands - list of dicts describing the commands. Same arguments as the **main cli** are supported. And **func** which is really important.
- prog - usage information that will be displayed with sub-command help, by default the name of the program and any positional arguments before the subparser argument
- action - the basic type of action to be taken when this argument is encountered at the command line
- dest - name of the attribute under which sub-command name will be stored; by default None and no value is stored
- required - Whether or not a subcommand must be provided, by default False.
- help - help for sub-parser group in help output, by default None
- metavar - string presenting available sub-commands in help; by default it is None and presents sub-commands in form {cmd1, cmd2, ..}


More info about `subcommands <https://docs.python.org/3/library/argparse.html#sub-commands>`_

Func
~~~~

Usually in a sub-command it's useful to specify to which function are they pointing to. That's why each command should have this parameter.


When you are building an app which does multiple things, each function should be mapped to a command this way, using the **func** argument.

Example:

.. code-block:: python

    from decli import cli

    data = {
        "prog": "myapp",
        "description": "This app does something cool",
        "epilog": "And that's it",
        "subcommands": {
            "title": "main",
            "commands": [
                {
                    "name": "sum",
                    "help": "new project",
                    "func": sum,
                    "arguments": [
                        {
                            "name": "integers",
                            "metavar": "N",
                            "type": int,
                            "nargs": "+",
                            "help": "an integer for the accumulator",
                        },
                        {"name": "--name", "nargs": "?"},
                    ],
                }
            ]
        }
    }

    parser = cli(data)
    args = parser.parse_args(["sum 1 2 3".split()])
    args.func(args.integers)  # Runs the sum of the integers

Groups
------

Used to group the arguments based on conceptual groups. This only affects the shown **help**, nothing else.

Example:

.. code-block:: python

    data = {
        "prog": "app",
        "arguments": [
            {"name": "foo", "help": "foo help", "group": "group1"},
            {"name": "choo", "help": "choo help", "group": "group1"},
            {"name": "--bar", "help": "bar help", "group": "group2"},
        ]
    }
    parser = cli(data)
    parser.print_help()

::

    usage: app [-h] [--bar BAR] foo choo

    optional arguments:
    -h, --help  show this help message and exit

    group1:
    foo         foo help
    choo        choo help

    group2:
    --bar BAR   bar help


Exclusive Groups
----------------

A mutually exclusive group allows to execute only one **optional** argument (starting with :code:`--`) from the group.
If the condition is not met, it will show an error.

Example:

.. code-block:: python

    data = {
        "prog": "app",
        "arguments": [
            {"name": "--foo", "help": "foo help", "exclusive_group": "group1"},
            {"name": "--choo", "help": "choo help", "exclusive_group": "group1"},
            {"name": "--bar", "help": "bar help", "exclusive_group": "group1"},
        ]
    }
    parser = cli(data)
    parser.print_help()

::

    usage: app [-h] [--foo FOO | --choo CHOO | --bar BAR]

    optional arguments:
    -h, --help   show this help message and exit
    --foo FOO    foo help
    --choo CHOO  choo help
    --bar BAR    bar help

::

    In [1]: parser.parse_args("--foo 1 --choo 2".split())

    usage: app [-h] [--foo FOO | --choo CHOO | --bar BAR]
    app: error: argument --choo: not allowed with argument --foo


Groups and Exclusive groups
---------------------------

It is not possible to have groups inside exclusive groups with **decli**.

**Decli** will prevent from doing this by raising a :code:`ValueError`.

It is possible to accomplish it with argparse, but the help message generated will be broken and the
exclusion won't work.

Parents
-------

Sometimes, several cli share a common set of arguments.

Rather than repeating the definitions of these arguments,
one or more parent clis with all the shared arguments can be passed
to :code:`parents=argument` to cli.

More info about `parents <https://docs.python.org/3/library/argparse.html#parents>`_

Example:

.. code-block:: python

    parent_foo_data = {
        "add_help": False,
        "arguments": [{"name": "--foo-parent", "type": int}],
    }
    parent_bar_data = {
        "add_help": False,
        "arguments": [{"name": "--bar-parent", "type": int}],
    }
    parent_foo_cli = cli(parent_foo_data)
    parent_bar_cli = cli(parent_bar_data)

    parents = [parent_foo_cli, parent_bar_cli]

    data = {
        "prog": "app",
        "arguments": [
            {"name": "foo"}
        ]
    }
    parser = cli(data, parents=parents)
    parser.print_help()

::

    usage: app [-h] [--foo-parent FOO_PARENT] [--bar-parent BAR_PARENT] foo

    positional arguments:
    foo

    optional arguments:
    -h, --help            show this help message and exit
    --foo-parent FOO_PARENT
    --bar-parent BAR_PARENT


Recipes
=======

Subcommands
-----------------

.. code-block:: python

    from decli import cli

    data = {
        "prog": "myapp",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": "The software has subcommands which you can use",
        "subcommands": {
            "title": "main",
            "description": "main commands",
            "commands": [
                {
                    "name": "all",
                    "help": "check every values is true",
                    "func": all
                },
                {
                    "name": ["s", "sum"],
                    "help": "new project",
                    "func": sum,
                    "arguments": [
                        {
                            "name": "integers",
                            "metavar": "N",
                            "type": int,
                            "nargs": "+",
                            "help": "an integer for the accumulator",
                        },
                        {"name": "--name", "nargs": "?"},
                    ],
                }
            ],
        },
    }
    parser = cli(data)
    args = parser.parse_args(["sum 1 2 3".split()])
    args.func(args.integers)  # Runs the sum of the integers


Minimal
-------

This app does nothing, but it's the min we can have:

.. code-block:: python

    from decli import cli

    parser = cli({})
    parser.print_help()

::

    usage: ipython [-h]

    optional arguments:
    -h, --help  show this help message and exit


Positional arguments
--------------------

.. code-block:: python

    from decli import cli

    data = {
        "arguments": [
            {
                "name": "echo"
            }
        ]
    }
    parser = cli(data)
    args = parser.parse_args(["foo"])

::

    In [11]: print(args.echo)
    foo


Positional arguments with type
------------------------------

When a type is specified, the argument will be treated as that type, otherwise it'll fail.

.. code-block:: python

    from decli import cli

    data = {
        "arguments": [
            {
                "name": "square",
                "type": int
            }
        ]
    }
    parser = cli(data)
    args = parser.parse_args(["1"])

::

    In [11]: print(args.echo)
    1

Optional arguments
------------------

.. code-block:: python

    from decli import cli

    data = {
        "arguments": [
            {
                "name": "--verbose",
                "help": "increase output verbosity"
            }
        ]
    }
    parser = cli(data)
    args = parser.parse_args(["--verbosity 1"])

::

    In [11]: print(args.verbosity)
    1

    In [15]: args = parser.parse_args([])

    In [16]: args
    Out[16]: Namespace(verbose=None)


Flags
-----

Flags are a boolean only (True/False) subset of options.

.. code-block:: python

    from decli import cli

    data = {
        "arguments": [
            {
                "name": "--verbose",
                "action": "store_true",  # defaults to False
            },
            {
                "name": "--noisy",
                "action": "store_false",  # defaults to True
            }
        ]
    }
    parser = cli(data)




Short options
-------------

Used to add short versions of the options.

.. code-block:: python

    data = {
        "arguments": [
            {
                "name": ["-v", "--verbose"],
                "help": "increase output verbosity"
            }
        ]
    }


Grouping
--------

This is only possible using **arguments**.

Only affect the way the help gets displayed. You might be looking for subcommands.


.. code-block:: python

    data = {
        "prog": "mycli",
        "arguments": [
            {
                "name": "--save",
                "group": "main",
                "help": "This save belongs to the main group",
            },
            {
                "name": "--remove",
                "group": "main",
                "help": "This remove belongs to the main group",
            },
        ],
    }
    parser = cli(data)
    parser.print_help()

::

    usage: mycli [-h] [--save SAVE] [--remove REMOVE]

    optional arguments:
    -h, --help       show this help message and exit

    main:
    --save SAVE      This save belongs to the main group
    --remove REMOVE  This remove belongs to the main group


Exclusive group
---------------

This is only possible using **optional arguments**.


.. code-block:: python

    data = {
        "prog": "mycli",
        "arguments": [
            {
                "name": "--save",
                "exclusive_group": "main",
                "help": "This save belongs to the main group",
            },
            {
                "name": "--remove",
                "exclusive_group": "main",
                "help": "This remove belongs to the main group",
            },
        ],
    }
    parser = cli(data)
    parser.print_help()

::

    usage: mycli [-h] [--save SAVE | --remove REMOVE]

    optional arguments:
    -h, --help       show this help message and exit
    --save SAVE      This save belongs to the main group
    --remove REMOVE  This remove belongs to the main group


Combining Positional and Optional arguments
-------------------------------------------

.. code-block:: python

    data = {
        "arguments": [
            {
                "name": "square",
                "type": int,
                "help": "display a square of a given number"
            },
            {
                "name": ["-v", "--verbose"],
                "action": "store_true",
                "help": "increase output verbosity"
            }
        ]
    }
    parser = cli(data)

    args = parser.parse_args()
    answer = args.square**2
    if args.verbose:
        print(f"the square of {args.square} equals {answer}")
    else:
        print(answer)


More Examples
-------------

Many examples from `argparse documentation <https://docs.python.org/3/library/argparse.html>`_
are covered in test/examples.py


Contributing
============

1. Clone the repo
2. Install dependencies

::

    poetry install

3. Run tests

::

    ./scripts/tests


Contributing
============

**PRs are welcome!**
