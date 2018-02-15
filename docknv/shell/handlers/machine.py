"""Machine sub commands."""

from docknv import (
    lifecycle_handler,
    command_handler,
    user_handler,
    dockerfile_packer
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("machine", help="manage one machine at a time (machine mode)")
    subs = cmd.add_subparsers(dest="machine_cmd", metavar="")

    start_cmd = subs.add_parser("start", help="start a container")
    start_cmd.add_argument("machine", help="machine name")

    stop_cmd = subs.add_parser("stop", help="stop a container")
    stop_cmd.add_argument("machine", help="machine name")

    restart_cmd = subs.add_parser("restart", help="restart a container")
    restart_cmd.add_argument("machine", help="machine name")
    restart_cmd.add_argument("-f", "--force", action="store_true", help="force restart")

    run_cmd = subs.add_parser("run", help="run a command on a container")
    run_cmd.add_argument("machine", help="machine name")
    run_cmd.add_argument("run_command", help="command to run")
    run_cmd.add_argument("-d", "--daemon", action="store_true", help="run in background")

    exec_cmd = subs.add_parser("exec", help="execute command on a running container")
    exec_cmd.add_argument("machine", help="machine name")
    exec_cmd.add_argument("run_command", help="command to run")
    exec_cmd.add_argument("--no-tty", help="disable tty", action="store_true")

    shell_cmd = subs.add_parser("shell", help="run shell")
    shell_cmd.add_argument("machine", help="machine name")
    shell_cmd.add_argument("shell", help="shell executable", default="/bin/bash", nargs="?")
    shell_cmd.add_argument("-c", "--create", help="create the container if it does not exist", action="store_true")

    logs_cmd = subs.add_parser("logs", help="show container logs")
    logs_cmd.add_argument("machine", help="machine name")
    logs_cmd.add_argument("--tail", type=int, help="tail logs", default=0)
    logs_cmd.add_argument("-f", "--follow", help="follow logs", action="store_true", default=False)

    push_cmd = subs.add_parser("push", help="push a file to a container")
    push_cmd.add_argument("machine", help="machine name")
    push_cmd.add_argument("host_path", help="host path")
    push_cmd.add_argument("container_path", help="container path")

    pull_cmd = subs.add_parser("pull", help="pull a file from a container")
    pull_cmd.add_argument("machine", help="machine name")
    pull_cmd.add_argument("container_path", help="container path")
    pull_cmd.add_argument("host_path", help="host path")

    build_cmd = subs.add_parser("build", help="build a machine")
    build_cmd.add_argument("machine", help="machine name")
    build_cmd.add_argument("--do-not-push", help="do not push to registry", action="store_true")
    build_cmd.add_argument("--no-cache", help="build without cache", action="store_true")

    freeze_cmd = subs.add_parser("freeze", help="freeze a machine")
    freeze_cmd.add_argument("machine", help="machine name")


def _handle(args):
    return exec_handler("machine", args, globals())


def _handle_build(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_build(
        ".", args.machine,
        no_cache=args.no_cache,
        push_to_registry=not args.do_not_push,
        namespace_name=namespace_name)


def _handle_run(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_run(
        ".", args.machine, args.run_command,
        daemon=args.daemon, namespace_name=namespace_name)


def _handle_exec(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_exec(
        ".", args.machine, args.run_command,
        no_tty=args.no_tty, namespace_name=namespace_name)


def _handle_shell(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_shell(
        ".", args.machine, shell_path=args.shell,
        namespace_name=namespace_name, create=args.create)


def _handle_restart(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_restart(
            ".", args.machine, force=args.force,
            namespace_name=namespace_name)


def _handle_stop(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_stop(
            ".", args.machine, namespace_name=namespace_name)


def _handle_start(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_machine_start(
            ".", args.machine, namespace_name=namespace_name)


def _handle_push(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_push(
        ".", args.machine, args.host_path, args.container_path, namespace_name=namespace_name)


def _handle_pull(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_pull(
        ".", args.machine, args.container_path, args.host_path, namespace_name=namespace_name)


def _handle_logs(args):
    context = command_handler.command_get_context(".")
    namespace_name = context.namespace_name
    return lifecycle_handler.lifecycle_machine_logs(
        ".", args.machine,
        tail=args.tail, follow=args.follow, namespace_name=namespace_name)


def _handle_freeze(args):
    return dockerfile_packer.dockerfile_packer(".", args.machine)
