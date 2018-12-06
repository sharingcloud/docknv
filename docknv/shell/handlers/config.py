"""Config sub commands."""

from docknv.logger import Logger
from docknv.shell.common import exec_handler, load_project


def _init(subparsers):
    cmd = subparsers.add_parser(
        "config", help="manage groups of machines at once (config mode)")
    subs = cmd.add_subparsers(dest="config_cmd", metavar="")

    # Status
    subs.add_parser("status", help="show current configuration")

    # Ls
    subs.add_parser("ls", help="list known configurations")

    # Set
    set_cmd = subs.add_parser("set", help="set configuration")
    set_cmd.add_argument("name", help="configuration name")

    # Start
    start_cmd = subs.add_parser("start", help="boot machines from schema")
    start_cmd.add_argument("configs", nargs="*", help="configurations")

    # Restart
    restart_cmd = subs.add_parser(
        "restart", help="restart machines from schema")
    restart_cmd.add_argument("configs", nargs="*", help="configurations")
    restart_cmd.add_argument(
        "-f", "--force", action="store_true", help="force restart")

    # Stop
    stop_cmd = subs.add_parser("stop", help="shutdown machines from schema")
    stop_cmd.add_argument("configs", nargs="*", help="configurations")

    # Ps
    ps_cmd = subs.add_parser("ps", help="list schema processes")
    ps_cmd.add_argument("configs", nargs="*", help="configurations")

    # Unset
    subs.add_parser("unset", help="unset configuration")

    # Build
    build_cmd = subs.add_parser("build", help="build machines from schema")
    build_cmd.add_argument("config", nargs="?", help="configuration")
    build_cmd.add_argument(
        "-b", "--build-args", nargs="+", help="build arguments")
    build_cmd.add_argument("--no-cache", help="no cache", action="store_true")

    # Create
    create_cmd = subs.add_parser(
        "create", help="create a docknv configuration")
    create_cmd.add_argument("name", help="configuration name")
    create_cmd.add_argument(
        "-e", "--environment", required=True, help="environment name")
    create_cmd.add_argument(
        "-s", "--schemas", nargs="*", help="schemas to use")
    create_cmd.add_argument(
        "-S", "--services", nargs="*", help="services to use")
    create_cmd.add_argument(
        "-V", "--volumes", nargs="*", help="volumes to use")
    create_cmd.add_argument(
        "-N", "--networks", nargs="*", help="networks to use")
    create_cmd.add_argument(
        "-n", "--namespace", help="namespace name", nargs="?",
        default=None)

    # Update
    update_cmd = subs.add_parser("update", help="update a known configuration")
    update_cmd.add_argument(
        "name", help="configuration name", nargs="?", default=None)
    update_cmd.add_argument(
        "-e", "--environment", help="environment name")
    update_cmd.add_argument(
        "-s", "--schemas", nargs="*", help="schemas to use")
    update_cmd.add_argument(
        "-S", "--services", nargs="*", help="services to use")
    update_cmd.add_argument(
        "-V", "--volumes", nargs="*", help="volumes to use")
    update_cmd.add_argument(
        "-N", "--networks", nargs="*", help="networks to use")
    update_cmd.add_argument(
        "-n", "--namespace", help="namespace name", nargs="?",
        default=None)
    update_cmd.add_argument(
        "--no-namespace", help="remove namespace", action="store_true")
    update_cmd.add_argument(
        "-r", "--restart", action="store_true",
        help="restart after update")

    # Remove
    remove_cmd = subs.add_parser("rm", help="remove known configurations")
    remove_cmd.add_argument("configs", nargs="+", help="configurations")
    remove_cmd.add_argument(
        "-f", "--force", help="force remove", action="store_true")


def _handle(args):
    return exec_handler("config", args, globals())


def _handle_build(args):
    project = load_project(args.project)
    project.lifecycle.config.build(
        args.config, args.build_args, args.no_cache, dry_run=args.dry_run)


def _handle_ls(args):
    project = load_project(args.project)
    project.database.show_configuration_list()


def _handle_start(args):
    project = load_project(args.project)
    with project.session.get_lock().try_lock():
        project.lifecycle.config.start(args.configs, dry_run=args.dry_run)


def _handle_stop(args):
    project = load_project(args.project)
    with project.session.get_lock().try_lock():
        project.lifecycle.config.stop(args.configs, dry_run=args.dry_run)


def _handle_restart(args):
    project = load_project(args.project)
    with project.session.get_lock().try_lock():
        project.lifecycle.config.restart(
            args.configs, force=args.force, dry_run=args.dry_run)


def _handle_ps(args):
    project = load_project(args.project)
    project.lifecycle.config.ps(
        args.configs, dry_run=args.dry_run)


def _handle_rm(args):
    project = load_project(args.project)

    # Check configs
    for config in args.configs:
        project.database.get_configuration(config)

    # Remove configs
    for config in args.configs:
        project.database.remove_configuration(config, force=args.force)


def _handle_create(args):
    project = load_project(args.project)
    project.lifecycle.config.create(
        args.name, args.environment, args.schemas, args.services, args.volumes,
        args.networks, args.namespace)


def _handle_set(args):
    project = load_project(args.project)
    project.set_current_configuration(args.name)


def _handle_unset(args):
    project = load_project(args.project)
    project.unset_current_configuration()


def _handle_update(args):
    project = load_project(args.project)
    project.lifecycle.config.update(
        args.name, args.environment, args.schemas, args.services, args.volumes,
        args.networks, args.namespace, restart=args.restart)


def _handle_status(args):
    project = load_project(args.project)
    config_name = project.get_current_configuration()

    if config_name:
        config = project.database.get_configuration(config_name)

        Logger.info("current configuration: ")
        config.show()
    else:
        Logger.warn(
            "no configuration selected. "
            "use 'docknv config set [configuration]' "
            "to select a configuration.")
