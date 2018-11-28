"""User sub commands."""

from docknv.shell.common import exec_handler, load_project
from docknv.utils.ioutils import get_editor_executable

from docknv.wrapper import exec_process


def _init(subparsers):
    cmd = subparsers.add_parser("user", help="manage user config files")
    subs = cmd.add_subparsers(dest="user_cmd", metavar="")

    clean_cmd = subs.add_parser(
        "clean", help="clean user config files for this project")
    clean_cmd.add_argument("config", nargs="?", default=None)

    edit_cmd = subs.add_parser(
        "edit", help="edit user config for this project")
    edit_cmd.add_argument("config", nargs="?", default=None)
    edit_cmd.add_argument(
        "-e", "--editor", nargs="?", default=None,
        help="editor to use (default: auto-detect)")

    subs.add_parser("rm-lock", help="remove the user lockfile")


def _handle(args):
    return exec_handler("user", args, globals())


def _handle_clean(args):
    project = load_project(args.project)
    session = project.session
    session.remove_path(args.config)


def _handle_edit(args):
    editor = get_editor_executable(args.editor)

    project = load_project(args.project)
    session = project.session

    if args.config:
        path = session.get_paths().get_user_configuration_root(args.config)
    else:
        path = session.get_paths().get_user_root()

    return exec_process([editor, path], shell=True, dry_run=args.dry_run)


def _handle_rm_lock(args):
    project = load_project(args.project)
    session = project.session
    session.get_lock().unlock()
