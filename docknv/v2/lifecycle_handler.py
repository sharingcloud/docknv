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
    def build_schema(project_path):
        LifecycleHandler._exec_compose(project_path, ["build"])

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
    def build_machine(project_path, machine_name):
        LifecycleHandler._exec_compose(project_path, ["build", machine_name])

    @staticmethod
    def shell_machine(project_path, machine_name, shell_path="/bin/bash"):
        LifecycleHandler.exec_machine(
            project_path, machine_name, shell_path, False, False)

    @staticmethod
    def daemon_machine(project_path, machine_name, command=None):
        LifecycleHandler._exec_compose(
            project_path, ["run", "--service-ports", "-d", machine_name, command])

    @staticmethod
    def restart_machine(project_path, machine_name):
        LifecycleHandler._exec_compose(
            project_path, ["restart", machine_name])

    @staticmethod
    def run_machine(project_path, machine_name, command=None):
        LifecycleHandler._exec_compose(
            project_path, ["run", "--service-ports", machine_name, command])

    @staticmethod
    def exec_machine(project_path, machine_name, command=None, no_tty=False, return_code=False):
        container = LifecycleHandler._get_container(machine_name)
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
        container = LifecycleHandler._get_container(machine_name)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(
                machine_name), crash=False)
        else:
            cmd = "docker logs {0}".format(container)
            if tail != 0:
                cmd = "{0} --tail {1}".format(cmd, tail)

            os.system(cmd)

    # INTERNAL FUNCTIONS ###########

    @staticmethod
    def _get_container(machine):
        cmd = "docker-compose -f {0} ps -q {1}".format(
            ".docker-compose.yml", machine)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, _) = proc.communicate()

        if out == "":
            return None

        return out.strip()

    @staticmethod
    def _exec_docker(project_path, args):
        os.system(
            "pushd {0} > /dev/null; docker {1}; popd > /dev/null".format(project_path, " ".join(args)))

    @staticmethod
    def _exec_compose(project_path, args):
        os.system("pushd {0} > /dev/null; docker-compose -f {1} {2}; popd > /dev/null".format(
            project_path, ".docker-compose.yml", " ".join(args)))
