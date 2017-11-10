"""Registry sub commands."""

from docknv import lifecycle_handler

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("registry", help="start and stop registry")
    subs = cmd.add_subparsers(dest="registry_cmd", metavar="")

    start_cmd = subs.add_parser("start", help="start registry")
    start_cmd.add_argument("-p", "--path", help="storage path", nargs="?", default=None)
    subs.add_parser("stop", help="stop registry")


def _handle(args):
    return exec_handler("registry", args, globals())


def _handle_start(args):
    return lifecycle_handler.lifecycle_registry_start(args.path)


def _handle_stop(args):
    return lifecycle_handler.lifecycle_registry_stop()
