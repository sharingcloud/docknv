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
        return os.geteuid() == 0

    @staticmethod
    def get_user_id():
        return os.geteuid()

    @staticmethod
    def get_user_config_path():
        return os.path.expanduser("~/.docknv")

    @staticmethod
    def get_user_project_config_path(project_name):
        return os.path.join(MultiUserHandler.get_user_config_path(), project_name)

    @staticmethod
    def get_user_project_file(project_name, path_to_file):
        return os.path.join(MultiUserHandler.get_user_project_config_path(project_name), path_to_file)

    @staticmethod
    def create_user_project_config(project_name, config):
        user_config_path = MultiUserHandler.get_user_config_path()
        user_project_config_path = MultiUserHandler.get_user_project_config_path(
            project_name)

        MultiUserHandler.ensure_config_path_exists(project_name)

        return

    @staticmethod
    def ensure_config_path_exists(project_name):
        user_config_path = MultiUserHandler.get_user_config_path()
        user_project_config_path = MultiUserHandler.get_user_project_config_path(
            project_name)

        if not os.path.exists(user_config_path):
            os.makedirs(user_config_path)
        if not os.path.exists(user_project_config_path):
            os.makedirs(user_project_config_path)

    @staticmethod
    def get_current_config(project_name):
        config_path = os.path.join(
            MultiUserHandler.get_user_project_config_path(project_name), "docknv.yml")
        MultiUserHandler.ensure_config_path_exists(project_name)

        content = None
        if os.path.exists(config_path):
            with open(config_path, mode="rt") as handle:
                content = yaml_utils.ordered_load(handle.read())

        return content["current"] if content else None

    @staticmethod
    def copy_file_to_user_config_path(project_name, path_to_file):
        MultiUserHandler.ensure_config_path_exists(project_name)

        config_path = MultiUserHandler.get_user_project_config_path(
            project_name)
        file_name = os.path.basename(path_to_file)

        shutil.copyfile(path_to_file, os.path.join(config_path, file_name))

    @staticmethod
    def set_current_config(project_name, config_name):
        config_path = os.path.join(
            MultiUserHandler.get_user_project_config_path(project_name), "docknv.yml")
        MultiUserHandler.ensure_config_path_exists(project_name)

        config = {"current": config_name}
        with open(config_path, mode="wt") as handle:
            handle.write(yaml_utils.ordered_dump(config))

    @staticmethod
    @contextmanager
    def temporary_copy_file(project_name, path_to_file):
        path = MultiUserHandler.get_user_project_file(
            project_name, path_to_file)

        generated_file_name = ".{0}.{1}".format(
            MultiUserHandler.get_user_id(), os.path.basename(path))
        shutil.copyfile(path, generated_file_name)

        yield generated_file_name

        os.remove(generated_file_name)
