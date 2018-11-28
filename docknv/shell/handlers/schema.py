"""Schema sub commands."""

from docknv.shell.common import exec_handler, load_project


def _init(subparsers):
    cmd = subparsers.add_parser("schema", help="manage schemas")
    subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

    # Ls
    subs.add_parser("ls", help="list schemas")


def _handle(args):
    return exec_handler("schema", args, globals())


def _handle_ls(args):
    project = load_project(args.project)
    schemas = project.schemas
    schemas.show()
