"""
Schema handler
"""

import os
import copy

from docknv.v2.config_handler import ConfigHandler
from docknv.v2.env_handler import EnvHandler
from docknv.v2.compose_handler import ComposeHandler

from docknv.v2.project_handler import get_composefile_path

from docknv import yaml_utils, utils
from docknv.logger import Logger, Fore


class SchemaHandler(object):
    """
    Schema handler
    """

    @staticmethod
    def list_schemas(project_path):
        """
        List available schemas for the project.
        """

        config_data = ConfigHandler.load_config_from_path(project_path)
        schemas_count = len(config_data.schemas)
        if schemas_count == 0:
            Logger.warn("No schema found.")
        else:
            for name in config_data.schemas:
                schema = SchemaHandler.get_schema_configuration(
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

    @staticmethod
    def get_schema_configuration(config_data, schema_name):
        """
        Get schema configuration

        @param config_data  Config data
        @param schema_name  Schema name
        """

        if schema_name == "all":
            return {"name": "all", "config": {}}

        elif schema_name not in config_data.schemas:
            Logger.error("Schema `{0}` does not exist.".format(schema_name))
        else:
            schema_config = config_data.schemas[schema_name]

            # Inclusions
            if "includes" in schema_config:
                includes = schema_config["includes"]
                include_schemas = [SchemaHandler.get_schema_configuration(
                    config_data, include_name)["config"] for include_name in includes]

                current_schema = copy.deepcopy(schema_config)
                del current_schema["includes"]

                include_schemas.append(current_schema)
                schema_config = yaml_utils.merge_yaml(include_schemas)

            return {"name": schema_name, "config": schema_config}

    @staticmethod
    def generate_compose_from_configuration(project_path, config_name):
        """
        Generate a valid Docker Compose file from a known configuration name.

        @param project_path Project path
        @param config_name  Configuration nickname
        """
        config = ConfigHandler.get_known_configuration(
            project_path, config_name)
        SchemaHandler.generate_compose(
            ".", config["schema"], config["namespace"], config["environment"], config_name)

    @staticmethod
    def generate_compose(project_path, schema_name="all", namespace="default", environment="default", config_name=None):
        """
        Generate a valid Docker Compose file.

        @param project_path     Project path
        @param schema_name      Schema name
        @param namespace        Namespace name
        @param environment      Environment config
        @param config_name      Configuration nickname
        """

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

        # Load config file
        config_data = ConfigHandler.load_config_from_path(project_path)

        # Load environment
        if not EnvHandler.check_environment_file(project_path, environment):
            Logger.error(
                "Environment file `{0}` does not exist.".format(environment))

        env_content = EnvHandler.load_env_in_memory(project_path, environment)

        # Generate .env file
        # EnvHandler.write_env_to_file(
        # env_content, os.path.join(project_path, ".env"))

        # Get schema configuration
        schema_config = SchemaHandler.get_schema_configuration(
            config_data, schema_name)

        # List linked composefiles
        compose_files_content = ComposeHandler.load_multiple_compose_files(
            project_path, config_data.composefiles)

        # Merge and filter using schema
        merged_content = ComposeHandler.filter_content_with_schema(
            compose_files_content, schema_config)

        # Resolve compose content
        resolved_content = ComposeHandler.resolve_compose_content(
            merged_content, env_content)

        # Generate volumes declared in composefiles
        rendered_content = ComposeHandler.resolve_volumes(
            project_path, resolved_content, namespace, environment, env_content)

        # Apply namespace
        namespaced_content = ComposeHandler.apply_namespace(
            rendered_content, namespace, environment)

        # Generate main compose file
        output_compose_file = get_composefile_path(
            project_path, namespace, environment, schema_name)
        if not os.path.exists(output_compose_file):
            utils.create_path_tree(os.path.dirname(output_compose_file))

        ComposeHandler.write_compose_content_to_file(
            namespaced_content, output_compose_file)

        # Get temporary config
        config = ConfigHandler.load_temporary_config_from_path(project_path)

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
                new_name = ConfigHandler.generate_config_name(old_keys)
                Logger.warn(
                    "Configuration name `{0}` already exist. New name generated: `{1}`".format(config_name, new_name))
                config_name = new_name
            elif config_name is None:
                config_name = ConfigHandler.generate_config_name(old_keys)
                Logger.info("Generated config name: `{0}`".format(config_name))
            else:
                Logger.info("Config name: `{0}`".format(config_name))

            config["values"][config_name] = current_combination

        elif changing_key:
            if config_name is None:
                config_name = ConfigHandler.generate_config_name(old_keys)

            config["values"][config_name] = config["values"][changing_key]
            del config["values"][changing_key]

            Logger.info("Changing config name to `{0}`".format(config_name))

        else:
            Logger.info("Config name: `{0}`".format(config_name))

        ConfigHandler.write_temporary_config(project_path, config)
