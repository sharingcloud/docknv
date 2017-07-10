"""
docknv config handler
"""

import os
import codecs
from contextlib import contextmanager

from docknv.logger import Logger, Fore
from docknv import yaml_utils, utils

from docknv.v2.project_handler import get_composefile_path
from docknv.v2.environment_handler import EnvironmentHandler
from docknv.v2.multi_user_handler import MultiUserHandler


class ConfigHandler(object):
    """
    docknv config handler
    """

    CONFIG_FILE_NAME = "config.yml"
    SESSION_FILE_NAME = ".docknv.yml"

    class ConfigHandlerData(object):
        """
        docknv config data object
        """

        def __init__(self, project_path, config_data):
            self.project_path = project_path
            self.project_name = os.path.basename(
                os.path.abspath(project_path)).lower()
            self.configuration = config_data.get("configuration", {})
            self.schemas = config_data.get("schemas", [])
            self.composefiles = config_data.get("composefiles", [])

            self.config_data = config_data

    @staticmethod
    def read_docknv_configuration(project_path):
        """
        Load a docknv config file from a project path.

        @param project_path Project path
        """

        project_file_path = os.path.join(
            project_path, ConfigHandler.CONFIG_FILE_NAME)

        if os.path.isfile(project_file_path):
            with codecs.open(project_file_path, encoding="utf-8", mode="r") as handle:
                config_data = yaml_utils.ordered_load(handle.read())
        else:
            Logger.error(
                "Config file `{0}` does not exist.".format(project_file_path))
            return

        # Validation
        ConfigHandler._validate_config(project_file_path, config_data)

        return ConfigHandler.ConfigHandlerData(project_path, config_data)

    @staticmethod
    def read_session_configuration(project_path):
        """
        Read a session config file.
        Contains available namespaces.
        """

        project_file_path = os.path.join(
            project_path, ConfigHandler.SESSION_FILE_NAME)

        if os.path.isfile(project_file_path):
            with codecs.open(project_file_path, encoding="utf-8", mode="r") as handle:
                config_data = yaml_utils.ordered_load(handle.read())

            return config_data

        return {"values": {}}

    @staticmethod
    def list_configurations(project_path):
        """
        Get configurations list
        """

        config = ConfigHandler.read_session_configuration(project_path)
        return config["values"]

    @staticmethod
    def show_configuration_list(project_path):
        """
        List known configurations.
        """

        config = ConfigHandler.read_session_configuration(project_path)
        len_values = len(config["values"])
        if len_values == 0:
            Logger.warn(
                "No configuration found. Use `docknv config generate` to generate configurations.")
        else:
            Logger.info("Known configurations:")
            for key in config["values"]:
                namespace = config["values"][key]["namespace"]
                environment = config["values"][key]["environment"]
                schema = config["values"][key]["schema"]
                user = config["values"][key]["user"]

                Logger.raw("  - {0} [namespace: {1}, environment: {2}, schema: {3}, user id: {4}]".format(
                    key, namespace, environment, schema, user), color=Fore.BLUE)

    @staticmethod
    def get_configuration(project_path, name):
        """
        Get a known configuration by name.
        """
        config = ConfigHandler.read_session_configuration(project_path)
        if name in config["values"]:
            return config["values"][name]
        else:
            Logger.error(
                "Missing configuration `{0}` in known configuration.".format(name))

    @staticmethod
    def set_active_configuration(project_path, config_name, quiet=False):
        """
        Set a current config
        """
        config = ConfigHandler.read_docknv_configuration(project_path)
        MultiUserHandler.set_current_configuration(
            config.project_name, config_name)

        if not quiet:
            Logger.info(
                "Configuration `{0}` set as current configuration.".format(config_name))

    @staticmethod
    def check_configuration(config_data, config_name):
        if config_name not in config_data["values"]:
            Logger.error("Missing configuration `{0}`.".format(config_name))

        return True

    @staticmethod
    def remove_configuration(project_path, config_name):
        """
        Remove a config
        """
        config = ConfigHandler.read_session_configuration(project_path)
        if config_name not in config["values"]:
            Logger.error("Missing configuration `{0}`.".format(config_name))
        uid = MultiUserHandler.get_user_id()

        if config["user"] != uid:
            Logger.error(
                "You can not remove configuration `{0}`. Access denied.".format(config_name))

        choice = utils.prompt_yes_no(
            "/!\\ Are you sure you want to remove configuration `{0}` ?".format(config_name))

        if choice:
            # Check current
            if "current" in config and config["current"] == config_name:
                if os.path.exists(os.path.join(project_path, ".docker-compose.yml")):
                    os.remove(os.path.join(
                        project_path, ".docker-compose.yml"))
                del config["current"]

            # Remove configuration and docker-compose file.
            config_to_remove = config["values"][config_name]
            path = get_composefile_path(
                project_path, config_to_remove["namespace"], config_to_remove["environment"],
                config_to_remove["schema"])
            os.remove(path)

            del config["values"][config_name]

            ConfigHandler.write_session_configuration(project_path, config)
            Logger.info("Configuration `{0}` removed.".format(config_name))

    @staticmethod
    def update_configuration_schema(project_path, config_name, schema_name):
        """
        Change a config schema
        """

        from docknv.v2.schema_handler import SchemaHandler

        project_config = ConfigHandler.read_docknv_configuration(project_path)
        if SchemaHandler.do_schema_exist(project_config, schema_name):
            docknv_config = ConfigHandler.read_session_configuration(
                project_path)

            if ConfigHandler.check_configuration(docknv_config, config_name):
                docknv_config["values"][config_name]["schema"] = schema_name
                ConfigHandler.write_session_configuration(
                    project_path, docknv_config)
                Logger.info("Configuration `{0}` updated with schema `{1}`".format(
                    config_name, schema_name))

    @staticmethod
    def update_configuration_environment(project_path, config_name, environment_name):
        """
        Change a config environment
        """

        if EnvironmentHandler.check_environment_file(project_path, environment_name):
            docknv_config = ConfigHandler.read_session_configuration(
                project_path)

            if ConfigHandler.check_configuration(docknv_config, config_name):
                docknv_config["values"][config_name]["environment"] = environment_name
                ConfigHandler.write_session_configuration(
                    project_path, docknv_config)
                Logger.info("Configuration `{0}` updated with environment `{1}`".format(
                    config_name, environment_name))

    @staticmethod
    def get_active_configuration(project_path):
        """
        Get the current config
        """
        config = ConfigHandler.read_docknv_configuration(project_path)
        return MultiUserHandler.get_current_configuration(config.project_name)

    @staticmethod
    def use_configuration(project_path, config_name, quiet=False):
        """
        Use a composefile from a known configuration.
        Set it at .docker-compose.yml.
        """

        config_content = ConfigHandler.read_docknv_configuration(project_path)

        config = ConfigHandler.get_configuration(
            project_path, config_name)

        current_id = MultiUserHandler.get_user_id()
        if config["user"] != current_id:
            Logger.error(
                "Can not access to `{0}` configuration. Access denied.".format(config_name))

        path = get_composefile_path(
            project_path, config["namespace"], config["environment"], config["schema"])

        if not os.path.exists(path):
            Logger.error(
                "Missing composefile for configuration `{0}`".format(config_name))

        MultiUserHandler.copy_file_to_user_config_path(
            config_content.project_name, path)

        ConfigHandler.set_active_configuration(
            project_path, config_name, quiet)

    @staticmethod
    def write_session_configuration(project_path, content):
        """
        Write a temporary config file.
        """
        project_file_path = os.path.join(
            project_path, ConfigHandler.SESSION_FILE_NAME)

        with codecs.open(project_file_path, encoding="utf-8", mode="w") as handle:
            handle.write(yaml_utils.ordered_dump(content))

    @staticmethod
    @contextmanager
    def using_temporary_configuration(project_path, config_name):
        """
        Use a temporary config
        """

        old_config = ConfigHandler.get_active_configuration(project_path)
        if old_config is None:
            Logger.error(
                "You should already use one config before using this tool")

        ConfigHandler.use_configuration(project_path, config_name, quiet=True)
        yield
        ConfigHandler.use_configuration(project_path, old_config, quiet=True)

    ###############
    # Internal

    @staticmethod
    def _validate_config(project_file_path, config_data):
        if "composefiles" not in config_data:
            Logger.error(
                "Missing `composefiles` key in config file `{0}`"
                .format(project_file_path)
            )

        if "schemas" not in config_data:
            Logger.error(
                "Missing `schemas` key in config file `{0}`"
                .format(project_file_path)
            )
