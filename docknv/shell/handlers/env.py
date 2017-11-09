"""Env sub commands."""

from docknv import environment_handler
from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("env", args, globals())


def _handle_ls(args):
    return environment_handler.env_list(".")


def _handle_show(args):
    return environment_handler.env_show(".", args.env_name)
