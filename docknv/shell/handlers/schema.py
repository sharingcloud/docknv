"""Schema sub commands."""

from docknv import (
    schema_handler,
    project_handler
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("schema", help="manage schemas")
    subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

    subs.add_parser("ls", help="list schemas")


def _handle(args):
    return exec_handler("schema", args, globals())


def _handle_ls(args):
    project_data = project_handler.project_read(args.context)
    return schema_handler.schema_list(project_data)
