"""Bundle sub commands."""

from docknv import (
    user_handler,
    lifecycle_handler
)

from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("bundle", args, globals())


def _handle_start(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_bundle_start(".", args.configs)


def _handle_stop(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_bundle_stop(".", args.configs)


def _handle_restart(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_bundle_restart(".", args.configs, args.force)


def _handle_ps(args):
    return lifecycle_handler.lifecycle_bundle_ps(".", args.configs)


def _handle_build(args):
    return lifecycle_handler.lifecycle_bundle_build(
        ".", args.configs, args.no_cache, not args.do_not_push)
