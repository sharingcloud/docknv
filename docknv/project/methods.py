"""Project methods."""

import os

CONFIG_FILE_NAME = "config.yml"


def project_get_config_path(project_path):
    """
    Get config path.

    :param project_path:    Project path
    """
    return os.path.join(project_path, CONFIG_FILE_NAME)


def project_is_valid(project_path):
    """
    Check if a project is valid.

    :param project_path:    Project path
    :rtype: True/False
    """
    return os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME))
