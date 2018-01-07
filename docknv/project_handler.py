"""Project handler."""

import os

from contextlib import contextmanager

from docknv.logger import Logger
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump, yaml_merge
from docknv.utils.words import generate_config_name
from docknv.utils.paths import create_path_tree, get_lower_basename
from docknv.utils.ioutils import io_open

CONFIG_FILE_NAME = "config.yml"


class ProjectData(object):
    """docknv config data object."""

    def __init__(self, project_path, config_data):
        """
        Project data constructor.

        :param project_path:     Project path (str)
        :param config_data:      Config data (dict)
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

    :param project_path: Project path (str)
    :rtype: Project data (ProjectData)
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


def project_is_valid(project_path):
    """
    Check if a project is valid.

    :param project_path:    Project path
    :rtype: True/False
    """
    return os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME))


def project_set_active_configuration(project_path, config_name, quiet=False):
    """
    Set the active configuration.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    :param quiet:            Be quiet (bool) (default: False)
    """
    from docknv.user_handler import (
        user_read_docknv_config, user_write_docknv_config
    )

    config = project_read(project_path)
    docknv_config = user_read_docknv_config(config.project_name)
    docknv_config["current"] = config_name

    user_write_docknv_config(config.project_name, docknv_config)

    if not quiet:
        Logger.info("Configuration `{0}` set as current configuration.".format(config_name))


def project_get_active_configuration(project_path):
    """
    Get the active configuration.

    :param project_path:     Project path (str)
    :rtype: Active configuration (str?)
    """
    from docknv.user_handler import user_read_docknv_config

    config = project_read(project_path)
    content = user_read_docknv_config(config.project_name)

    return content.get("current", None)


def project_update_configuration_schema(project_path, config_name, schema_name):
    """
    Update a configuration schema.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    :param schema_name:      Schema name (str)
    """
    from docknv.session_handler import session_update_schema

    project_config = project_read(project_path)
    session_update_schema(project_path, project_config, config_name, schema_name)


def project_use_configuration(project_path, config_name, quiet=False):
    """
    Use a composefile from a known configuration.

    Set it at .docker-compose.yml.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    :param quiet:            Be quiet (bool) (default: False)
    """
    from docknv.session_handler import session_get_configuration
    from docknv.user_handler import user_get_id, user_copy_file_to_config

    config_content = project_read(project_path)
    config = session_get_configuration(project_path, config_name)

    current_id = user_get_id()
    if config["user"] != current_id:
        Logger.error("Can not access to `{0}` configuration. Access denied.".format(config_name))

    path = project_get_composefile(project_path, config_name)

    if not os.path.exists(path):
        Logger.error("Missing composefile for configuration `{0}`".format(config_name))

    user_copy_file_to_config(config_content.project_name, path)
    project_set_active_configuration(project_path, config_name, quiet)


def project_unset_configuration(project_path):
    """
    Unset the configuration.

    :param project_path:     Project path (str)
    """
    from docknv.user_handler import user_get_docknv_config_file

    config = project_read(project_path)
    config_path = user_get_docknv_config_file(config.project_name)

    if os.path.exists(config_path):
        os.remove(config_path)

    Logger.info("User project configuration has been unset.")


@contextmanager
def project_use_temporary_configuration(project_path, config_name):
    """
    Use a temporary configuration.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)

    **Context manager**
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

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    """
    from docknv.user_handler import user_get_file_from_project

    project_name = get_lower_basename(project_path)
    return user_get_file_from_project(project_name, "docker-compose.yml", config_name)


def project_generate_compose_from_configuration(project_path, config_name):
    """
    Generate a valid Docker Compose file from a known configuration name.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str)
    """
    from docknv.session_handler import session_get_configuration

    config = session_get_configuration(project_path, config_name)
    project_generate_compose(".", config["schema"], config["namespace"], config["environment"],
                             config_name, update=True)


def project_check_config_name(project_path, config_name):
    """
    Check config name, generate a new one if not valid.

    :param project_path:    Project path (str)
    :param config_name:     Config name (str)
    :rtype: Valid config name (str)
    """
    from docknv.session_handler import session_read_configuration

    config = session_read_configuration(project_path)
    config_names = list(config["values"].keys())

    if config_name not in config_names:
        return config_name

    if config_name is not None:
        Logger.info(
            "Already existing configuration name: {0}. Generating a new configuration name...".format(config_name))
    return generate_config_name(config_names)


def project_generate_compose(project_path, schema_name="all", namespace="default", environment="default",
                             config_name=None, update=False):
    """
    Generate a valid Docker Compose file.

    :param project_path:     Project path (str)
    :param schema_name:      Schema name (str) (default: all)
    :param namespace:        Namespace name (str) (default: default)
    :param environment:      Environment config (str) (default: default)
    :param config_name:      Config name (str?) (default: None)
    :param update:           Update configuration (bool) (default: False)
    :rtype: Config name (str)
    """
    from docknv.schema_handler import schema_get_configuration
    from docknv.template_renderer import renderer_render_compose_template
    from docknv.environment_handler import (
        env_yaml_check_file, env_yaml_load_in_memory,
        env_yaml_resolve_variables, env_yaml_key_value_export
    )
    from docknv.user_handler import user_get_id, user_get_file_from_project

    from docknv.session_handler import (
        session_read_configuration, session_write_configuration, session_insert_configuration
    )

    from docknv.composefile_handler import (
        composefile_multiple_read, composefile_filter, composefile_resolve_volumes,
        composefile_apply_namespace, composefile_write, composefile_handle_service_tags
    )

    ####################
    # Configuration name

    if not update:
        session = session_read_configuration(project_path)
        config_name = project_check_config_name(project_path, config_name)
        Logger.info("Creating configuration: `{0}`".format(config_name))

        new_session = session_insert_configuration(session, config_name, schema_name,
                                                   environment, namespace, user_get_id())

        # Set project path
    else:
        Logger.info("Updating configuration: `{0}`".format(config_name))

    # Load config file
    config_data = project_read(project_path)

    try:
        registry_url = config_data.config_data["registry"]["url"]
    except BaseException:
        registry_url = "localhost:5000"

    # Load environment
    if not env_yaml_check_file(project_path, environment):
        Logger.error("Environment file `{0}` does not exist.".format(environment))

    env_content = env_yaml_load_in_memory(project_path, environment)
    env_content = env_yaml_resolve_variables(env_content)

    # Save environment
    with io_open(
        user_get_file_from_project(config_data.project_name, 'environment.env', config_name), mode='wt'
    ) as handle:
        handle.write(env_yaml_key_value_export(env_content))

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

    # Handle services tags
    rendered_content = composefile_handle_service_tags(rendered_content, registry_url)

    # Apply namespace
    namespaced_content = composefile_apply_namespace(rendered_content, namespace, environment)

    # Generate main compose file
    output_compose_file = project_get_composefile(project_path, config_name)
    if not os.path.exists(output_compose_file):
        create_path_tree(os.path.dirname(output_compose_file))

    composefile_write(namespaced_content, output_compose_file)

    if not update:
        # Write new session configuration
        session_write_configuration(project_path, new_session)

    return config_name


def project_validate(project_file_path, config_data):
    """
    Validate project file structure.

    :param project_file_path:    Project path (str)
    :param config_data:          Config data (dict)
    """
    if "composefiles" not in config_data:
        Logger.error("Missing `composefiles` key in config file `{0}`".format(project_file_path))

    if "schemas" not in config_data:
        Logger.error("Missing `schemas` key in config file `{0}`".format(project_file_path))


def project_clean_user_config_path(project_path, config_name=None):
    """
    Clean the user config path.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str?) (default: None)
    """
    from docknv.user_handler import user_clean_config_path

    project_name = get_lower_basename(project_path)
    if not config_name:
        Logger.info("Attempting to clean user configuration for project `{0}`".format(project_name))
    else:
        Logger.info("Attempting to clean user configuration for project `{0}` and config `{1}`".format(
            project_name, config_name))

    user_clean_config_path(project_name, config_name)
