"""Simple app example"""
from decli import cli

data = {
    "prog": "app",
    "arguments": [
        {"name": "--install", "action": "store_true", "group": "opas"},
        {"name": "--purge", "action": "store_false", "group": "opas"},
    ],
    "subcommands": {
        "title": "main",
        "commands": [
            {
                "name": "commit",
                "arguments": [
                    {
                        "name": "--bocha",
                        "action": "store_true",
                        "group": "opas",
                    }
                ],
            }
        ],
    },
}

parser = cli(data)
args = parser.parse_args()
print(args)
