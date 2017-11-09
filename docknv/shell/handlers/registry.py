"""Registry sub commands."""

from docknv import lifecycle_handler

from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("registry", args, globals())


def _handle_start(args):
    return lifecycle_handler.lifecycle_registry_start(args.path)


def _handle_stop(args):
    return lifecycle_handler.lifecycle_registry_stop()
