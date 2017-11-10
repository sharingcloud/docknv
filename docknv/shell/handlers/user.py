"""User sub commands."""

from docknv import (
    project_handler,
    user_handler
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("user", help="manage user config files")
    subs = cmd.add_subparsers(dest="user_cmd", metavar="")

    clean_cmd = subs.add_parser("clean", help="clean user config files for this project")
    clean_cmd.add_argument("config", nargs="?", default=None)

    subs.add_parser("rm-lock", help="remove the user lockfile")


def _handle(args):
    return exec_handler("user", args, globals())


def _handle_clean_config(args):
    return project_handler.project_clean_user_config_path(".", args.config)


def _handle_rm_lock(args):
    return user_handler.user_disable_lock(".")
