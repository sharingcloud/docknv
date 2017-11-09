"""Machine sub commands."""

from docknv import (
    lifecycle_handler,
    command_handler,
    user_handler,
    dockerfile_packer
)

from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("machine", args, globals())


def _handle_build(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_build(
        ".", args.machine, args.no_cache, not args.do_not_push, namespace_name)


def _handle_daemon(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_daemon(
        ".", args.machine, args.run_command, namespace_name)


def _handle_run(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_run(
        ".", args.machine, args.run_command, namespace_name)


def _handle_exec(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_exec(
        ".", args.machine, args.run_command, args.no_tty, args.return_code, namespace_name)


def _handle_shell(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_shell(
        ".", args.machine, args.shell, namespace_name, args.create)


def _handle_restart(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_restart(
            ".", args.machine, args.force, namespace_name)


def _handle_stop(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_stop(
            ".", args.machine, namespace_name)


def _handle_start(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_start(
            ".", args.machine, namespace_name)


def _handle_push(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_push(
        ".", args.machine, args.host_path, args.container_path, namespace_name)


def _handle_pull(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_pull(
        ".", args.machine, args.container_path, args.host_path, namespace_name)


def _handle_logs(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_logs(
        ".", args.machine, tail=args.tail, follow=args.follow, namespace_name=namespace_name)


def _handle_freeze(args):
    return dockerfile_packer.dockerfile_packer(".", args.machine)
