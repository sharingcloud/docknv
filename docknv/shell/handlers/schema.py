"""Schema sub commands."""

from docknv import (
    schema_handler,
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("schema", help="manage schemas")
    subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

    subs.add_parser("ls", help="list schemas")


def _handle(args):
    return exec_handler("schema", args, globals())


def _handle_ls(args):
    return schema_handler.schema_list(".")
