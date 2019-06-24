"""Env sub commands."""

from docknv.environment import EnvironmentCollection

from docknv.shell.common import exec_handler
from docknv.utils.ioutils import get_editor_executable
from docknv.wrapper import exec_process


def _init(subparsers):
    cmd = subparsers.add_parser("env", help="manage environments")
    subs = cmd.add_subparsers(dest="env_cmd", metavar="")

    subs.add_parser("ls", help="list envs")

    show_cmd = subs.add_parser("show", help="show an environment file")
    show_cmd.add_argument("env_name", help="environment file name")

    edit_cmd = subs.add_parser("edit", help="edit an environment file")
    edit_cmd.add_argument("env_name", help="environment file name")
    edit_cmd.add_argument(
        "-e",
        "--editor",
        nargs="?",
        default=None,
        help="editor to use (default: auto-detect)",
    )


def _handle(args):
    return exec_handler("env", args, globals())


def _handle_ls(args):
    collection = EnvironmentCollection.load_from_project(args.project)
    collection.show_environments()


def _handle_show(args):
    collection = EnvironmentCollection.load_from_project(args.project)
    environment = collection.get_environment(args.env_name)
    environment.show()


def _handle_edit(args):
    collection = EnvironmentCollection.load_from_project(args.project)
    editor = get_editor_executable(args.editor)
    path = collection.get_environment_path(args.env_name)

    return exec_process([editor, path], shell=True, dry_run=args.dry_run)
