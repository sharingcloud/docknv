"""Lifecycle models."""

import copy
import shlex

from docknv.database import Configuration
from docknv.user import user_get_username
from docknv.wrapper import StoppedCommandExecution

from .methods import (
    lifecycle_compose_command_on_configs,
    lifecycle_compose_command_on_current_config,
    lifecycle_docker_command_on_service,
    lifecycle_get_container_from_service,
    lifecycle_get_config,
    lifecycle_get_service_name,
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
        service_name = lifecycle_get_service_name(self.project, service_name)
        lifecycle_compose_command_on_current_config(
            self.project, ["start", service_name], dry_run=dry_run
        )

    def stop(self, service_name, dry_run=False):
        """
        Stop service.

        :param service_name:    Service name (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)
        lifecycle_compose_command_on_current_config(
            self.project, ["stop", service_name], dry_run=dry_run
        )

    def restart(self, service_name, force=False, dry_run=False):
        """
        Restart service.

        :param service_name:    Service name (str)
        :param force:           Force? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)
        if force:
            lifecycle_compose_command_on_current_config(
                self.project, ["stop", service_name], dry_run=dry_run
            )
            lifecycle_compose_command_on_current_config(
                self.project, ["rm", "-f", service_name], dry_run=dry_run
            )
            lifecycle_compose_command_on_current_config(
                self.project, ["up", "-d", service_name], dry_run=dry_run
            )
        else:
            lifecycle_compose_command_on_current_config(
                self.project, ["restart", service_name], dry_run=dry_run
            )

    def run(
        self, service_name, cmd, daemon=False, env_vars=None, dry_run=False
    ):
        """
        Create container with command.

        :param service_name:    Service name (str)
        :param cmd:             Command (str)
        :param daemon:          Daemon mode? (bool) (default: False)
        :param env_vars:        Env vars (dict) (default: None)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        env_vars = env_vars or {}
        service_name = lifecycle_get_service_name(self.project, service_name)
        more_args = ["--use-aliases", "--service-ports", "--rm"]
        if daemon:
            more_args.remove("--rm")
            more_args += ["-d"]
        for key, value in env_vars.items():
            more_args += ["-e", f"{key}={value}"]

        lifecycle_compose_command_on_current_config(
            self.project,
            ["run", *more_args, service_name, *shlex.split(cmd)],
            dry_run=dry_run,
        )

    def execute(self, service_name, cmds=None, no_tty=False, dry_run=False):
        """
        Execute command on service.

        :param service_name:    Service name (str)
        :param cmds:            Commands (list?)
        :param no_tty:          Disable TTY? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)
        cmds = cmds or []

        args = []
        if no_tty:
            args += ["-T"]

        for cmd in cmds:
            lifecycle_compose_command_on_current_config(
                self.project,
                ["exec", *args, service_name, *shlex.split(cmd)],
                dry_run=dry_run,
            )

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
        args = []
        if tail != 0:
            args += ["--tail", tail]
        if follow:
            args += ["-f"]

        service_name = lifecycle_get_service_name(self.project, service_name)

        try:
            lifecycle_compose_command_on_current_config(
                self.project, ["logs", *args, service_name], dry_run=dry_run
            )
        except StoppedCommandExecution as exc:
            print(exc)

    def attach(self, service_name, dry_run=False):
        """
        Attach to a running container.

        :param service_name:    Service name (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)
        lifecycle_compose_command_on_current_config(
            self.project, ["attach", service_name], dry_run=dry_run
        )

    def build(
        self, service_name, build_args=None, no_cache=False, dry_run=False
    ):
        """
        Build a service.

        :param service_name:    Service name (str)
        :param build_args:      Build args (list?)
        :param no_cache:        No cache? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)
        args = []
        build_args = build_args or []
        for x in build_args:
            args.append("--build-arg")
            args.append(x)

        if no_cache:
            args.append("--no-cache")

        lifecycle_compose_command_on_current_config(
            self.project, ["build", *args, service_name], dry_run=dry_run
        )

    def push(self, service_name, host_path, container_path, dry_run=False):
        """
        Push a file from host to container.

        :param service_name:    Service name (str)
        :param host_path:       Host path (str)
        :param container_path:  Container path (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)

        # Get container from service
        container = lifecycle_get_container_from_service(
            self.project, service_name
        )

        lifecycle_docker_command_on_service(
            self.project,
            service_name,
            ["cp", host_path, f"{container}:{container_path}"],
            add_name=False,
            dry_run=dry_run,
        )

    def pull(self, service_name, container_path, host_path, dry_run=False):
        """
        Pull a file from host to container.

        :param service_name:    Service name (str)
        :param container_path:  Container path (str)
        :param host_path:       Host path (str)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        service_name = lifecycle_get_service_name(self.project, service_name)

        # Get container from service
        container = lifecycle_get_container_from_service(
            self.project, service_name
        )

        lifecycle_docker_command_on_service(
            self.project,
            service_name,
            ["cp", f"{container}:{container_path}", host_path],
            add_name=False,
            dry_run=dry_run,
        )


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
            self.project, config_names, ["up", "-d"], dry_run=dry_run
        )

    def stop(self, config_names=None, dry_run=False):
        """
        Stop configurations.

        :param config_names:    Config names (list)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["stop"], dry_run=dry_run
        )
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["rm", "-f"], dry_run=dry_run
        )

    def restart(self, config_names=None, force=False, dry_run=False):
        """
        Restart configurations.

        :param config_names:    Config names (list)
        :param force:           Force restart? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        if force:
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["stop"], dry_run=dry_run
            )
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["rm", "-f"], dry_run=dry_run
            )
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["up", "-d"], dry_run=dry_run
            )
        else:
            lifecycle_compose_command_on_configs(
                self.project, config_names, ["restart"], dry_run=dry_run
            )

    def create(
        self,
        name,
        environment="default",
        schemas=None,
        services=None,
        volumes=None,
        networks=None,
        namespace=None,
    ):
        """
        Create configuration.

        :param name:        Name (str)
        :param environment: Environment name (str)
        :param schemas:     Schemas (list)
        :param services:    Services (list)
        :param volumes:     Volumes (list)
        :param networks:    Networks (list)
        :param namespace:   Namespace (str?)
        """
        database = self.project.database

        # Resolve schemas
        schemas = schemas or []
        services, volumes, networks = self.project.schemas.resolve_schemas(
            schemas, services, volumes, networks
        )

        # Create configuration
        config = Configuration(
            database,
            name,
            user_get_username(),
            environment,
            services,
            volumes,
            networks,
            namespace,
        )
        database.create_configuration(config)
        database.save()

        self.project.session.set_current_configuration(name)
        self.project.session.save()

    def update(
        self,
        name=None,
        environment=None,
        schemas=None,
        services=None,
        volumes=None,
        networks=None,
        namespace=None,
        restart=False,
        dry_run=False,
    ):
        """
        Update configurations.

        :param name:        Name (str?)
        :param environment: Environment name (str)
        :param schemas:     Schemas (list)
        :param services:    Services (list)
        :param volumes:     Volumes (list)
        :param networks:    Networks (list)
        :param namespace:   Namespace (str?)
        :param restart:     Restart? (bool) (default: False)
        :param dry_run:     Dry run? (bool) (default: False)
        """
        database = self.project.database
        config = lifecycle_get_config(self.project, name)

        # New elements
        new_services = None
        new_volumes = None
        new_networks = None

        if restart:
            self.stop(name, dry_run=dry_run)

        if environment is not None:
            config.environment = environment
        if services is not None:
            new_services = copy.deepcopy(services)
        if volumes is not None:
            new_volumes = copy.deepcopy(volumes)
        if networks is not None:
            new_networks = copy.deepcopy(networks)
        if schemas is not None:
            rs = self.project.schemas.resolve_schemas
            new_services, new_volumes, new_networks = rs(
                schemas, new_services, new_volumes, new_networks
            )
        if namespace is not None:
            if namespace == "":
                config.namespace = None
            else:
                config.namespace = namespace

        if new_services is not None:
            config.services = new_services
        if new_volumes is not None:
            config.volumes = new_volumes
        if new_networks is not None:
            config.networks = new_networks

        database.update_configuration(config)
        database.save()

        if restart:
            self.start(name, dry_run=dry_run)

    def build(self, name=None, build_args=None, no_cache=False, dry_run=False):
        """
        Build configurations.

        :param name:            Config name (str?)
        :param build_args:      Build args (list)
        :param no_cache:        No cache? (bool) (default: False)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        args = []
        name = [name] if name else None
        build_args = build_args or []

        for x in build_args:
            args.append("--build-arg")
            args.append(x)

        if no_cache:
            args.append("--no-cache")

        lifecycle_compose_command_on_configs(
            self.project, name, ["build", *args], dry_run=dry_run
        )

    def ps(self, config_names=None, dry_run=False):
        """
        Show running containers from configurations.

        :param config_names:    Config names (list)
        :param dry_run:         Dry run? (bool) (default: False)
        """
        lifecycle_compose_command_on_configs(
            self.project, config_names, ["ps"], dry_run=dry_run
        )


class ProjectLifecycle(object):
    """Project lifecycle."""

    def __init__(self, project):
        """Init."""
        self.project = project
        self.config = ConfigLifecycle(project)
        self.service = ServiceLifecycle(project)
