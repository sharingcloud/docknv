"""
docknv machines and schema lifecycle handling
"""

import os
import sys
import subprocess

from docknv.logger import Logger


class LifecycleHandler(object):
    """
    docknv machines and schema lifecycle handling
    """

    # SCHEMA FUNCTIONS ###############

    @staticmethod
    def build_schema(project_path, push_to_registry=False):

        # Get services from current config
        from docknv.v2.config_handler import ConfigHandler
        from docknv.v2.schema_handler import SchemaHandler

        current_config = ConfigHandler.get_current_config(project_path)
        current_config_data = ConfigHandler.get_known_configuration(
            project_path, current_config)

        config_data = ConfigHandler.load_config_from_path(project_path)
        schema_config = SchemaHandler.get_schema_configuration(
            config_data, current_config_data["schema"])

        namespace = current_config_data["namespace"]
        for service in schema_config["config"]["services"]:
            service_name = "{0}_{1}".format(
                namespace, service) if namespace != "default" else service

            LifecycleHandler._exec_compose(
                project_path, ["build", service_name])
            LifecycleHandler._exec_compose(
                project_path, ["push", service_name])

        # LifecycleHandler._exec_compose(project_path, ["build"])

    @staticmethod
    def start_schema(project_path, foreground=False):
        command = ["up"]
        if not foreground:
            command.append("-d")

        LifecycleHandler._exec_compose(project_path, command)

    @staticmethod
    def stop_schema(project_path):
        LifecycleHandler._exec_compose(project_path, ["down"])

    @staticmethod
    def ps_schema(project_path):
        LifecycleHandler._exec_compose(project_path, ["ps"])

    @staticmethod
    def restart_schema(project_path):
        LifecycleHandler._exec_compose(project_path, ["restart"])

    # MACHINE FUNCTIONS #############

    @staticmethod
    def build_machine(project_path, machine_name, push_to_registry=False):
        LifecycleHandler._exec_compose(project_path, ["build", machine_name])

        if push_to_registry:
            LifecycleHandler._exec_compose(
                project_path, ["push", machine_name])

    @staticmethod
    def stop_machine(project_path, machine_name):
        LifecycleHandler._exec_compose(project_path, ["stop", machine_name])

    @staticmethod
    def start_machine(project_path, machine_name):
        LifecycleHandler._exec_compose(project_path, ["start", machine_name])

    @staticmethod
    def shell_machine(project_path, machine_name, shell_path="/bin/bash"):
        LifecycleHandler.exec_machine(
            project_path, machine_name, shell_path, False, False)

    @staticmethod
    def daemon_machine(project_path, machine_name, command=None):
        LifecycleHandler._exec_compose(
            project_path, ["run", "--service-ports", "-d", machine_name, command])

    @staticmethod
    def restart_machine(project_path, machine_name, force=False):
        if force:
            LifecycleHandler.stop_machine(project_path, machine_name)
            LifecycleHandler.start_machine(project_path, machine_name)
        else:
            LifecycleHandler._exec_compose(
                project_path, ["restart", machine_name])

    @staticmethod
    def run_machine(project_path, machine_name, command=None):
        LifecycleHandler._exec_compose(
            project_path, ["run", "--service-ports", machine_name, command])

    @staticmethod
    def push_machine(project_path, machine_name, host_path, container_path):
        container = LifecycleHandler._get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            Logger.info("Copying file from host to `{0}`: `{1}` => `{2}".format(
                machine_name, host_path, container_path))
            os.system("docker cp {0} {1}:{2}".format(
                host_path, container, container_path))

    @staticmethod
    def pull_machine(project_path, machine_name, container_path, host_path):
        container = LifecycleHandler._get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            Logger.info("Copying file from `{0}`: `{1}` => `{2}".format(
                machine_name, container_path, host_path))
            os.system("docker cp {0}:{1} {2}".format(
                container, container_path, host_path))

    @staticmethod
    def exec_machine(project_path, machine_name, command=None, no_tty=False, return_code=False):
        container = LifecycleHandler._get_container(project_path, machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            code = os.system("docker exec {2} {0} {1}".format(
                container, command, "-ti" if not no_tty else ""))
            if return_code:
                sys.exit(os.WEXITSTATUS(code))

    @staticmethod
    def logs_machine(project_path, machine_name, tail=0):
        container = LifecycleHandler._get_container(project_path, machine_name)
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

        project_name = LifecycleHandler._get_project_name(project_path)
        os.system("docker volume list | grep -i {0}".format(project_name))

    @staticmethod
    def remove_volume(project_path, volume_name):
        """
        Remove a volume
        """

        Logger.info("Removing volume `{0}`".format(volume_name))

        project_name = LifecycleHandler._get_project_name(project_path)
        os.system("docker volume rm {0}_{1}".format(project_name, volume_name))

    @staticmethod
    def start_registry(path):
        Logger.info("Starting registry... %s" % path)

        cmd = "docker run -d -p 5000:5000 {0} --restart=always --name registry registry:2"
        if path:
            cmd = cmd.format("-v {0}:/var/lib/registry".format(path))
        else:
            cmd = cmd.format("")

        os.system(cmd)

    @staticmethod
    def stop_registry():
        os.system("docker stop registry && docker rm registry")

    # INTERNAL FUNCTIONS ###########

    @staticmethod
    def _get_project_name(project_path):
        """
        Get project name from path.
        """

        return os.path.basename(os.path.abspath(project_path)).lower()

    @staticmethod
    def _get_container(project_path, machine):
        """
        Return a Docker container ID.
        """
        from docknv.v2.config_handler import ConfigHandler
        from docknv.v2.multi_user_handler import MultiUserHandler

        config = ConfigHandler.load_config_from_path(project_path)

        with MultiUserHandler.temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
            cmd = "docker-compose -f {0} ps -q {1}".format(
                user_file, machine)
            proc = subprocess.Popen(cmd, cwd=project_path,
                                    stdout=subprocess.PIPE, shell=True)
            (out, _) = proc.communicate()

            if out == "":
                return None

            return out.strip()

    @staticmethod
    def _exec_docker(project_path, args):
        """
        Execute a Docker command.
        """
        if os.name == 'nt':
            commands = "cd {0} & docker {1}".format(project_path, " ".join(args))
        else:
            commands = "cd {0}; docker {1}; cd - > /dev/null".format(project_path, " ".join(args))
        
        os.system(commands)

    @staticmethod
    def _exec_compose(project_path, args):
        """
        Execute a Docker Compose command.
        """
        from docknv.v2.config_handler import ConfigHandler
        from docknv.v2.multi_user_handler import MultiUserHandler

        config = ConfigHandler.load_config_from_path(project_path)

        with MultiUserHandler.temporary_copy_file(config.project_name, "docker-compose.yml") as user_file:
            if os.name == 'nt':
                commands = "cd {0} & docker-compose -f {1} {2}".format(project_path, user_file, " ".join(args))
            else:
                commands = "cd {0}; docker-compose -f {1} {2}; cd - > /dev/null".format(project_path, user_file, " ".join(args))
            
            os.system(commands)
