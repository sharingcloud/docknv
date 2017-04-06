import os
import time
import subprocess
import re
import sys

from .logger import Logger

class Compose(object):
    def __init__(self, namespace, compose_file="./.docker-compose.yml"):
        self.namespace = namespace
        self.compose_file = compose_file

    ##############

    def _exec_compose(self, args_str):
        os.system("docker-compose -f {0} {1}".format(self.compose_file, args_str))

    def _get_container(self, machine):
        cmd = "docker-compose -f {0} ps -q {1}".format(self.compose_file, machine)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if out == "":
            return None

        return out.strip()

    def _get_service(self, machine):
        cmd = "docker service ps -q {0}_{1}".format(self.namespace, machine)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if out == "":
            return None

        return out.strip()

    ##############

    def ps(self):
        self._exec_compose("ps")

    def build(self, machine):
        Logger.info("Building machine `{0}`...".format(machine))
        self._exec_compose("build {0}".format(machine))

    def build_all(self):
        Logger.info("Building machines...")
        self._exec_compose("build")

    def run(self, machine, command=""):
        msg = "Running machine `{0}`".format(machine)
        if command != "":
            msg += " with command `{0}`...".format(command)
        else:
            msg += "..."

        Logger.info(msg)
        self._exec_compose("run --service-ports {0} {1}".format(machine, command))

    def up(self):
        Logger.info("Starting up all machines...")
        self._exec_compose("up -d")

    def down(self):
        Logger.info("Shutting down all machines...")
        self._exec_compose("down")

    def reup(self):
        Logger.info("Reupping all machines...")
        self._exec_compose("down")
        self._exec_compose("up -d")

    def service_list(self):
        os.system("docker service ls")

    def service_ps(self, machine):
        service = self._get_service(machine)
        if not service:
            Logger.error("Service `{0}` is not running.".format(service), crash=False)
        else:
            os.system("docker service ps {1}".format(service))

    def daemon(self, machine, command=""):
        msg = "Running machine `{0}` in background".format(machine)
        if command != "":
            msg += " with command `{0}`...".format(command)
        else:
            msg += "..."

        Logger.info(msg)
        self._exec_compose("run --service-ports -d {0} {1} > /dev/null".format(machine, command))
        time.sleep(2)

    def shell(self, machine, shell="/bin/bash"):
        Logger.info("Running shell `{0}` in machine `{1}`...".format(shell, machine))
        self.execute(machine, shell)

    def stop(self, machine):
        Logger.info("Stopping machine `{0}`...".format(machine))

        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            os.system("docker stop {0} > /dev/null && docker rm {0} > /dev/null".format(container))

    def restart(self, machine):
        Logger.info("Restarting machine `{0}`...".format(machine))

        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            os.system("docker restart {0} > /dev/null".format(container))

    def logs(self, machine):
        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            os.system("docker logs {0}".format(container))

    def execute(self, machine, command="", tty=True, return_code=False):
        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            code = os.system("docker exec {2} {0} {1}".format(container, command, "-ti" if tty else ""))
            if return_code:
                sys.exit(os.WEXITSTATUS(code))

    def copy(self, machine, container_path, host_path):
        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            Logger.info("Copying file from `{0}`: `{1}` => `{2}".format(machine, container_path, host_path))
            os.system("docker cp {0}:{1} {2}".format(container, container_path, host_path))

    def remove_network(self, network):
        Logger.info("Removing network `{0}`...".format(network))
        os.system("docker network rm {0} > /dev/null".format(network))

    def list_volumes(self):
        os.system("docker volume list | grep {0}".format(self.namespace))

    def create_volume(self, name):
        Logger.info("Creating volume `{0}`...".format(name))
        os.system("docker volume create --name {0}_{1} -d local".format(self.namespace, name))

    def remove_volume(self, name):
        Logger.info("Removing volume `{0}`...".format(name))
        os.system("docker volume rm {0}_{1}".format(self.namespace, name))

    def reset_volume(self, name):
        self.remove_volume(name)
        self.create_volume(name)

    ##################

    def create_volumes(self, names):
        for name in names:
            self.create_volume(name)

    def remove_volumes(self, names):
        for name in names:
            self.remove_volume(name)

    def reset_volumes(self, names):
        for name in names:
            self.reset_volume(name)

    ##################

    def push_stack(self):
        self._exec_compose("push")

    def deploy_stack(self):
        os.system("docker stack deploy --compose-file {0} {1}".format(self.compose_file, self.namespace))

    def rm_stack(self):
        os.system("docker stack rm {0}".format(self.namespace))

    ###################

    def create_overlay_network(self, name):
        Logger.info("Creating overlay network `{0}`...".format(name))
        os.system("docker network create --driver=overlay --attachable {0}".format(name))

    def list_networks(self):
        os.system("docker network ls")

    def remove_network(self, name):
        Logger.info("Removing network `{0}`...".format(name))
        os.system("docker network rm {0}".format(name))
