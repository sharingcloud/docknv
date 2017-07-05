"""
Project handler
"""

import os


def get_project_name(project_path):
    """
    Get project name from path.
    """

    return os.path.basename(os.path.abspath(project_path)).lower()


def get_composefile_path(project_path, namespace, environment, schema):
    """
    Generate a composefile path.
    """
    return os.path.join(project_path, "data", "local", namespace, environment, "composefiles", schema, "docker-compose.yml")
