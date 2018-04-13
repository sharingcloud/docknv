"""Command handler."""

import os
import pprint

from docknv.utils.prompt import prompt_yes_no

from docknv.project_handler import project_read, project_get_active_configuration, project_is_valid
from docknv.session_handler import session_get_configuration
from docknv.schema_handler import schema_get_configuration
from docknv.environment_handler import env_yaml_load_in_memory, env_yaml_resolve_variables
from docknv.user_handler import user_read_docknv_config, user_write_docknv_config


class CommandContext(object):
    """Command context."""

    def __init__(self):
        """Init."""
        self.project_name = None
        self.config_name = None
        self.schema_name = None
        self.namespace_name = None
        self.environment_name = None
        self.environment_data = {}
        self.schema_data = []

    def __repr__(self):
        """Repr."""
        return pprint.pformat({
            "project_name": self.project_name,
            "config_name": self.config_name,
            "schema_name": self.schema_name,
            "namespace_name": self.namespace_name,
            "environment_name": self.environment_name,
            "environment_data": self.environment_data,
            "schema_data": self.schema_data
        })


def command_get_config(config_data, command):
    """
    Get command configuration from config.yml.

    :param config_data:      Config data (dict)
    :param command:          Command name (str)
    :rtype: Command configuration (dict)
    """
    commands = config_data.get('commands', None)
    if not commands:
        return {}

    command_config = commands.get(command)
    if not command_config:
        return {}

    return command_config


def command_get_context_from(project_data, config_name, session_data, schema_data, env_data):
    """
    Get context from a configuration.

    :param project_data:    Project data (dict)
    :param config_name:     Configuration name (str)
    :param session_data:    Session data (dict)
    :param schema_data:     Schema data (dict)
    :param env_data:        Environment data (dict)
    :rtype: Context data (dict)
    """
    context = CommandContext()

    environment_name = session_data['environment']
    schema_name = session_data['schema']
    namespace_name = session_data['namespace']

    context.project_name = project_data.project_name
    context.config_name = config_name
    context.namespace_name = None if namespace_name == "default" else namespace_name
    context.schema_name = schema_name
    context.environment_name = environment_name
    context.schema_data = schema_data['config']
    context.environment_data = env_data

    return context


def command_get_context(project_path):
    """
    Get current context from active configuration.

    :param project_path: Project path (str)
    :rtype: Context data (dict)
    """
    if not project_is_valid(project_path):
        return CommandContext()

    project_data = project_read(project_path)
    project_name = project_data.project_name

    # User project path
    docknv_config = user_read_docknv_config(project_name)
    user_project_path = docknv_config.get("project_path", None)
    if user_project_path is None:
        docknv_config["project_path"] = os.path.realpath(project_path)
        user_write_docknv_config(project_name, docknv_config)
    elif user_project_path != os.path.realpath(project_path):
        print("Project named `{0}` already exist at location `{1}`.".format(project_name, user_project_path))
        choice = prompt_yes_no("/!\\ Are you sure to overwrite the configuration ?")
        if not choice:
            raise RuntimeError("No configuration overwrite.")
        else:
            docknv_config["project_path"] = os.path.realpath(project_path)
            user_write_docknv_config(project_name, docknv_config)

    config_name = project_get_active_configuration(project_path)
    if not config_name:
        return CommandContext()

    session_data = session_get_configuration(project_path, config_name)
    schema_data = schema_get_configuration(project_data, session_data['schema'])
    env_data = env_yaml_load_in_memory(project_path, session_data['environment'])
    env_data = env_yaml_resolve_variables(env_data)

    return command_get_context_from(project_data, config_name, session_data, schema_data, env_data)
