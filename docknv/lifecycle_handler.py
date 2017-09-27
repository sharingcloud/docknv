"""docknv machines and schema lifecycle handling."""

import os
import sys

from docknv.logger import Logger

from docknv.docker_wrapper import exec_compose, exec_compose_pretty, get_docker_container


def lifecycle_get_machine_name(machine_name, environment_name=None):
    """
    Get docker container name.

    :param machine_name     Machine name (str)
    :param environment_name Environment name (str?) (default: None)
    :return Machine name (str)
    """
    return "{0}_{1}".format(environment_name, machine_name) if environment_name else machine_name

# SCHEMA FUNCTIONS ###############


def lifecycle_schema_build(project_path, no_cache=False, push_to_registry=True):
    """
    Build a schema.

    :param project_path         Project path (str)
    :param no_cache             Do not use cache (bool) (default: False)
    :param push_to_registry     Push to registry (bool) (default: True)
    """
    from docknv.session_handler import session_get_configuration
    from docknv.schema_handler import schema_get_configuration
    from docknv.project_handler import project_get_active_configuration, project_read

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

        no_cache_cmd = "--no-cache" if no_cache else ""
        exec_compose(
            project_path, ["build", service_name, no_cache_cmd])

        if push_to_registry:
            exec_compose(
                project_path, ["push", service_name])


def lifecycle_schema_start(project_path, foreground=False):
    """
    Start a schema.

    :param project_path     Project path (str)
    :param foreground       Start in foreground (bool) (default: False)
    """
    command = ["up"]
    if not foreground:
        command.append("-d")

    exec_compose_pretty(project_path, command)


def lifecycle_schema_stop(project_path):
    """
    Stop a schema.

    :param project_path     Project path (str)
    """
    exec_compose_pretty(project_path, ["down"])


def lifecycle_schema_ps(project_path):
    """
    Check processes of a schema.

    :param project_path     Project path (str)
    """
    exec_compose_pretty(project_path, ["ps"])


def lifecycle_schema_restart(project_path, force=False):
    """
    Restart a schema.

    :param project_path     Project path (str)
    """
    if not force:
        exec_compose_pretty(project_path, ["restart"])
    else:
        lifecycle_schema_stop(project_path)
        lifecycle_schema_start(project_path)

# BUNDLE FUNCTIONS ##############


def lifecycle_bundle_stop(project_path, config_names):
    """
    Stop multiple configurations.

    :param project_path     Project path (str)
    :param config_names     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_stop(project_path)


def lifecycle_bundle_start(project_path, config_names):
    """
    Start multiple configurations.

    :param project_path     Project path (str)
    :param config_names     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_start(project_path)


def lifecycle_bundle_restart(project_path, config_names, force=False):
    """
    Restart multiple configurations.

    :param project_path     Project path (str)
    :param config_names     Config names (iterable)
    :param force            Force restart (bool) (default: False)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_restart(project_path, force)


def lifecycle_bundle_ps(project_path, config_names):
    """
    Check processes for multiple configurations.

    :param project_path     Project path (str)
    :param config_names     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_ps(project_path)


def lifecycle_bundle_build(project_path, config_names, no_cache=False, push_to_registry=True):
    """
    Build multiple configurations.

    :param project_path         Project path (str)
    :param config_names         Config names (iterable)
    :param no_cache             Do not use cache (bool) (default: False)
    :param push_to_registry     Push to registry (bool) (default: True)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            lifecycle_schema_build(project_path, no_cache, push_to_registry)

# MACHINE FUNCTIONS #############


def lifecycle_machine_build(project_path, machine_name, no_cache=False, push_to_registry=True, environment_name=None):
    """
    Build a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param no_cache             Do not use cache (bool) (default: False)
    :param push_to_registry     Push to registry (bool) (default: True)
    :param environment_name     Environment name (str?) (default: None)
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
    Stop a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    exec_compose_pretty(project_path, ["stop", machine_name])


def lifecycle_machine_start(project_path, machine_name, environment_name=None):
    """
    Start a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    exec_compose_pretty(project_path, ["start", machine_name])


def lifecycle_machine_shell(project_path, machine_name, shell_path="/bin/bash", environment_name=None, create=False):
    """
    Execute a shell on a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param shell_path           Shell path (str) (default: /bin/bash)
    :param environment_name     Environment name (str?) (default: None)
    :param create               Create the container (bool) (default: False)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)

    if create:
        lifecycle_machine_run(
            project_path, machine_name, shell_path, environment_name)
    else:
        lifecycle_machine_exec(
            project_path, machine_name, shell_path, False, False)


def lifecycle_machine_daemon(project_path, machine_name, command=None, environment_name=None):
    """
    Execute a process in background for a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param command              Command (str)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    exec_compose_pretty(
        project_path, ["run", "--service-ports", "-d", machine_name, command])


def lifecycle_machine_restart(project_path, machine_name, force=False, environment_name=None):
    """
    Restart a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param force                Force restart (bool) (default: False)
    :param environment_name     Environment name (str?) (default: None)
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
    Run a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param command              Command (str?) (default: None)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    exec_compose(
        project_path, ["run", "--service-ports", machine_name, command])


def lifecycle_machine_push(project_path, machine_name, host_path, container_path, environment_name=None):
    """
    Push a file to a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param host_path            Host path (str)
    :param container_path       Container path (str)
    :param environment_name     Environment name (str?) (default: None)
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
    Pull a file from a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param container_path       Container path (str)
    :param host_path            Host path (str)
    :param environment_name     Environment name (str?) (default: None)
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


def lifecycle_machine_exec(project_path, machine_name, command=None, no_tty=False, return_code=False,
                           environment_name=None):
    """
    Execute a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param command              Command (str?) (default: None)
    :param no_tty               Do not use TTY (bool) (default: False)
    :param return_code          Handle return code (bool) (default: False)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        code = os.system("docker exec {2} {0} {1}".format(container, command, "-ti" if not no_tty else ""))
        if return_code:
            sys.exit(os.WEXITSTATUS(code))


def lifecycle_machine_exec_multiple(project_path, machine_name, commands=None, no_tty=False, return_code=False,
                                    environment_name=None):
    """
    Execute multiple commands on a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param commands             Commands (iterable) (default: None)
    :param no_tty               Do not use TTY (bool) (default: False)
    :param return_code          Handle return code (bool) (default: False)
    :param environment_name     Environment name (str?) (default: None)
    """
    commands = commands if commands else [""]
    machine_name = lifecycle_get_machine_name(machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        code = 0
        for command in commands:
            code = os.system("docker exec {2} {0} {1}".format(container, command, "-ti" if not no_tty else ""))
        if return_code:
            sys.exit(os.WEXITSTATUS(code))


def lifecycle_machine_logs(project_path, machine_name, tail=0, follow=False, environment_name=None):
    """
    Get logs from a machine.

    :param project_path         Project path (str)
    :param machine_name         Machine name (str)
    :param tail                 Tail lines (int) (default: 0)
    :param follow               Follow logs (bool) (default: False)
    :param environment_name     Environment name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(
        machine_name, environment_name)
    container = get_docker_container(project_path, machine_name)
    if not container:
        Logger.error("Machine `{0}` is not running.".format(
            machine_name), crash=False)
    else:
        cmd = "docker logs {0}".format(container)
        if follow:
            cmd = "{0} -f".format(cmd)
        if tail != 0:
            cmd = "{0} --tail {1}".format(cmd, tail)

        os.system(cmd)


def lifecycle_volume_list(project_path):
    """
    List volumes.

    :param project_path     Project path (str)
    """
    from docknv.project_handler import project_get_name

    Logger.info("Listing volumes...")

    project_name = project_get_name(project_path)
    os.system("docker volume list | grep -i {0}".format(project_name))


def lifecycle_volume_remove(project_path, volume_name):
    """
    Remove a volume.

    :param project_path     Project path (str)
    :param volume_name      Volume name (str)
    """
    from docknv.project_handler import project_get_name

    Logger.info("Removing volume `{0}`".format(volume_name))

    project_name = project_get_name(project_path)
    os.system("docker volume rm {0}_{1}".format(project_name, volume_name))


def lifecycle_registry_start(path):
    """
    Start a registry.

    :param path     Registry path (str)
    """
    Logger.info("Starting registry... {0}".format(path))

    cmd = "docker run -d -p 5000:5000 {0} --restart=always --name registry registry:2"
    if path:
        cmd = cmd.format("-v {0}:/var/lib/registry".format(path))
    else:
        cmd = cmd.format("")

    os.system(cmd)


def lifecycle_registry_stop():
    """Stop a registry."""
    os.system("docker stop registry && docker rm registry")
