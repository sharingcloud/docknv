"""Docker commands wrapper."""

import os
import subprocess

import six

from docknv.logger import Logger, Fore


def get_docker_container(project_path, machine):
    """
    Return a Docker container ID.

    :param project_path:     Project path (str)
    :param machine:          Machine name (str)
    :rtype: Container name (str)
    """
    from docknv.project_handler import project_read
    from docknv.user_handler import user_temporary_copy_file

    config = project_read(project_path)

    with user_temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        cmd = "docker-compose -f {0} ps -q {1}".format(user_file, machine)
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
    if os.name == 'nt':
        commands = "cd {0} & docker {1}".format(project_path, " ".join(args))
    else:
        commands = "cd {0}; docker {1}; cd - > /dev/null".format(
            project_path, " ".join(args))

    os.system(commands)


def exec_compose(project_path, args):
    """
    Execute a Docker Compose command.

    :param project_path:     Project path (str)
    :param args:             Arguments (...)
    """
    from docknv.project_handler import project_read
    from docknv.user_handler import user_temporary_copy_file

    config = project_read(project_path)

    with user_temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        if os.name == 'nt':
            commands = "cd {0} & docker-compose -f {1} {2}".format(
                project_path, user_file, " ".join(args))
        else:
            commands = "cd {0}; docker-compose -f {1} {2}; cd - > /dev/null".format(project_path, user_file,
                                                                                    " ".join(args))

        os.system(commands)


def exec_compose_pretty(project_path, args):
    """
    Execute a Docker Compose command, properly filtered.

    :param project_path:     Project path (str)
    :param args:             Arguments (...)
    """
    from docknv.project_handler import project_read
    from docknv.user_handler import user_temporary_copy_file

    ##################

    config = project_read(project_path)

    with user_temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        cmd = "docker-compose -f {0} {1}".format(user_file, " ".join(args))

        proc = subprocess.Popen(cmd, cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True, universal_newlines=True)

        while True:
            out = proc.stdout.readline()
            if out == '' and proc.poll() is not None:
                break
            if out:
                out = out.strip()
                if _pretty_handler_new(out):
                    Logger.info(out)
        rc = proc.poll()

        Logger.debug("Return code: {0}".format(rc))


def _pretty_handler_new(line):
    # Ignore swarm warning
    if "Compose does not support 'deploy'" in line:
        return False

    elif line.startswith("Network") and line.endswith("not found."):
        return False

    elif line.startswith("network") and line.endswith("has active endpoints"):
        return False

    elif line.startswith("Found orphan containers"):
        return False

    elif line == "":
        return False

    elif line.startswith("Removing network"):
        return False

    elif line.startswith("\x1b"):
        return False

    return True
