"""
docknv machines and schema lifecycle handling
"""

import os
import sys

from docknv.logger import Logger

from docknv.v2.docker_wrapper import exec_compose, exec_compose_pretty, get_container
from docknv.v2.project_handler import get_project_name


class LifecycleHandler(object):
    """
    docknv machines and schema lifecycle handling
    """

    @staticmethod
    def get_machine_name(machine_name, environment_name=None):
        return "{0}_{1}".format(environment_name, machine_name) if environment_name else machine_name

    # SCHEMA FUNCTIONS ###############

    @staticmethod
    def build_schema(project_path, push_to_registry=False):
        """
        Build a schema
        """

        # Get services from current config
        from docknv.v2.config_handler import ConfigHandler
        from docknv.v2.schema_handler import SchemaHandler

        current_config = ConfigHandler.get_active_configuration(project_path)
        current_config_data = ConfigHandler.get_configuration(
            project_path, current_config)

        config_data = ConfigHandler.read_docknv_configuration(project_path)
        schema_config = SchemaHandler.get_schema_configuration(
            config_data, current_config_data["schema"])

        namespace = current_config_data["namespace"]
        for service in schema_config["config"]["services"]:
            service_name = "{0}_{1}".format(
                namespace, service) if namespace != "default" else service

            exec_compose(
                project_path, ["build", service_name])
            exec_compose(
                project_path, ["push", service_name])

    @staticmethod
    def start_schema(project_path, foreground=False):
        """
        Start a schema
        """

        command = ["up"]
        if not foreground:
            command.append("-d")

        exec_compose_pretty(project_path, command)

    @staticmethod
    def stop_schema(project_path):
        """
        Stop a schema
        """
        exec_compose_pretty(project_path, ["down"])

    @staticmethod
    def ps_schema(project_path):
        """
        Check processes of a schema
        """
        exec_compose_pretty(project_path, ["ps"])

    @staticmethod
    def restart_schema(project_path, force=False):
        """
        Restart a schema
        """

        if not force:
            exec_compose_pretty(project_path, ["restart"])
        else:
            LifecycleHandler.stop_schema(project_path)
            LifecycleHandler.start_schema(project_path)

    # BUNDLE FUNCTIONS ##############

    @staticmethod
    def stop_bundle(project_path, config_names):
        from docknv.v2.config_handler import ConfigHandler

        for config_name in config_names:
            with ConfigHandler.using_temporary_configuration(project_path, config_name):
                LifecycleHandler.stop_schema(project_path)

    @staticmethod
    def start_bundle(project_path, config_names):
        from docknv.v2.config_handler import ConfigHandler

        for config_name in config_names:
            with ConfigHandler.using_temporary_configuration(project_path, config_name):
                LifecycleHandler.start_schema(project_path)

    @staticmethod
    def restart_bundle(project_path, config_names, force=False):
        from docknv.v2.config_handler import ConfigHandler

        for config_name in config_names:
            with ConfigHandler.using_temporary_configuration(project_path, config_name):
                LifecycleHandler.restart_schema(project_path, force)

    @staticmethod
    def ps_bundle(project_path, config_names):
        from docknv.v2.config_handler import ConfigHandler

        for config_name in config_names:
            with ConfigHandler.using_temporary_configuration(project_path, config_name):
                LifecycleHandler.ps_schema(project_path)

    # MACHINE FUNCTIONS #############

    @staticmethod
    def build_machine(project_path, machine_name, push_to_registry=False, no_cache=False, environment_name=None):
        """
        Build a machine
        """

        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)

        if no_cache:
            args = ["build", "--no-cache", machine_name]
        else:
            args = ["build", machine_name]

        exec_compose(project_path, args)

        if push_to_registry:
            exec_compose(
                project_path, ["push", machine_name])

    @staticmethod
    def stop_machine(project_path, machine_name, environment_name=None):
        """
        Stop a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)

        exec_compose_pretty(project_path, ["stop", machine_name])

    @staticmethod
    def start_machine(project_path, machine_name, environment_name=None):
        """
        Start a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)

        exec_compose_pretty(project_path, ["start", machine_name])

    @staticmethod
    def shell_machine(project_path, machine_name, shell_path="/bin/bash", environment_name=None):
        """
        Execute a shell on a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        LifecycleHandler.exec_machine(
            project_path, machine_name, shell_path, False, False)

    @staticmethod
    def daemon_machine(project_path, machine_name, command=None, environment_name=None):
        """
        Execute a process in background for a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        exec_compose_pretty(
            project_path, ["run", "--service-ports", "-d", machine_name, command])

    @staticmethod
    def restart_machine(project_path, machine_name, force=False, environment_name=None):
        """
        Restart a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        if force:
            LifecycleHandler.stop_machine(project_path, machine_name)
            LifecycleHandler.start_machine(project_path, machine_name)
        else:
            exec_compose_pretty(
                project_path, ["restart", machine_name])

    @staticmethod
    def run_machine(project_path, machine_name, command=None, environment_name=None):
        """
        Run a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        exec_compose(
            project_path, ["run", "--service-ports", machine_name, command])

    @staticmethod
    def push_machine(project_path, machine_name, host_path, container_path, environment_name=None):
        """
        Push a file to a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        container = get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            Logger.info("Copying file from host to `{0}`: `{1}` => `{2}".format(
                machine_name, host_path, container_path))
            os.system("docker cp {0} {1}:{2}".format(
                host_path, container, container_path))

    @staticmethod
    def pull_machine(project_path, machine_name, container_path, host_path, environment_name=None):
        """
        Pull a file from a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        container = get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            Logger.info("Copying file from `{0}`: `{1}` => `{2}".format(
                machine_name, container_path, host_path))
            os.system("docker cp {0}:{1} {2}".format(
                container, container_path, host_path))

    @staticmethod
    def exec_machine(project_path, machine_name, command=None, no_tty=False, return_code=False, environment_name=None):
        """
        Execute a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        container = get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            code = os.system("docker exec {2} {0} {1}".format(
                container, command, "-ti" if not no_tty else ""))
            if return_code:
                sys.exit(os.WEXITSTATUS(code))

    @staticmethod
    def logs_machine(project_path, machine_name, tail=0, environment_name=None):
        """
        Get logs from a machine
        """
        machine_name = LifecycleHandler.get_machine_name(
            machine_name, environment_name)
        container = get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            cmd = "docker logs {0}".format(container)
            if tail != 0:
                cmd = "{0} --tail {1}".format(cmd, tail)

            os.system(cmd)

    @staticmethod
    def list_volumes(project_path):
        """
        List volumes
        """

        Logger.info("Listing volumes...")

        project_name = get_project_name(project_path)
        os.system("docker volume list | grep -i {0}".format(project_name))

    @staticmethod
    def remove_volume(project_path, volume_name):
        """
        Remove a volume
        """

        Logger.info("Removing volume `{0}`".format(volume_name))

        project_name = get_project_name(project_path)
        os.system("docker volume rm {0}_{1}".format(project_name, volume_name))

    @staticmethod
    def start_registry(path):
        """
        Start a registry
        """
        Logger.info("Starting registry... {0}".format(path))

        cmd = "docker run -d -p 5000:5000 {0} --restart=always --name registry registry:2"
        if path:
            cmd = cmd.format("-v {0}:/var/lib/registry".format(path))
        else:
            cmd = cmd.format("")

        os.system(cmd)

    @staticmethod
    def stop_registry():
        """
        Stop a registry
        """

        os.system("docker stop registry && docker rm registry")
