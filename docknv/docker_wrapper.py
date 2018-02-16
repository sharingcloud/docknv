"""Docker commands wrapper."""

import os
import subprocess
import six

from docknv.logger import Logger
from docknv.project_handler import project_read, project_get_active_configuration
from docknv.user_handler import user_get_file_from_project


def get_docker_container(project_path, machine):
    """
    Return a Docker container ID.

    :param project_path:     Project path (str)
    :param machine:          Machine name (str)
    :rtype: Container name (str)
    """
    config = project_read(project_path)
    config_name = project_get_active_configuration(project_path)
    config_filename = user_get_file_from_project(config.project_name, "docker-compose.yml", config_name)

    cmd = "docker-compose -f {0} --project-directory . ps -q {1}".format(config_filename, machine)
    proc = subprocess.Popen(cmd, cwd=project_path, stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()

    if six.PY3:
        out = out.decode('utf-8')

    if out == "":
        return None

    return out.strip()


def exec_docker(project_path, args):
    """
    Execute a Docker command.

    :param project_path:     Project path (str)
    :param args:             Arguments (...)
    """
    cmd = ["docker"] + [str(a) for a in args if a != ""]
    dry_run = os.environ.get('DOCKNV_FAKE_WRAPPER', '')
    Logger.debug("Executing docker command: {0}".format(cmd))

    if dry_run:
        return cmd

    return subprocess.call(cmd, cwd=project_path)


def exec_compose(project_path, config_filename, args, pretty=False):
    """
    Execute a Docker Compose command.

    :param project_path:     Project path (str)
    :param config_filename:  Config filename (str)
    :param args:             Arguments (...)
    :param pretty:           Pretty filtering ? (default: False) (bool)
    """
    dry_run = os.environ.get('DOCKNV_FAKE_WRAPPER', '')
    cmd = ["docker-compose", "-f", config_filename, "--project-directory", project_path]
    cmd += [str(a) for a in args if a != ""]

    Logger.debug("Executing compose command: {0}".format(cmd))

    if dry_run:
        return cmd

    if pretty:
        proc = subprocess.Popen(" ".join(cmd), cwd=project_path, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True, universal_newlines=True)

        while True:
            out = proc.stdout.readline()
            if out == '' and proc.poll() is not None:
                break
            if out:
                out = out.strip()
                if _pretty_handler(args, out):
                    print(out)

        rc = proc.poll()
        return rc

    return subprocess.call(cmd, cwd=project_path)


def _pretty_handler(args, line):
    action = args[0]
    if not _pretty_handler_common(line):
        return False

    if action in ["start", "stop", "restart", "up", "down"]:
        if not _pretty_handler_lifecycle(line):
            return False
        if not _pretty_handler_network(line):
            return False

    return True


def _pretty_handler_common(line):
    # Ignore swarm warning
    if "Compose does not support 'deploy'" in line:
        return False

    elif line.startswith("Found orphan containers"):
        return False

    elif line == "":
        return False

    return True


def _pretty_handler_network(line):
    if line.startswith("Network") and line.endswith("not found."):
        return False

    elif line.startswith("network") and line.endswith("has active endpoints"):
        return False

    elif line.startswith("Removing network"):
        return False

    return True


def _pretty_handler_lifecycle(line):
    if line.startswith("\x1b"):
        return False

    return True
