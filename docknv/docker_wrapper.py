"""
Docker commands wrapper
"""

import os
import subprocess

from docknv.logger import Logger, Fore

from docknv.project_handler import project_read
from docknv.user_handler import user_temporary_copy_file


def get_docker_container(project_path, machine):
    """
    Return a Docker container ID.
    """
    config = project_read(project_path)

    with user_temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        cmd = "docker-compose -f {0} ps -q {1}".format(
            user_file, machine)
        proc = subprocess.Popen(cmd, cwd=project_path,
                                stdout=subprocess.PIPE, shell=True)
        (out, _) = proc.communicate()

        if out == "":
            return None

        return out.strip()


def exec_docker(project_path, args):
    """
    Execute a Docker command.
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
    """

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
    Execute a Docker Compose command, property filtered.
    """

    config = project_read(project_path)
    with user_temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        cmd = "docker-compose -f {0} {1}".format(
            user_file, " ".join(args))

        proc = subprocess.Popen(cmd, cwd=project_path,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        lines = []
        if out != "":
            lines = lines + [l for l in out.split("\n") if l != ""]
        if err != "":
            lines = lines + [l for l in err.split("\n") if l != ""]

        for line in lines:

            # Ignore swarm warning
            if line.startswith("Some services"):
                continue
            # Ignore orphan container warning
            elif line.startswith("Found orphan"):
                continue
            # Ignore terminal manipulation characters
            elif line.startswith("\x1b"):
                continue
            # Ignore active endpoints
            elif line.endswith("has active endpoints"):
                continue
            # Ignore network not found
            elif line.startswith("Network") and line.endswith("not found."):
                continue

            if "up" in args or "down" in args or "restart" in args:
                # Handle network creation
                if line.startswith("Creating network"):
                    net_name = line.split()[2][1:-1]
                    Logger.raw("{1}[net created]{2} {0}".format(
                        net_name, Fore.GREEN, Fore.RESET))

                # Handle volume creation
                elif line.startswith("Creating volume"):
                    volume_name = line.split()[2]
                    Logger.raw("{1}[volume created]{2} {0}".format(
                        volume_name, Fore.GREEN, Fore.RESET))

                # Handle creation
                elif line.startswith("Creating"):
                    if line.endswith("\r"):
                        continue

                    service_name = line.split()[1]
                    Logger.raw("{1}[started]{2} {0}".format(
                        service_name, Fore.GREEN, Fore.RESET))

                # Handle starts
                elif line.startswith("Starting"):
                    if line.endswith("\r"):
                        continue

                    service_name = line.split()[1]
                    Logger.raw("{1}[started]{2} {0}".format(
                        service_name, Fore.GREEN, Fore.RESET))

                # Handle stops
                elif line.startswith("Stopping"):
                    if line.endswith("\r"):
                        service_name = line.split()[1]
                        Logger.raw("{1}[stopped]{2} {0}".format(
                            service_name, Fore.RED, Fore.RESET))

                # Handle removals
                elif line.startswith("Removing"):
                    if line.endswith("\r"):
                        service_name = line.split()[1]
                        Logger.raw("{1}[removed]{2} {0}".format(
                            service_name, Fore.RED, Fore.RESET))

                # Handle restarts
                elif line.startswith("Restarting"):
                    if line.endswith("\r"):
                        service_name = line.split()[1]
                        Logger.raw("{1}[restarted]{2} {0}".format(
                            service_name, Fore.GREEN, Fore.RESET))

                # Handle is up-to-date
                elif line.endswith("is up-to-date"):
                    service_name = line.split()[0]
                    Logger.raw("{1}[ready]{2} {0}".format(
                        service_name, Fore.YELLOW, Fore.RESET))

                else:
                    Logger.info(repr(line))

            elif "ps" in args:
                # Ignore many beginning spaces or dashes
                if line.startswith(" ") or line.startswith("-"):
                    continue
                elif line.startswith("Name"):
                    continue

                spl = [n.strip() for n in line.split("   ") if n.strip() != ""]
                if len(spl) == 3:
                    name, cmd, state = spl
                    port = ""
                elif len(spl) == 4:
                    name, cmd, state, port = spl
                else:
                    continue

                if state == "Up":
                    color = Fore.GREEN
                    small_state = "ok"
                elif state.startswith("Exit"):
                    color = Fore.RED
                    small_state = "ko {0}".format(state.split()[1])
                elif state == "Restarting":
                    color = Fore.YELLOW
                    small_state = "restarting"

                Logger.raw("{0}[{1}]{2} {3} - {4}{5}{2} - {6}{7}{2}".format(
                    color, small_state, Fore.RESET, name, Fore.YELLOW, cmd, Fore.CYAN, port))
