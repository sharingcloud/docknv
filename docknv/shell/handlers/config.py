"""Config sub commands."""

from docknv import (
    session_handler,
    project_handler,
    lifecycle_handler
)

from docknv.logger import Logger
from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("config", args, globals())


def _handle_ls(args):
    return session_handler.session_show_configuration_list(".")


def _handle_rm(args):
    return session_handler.session_remove_configuration(".", args.name)


def _handle_generate(args):
    return project_handler.project_generate_compose(
        ".", args.name, args.namespace, args.environment, args.config_name)


def _handle_use(args):
    return project_handler.project_use_configuration(".", args.name)


def _handle_unset(args):
    return project_handler.project_unset_configuration(".")


def _handle_change_schema(args):
    res = project_handler.project_update_configuration_schema(".", args.config_name, args.schema_name)

    if args.update:
        project_handler.project_generate_compose_from_configuration(".", args.config_name)
        return project_handler.project_use_configuration(".", args.config_name)

    return res


def _handle_change_env(args):
    res = session_handler.session_update_environment(".", args.config_name, args.environment)

    if args.update:
        project_handler.project_generate_compose_from_configuration(".", args.config_name)
        return project_handler.project_use_configuration(".", args.config_name)

    return res


def _handle_update(args):
    if args.name is None:
        config = project_handler.project_get_active_configuration(".")
        if not config:
            Logger.warn(
                "No configuration selected. Use 'docknv config use [configuration]' to select a \
                configuration.")
        else:
            project_handler.project_generate_compose_from_configuration(".", config)
            res = project_handler.project_use_configuration(".", config)
            if args.restart:
                lifecycle_handler.lifecycle_schema_stop(".")
                return lifecycle_handler.lifecycle_schema_start(".")

            return res

    else:
        res = project_handler.project_generate_compose_from_configuration(".", args.name)

        if args.set_current:
            return project_handler.project_use_configuration(".", args.name)
        if args.restart:
            lifecycle_handler.lifecycle_schema_stop(".")
            return lifecycle_handler.lifecycle_schema_start(".")

        return res


def _handle_status(args):
    config = project_handler.project_get_active_configuration(".")
    if not config:
        Logger.warn(
            "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
    else:
        Logger.info("Current configuration: `{0}`".format(config))
