"""User sub commands."""

from docknv import (
    project_handler,
    user_handler
)

from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("user", args, globals())


def _handle_clean_config(args):
    return project_handler.project_clean_user_config_path(".", args.config_name)


def _handle_rm_lock(args):
    return user_handler.user_disable_lock(".")
