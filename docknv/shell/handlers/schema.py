"""Schema sub commands."""

from docknv import (
    lifecycle_handler,
    user_handler,
    schema_handler,
    project_handler
)

from docknv.logger import Logger
from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("schema", help="manage groups of machines at once (schema mode)")
    subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

    subs.add_parser("ls", help="list schemas")
    subs.add_parser("ps", help="list schema processes")
    subs.add_parser("stop", help="shutdown machines from schema")
    subs.add_parser("status", help="get current config name")

    start_cmd = subs.add_parser("start", help="boot machines from schema")
    start_cmd.add_argument("--foreground", action="store_true", help="start in foreground")

    restart_cmd = subs.add_parser("restart", help="restart machines from schema")
    restart_cmd.add_argument("-f", "--force", action="store_true", help="force restart")

    build_cmd = subs.add_parser("build", help="build machines from schema")
    build_cmd.add_argument("--no-cache", help="no cache", action="store_true")
    build_cmd.add_argument("--do-not-push", help="do not push to registry", action="store_true")


def _handle(args):
    return exec_handler("schema", args, globals())


def _handle_build(args):
    return lifecycle_handler.lifecycle_schema_build(".", args.no_cache, not args.do_not_push)


def _handle_start(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_start(".", foreground=args.foreground)


def _handle_status(args):
    config = project_handler.project_get_active_configuration(".")
    if not config:
        Logger.warn("No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
    else:
        Logger.info("Current configuration: `{0}`".format(config))


def _handle_stop(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_stop(".")


def _handle_restart(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_restart(".", args.force)


def _handle_ps(args):
    return lifecycle_handler.lifecycle_schema_ps(".")


def _handle_ls(args):
    return schema_handler.schema_list(".")
