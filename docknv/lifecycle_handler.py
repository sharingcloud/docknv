"""
docknv machines and schema lifecycle handling
"""

import os
import sys

from docknv.logger import Logger

from docknv.docker_wrapper import exec_compose, exec_compose_pretty, get_docker_container
from docknv.project_handler import project_get_name, project_get_active_configuration, project_read, project_use_temporary_configuration
from docknv.session_handler import session_get_configuration
from docknv.schema_handler import schema_get_configuration


def lifecycle_get_machine_name(machine_name, environment_name=None):
    return "{0}_{1}".format(environment_name, machine_name) if environment_name else machine_name

# SCHEMA FUNCTIONS ###############


def lifecycle_schema_build(project_path, no_push_to_registry=False):
    """
    Build a schema
    """

    # Get services from current config

    current_config = project_get_active_configuration(project_path)
    current_config_data = session_get_configuration(
        project_path, current_config)

    config_data = project_read(project_path)
    schema_config = schema_get_configuration(
        config_data, current_config_data["schema"])

    namespace = current_config_data["namespace"]
    for service in schema_config["config"]["services"]:
        service_name = "{0}_{1}".format(
            namespace, service) if namespace != "default" else service

        exec_compose(
            project_path, ["build", service_name])
        if not no_push_to_registry:
            exec_compose(
                project_path, ["push", service_name])


def lifecycle_schema_start(project_path, foreground=False):
    """
    Start a schema
    """

    command = ["up"]
    if not foreground:
        command.append("-d")

    exec_compose_pretty(project_path, command)


def lifecycle_schema_stop(project_path):
    """
    Stop a schema
    """
    exec_compose_pretty(project_path, ["down"])


def lifecycle_schema_ps(project_path):
    """
    Check processes of a schema
    """
    exec_compose_pretty(project_path, ["ps"])


def lifecycle_schema_restart(project_path, force=False):
    """
    Restart a schema
    """

    if not force:
        exec_compose_pretty(project_path, ["restart"])
    else:
        lifecycle_schema_stop(project_path)
        lifecycle_schema_start(project_path)

# BUNDLE FUNCTIONS ##############


def lifecycle_bundle_stop(project_path, config_names):
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_stop(project_path)


def lifecycle_bundle_start(project_path, config_names):
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_start(project_path)


def lifecycle_bundle_restart(project_path, config_names, force=False):
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_restart(project_path, force)


def lifecycle_bundle_ps(project_path, config_names):
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_ps(project_path)

# MACHINE FUNCTIONS #############


def lifecycle_machine_build(project_path, machine_name, push_to_registry=False, no_cache=False, environment_name=None):
    """
    Build a machine
    """

    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    if no_cache:
        args = ["build", "--no-cache", machine_name]
    else:
        args = ["build", machine_name]

    exec_compose(project_path, args)

    if push_to_registry:
        exec_compose(
            project_path, ["push", machine_name])


def lifecycle_machine_stop(project_path, machine_name, environment_name=None):
    """
    Stop a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    exec_compose_pretty(project_path, ["stop", machine_name])


def lifecycle_machine_start(project_path, machine_name, environment_name=None):
    """
    Start a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    exec_compose_pretty(project_path, ["start", machine_name])


def lifecycle_machine_shell(project_path, machine_name, shell_path="/bin/bash", environment_name=None):
    """
    Execute a shell on a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    lifecycle_machine_exec(
        project_path, machine_name, shell_path, False, False)


def lifecycle_machine_daemon(project_path, machine_name, command=None, environment_name=None):
    """
    Execute a process in background for a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    exec_compose_pretty(
        project_path, ["run", "--service-ports", "-d", machine_name, command])


def lifecycle_machine_restart(project_path, machine_name, force=False, environment_name=None):
    """
    Restart a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    if force:
        lifecycle_machine_stop(project_path, machine_name)
        lifecycle_machine_start(project_path, machine_name)
    else:
        exec_compose_pretty(
            project_path, ["restart", machine_name])


def lifecycle_machine_run(project_path, machine_name, command=None, environment_name=None):
    """
    Run a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    exec_compose(
        project_path, ["run", "--service-ports", machine_name, command])


def lifecycle_machine_push(project_path, machine_name, host_path, container_path, environment_name=None):
    """
    Push a file to a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(
            machine_name), crash=False)
    else:
        Logger.info("Copying file from host to `{0}`: `{1}` => `{2}".format(
            machine_name, host_path, container_path))
        os.system("docker cp {0} {1}:{2}".format(
            host_path, container, container_path))


def lifecycle_machine_pull(project_path, machine_name, container_path, host_path, environment_name=None):
    """
    Pull a file from a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(
            machine_name), crash=False)
    else:
        Logger.info("Copying file from `{0}`: `{1}` => `{2}".format(
            machine_name, container_path, host_path))
        os.system("docker cp {0}:{1} {2}".format(
            container, container_path, host_path))


def lifecycle_machine_exec(project_path, machine_name, command=None, no_tty=False, return_code=False, environment_name=None):
    """
    Execute a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(
            machine_name), crash=False)
    else:
        code = os.system("docker exec {2} {0} {1}".format(
            container, command, "-ti" if not no_tty else ""))
        if return_code:
            sys.exit(os.WEXITSTATUS(code))


def lifecycle_machine_logs(project_path, machine_name, tail=0, environment_name=None):
    """
    Get logs from a machine
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(
            machine_name), crash=False)
    else:
        cmd = "docker logs {0}".format(container)
        if tail != 0:
            cmd = "{0} --tail {1}".format(cmd, tail)

        os.system(cmd)


def lifecycle_volume_list(project_path):
    """
    List volumes
    """

    Logger.info("Listing volumes...")

    project_name = project_get_name(project_path)
    os.system("docker volume list | grep -i {0}".format(project_name))


def lifecycle_volume_remove(project_path, volume_name):
    """
    Remove a volume
    """

    Logger.info("Removing volume `{0}`".format(volume_name))

    project_name = project_get_name(project_path)
    os.system("docker volume rm {0}_{1}".format(project_name, volume_name))


def lifecycle_registry_start(path):
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


def lifecycle_registry_stop():
    """
    Stop a registry
    """

    os.system("docker stop registry && docker rm registry")
