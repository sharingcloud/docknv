import os
import time
import subprocess
import re

from .logger import Logger

class Compose(object):
    def __init__(self, namespace, compose_file="./.docker-compose.yml"):
        self.namespace = namespace
        self.compose_file = compose_file

    ##############

    def _exec_compose(self, args_str):
        os.system("docker-compose -f {0} {1}".format(self.compose_file, args_str))

    def _get_container(self, machine):
        cmd = "docker-compose -f {0} ps | grep {1}_{2}_run".format(self.compose_file, self.namespace, machine)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if out == "":
            return None

        return re.search(r'([a-zA-Z0-9_]+)', out).group(0)

    ##############

    def ps(self):
        self._exec_compose("ps")

    def build(self, machine):
        Logger.info("Building machine `{0}`...".format(machine))
        self._exec_compose("build {0}".format(machine))

    def run(self, machine, command=""):
        command = "Running machine `{0}`".format(machine)
        if command != "":
            command += " with command `{0}`...".format(command)
        else:
            command += "..."

        Logger.info(command)
        self._exec_compose("run --service-ports {0} {1}".format(machine, command))

    def down(self):
        Logger.info("Shutting down all machines...")
        self._exec_compose("down")

    def daemon(self, machine, command=""):
        command = "Running machine `{0}` in background".format(machine)
        if command != "":
            command += " with command `{0}`...".format(command)
        else:
            command += "..."

        Logger.info(command)
        self._exec_compose("run --service-ports -d {0} {1} > /dev/null".format(machine, command))
        time.sleep(2)

    def shell(self, machine, shell="/bin/bash"):
        Logger.info("Running shell `{0}` in machine `{1}`...".format(shell, machine))
        self.run(machine, shell)

    def stop(self, machine):
        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            Logger.info("Stopping machine `{0}`...".format(machine))
            os.system("docker stop {0} > /dev/null && docker rm {0} > /dev/null".format(container))

    def restart(self, machine):
        container = self._get_container(machine)
        if not container:
            Logger.error("Machine `{0}` is not running.".format(machine), crash=False)
        else:
            Logger.info("Restarting machine `{0}`...".format(machine))
            os.system("docker restart {0} > /dev/null".format(container))

    def remove_network(self, network):
        Logger.info("Removing network `{0}`...".format(network))
        os.system("docker network rm {0}".format(network))

    def create_volume(self, name):
        Logger.info("Creating volume `{0}`...".format(name))
        os.system("docker volume create --name {0}_{1} -d local".format(self.namespace, name))

    def remove_volume(self, name):
        Logger.info("Removing volume `{0}`...".format(name))
        os.system("docker volume remove {0}_{1}".format(self.namespace, name))

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
