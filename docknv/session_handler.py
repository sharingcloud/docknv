"""Session config handler."""

import os

from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump
from docknv.utils.prompt import prompt_yes_no
from docknv.utils.ioutils import io_open
from docknv.utils.paths import get_lower_basename
from docknv.utils.diff_system import read_last_modification_time, save_last_modification_time

from docknv.logger import Logger, Fore

from docknv.environment_handler import env_yaml_check_file

from docknv.user_handler import user_get_id, user_clean_config_path, user_get_file_from_project

from docknv.schema_handler import schema_check


SESSION_FILE_NAME = ".docknv.yml"


def session_read_configuration(project_path):
    """
    Read a session config file.

    Contains available namespaces.

    :param project_path:     Project path (str)
    :rtype: Session configuration (dict)
    """
    project_file_path = os.path.join(project_path, SESSION_FILE_NAME)

    if os.path.isfile(project_file_path):
        with io_open(project_file_path, encoding="utf-8", mode="r") as handle:
            config_data = yaml_ordered_load(handle.read())
        return config_data

    return {"values": {}, "project_path": None}


def session_write_configuration(project_path, content):
    """
    Write a temporary config file.

    :param project_path:     Project path (str)
    :param content:          Content (dict)
    """
    project_file_path = os.path.join(project_path, SESSION_FILE_NAME)

    with io_open(project_file_path, encoding="utf-8", mode="w") as handle:
        handle.write(yaml_ordered_dump(content))


def session_check_configuration(config_data, config_name):
    """
    Check configuration.

    :param config_data:      Config data (dict)
    :param config_name:      Config name (str)
    :rtype: bool
    """
    if config_name not in config_data["values"]:
        Logger.error("Missing configuration `{0}`.".format(config_name))

    return True


def session_check_bundle_configurations(project_path, config_names):
    """
    Check multiple configurations.

    :param project_path:     Project path (str)
    :param config_names:     Config names (iterable)
    :rtype: bool
    """
    config_data = session_read_configuration(project_path)

    for config_name in config_names:
        session_check_configuration(config_data, config_name)

    return True


def session_update_environment(project_path, config_name, environment_name):
    """
    Change a configuration environment.

    :param project_path:         Project path (str)
    :param config_name:          Config name (str)
    :param environment_name:     Environment name (str)
    """
    if env_yaml_check_file(project_path, environment_name):
        docknv_config = session_read_configuration(project_path)

        if session_check_configuration(docknv_config, config_name):
            docknv_config["values"][config_name]["environment"] = environment_name
            session_write_configuration(project_path, docknv_config)
            Logger.info("Configuration `{0}` updated with environment `{1}`".format(config_name, environment_name))
    else:
        Logger.error("Environment `{0}` does not exist.".format(environment_name))


def session_remove_configuration(project_path, config_name):
    """
    Remove a configuration.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    """
    from docknv.project_handler import (
        project_get_composefile, project_get_active_configuration,
        project_unset_configuration
    )

    config = session_read_configuration(project_path)
    project_name = get_lower_basename(project_path)
    if config_name not in config["values"]:
        Logger.error("Missing configuration `{0}`.".format(config_name))

    uid = user_get_id()

    config_to_remove = config["values"][config_name]
    if config_to_remove["user"] != uid:
        Logger.error("You can not remove configuration `{0}`. Access denied.".format(config_name))

    choice = prompt_yes_no("/!\\ Are you sure you want to remove configuration `{0}` ?".format(config_name))

    if choice:
        # Remove configuration and docker-compose file.
        path = project_get_composefile(project_path, config_name)
        if os.path.exists(path):
            os.remove(path)

        del config["values"][config_name]

        # Check if config is active
        active_configuration = project_get_active_configuration(project_path)
        if active_configuration == config_name:
            project_unset_configuration(project_path)

        session_write_configuration(project_path, config)
        user_clean_config_path(project_name, config_name)

        Logger.info("Configuration `{0}` removed.".format(config_name))


def session_update_schema(project_path, project_config, config_name, schema_name):
    """
    Change a configuration schema.

    :param project_path:     Project path (str)
    :param project_config:   Project config (dict)
    :param config_name:      Config name (str)
    :param schema_name:      Schema name (str)
    """
    if schema_check(project_config, schema_name):
        docknv_config = session_read_configuration(project_path)

        if session_check_configuration(docknv_config, config_name):
            docknv_config["values"][config_name]["schema"] = schema_name
            session_write_configuration(project_path, docknv_config)
            Logger.info("Configuration `{0}` updated with schema `{1}`".format(config_name, schema_name))


def session_get_configuration(project_path, name):
    """
    Get a known configuration by name.

    :param project_path:     Project path (str)
    :param name:             Config name (str)
    :rtype: Configuration data (dict)
    """
    if name is None:
        Logger.error("No configuration set. Please set an active configuration.")

    config = session_read_configuration(project_path)
    if name in config["values"]:
        return config["values"][name]
    else:
        Logger.error("Missing configuration `{0}` in known configuration.".format(name))


def session_list_configurations(project_path):
    """
    Get configuration list.

    :param project_path:     Project path (str):
    :rtype: Configuration data dict (dict)
    """
    config = session_read_configuration(project_path)
    return config["values"]


def session_show_configuration_list(project_path):
    """
    Show known configurations.

    :param project_path     Project path (str)
    """
    config = session_read_configuration(project_path)
    len_values = len(config["values"])
    if len_values == 0:
        Logger.warn("No configuration found. Use `docknv config generate` to generate configurations.")
    else:
        Logger.info("Known configurations:")
        for key in config["values"]:
            namespace = config["values"][key]["namespace"]
            environment = config["values"][key]["environment"]
            schema = config["values"][key]["schema"]
            user = config["values"][key]["user"]

            Logger.raw("  - {0} [namespace: {1}, environment: {2}, schema: {3}, user id: {4}]".format(
                key, namespace, environment, schema, user), color=Fore.BLUE)


def session_insert_configuration(session_data, config_name, schema_name, environment_name, namespace_name, user_id):
    """
    Insert a new configuration in the session data.

    :param session_data:        Session data (dict)
    :param config_name:         Configuration name (str)
    :param schema_name:         Schema name (str)
    :param environment_name:    Environment name (str)
    :param namespace_name:      Namespace name (str)
    :param user_id:             User ID (str/int)
    """
    session_data["values"][config_name] = {
        "environment": environment_name,
        "schema": schema_name,
        "namespace": namespace_name,
        "user": user_id
    }

    return session_data


def session_read_timestamps(project_name, config_name):
    """
    Read timestamps for a project name and a config name.

    :param project_name:    Project name (str)
    :param config_name:     Config name (str)
    :rtype: Timestamp data (dict)
    """
    timestamps_path = user_get_file_from_project(project_name, "timestamps.json", config_name)
    original_timestamps = {}
    if os.path.exists(timestamps_path):
        with io_open(timestamps_path, mode="r") as stream:
            original_timestamps = read_last_modification_time(stream)

    return original_timestamps


def session_save_timestamps(project_name, config_name, timestamps):
    """
    Save timestamps for a project name and a config name.

    :param project_name:    Project name (str)
    :param config_name:     Config name (str)
    :param timestamps:      Timestamp data (dict)
    """
    timestamps_path = user_get_file_from_project(project_name, "timestamps.json", config_name)
    with io_open(timestamps_path, mode="w") as stream:
        save_last_modification_time(stream, timestamps)
