"""Service sub commands."""

from docknv.shell.common import exec_handler, load_project


def _init(subparsers):
    cmd = subparsers.add_parser(
        "service", help="manage one service at a time (service mode)"
    )
    cmd.add_argument(
        "-c", "--config", help="configuration name (swap)", default=None
    )
    subs = cmd.add_subparsers(dest="service_cmd", metavar="")

    # Start
    start_cmd = subs.add_parser("start", help="start a container")
    start_cmd.add_argument("service", help="service name")

    # Stop
    stop_cmd = subs.add_parser("stop", help="stop a container")
    stop_cmd.add_argument("service", help="service name")

    # Restart
    restart_cmd = subs.add_parser("restart", help="restart a container")
    restart_cmd.add_argument("service", help="service name")
    restart_cmd.add_argument(
        "-f", "--force", action="store_true", help="force restart"
    )

    # Run
    run_cmd = subs.add_parser("run", help="run a command on a container")
    run_cmd.add_argument("service", help="service name")
    run_cmd.add_argument("run_command", help="command to run")
    run_cmd.add_argument(
        "-d", "--daemon", action="store_true", help="run in background"
    )

    # Exec
    exec_cmd = subs.add_parser(
        "exec", help="execute command on a running container"
    )
    exec_cmd.add_argument("service", help="service name")
    exec_cmd.add_argument("run_command", help="command to run")

    # Shell
    shell_cmd = subs.add_parser("shell", help="run shell")
    shell_cmd.add_argument("service", help="service name")
    shell_cmd.add_argument(
        "shell", help="shell executable", default="/bin/bash", nargs="?"
    )

    # Logs
    logs_cmd = subs.add_parser("logs", help="show container logs")
    logs_cmd.add_argument("service", help="service name")
    logs_cmd.add_argument(
        "-t", "--tail", type=int, help="tail logs", default=0
    )
    logs_cmd.add_argument(
        "-f",
        "--follow",
        help="follow logs",
        action="store_true",
        default=False,
    )

    # Push
    push_cmd = subs.add_parser("push", help="push a file to a container")
    push_cmd.add_argument("service", help="service name")
    push_cmd.add_argument("host_path", help="host path")
    push_cmd.add_argument("container_path", help="container path")

    # Pull
    pull_cmd = subs.add_parser("pull", help="pull a file from a container")
    pull_cmd.add_argument("service", help="service name")
    pull_cmd.add_argument("container_path", help="container path")
    pull_cmd.add_argument("host_path", help="host path")

    # Build
    build_cmd = subs.add_parser("build", help="build a service")
    build_cmd.add_argument("service", help="service name")
    build_cmd.add_argument("-b", "--build-args", nargs="+", help="build args")
    build_cmd.add_argument(
        "--no-cache", help="build without cache", action="store_true"
    )


def _handle(args):
    return exec_handler("service", args, globals())


def _handle_build(args):
    project = load_project(args.project)
    project.lifecycle.service.build(
        args.service,
        config_name=args.config,
        build_args=args.build_args,
        no_cache=args.no_cache,
        dry_run=args.dry_run,
    )


def _handle_run(args):
    project = load_project(args.project)
    project.lifecycle.service.run(
        args.service,
        args.run_command,
        daemon=args.daemon,
        config_name=args.config,
        dry_run=args.dry_run,
    )


def _handle_exec(args):
    project = load_project(args.project)
    project.lifecycle.service.execute(
        args.service,
        cmds=[args.run_command],
        config_name=args.config,
        dry_run=args.dry_run,
    )


def _handle_shell(args):
    project = load_project(args.project)
    project.lifecycle.service.shell(
        args.service,
        config_name=args.config,
        shell=args.shell,
        dry_run=args.dry_run,
    )


def _handle_restart(args):
    project = load_project(args.project)
    project.lifecycle.service.restart(
        args.service,
        config_name=args.config,
        force=args.force,
        dry_run=args.dry_run,
    )


def _handle_stop(args):
    project = load_project(args.project)
    project.lifecycle.service.stop(
        args.service, config_name=args.config, dry_run=args.dry_run
    )


def _handle_start(args):
    project = load_project(args.project)
    project.lifecycle.service.start(
        args.service, config_name=args.config, dry_run=args.dry_run
    )


def _handle_push(args):
    project = load_project(args.project)
    project.lifecycle.service.push(
        args.service,
        args.host_path,
        args.container_path,
        config_name=args.config,
        dry_run=args.dry_run,
    )


def _handle_pull(args):
    project = load_project(args.project)
    project.lifecycle.service.pull(
        args.service,
        args.container_path,
        args.host_path,
        config_name=args.config,
        dry_run=args.dry_run,
    )


def _handle_logs(args):
    project = load_project(args.project)
    project.lifecycle.service.logs(
        args.service,
        config_name=args.config,
        tail=args.tail,
        follow=args.follow,
        dry_run=args.dry_run,
    )
