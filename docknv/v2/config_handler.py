"""
docknv config handler
"""

import os
import random
import shutil
import codecs

from docknv.logger import Logger, Fore
from docknv import yaml_utils, utils


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
            with codecs.open(project_file_path, encoding="utf-8", mode="rt") as handle:
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
            with codecs.open(project_file_path, encoding="utf-8", mode="rt") as handle:
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

                Logger.raw("  - {0} [namespace: {1}, environment: {2}, schema: {3}]".format(
                    key, namespace, environment, schema), color=Fore.BLUE)

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
    def get_composefile_path(project_path, namespace, environment, schema):
        return os.path.join(project_path, "data", "local", namespace, environment, "composefiles", schema, "docker-compose.yml")

    @staticmethod
    def set_current_config(project_path, config_name):
        config = ConfigHandler.load_temporary_config_from_path(project_path)
        config["current"] = config_name

        ConfigHandler.write_temporary_config(project_path, config)

        Logger.info(
            "Configuration `{0}` set as current configuration.".format(config_name))

    @staticmethod
    def remove_config(project_path, config_name):
        config = ConfigHandler.load_temporary_config_from_path(project_path)
        if config_name not in config["values"]:
            Logger.error("Missing configuration `{0}`.".format(config_name))

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
            path = ConfigHandler.get_composefile_path(
                project_path, config_to_remove["namespace"], config_to_remove["environment"], config_to_remove["schema"])
            os.remove(path)

            del config["values"][config_name]

            ConfigHandler.write_temporary_config(project_path, config)
            Logger.info("Configuration `{0}` removed.".format(config_name))

    @staticmethod
    def get_current_config(project_path):
        config = ConfigHandler.load_temporary_config_from_path(project_path)
        return config.get("current", None)

    @staticmethod
    def use_composefile_configuration(project_path, config_name):
        """
        Use a composefile from a known configuration.
        Set it at .docker-compose.yml.
        """
        config = ConfigHandler.get_known_configuration(
            project_path, config_name)

        path = ConfigHandler.get_composefile_path(
            project_path, config["namespace"], config["environment"], config["schema"])

        if not os.path.exists(path):
            Logger.error(
                "Missing composefile for configuration `{0}`".format(config_name))

        shutil.copyfile(path, ".docker-compose.yml")

        ConfigHandler.set_current_config(project_path, config_name)

    @staticmethod
    def write_temporary_config(project_path, content):
        """
        Write a temporary config file.
        """
        project_file_path = os.path.join(
            project_path, ConfigHandler.TEMPORARY_FILE_NAME)

        with codecs.open(project_file_path, encoding="utf-8", mode="wt") as handle:
            handle.write(yaml_utils.ordered_dump(content))

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
