"""docknv machines and schema lifecycle handling."""

import shlex

from docknv.logger import Logger, Fore, Style
from docknv.docker_wrapper import (
    exec_compose, exec_compose_pretty, get_docker_container,
    exec_docker
)


def lifecycle_get_machine_name(machine_name, namespace_name=None):
    """
    Get docker container name.

    :param machine_name:     Machine name (str)
    :param namespace_name:   Namespace name (str?) (default: None)
    :rtype: Machine name (str)
    """
    return "{0}_{1}".format(namespace_name, machine_name) if namespace_name else machine_name

# SCHEMA FUNCTIONS ###############


def lifecycle_schema_build(project_path, no_cache=False, push_to_registry=True):
    """
    Build a schema.

    :param project_path:         Project path (str)
    :param no_cache:             Do not use cache (bool) (default: False)
    :param push_to_registry:     Push to registry (bool) (default: True)
    """
    from docknv.session_handler import session_get_configuration
    from docknv.schema_handler import schema_get_configuration
    from docknv.project_handler import project_get_active_configuration, project_read

    current_config = project_get_active_configuration(project_path)
    current_config_data = session_get_configuration(project_path, current_config)

    config_data = project_read(project_path)
    schema_config = schema_get_configuration(config_data, current_config_data["schema"])

    namespace = current_config_data["namespace"]
    rcode = 0
    for service in schema_config["config"]["services"]:
        service_name = "{0}_{1}".format(namespace, service) if namespace != "default" else service

        no_cache_cmd = "--no-cache" if no_cache else ""
        rcode = exec_compose_pretty(project_path, ["build", service_name, no_cache_cmd])
        if rcode != 0:
            raise RuntimeError("Build failed for service {0}.".format(service_name))

        if push_to_registry:
            rcode = exec_compose_pretty(project_path, ["push", service_name])
            if rcode != 0:
                raise RuntimeError("Push failed for service {0}.".format(service_name))

    return rcode


def lifecycle_schema_start(project_path):
    """
    Start a schema.

    :param project_path:     Project path (str)
    """
    command = ["up", "-d"]
    return exec_compose_pretty(project_path, command)


def lifecycle_schema_stop(project_path):
    """
    Stop a schema.

    :param project_path:     Project path (str)
    """
    return exec_compose_pretty(project_path, ["down"])


def lifecycle_schema_ps(project_path):
    """
    Check processes of a schema.

    :param project_path:     Project path (str)
    """
    from docknv.docker_api_wrapper import docker_ps, using_docker_client, text_ellipse
    from docknv.command_handler import command_get_context
    ctx = command_get_context(project_path)

    with using_docker_client() as client:
        ps = docker_ps(client, ctx.project_name, ctx.namespace_name)
        if len(ps) == 0:
            Logger.warn("Configuration is stopped. Run it with `docknv config start`.")
        for line in ps:
            print("{sc}{status:10}{ec} {name:40} {ports:10}".format(
                status=line["status"],
                name=text_ellipse(line["name"], 38),
                ports=line["ports"],
                sc=Fore.GREEN if line["status"] == "running" else Fore.RED,
                ec=Style.RESET_ALL
            ))


def lifecycle_schema_restart(project_path, force=False):
    """
    Restart a schema.

    :param project_path:     Project path (str)
    :param force:            Force restart (bool) (default: False)
    """
    if not force:
        return exec_compose_pretty(project_path, ["restart"])
    else:
        lifecycle_schema_stop(project_path)
        return lifecycle_schema_start(project_path)

# BUNDLE FUNCTIONS ##############


def lifecycle_bundle_stop(project_path, config_names):
    """
    Stop multiple configurations.

    :param project_path:     Project path (str)
    :param config_names:     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    code = 0
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            code = lifecycle_schema_stop(project_path)

    return code


def lifecycle_bundle_start(project_path, config_names):
    """
    Start multiple configurations.

    :param project_path:     Project path (str)
    :param config_names:     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    code = 0
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            code = lifecycle_schema_start(project_path)

    return code


def lifecycle_bundle_restart(project_path, config_names, force=False):
    """
    Restart multiple configurations.

    :param project_path:     Project path (str)
    :param config_names:     Config names (iterable)
    :param force:            Force restart (bool) (default: False)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    code = 0
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            code = lifecycle_schema_restart(project_path, force=force)

    return code


def lifecycle_bundle_ps(project_path, config_names):
    """
    Check processes for multiple configurations.

    :param project_path:     Project path (str)
    :param config_names:     Config names (iterable)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    code = 0
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            code = lifecycle_schema_ps(project_path)

    return code


def lifecycle_bundle_build(project_path, config_names, no_cache=False, push_to_registry=True):
    """
    Build multiple configurations.

    :param project_path:         Project path (str)
    :param config_names:         Config names (iterable)
    :param no_cache:             Do not use cache (bool) (default: False)
    :param push_to_registry:     Push to registry (bool) (default: True)
    """
    from docknv.session_handler import session_check_bundle_configurations
    from docknv.project_handler import project_use_temporary_configuration

    session_check_bundle_configurations(project_path, config_names)
    code = 0
    for config_name in config_names:
        with project_use_temporary_configuration(project_path, config_name):
            code = lifecycle_schema_build(project_path, no_cache, push_to_registry)

    return code

# MACHINE FUNCTIONS #############


def lifecycle_machine_build(project_path, machine_name, no_cache=False, push_to_registry=True, namespace_name=None):
    """
    Build a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param no_cache:             Do not use cache (bool) (default: False)
    :param push_to_registry:     Push to registry (bool) (default: True)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)

    if no_cache:
        args = ["build", "--no-cache", machine_name]
    else:
        args = ["build", machine_name]

    code = exec_compose_pretty(project_path, args)
    if code != 0:
        raise RuntimeError("Build failed for machine {0}.".format(machine_name))

    if push_to_registry:
        code = exec_compose_pretty(project_path, ["push", machine_name])
        if code != 0:
            raise RuntimeError("Push failed for machine {0}.".format(machine_name))

    return code


def lifecycle_machine_stop(project_path, machine_name, namespace_name=None):
    """
    Stop a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)

    return exec_compose_pretty(project_path, ["stop", machine_name])


def lifecycle_machine_start(project_path, machine_name, namespace_name=None):
    """
    Start a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    return exec_compose_pretty(project_path, ["start", machine_name])


def lifecycle_machine_shell(project_path, machine_name, shell_path="/bin/bash", namespace_name=None, create=False):
    """
    Execute a shell on a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param shell_path:           Shell path (str) (default: /bin/bash)
    :param namespace_name:       Namespace name (str?) (default: None)
    :param create:               Create the container (bool) (default: False)
    """
    if create:
        return lifecycle_machine_run(project_path, machine_name, shell_path, namespace_name=namespace_name)
    else:
        return lifecycle_machine_exec(
            project_path, machine_name, shell_path,
            no_tty=False, namespace_name=namespace_name)


def lifecycle_machine_restart(project_path, machine_name, force=False,
                              namespace_name=None):
    """
    Restart a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param force:                Force restart (bool) (default: False)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)

    if force:
        lifecycle_machine_stop(project_path, machine_name, namespace_name=namespace_name)
        return lifecycle_machine_start(project_path, machine_name, namespace_name=namespace_name)
    else:
        return exec_compose_pretty(project_path, ["restart", machine_name])


def lifecycle_machine_run(project_path, machine_name, command, daemon=False, namespace_name=None):
    """
    Run a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param command:              Command (str)
    :param daemon:               Run in background? (bool) (default: False)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)

    d_cmd = "-d" if daemon else ""

    return exec_compose(project_path, ["run", "--rm", "--service-ports", d_cmd, machine_name, *shlex.split(command)])


def lifecycle_machine_push(project_path, machine_name, host_path, container_path, namespace_name=None):
    """
    Push a file to a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param host_path:            Host path (str)
    :param container_path:       Container path (str)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    container = get_docker_container(project_path, machine_name)

    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        Logger.info("Copying file from host to `{0}`: `{1}` => `{2}".format(machine_name, host_path, container_path))
        return exec_docker(project_path, ["cp", host_path, "{0}:{1}".format(container, container_path)])


def lifecycle_machine_pull(project_path, machine_name, container_path, host_path, namespace_name=None):
    """
    Pull a file from a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param container_path:       Container path (str)
    :param host_path:            Host path (str)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    container = get_docker_container(project_path, machine_name)

    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        Logger.info("Copying file from `{0}`: `{1}` => `{2}".format(machine_name, container_path, host_path))
        return exec_docker(project_path, ["cp", "{0}:{1}".format(container, container_path), host_path])


def lifecycle_machine_exec(project_path, machine_name, command=None, no_tty=False,
                           namespace_name=None):
    """
    Execute a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param command:              Command (str?) (default: None)
    :param no_tty:               Do not use TTY (bool) (default: False)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    container = get_docker_container(project_path, machine_name)

    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name))
    else:
        tty_cmd = "-ti" if not no_tty else ""
        cmd = ["exec", tty_cmd, container, *shlex.split(command)]
        code = exec_docker(project_path, cmd)
        if code != 0:
            Logger.error("Error while executing command {0} on machine {1}".format(
                cmd, machine_name
            ))

        return code


def lifecycle_machine_exec_multiple(project_path, machine_name, commands, no_tty=False,
                                    namespace_name=None):
    """
    Execute multiple commands on a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param commands:             Commands (iterable)
    :param no_tty:               Do not use TTY (bool) (default: False)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    container = get_docker_container(project_path, machine_name)

    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        code = 0
        for command in commands:
            tty_cmd = "-ti" if not no_tty else ""
            code = exec_docker(project_path, ["exec", tty_cmd, container, *shlex.split(command)])
            if code != 0:
                break

        return code


def lifecycle_machine_logs(project_path, machine_name, tail=0, follow=False, namespace_name=None):
    """
    Get logs from a machine.

    :param project_path:         Project path (str)
    :param machine_name:         Machine name (str)
    :param tail:                 Tail lines (int) (default: 0)
    :param follow:               Follow logs (bool) (default: False)
    :param namespace_name:       Namespace name (str?) (default: None)
    """
    machine_name = lifecycle_get_machine_name(machine_name, namespace_name)
    container = get_docker_container(project_path, machine_name)

    if not container:
        Logger.error("Machine `{0}` is not running.".format(machine_name), crash=False)
    else:
        cmd = ["logs", container]
        if follow:
            cmd += ["-f"]
        if tail != 0:
            cmd += ["--tail", tail]

        return exec_docker(project_path, cmd)


def lifecycle_volume_list(project_path):
    """
    List volumes.

    :param project_path:     Project path (str)
    """
    Logger.info("Listing volumes...")
    return exec_docker(project_path, ["volume", "list"])


def lifecycle_volume_remove(project_path, volume_name):
    """
    Remove a volume.

    :param project_path:     Project path (str)
    :param volume_name:      Volume name (str)
    """
    from docknv.project_handler import project_get_name

    Logger.info("Removing volume `{0}`".format(volume_name))

    project_name = project_get_name(project_path)
    volume_path = "{0}_{1}".format(project_name, volume_name)
    code = exec_docker(project_path, ["volume", "rm", volume_path])
    if code != 0:
        raise RuntimeError("Error while removing volume {0}".format(volume_path))

    return code


def lifecycle_registry_start(path):
    """
    Start a registry.

    :param path:             Registry path (str)
    """
    Logger.info("Starting registry... {0}".format(path))

    cmd = ["run", "-d", "-p", "5000:5000"]
    if path:
        cmd += ["-v", "{0}:/var/lib/registry".format(path)]
    cmd += ["--restart=always", "--name", "registry", "registry:2"]

    return exec_docker(".", path)


def lifecycle_registry_stop():
    """Stop a registry."""
    return exec_docker(".", ["stop", "registry"]) and exec_docker(".", ["rm", "registry"])
