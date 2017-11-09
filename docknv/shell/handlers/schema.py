"""Schema sub commands."""

from docknv import (
    lifecycle_handler,
    user_handler,
    schema_handler,
    project_handler
)

from docknv.logger import Logger
from docknv.shell.common import exec_handler


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
