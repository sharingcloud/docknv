"""Lifecycle models."""

import copy
import shlex

from docknv.database import Configuration
from docknv.user import user_get_username

from .methods import (
    lifecycle_compose_command_on_configs,
    lifecycle_compose_command_on_current_config,
    lifecycle_docker_command_on_service,
    lifecycle_get_container_from_service,
    lifecycle_get_config,
)


class ServiceLifecycle(object):
    """Service lifecycle."""

    def __init__(self, project):
        """Init."""
        self.project = project

    def start(self, service_name, dry_run=False):
        """
        Start service.

        :param service_name:    Service name (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_current_config(
            self.project, ["start", service_name],
            dry_run=dry_run)

    def stop(self, service_name, dry_run=False):
        """
        Stop service.

        :param service_name:    Service name (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_current_config(
            self.project, ["stop", service_name],
            dry_run=dry_run)

    def restart(self, service_name, force=False, dry_run=False):
        """
        Restart service.

        :param service_name:    Service name (str)
        :param force:           Force? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        if force:
            lifecycle_compose_command_on_current_config(
                self.project, ["stop", service_name],
                dry_run=dry_run)
            lifecycle_compose_command_on_current_config(
                self.project, ["start", service_name],
                dry_run=dry_run)
        else:
            lifecycle_compose_command_on_current_config(
                self.project, ["restart", service_name],
                dry_run=dry_run)

    def run(self, service_name, command, daemon=False, dry_run=False):
        """
        Create container with command.

        :param service_name:    Service name (str)
        :param command:         Command (str)
        :param daemon:          Daemon mode? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        more_args = []
        if daemon:
            more_args += ["-d"]

        lifecycle_compose_command_on_current_config(
            self.project, ["run", service_name, *more_args, command],
            dry_run=dry_run)

    def execute(self, service_name, cmds=None, dry_run=False):
        """
        Execute command on service.

        :param service_name:    Service name (str)
        :param cmds:            Commands (list?)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        cmds = cmds or []
        for cmd in cmds:
            lifecycle_compose_command_on_current_config(
                self.project, ["exec", service_name, *shlex.split(cmd)],
                dry_run=dry_run)

    def shell(self, service_name, shell="/bin/bash", dry_run=False):
        """
        Execute shell on running container.

        :param service_name:    Service name (str)
        :param shell:           Shell executable (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        self.execute(service_name, [shell], dry_run=dry_run)

    def logs(self, service_name, tail=0, follow=False, dry_run=False):
        """
        Get logs from running container.

        :param service_name:    Service name (str)
        :param tail:            Apply tail lines (int)
        :param follow:          Follow logs (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_current_config(
            self.project, ["logs", service_name],
            dry_run=dry_run)

    def attach(self, service_name, dry_run=False):
        """
        Attach to a running container.

        :param service_name:    Service name (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_current_config(
            self.project, ["attach", service_name],
            dry_run=dry_run)

    def build(self, service_name, build_args=None, no_cache=False,
              dry_run=False):
        """
        Build a service.

        :param service_name:    Service name (str)
        :param build_args:      Build args (list?)
        :param no_cache:        No cache? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        build_args = build_args or []
        lifecycle_compose_command_on_current_config(
            self.project, ["build", service_name, *build_args],
            dry_run=dry_run)

    def push(self, service_name, host_path, container_path, dry_run=False):
        """
        Push a file from host to container.

        :param service_name:    Service name (str)
        :param host_path:       Host path (str)
        :param container_path:  Container path (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        # Get active config and container from service
        active_config = lifecycle_get_config(self.project)
        container = lifecycle_get_container_from_service(
            self.project, active_config, service_name)

        lifecycle_docker_command_on_service(
            self.project, service_name, [
                "cp", host_path, f"{container}:{container_path}"],
            add_name=False, dry_run=dry_run)

    def pull(self, service_name, container_path, host_path, dry_run=False):
        """
        Pull a file from host to container.

        :param service_name:    Service name (str)
        :param container_path:  Container path (str)
        :param host_path:       Host path (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        # Get active config and container from service
        active_config = lifecycle_get_config(self.project)
        container = lifecycle_get_container_from_service(
            self.project, active_config, service_name)

        lifecycle_docker_command_on_service(
            self.project, service_name, [
                "cp", f"{container}:{container_path}", host_path],
            add_name=False, dry_run=dry_run)


class ConfigLifecycle(object):
    """Config lifecycle."""

    def __init__(self, project):
        """Init."""
        self.project = project

    def start(self, config_names=None, dry_run=False):
        """
        Start configurations.

        :param config_names:    Config names (list)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["up", "-d"], dry_run=dry_run)

    def stop(self, config_names=None, dry_run=False):
        """
        Stop configurations.

        :param config_names:    Config names (list)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["stop"], dry_run=dry_run)
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["rm", "-f"], dry_run=dry_run)

    def restart(self, config_names=None, force=False, dry_run=False):
        """
        Restart configurations.

        :param config_names:    Config names (list)
        :param force:           Force restart? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        if force:
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["stop"], dry_run=dry_run)
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["start"], dry_run=dry_run)
        else:
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["restart"], dry_run=dry_run)

    def create(self, name, environment="default", services=None, volumes=None,
               networks=None, namespace=None):
        """
        Create configuration.

        :param name:        Name (str)
        :param environment: Environment name (str)
        :param services:    Services (list)
        :param volumes:     Volumes (list)
        :param networks:    Networks (list)
        :param namespace:   Namespace (str?)
        """
        database = self.project.database
        config = Configuration(
            database, name, user_get_username(), environment, services,
            volumes, networks, namespace)
        database.create_configuration(config)
        database.save()

        self.project.session.set_current_configuration(name)
        self.project.session.save()

    def update(self, name=None, environment=None, services=None,
               volumes=None, networks=None, namespace=None, restart=False,
               dry_run=False):
        """
        Update configurations.

        :param name:        Name (str?)
        :param environment: Environment name (str)
        :param services:    Services (list)
        :param volumes:     Volumes (list)
        :param networks:    Networks (list)
        :param namespace:   Namespace (str?)
        :param restart:     Restart? (bool) (default: False)
        :param dry_run:     Dry run? (bool) (default: False)
        """
        database = self.project.database
        config = lifecycle_get_config(self.project, name)

        if restart:
            self.stop(name, dry_run=dry_run)

        if environment is not None:
            config.environment = environment
        if services is not None:
            config.services = copy.deepcopy(services)
        if volumes is not None:
            config.volumes = copy.deepcopy(volumes)
        if networks is not None:
            config.networks = copy.deepcopy(networks)
        if namespace is not None:
            if namespace == '':
                config.namespace = None
            else:
                config.namespace = namespace

        database.update_configuration(config)
        database.save()

        if restart:
            self.start(name, dry_run=dry_run)

    def build(self, config_names=None, build_args=None, no_cache=False,
              dry_run=False):
        """
        Build configurations.

        :param config_names:    Config names (list)
        :param build_args:      Build args (list)
        :param no_cache:        No cache? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        build_args = build_args or []
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["build", *build_args],
            dry_run=dry_run)

    def ps(self, config_names=None, dry_run=False):
        """
        Show running containers from configurations.

        :param config_names:    Config names (list)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["ps"],
            dry_run=dry_run)


class ProjectLifecycle(object):
    """Project lifecycle."""

    def __init__(self, project):
        """Init."""
        self.project = project
        self.config = ConfigLifecycle(project)
        self.service = ServiceLifecycle(project)
