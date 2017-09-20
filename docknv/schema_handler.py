"""Schema handler."""

import copy

from docknv.project_handler import project_read
from docknv.logger import Logger, Fore

from docknv.utils.serialization import yaml_merge


def schema_list(project_path):
    """
    List available schemas for the project.

    :param project_path     Project path (str)
    """
    config_data = project_read(project_path)
    schemas_count = len(config_data.schemas) if config_data.schemas is not None else 0
    if schemas_count == 0:
        Logger.warn("No schema found.")
    else:
        for name in config_data.schemas:
            schema = schema_get_configuration(
                config_data, name)
            Logger.raw("Schema: " + name, color=Fore.GREEN)
            if "volumes" in schema["config"]:
                Logger.raw("  Volumes: ", color=Fore.BLUE)
                volumes = schema["config"]["volumes"]
                for volume in volumes:
                    Logger.raw("    " + volume)

            if "services" in schema["config"]:
                Logger.raw("  Services: ", color=Fore.BLUE)
                services = schema["config"]["services"]
                for service in services:
                    Logger.raw("    " + service)
            Logger.raw("")


def schema_get_configuration(config_data, schema_name):
    """
    Get schema configuration.

    :param config_data  Config data (dict)
    :param schema_name  Schema name (str)
    :return Schema configuration (dict)
    """
    if schema_name not in config_data.schemas:
        Logger.error("Schema `{0}` does not exist.".format(schema_name))
    else:
        schema_config = config_data.schemas[schema_name]

        # Inclusions
        if "includes" in schema_config:
            includes = schema_config["includes"]
            include_schemas = [schema_get_configuration(
                config_data, include_name)["config"] for include_name in includes]

            current_schema = copy.deepcopy(schema_config)
            del current_schema["includes"]

            include_schemas.append(current_schema)
            schema_config = yaml_merge(include_schemas)

        return {"name": schema_name, "config": schema_config}


def schema_check(config_data, schema_name):
    """
    Check if a schema exist.

    :param config_data      Config data (dict)
    :param schema_name      Schema name (str)
    :return bool
    """
    if schema_name not in config_data.schemas:
        Logger.error("Schema `{0}` does not exist.".format(schema_name))

    return True
