"""
Docker commands wrapper
"""

import os
import subprocess


def get_container(project_path, machine):
    """
    Return a Docker container ID.
    """
    from docknv.v2.config_handler import ConfigHandler
    from docknv.v2.multi_user_handler import MultiUserHandler

    config = ConfigHandler.read_docknv_configuration(project_path)

    with MultiUserHandler.temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
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
        commands = "cd {0}; docker {1}; cd - > /dev/null".format(project_path, " ".join(args))

    os.system(commands)


def exec_compose(project_path, args):
    """
    Execute a Docker Compose command.
    """
    from docknv.v2.config_handler import ConfigHandler
    from docknv.v2.multi_user_handler import MultiUserHandler

    config = ConfigHandler.read_docknv_configuration(project_path)

    with MultiUserHandler.temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
        if os.name == 'nt':
            commands = "cd {0} & docker-compose -f {1} {2}".format(project_path, user_file, " ".join(args))
        else:
            commands = "cd {0}; docker-compose -f {1} {2}; cd - > /dev/null".format(project_path, user_file,
                                                                                    " ".join(args))

        os.system(commands)
