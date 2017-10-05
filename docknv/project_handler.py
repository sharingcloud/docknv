"""Project handler."""

import os

from contextlib import contextmanager

from docknv.logger import Logger
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump, yaml_merge
from docknv.utils.words import generate_config_name
from docknv.utils.paths import create_path_tree
from docknv.utils.ioutils import io_open

CONFIG_FILE_NAME = "config.yml"


class ProjectData(object):
    """docknv config data object."""

    def __init__(self, project_path, config_data):
        """
        The ProjectData constructor.

        :param project_path     Project path (str)
        :param config_data      Config data (dict)
        """
        self.project_path = project_path
        self.project_name = os.path.basename(os.path.abspath(project_path)).lower()
        self.configuration = config_data.get("configuration", {})
        self.schemas = config_data.get("schemas", [])
        self.composefiles = config_data.get("composefiles", [])
        self.config_data = config_data

    def __repr__(self):
        """Repr."""
        import pprint
        return pprint.pformat({
            "project_path": self.project_path,
            "project_name": self.project_name,
            "configuration": self.configuration,
            "schemas": self.schemas,
            "composefiles": self.composefiles,
            "config_data": self.config_data
        }, indent=4)


def project_read(project_path):
    """
    Load a docknv config file from a project path.

    :param project_path Project path (str)
    :return Project data (ProjectData)
    """
    project_file_path = os.path.join(project_path, CONFIG_FILE_NAME)

    if os.path.isfile(project_file_path):
        with io_open(project_file_path, encoding="utf-8", mode="r") as handle:
            config_data = yaml_ordered_load(handle.read())
    else:
        Logger.error("Config file `{0}` does not exist.".format(project_file_path))
        return

    # Validation
    project_validate(project_file_path, config_data)

    return ProjectData(project_path, config_data)


def project_set_active_configuration(project_path, config_name, quiet=False):
    """
    Set the active configuration.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    :param quiet            Be quiet (bool) (default: False)
    """
    from docknv.user_handler import user_get_project_config_file_path

    config = project_read(project_path)
    config_path = user_get_project_config_file_path(config.project_name)

    config = {"current": config_name}
    with io_open(config_path, mode="wt") as handle:
        handle.write(yaml_ordered_dump(config))

    if not quiet:
        Logger.info("Configuration `{0}` set as current configuration.".format(config_name))


def project_get_active_configuration(project_path):
    """
    Get the active configuration.

    :param project_path     Project path (str)
    :return Active configuration (str?)
    """
    from docknv.user_handler import user_get_project_config_file_path

    config = project_read(project_path)
    config_path = user_get_project_config_file_path(config.project_name)
    content = None

    if os.path.exists(config_path):
        with io_open(config_path, mode="rt") as handle:
            content = yaml_ordered_load(handle.read())

    return content["current"] if content else None


def project_update_configuration_schema(project_path, config_name, schema_name):
    """
    Update a configuration schema.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    :param schema_name      Schema name (str)
    """
    from docknv.session_handler import session_update_schema

    project_config = project_read(project_path)
    session_update_schema(project_path, project_config, config_name, schema_name)


def project_get_name(project_path):
    """
    Get project name from path.

    :param project_path     Project path (str)
    :return Project path (str)
    """
    return os.path.basename(os.path.abspath(project_path)).lower()


def project_use_configuration(project_path, config_name, quiet=False):
    """
    Use a composefile from a known configuration.

    Set it at .docker-compose.yml.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    :param quiet            Be quiet (bool) (default: False)
    """
    from docknv.session_handler import session_get_configuration
    from docknv.user_handler import user_current_get_id, user_copy_file_to_config_path

    config_content = project_read(project_path)
    config = session_get_configuration(project_path, config_name)

    current_id = user_current_get_id()
    if config["user"] != current_id:
        Logger.error("Can not access to `{0}` configuration. Access denied.".format(config_name))

    path = project_get_composefile(
        project_path, config_name)

    if not os.path.exists(path):
        Logger.error("Missing composefile for configuration `{0}`".format(config_name))

    user_copy_file_to_config_path(config_content.project_name, path)
    project_set_active_configuration(project_path, config_name, quiet)


def project_unset_configuration(project_path):
    """
    Unset the configuration.

    :param project_path     Project path (str)
    """
    from docknv.user_handler import user_get_project_config_file_path

    config = project_read(project_path)
    config_path = user_get_project_config_file_path(config.project_name)

    if os.path.exists(config_path):
        os.remove(config_path)

    Logger.info("User project configuration has been unset.")


@contextmanager
def project_use_temporary_configuration(project_path, config_name):
    """
    Use a temporary configuration.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    :coroutine
    """
    old_config = project_get_active_configuration(project_path)
    if old_config is None:
        Logger.error("You should already use one config before using this tool")

    project_use_configuration(project_path, config_name, quiet=True)
    yield
    project_use_configuration(project_path, old_config, quiet=True)


def project_get_composefile(project_path, config_name):
    """
    Generate a composefile path.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    """
    from docknv.user_handler import user_get_project_config_name_path

    project_name = project_get_name(project_path)
    config_path = user_get_project_config_name_path(project_name, config_name)

    return os.path.join(config_path, "docker-compose.yml")


def project_generate_compose_from_configuration(project_path, config_name):
    """
    Generate a valid Docker Compose file from a known configuration name.

    :param project_path     Project path (str)
    :param config_name      Config name (str)
    """
    from docknv.session_handler import session_get_configuration

    config = session_get_configuration(project_path, config_name)
    project_generate_compose(".", config["schema"], config["namespace"], config["environment"], config_name)


def project_generate_compose(project_path, schema_name="all", namespace="default", environment="default",
                             config_name=None):
    """
    Generate a valid Docker Compose file.

    :param project_path     Project path (str)
    :param schema_name      Schema name (str) (default: all)
    :param namespace        Namespace name (str) (default: default)
    :param environment      Environment config (str) (default: default)
    :param config_name      Config name (str?) (default: None)
    """
    from docknv.schema_handler import schema_get_configuration
    from docknv.template_renderer import renderer_render_compose_template
    from docknv.environment_handler import env_check_file, env_load_in_memory
    from docknv.session_handler import session_read_configuration, session_write_configuration
    from docknv.composefile_handler import (
        composefile_multiple_read, composefile_filter, composefile_resolve_volumes,
        composefile_apply_namespace, composefile_write
    )

    user = None
    try:
        user = os.geteuid()
    except Exception:
        import getpass
        user = getpass.getuser()

    current_combination = {
        "schema": schema_name,
        "namespace": namespace,
        "environment": environment,
        "user": user
    }

    ####################
    # Configuration name

    # Get temporary config
    config = session_read_configuration(project_path)

    # Insert combination into temporary config
    new_combination = True
    changing_key = None
    for key in config["values"]:
        other_config = {
            "schema": config["values"][key]["schema"],
            "environment": config["values"][key]["environment"],
            "namespace": config["values"][key]["namespace"],
            "user": config["values"][key]["user"]
        }

        if current_combination == other_config:
            if config_name != key:
                changing_key = key
            new_combination = False

    old_keys = config["values"].keys()

    if new_combination:
        if config_name and config_name in config["values"].keys():
            new_name = generate_config_name(old_keys)
            Logger.warn(
                "Configuration name `{0}` already exist. New name generated: `{1}`".format(config_name, new_name))
            config_name = new_name
        elif config_name is None:
            config_name = generate_config_name(old_keys)
            Logger.info("Generated config name: `{0}`".format(config_name))
        else:
            Logger.info("Config name: `{0}`".format(config_name))

        config["values"][config_name] = current_combination

    elif changing_key:
        if config_name is None:
            config_name = generate_config_name(old_keys)

        config["values"][config_name] = config["values"][changing_key]
        del config["values"][changing_key]

        Logger.info("Changing config name to `{0}`".format(config_name))

    else:
        Logger.info("Config name: `{0}`".format(config_name))

    ###############

    # Load config file
    config_data = project_read(project_path)

    # Load environment
    if not env_check_file(project_path, environment):
        Logger.error("Environment file `{0}` does not exist.".format(environment))

    env_content = env_load_in_memory(project_path, environment)

    # Get schema configuration
    schema_config = schema_get_configuration(config_data, schema_name)

    # List linked composefiles
    compose_files_content = composefile_multiple_read(project_path, config_data.composefiles)

    # Merge and filter using schema
    merged_content = composefile_filter(yaml_merge(compose_files_content), schema_config)

    # Resolve compose content
    resolved_content = renderer_render_compose_template(merged_content, env_content)

    # Generate volumes declared in composefiles
    rendered_content = composefile_resolve_volumes(project_path, resolved_content, config_name, namespace,
                                                   environment, env_content)

    # Apply namespace
    namespaced_content = composefile_apply_namespace(rendered_content, namespace, environment)

    # Generate main compose file
    output_compose_file = project_get_composefile(project_path, config_name)
    if not os.path.exists(output_compose_file):
        create_path_tree(os.path.dirname(output_compose_file))

    composefile_write(namespaced_content, output_compose_file)
    session_write_configuration(project_path, config)


def project_validate(project_file_path, config_data):
    """
    Validate project file structure.

    :param project_file_path    Project path (str)
    :param config_data          Config data (dict)
    """
    if "composefiles" not in config_data:
        Logger.error("Missing `composefiles` key in config file `{0}`".format(project_file_path))

    if "schemas" not in config_data:
        Logger.error("Missing `schemas` key in config file `{0}`".format(project_file_path))


def project_clean_user_config_path(project_path, config_name=None):
    """
    Clean the user config path.

    :param project_path     Project path (str)
    :param config_name      Config name (str?) (default: None)
    """
    from docknv.user_handler import user_clean_config_path

    project_name = project_get_name(project_path)
    if not config_name:
        Logger.info("Attempting to clean user configuration for project `{0}`".format(project_name))
    else:
        Logger.info("Attempting to clean user configuration for project `{0}` and config `{1}`".format(
            project_name, config_name))

    user_clean_config_path(project_name, config_name)
