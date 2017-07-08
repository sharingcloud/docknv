"""
Handle multiple users
"""

import os
import shutil
from contextlib import contextmanager

from docknv import yaml_utils


class MultiUserHandler(object):
    """
    Handle multiple users
    """

    @staticmethod
    def is_user_root():
        """
        Check if the user is root
        :return: Is root ?
        """

        return os.geteuid() == 0

    @staticmethod
    def get_user_id():
        """
        Return the user ID
        :return: User ID
        """

        try:
            os.geteuid()
        except Exception:
            import getpass
            return getpass.getuser()
        
        return os.geteuid()

    @staticmethod
    def get_user_config_path():
        """
        :return: The docknv user config path 
        """
        return os.path.expanduser("~/.docknv")

    @staticmethod
    def get_user_project_config_path(project_name):
        """
        :param project_name: Project name 
        :return: The docknv project config path
        """
        return os.path.join(MultiUserHandler.get_user_config_path(), project_name)

    @staticmethod
    def get_user_project_file(project_name, path_to_file):
        """
        :param project_name: Project name 
        :param path_to_file: Path to file
        :return: The docknv project config path to file
        """
        return os.path.join(MultiUserHandler.get_user_project_config_path(project_name), path_to_file)

    @staticmethod
    def create_user_project_config(project_name, config):
        """
        Create a docknv config path for a project
        
        :param project_name: Project name 
        :param config: Config
        """
        user_config_path = MultiUserHandler.get_user_config_path()
        user_project_config_path = MultiUserHandler.get_user_project_config_path(
            project_name)

        MultiUserHandler.ensure_config_path_exists(project_name)

    @staticmethod
    def ensure_config_path_exists(project_name):
        """
        Ensure the config path existence.
        :param project_name: 
        :return: 
        """
        user_config_path = MultiUserHandler.get_user_config_path()
        user_project_config_path = MultiUserHandler.get_user_project_config_path(
            project_name)

        if not os.path.exists(user_config_path):
            os.makedirs(user_config_path)
        if not os.path.exists(user_project_config_path):
            os.makedirs(user_project_config_path)

    @staticmethod
    def get_current_configuration(project_name):
        """
        Get the current user configuration.
        :param project_name: Project name
        """
        config_path = os.path.join(
            MultiUserHandler.get_user_project_config_path(project_name), "docknv.yml")
        MultiUserHandler.ensure_config_path_exists(project_name)

        content = None
        if os.path.exists(config_path):
            with open(config_path, mode="rt") as handle:
                content = yaml_utils.ordered_load(handle.read())

        return content["current"] if content else None

    @staticmethod
    def set_current_configuration(project_name, config_name):
        """
        Set the current user configuration.
        :param project_name: Project name
        :param config_name: Configuration name
        """
        config_path = os.path.join(
            MultiUserHandler.get_user_project_config_path(project_name), "docknv.yml")
        MultiUserHandler.ensure_config_path_exists(project_name)

        config = {"current": config_name}
        with open(config_path, mode="wt") as handle:
            handle.write(yaml_utils.ordered_dump(config))

    @staticmethod
    def copy_file_to_user_config_path(project_name, path_to_file):
        """
        Copy file to the user config path.
        :param project_name: Project name
        :param path_to_file: Path to file
        """
        MultiUserHandler.ensure_config_path_exists(project_name)

        config_path = MultiUserHandler.get_user_project_config_path(
            project_name)
        file_name = os.path.basename(path_to_file)

        shutil.copyfile(path_to_file, os.path.join(config_path, file_name))

    @staticmethod
    @contextmanager
    def temporary_copy_file(project_name, path_to_file):
        """
        Make a temporary copy of a user config file.
        :param project_name: Project name
        :param path_to_file: Path to file
        """
        path = MultiUserHandler.get_user_project_file(
            project_name, path_to_file)

        generated_file_name = ".{0}.{1}".format(
            MultiUserHandler.get_user_id(), os.path.basename(path))
        shutil.copyfile(path, generated_file_name)

        yield generated_file_name

        os.remove(generated_file_name)
