"""Config sub commands."""

from docknv import (
    session_handler,
    project_handler,
    user_handler,
    lifecycle_handler
)

from docknv.logger import Logger
from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("config", help="manage groups of machines at once (config mode)")
    subs = cmd.add_subparsers(dest="config_cmd", metavar="")

    # Status
    subs.add_parser("status", help="show current configuration")

    # Ls
    subs.add_parser("ls", help="list known configurations")

    # Use
    use_cmd = subs.add_parser("use", help="use configuration")
    use_cmd.add_argument("name", help="configuration name")

    # Start
    start_cmd = subs.add_parser("start", help="boot machines from schema")
    start_cmd.add_argument("--foreground", action="store_true", help="start in foreground")

    # Restart
    restart_cmd = subs.add_parser("restart", help="restart machines from schema")
    restart_cmd.add_argument("--foreground", action="store_true", help="restart in foreground")
    restart_cmd.add_argument("-f", "--force", action="store_true", help="force restart")

    # Stop
    subs.add_parser("stop", help="shutdown machines from schema")

    # Ps
    subs.add_parser("ps", help="list schema processes")

    # Unset
    subs.add_parser("unset", help="unset configuration")

    # Build
    build_cmd = subs.add_parser("build", help="build machines from schema")
    build_cmd.add_argument("--no-cache", help="no cache", action="store_true")
    build_cmd.add_argument("--do-not-push", help="do not push to registry", action="store_true")

    # Create
    create_cmd = subs.add_parser("create", help="create a docknv configuration")
    create_cmd.add_argument("config_name", help="configuration name")
    create_cmd.add_argument("schema_name", help="schema name")
    create_cmd.add_argument("environment_name", help="environment name")
    create_cmd.add_argument("-n", "--namespace", help="namespace name", nargs="?", default="default")

    # Update
    update_cmd = subs.add_parser("update", help="update a known configuration")
    update_cmd.add_argument("name", help="configuration name", nargs="?", default=None)
    update_cmd.add_argument("-r", "--restart", help="automatically stop, update, and start")

    # Set schema
    set_schema_cmd = subs.add_parser("set-schema", help="change a configuration schema")
    set_schema_cmd.add_argument("config_name", help="configuration name")
    set_schema_cmd.add_argument("schema_name", help="schema name")

    # Set environment
    set_env_cmd = subs.add_parser("set-env", help="change a configuration environment file")
    set_env_cmd.add_argument("config_name", help="configuration name")
    set_env_cmd.add_argument("environment", help="environment name")

    # Remove
    remove_cmd = subs.add_parser("rm", help="remove a known configuration")
    remove_cmd.add_argument("name", help="configuration name")


def _handle(args):
    return exec_handler("config", args, globals())


def _handle_build(args):
    return lifecycle_handler.lifecycle_schema_build(".", args.no_cache, not args.do_not_push)


def _handle_ls(args):
    return session_handler.session_show_configuration_list(".")


def _handle_start(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_start(".", foreground=args.foreground)


def _handle_stop(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_stop(".")


def _handle_restart(args):
    with user_handler.user_try_lock("."):
        return lifecycle_handler.lifecycle_schema_restart(".", args.foreground, args.force)


def _handle_ps(args):
    return lifecycle_handler.lifecycle_schema_ps(".")


def _handle_rm(args):
    return session_handler.session_remove_configuration(".", args.name)


def _handle_create(args):
    config_name = project_handler.project_generate_compose(".", args.schema_name, args.namespace,
                                                           args.environment_name, args.config_name)
    project_handler.project_use_configuration(".", config_name)


def _handle_use(args):
    return project_handler.project_use_configuration(".", args.name)


def _handle_unset(args):
    return project_handler.project_unset_configuration(".")


def _handle_set_schema(args):
    project_handler.project_update_configuration_schema(".", args.config_name, args.schema_name)
    project_handler.project_generate_compose_from_configuration(".", args.config_name)
    return project_handler.project_use_configuration(".", args.config_name)


def _handle_set_env(args):
    session_handler.session_update_environment(".", args.config_name, args.environment)
    project_handler.project_generate_compose_from_configuration(".", args.config_name)
    return project_handler.project_use_configuration(".", args.config_name)


def _handle_update(args):
    config_name = args.name
    if config_name is None:
        config = project_handler.project_get_active_configuration(".")
        if not config:
            Logger.error(
                "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.",
                crash=True)

    if args.restart:
        with user_handler.user_try_lock("."):
            lifecycle_handler.lifecycle_schema_stop(".")
            project_handler.project_generate_compose_from_configuration(".", config_name)
            lifecycle_handler.lifecycle_schema_start(".")
    else:
        return project_handler.project_generate_compose_from_configuration(".", config_name)


def _handle_status(args):
    config = project_handler.project_get_active_configuration(".")
    if not config:
        Logger.warn(
            "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
    else:
        Logger.info("Current configuration: `{0}`".format(config))
