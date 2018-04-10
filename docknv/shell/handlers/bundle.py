"""Bundle sub commands."""

from docknv import (
    user_handler,
    lifecycle_handler
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("bundle", help="manage groups of configs at once (bundle mode)")
    subs = cmd.add_subparsers(dest="bundle_cmd", metavar="")

    start_cmd = subs.add_parser("start", help="boot machines from schemas")
    start_cmd.add_argument("configs", nargs="+")

    restart_cmd = subs.add_parser("restart", help="restart machines from schemas")
    restart_cmd.add_argument("-f", "--force", action="store_true", help="force restart")
    restart_cmd.add_argument("configs", nargs="+")

    stop_cmd = subs.add_parser("stop", help="shutdown machines from schemas")
    stop_cmd.add_argument("configs", nargs="+")

    ps_cmd = subs.add_parser("ps", help="list schemas processes")
    ps_cmd.add_argument("configs", nargs="+")

    build_cmd = subs.add_parser("build", help="build machines from schemas")
    build_cmd.add_argument("configs", nargs="+")
    build_cmd.add_argument("--no-cache", help="no cache", action="store_true")
    build_cmd.add_argument("--push", help="push to registry", action="store_true")


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
        return lifecycle_handler.lifecycle_bundle_restart(
            ".", args.configs, force=args.force)


def _handle_ps(args):
    return lifecycle_handler.lifecycle_bundle_ps(".", args.configs)


def _handle_build(args):
    return lifecycle_handler.lifecycle_bundle_build(
        ".", args.configs,
        no_cache=args.no_cache, push_to_registry=args.push)
