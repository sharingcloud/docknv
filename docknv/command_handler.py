"""Command handler."""


class CommandContext(object):
    """Command context."""

    def __init__(self):
        """Init."""
        self.config_name = None
        self.schema_name = None
        self.namespace_name = None
        self.environment_name = None
        self.environment_data = {}
        self.schema_data = []

    def __repr__(self):
        """Repr."""
        import pprint
        return pprint.pformat({
            "config_name": self.config_name,
            "schema_name": self.schema_name,
            "namespace_name": self.namespace_name,
            "environment_name": self.environment_name,
            "environment_data": self.environment_data,
            "schema_data": self.schema_data
        })


def command_get_config(project_path, command):
    """
    Get command configuration from config.yml.

    :param project_path:     Project path (str)
    :param command:          Command name (str)
    :rtype: Command configuration (dict)
    """
    from docknv.project_handler import project_read

    project_data = project_read(project_path)
    config_data = project_data.config_data

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
    from docknv.project_handler import project_read, project_get_active_configuration
    from docknv.session_handler import session_get_configuration
    from docknv.schema_handler import schema_get_configuration
    from docknv.environment_handler import env_load_in_memory

    project_data = project_read(project_path)
    config_name = project_get_active_configuration(project_path)
    if not config_name:
        return CommandContext()

    session_data = session_get_configuration(project_path, config_name)
    schema_data = schema_get_configuration(project_data, session_data['schema'])
    env_data = env_load_in_memory(project_path, session_data['environment'])

    return command_get_context_from(project_data, config_name, session_data, schema_data, env_data)
