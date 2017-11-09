"""Volume sub commands."""

from docknv import lifecycle_handler

from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("volume", args, globals())


def _handle_ls(args):
    return lifecycle_handler.lifecycle_volume_list(".")


def _handle_rm(args):
    return lifecycle_handler.lifecycle_volume_remove(".", args.name)
