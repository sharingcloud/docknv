"""User sub commands."""

import subprocess

from docknv import (
    project_handler,
    user_handler
)

from docknv.shell.common import exec_handler
from docknv.utils.ioutils import get_editor_executable


def _init(subparsers):
    cmd = subparsers.add_parser("user", help="manage user config files")
    subs = cmd.add_subparsers(dest="user_cmd", metavar="")

    clean_cmd = subs.add_parser("clean", help="clean user config files for this project")
    clean_cmd.add_argument("config", nargs="?", default=None)

    edit_cmd = subs.add_parser("edit", help="edit user config for this project")
    edit_cmd.add_argument("config", nargs="?", default=None)
    edit_cmd.add_argument("-e", "--editor", nargs="?", default=None, help="editor to use (default: auto-detect)")

    subs.add_parser("rm-lock", help="remove the user lockfile")
    subs.add_parser("migrate", help="migrate old configuration")


def _handle(args):
    return exec_handler("user", args, globals())


def _handle_clean(args):
    return project_handler.project_clean_user_config_path(".", args.config)


def _handle_edit(args):
    editor = get_editor_executable(args.editor)
    path = user_handler.user_get_project_path(".", args.config)
    return subprocess.call([editor, path], shell=True)


def _handle_rm_lock(args):
    return user_handler.user_disable_lock(".")


def _handle_migrate(args):
    config_data = project_handler.project_read(".")
    project_name = config_data.project_name
    return user_handler.user_migrate_config(".", project_name)
