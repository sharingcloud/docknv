"""Database methods."""

import os


DATABASE_FILE_NAME = ".docknv.yml"


def database_get_config_path(project_path):
    """
    Get configuration path from project path.

    :param project_path:    Project path
    :rtype: Configuration path
    """
    return os.path.join(project_path, ".docknv")


def database_get_database_path(project_path):
    """
    Get database path from project path.

    :param project_path:    Project path
    :rtype: Path to database file.
    """
    return os.path.join(
        database_get_config_path(project_path), DATABASE_FILE_NAME
    )
