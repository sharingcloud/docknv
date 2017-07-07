"""
docknv config handler
"""

import os
import random
import codecs
from contextlib import contextmanager

from docknv.logger import Logger, Fore
from docknv import yaml_utils, utils

from docknv.v2.project_handler import get_composefile_path


class ConfigHandler(object):
    """
    docknv config handler
    """

    CONFIG_FILE_NAME = "config.yml"
    TEMPORARY_FILE_NAME = ".docknv.yml"

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
    def load_config_from_path(project_path):
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

        # Validation
        ConfigHandler._validate_config(project_file_path, config_data)

        return ConfigHandler.ConfigHandlerData(project_path, config_data)

    @staticmethod
    def load_temporary_config_from_path(project_path):
        """
        Load a temporary config file.
        Contains available namespaces.
        """

        project_file_path = os.path.join(
            project_path, ConfigHandler.TEMPORARY_FILE_NAME)

        if os.path.isfile(project_file_path):
            with codecs.open(project_file_path, encoding="utf-8", mode="r") as handle:
                config_data = yaml_utils.ordered_load(handle.read())

            return config_data

        return {"values": {}}

    @staticmethod
    def _get_word_from_dictionary():
        with codecs.open("/usr/share/dict/words", encoding="utf-8", mode="rt") as handle:
            words = handle.readlines()

        return random.choice(words).lower()[:-1]

    @staticmethod
    def generate_config_name(config_list):
        """
        Generate a unique config name.
        """

        if os.path.isfile("/usr/share/dict/words"):
            success = False
            key = None

            while not success:
                word1 = ConfigHandler._get_word_from_dictionary()
                word2 = ConfigHandler._get_word_from_dictionary()
                key = "{0}_{1}".format(word1, word2)

                if key not in config_list:
                    success = True

            return key

        return "config_{0}".format(len(config_list) + 1)

    @staticmethod
    def get_configurations_list(project_path):
        """
        Get configurations list
        """
        config = ConfigHandler.load_temporary_config_from_path(project_path)
        return config["values"]

    @staticmethod
    def list_known_configurations(project_path):
        """
        List known configurations.
        """

        config = ConfigHandler.load_temporary_config_from_path(project_path)
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
    def get_known_configuration(project_path, name):
        """
        Get a known configuration by name.
        """
        config = ConfigHandler.load_temporary_config_from_path(project_path)
        if name in config["values"]:
            return config["values"][name]
        else:
            Logger.error(
                "Missing configuration `{0}` in known configuration.".format(name))

    @staticmethod
    def set_current_config(project_path, config_name):
        """
        Set a current config
        """
        config = ConfigHandler.load_config_from_path(project_path)

        from docknv.v2.multi_user_handler import MultiUserHandler
        MultiUserHandler.set_current_config(config.project_name, config_name)

        Logger.info(
            "Configuration `{0}` set as current configuration.".format(config_name))

    @staticmethod
    def do_config_exist(config_data, config_name):
        if config_name not in config_data["values"]:
            Logger.error("Missing configuration `{0}`.".format(config_name))

        return True

    @staticmethod
    def remove_config(project_path, config_name):
        """
        Remove a config
        """
        from docknv.v2.multi_user_handler import MultiUserHandler
        config = ConfigHandler.load_temporary_config_from_path(project_path)
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
                project_path, config_to_remove["namespace"], config_to_remove["environment"], config_to_remove["schema"])
            os.remove(path)

            del config["values"][config_name]

            ConfigHandler.write_temporary_config(project_path, config)
            Logger.info("Configuration `{0}` removed.".format(config_name))

    @staticmethod
    def update_config_schema(project_path, config_name, schema_name):
        """
        Change a config schema
        """

        from docknv.v2.schema_handler import SchemaHandler

        project_config = ConfigHandler.load_config_from_path(project_path)
        if SchemaHandler.do_schema_exist(project_config, schema_name):
            docknv_config = ConfigHandler.load_temporary_config_from_path(
                project_path)

            if ConfigHandler.do_config_exist(docknv_config, config_name):
                docknv_config["values"][config_name]["schema"] = schema_name
                ConfigHandler.write_temporary_config(
                    project_path, docknv_config)
                Logger.info("Configuration `{0}` updated with schema `{1}`".format(
                    config_name, schema_name))

    @staticmethod
    def update_config_environment(project_path, config_name, environment_name):
        """
        Change a config environment
        """

        from docknv.v2.env_handler import EnvHandler

        if EnvHandler.check_environment_file(project_path, environment_name):
            docknv_config = ConfigHandler.load_temporary_config_from_path(
                project_path)

            if ConfigHandler.do_config_exist(docknv_config, config_name):
                docknv_config["values"][config_name]["environment"] = environment_name
                ConfigHandler.write_temporary_config(
                    project_path, docknv_config)
                Logger.info("Configuration `{0}` updated with environment `{1}`".format(
                    config_name, environment_name))

    @staticmethod
    def get_current_config(project_path):
        """
        Get the current config
        """
        config = ConfigHandler.load_config_from_path(project_path)

        from docknv.v2.multi_user_handler import MultiUserHandler
        return MultiUserHandler.get_current_config(config.project_name)

    @staticmethod
    def use_composefile_configuration(project_path, config_name):
        """
        Use a composefile from a known configuration.
        Set it at .docker-compose.yml.
        """
        from docknv.v2.multi_user_handler import MultiUserHandler

        config_content = ConfigHandler.load_config_from_path(project_path)

        config = ConfigHandler.get_known_configuration(
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

        ConfigHandler.set_current_config(project_path, config_name)

    @staticmethod
    def write_temporary_config(project_path, content):
        """
        Write a temporary config file.
        """
        project_file_path = os.path.join(
            project_path, ConfigHandler.TEMPORARY_FILE_NAME)

        with codecs.open(project_file_path, encoding="utf-8", mode="w") as handle:
            handle.write(yaml_utils.ordered_dump(content))

    @staticmethod
    @contextmanager
    def using_temporary_config(project_path, config_name):
        """
        Use a temporary config
        """

        old_config = ConfigHandler.get_current_config(project_path)
        if old_config is None:
            Logger.error(
                "You should already use one config before using this tool")

        ConfigHandler.use_composefile_configuration(project_path, config_name)
        yield
        ConfigHandler.use_composefile_configuration(project_path, old_config)

    # PRIVATE METHODS #############

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
