"""Dockerfile packer."""

from docknv.logger import Logger


def dockerfile_packer(project_path, service_name):
    """
    Pack a Dockerfile for a service with its associated content.

    Freeze template, static and shared content inside of a Dockerfile.

    :param project_path:     Project path (str)
    :param service_name:     Service name (str)
    """
    from docknv.project_handler import project_get_active_configuration, project_read

    # Get project data
    project_data = project_read(project_path)

    # Get current configuration
    config = project_get_active_configuration(project_path)
    if config is None:
        Logger.warn("No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
        return

    print(project_data)
    print(config)
