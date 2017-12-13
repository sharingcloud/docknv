"""Image handler."""

from __future__ import unicode_literals

import os

from docknv.utils.ioutils import io_open


def image_check_dockerfile(project_path, image_name):
    """
    Check if a Dockerfile image exist.

    :param project_path:    Project path (str)
    :param image_name:      Image name (str)
    :rtype: True/False
    """
    env_path = image_get_dockerfile_path(project_path, image_name)
    return os.path.exists(env_path)


def image_get_dockerfile_path(project_path, image_name):
    """
    Get a Dockerfile image path.

    :param project_path:    Project path (str)
    :param image_name:      Image name (str)
    :rtype: Dockerfile path (str)
    """
    return os.path.join(project_path, "images", image_name, "Dockerfile")


def image_load_in_memory(project_path, image_name):
    """
    Load a Dockerfile image in memory.

    :param project_path:    Project path (str)
    :param image_name:      Image name (str)
    :rtype: File content (str)
    """
    if not image_check_dockerfile(project_path, image_name):
        return None

    filepath = image_get_dockerfile_path(project_path, image_name)
    with io_open(filepath, encoding="utf-8", mode="rt") as handle:
        return handle.read()
