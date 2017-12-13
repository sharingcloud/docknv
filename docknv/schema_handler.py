"""Schema handler."""

from __future__ import unicode_literals

import copy

from docknv.logger import Logger, Fore

from docknv.utils.serialization import yaml_merge


def schema_list(project_data):
    """
    List available schemas for the project.

    :param project_data:     Project data (str)
    """
    schemas_count = len(project_data.schemas) if project_data.schemas is not None else 0
    if schemas_count == 0:
        Logger.warn("No schema found.")
    else:
        for name in project_data.schemas:
            schema = schema_get_configuration(project_data, name)
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


def schema_get_configuration(project_data, schema_name):
    """
    Get schema configuration.

    :param project_data:  Project data (dict)
    :param schema_name:  Schema name (str)
    :rtype: Schema configuration (dict)
    """
    if schema_name not in project_data.schemas:
        Logger.error("Schema `{0}` does not exist.".format(schema_name))
    else:
        schema_config = project_data.schemas[schema_name]

        # Inclusions
        if "includes" in schema_config:
            includes = schema_config["includes"]
            include_schemas = [schema_get_configuration(
                project_data, include_name)["config"] for include_name in includes]

            current_schema = copy.deepcopy(schema_config)
            del current_schema["includes"]

            include_schemas.append(current_schema)
            schema_config = yaml_merge(include_schemas)

        return {"name": schema_name, "config": schema_config}


def schema_check(project_data, schema_name):
    """
    Check if a schema exist.

    :param project_data:      Project data (dict)
    :param schema_name:      Schema name (str)
    :rtype: bool
    """
    if schema_name not in project_data.schemas:
        Logger.error("Schema `{0}` does not exist.".format(schema_name))

    return True
