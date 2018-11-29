"""Lifecycle methods."""

from docknv.database import MissingActiveConfiguration
from docknv.wrapper import exec_compose, exec_docker


def lifecycle_get_configs(project, config_list=None):
    """
    Get configs from project.

    If list is empty, get current config.

    :param project:     Project
    :param config_list: Config name list (list?)
    """
    config_list = config_list or []
    database = project.database
    session = project.session
    if len(config_list) == 0:
        current_config = session.get_current_configuration()
        if current_config is None:
            raise MissingActiveConfiguration()

        return [database.get_configuration(current_config)]

    return [database.get_configuration(config) for config in config_list]


def lifecycle_get_config(project, config_name=None):
    """
    Get config from project.

    If config name is none, get current config.

    :param project:     Project
    :param config_name: Config name (str?)
    """
    config_name = [config_name] if config_name else None
    return lifecycle_get_configs(project, config_name)[0]


def lifecycle_get_service_name(project, service_name):
    """
    Get service name from project, applying namespace if necessary.

    :param project:         Project
    :param service_name:    Service name (str)
    """
    config = lifecycle_get_config(project)
    if config.namespace:
        return f"{config.namespace}_{service_name}"
    return service_name


def lifecycle_compose_command_on_configs(project, configs, args,
                                         dry_run=False):
    """
    Execute a compose command on configs.

    :param project: Project
    :param configs: Configuration name list (list)
    :param args:    Arguments
    :param dry_run: Dry run? (bool) (default: False)
    """
    project_path = project.project_path
    configs = lifecycle_get_configs(project, configs)

    for config in configs:
        composefile = config.get_composefile_path()
        exec_compose(project_path, composefile, args, dry_run=dry_run)


def lifecycle_compose_command_on_current_config(project, args, dry_run=False):
    """
    Execute a compose command on current config.

    :param project: Project
    :param args:    Arguments
    :param dry_run: Dry run? (bool) (default: False)
    """
    project_path = project.project_path
    config = lifecycle_get_config(project)

    composefile = config.get_composefile_path()
    exec_compose(project_path, composefile, args, dry_run=dry_run)


def lifecycle_get_container_from_service(project, config, service):
    """
    Get container from service.

    :param project: Project
    :param config:  Configuration
    :param service: Service name (str)
    """
    name = project.project_name
    namespace = config.namespace
    if namespace:
        return f"{name}_{namespace}_{service}_1"
    else:
        return f"{name}_{service}_1"


def lifecycle_docker_command_on_service(project, service, args, add_name=True,
                                        dry_run=False):
    """
    Execute Docker command on service.

    :param project:     Project
    :param service:     Service name (str)
    :param args:        Arguments
    :param add_name:    Add name in command (bool) (default: True)
    :param dry_run: Dry run? (bool) (default: False)
    """
    active_config = lifecycle_get_config(project)

    # Get container from service
    container = lifecycle_get_container_from_service(
        project, active_config, service)

    args = [x for x in args]
    if add_name:
        args += [container]

    exec_docker(project.project_path, args, dry_run=dry_run)
