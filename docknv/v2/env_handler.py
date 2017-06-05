"""
Handle docknv environment files
"""

import os
import imp
import codecs

from collections import OrderedDict

from docknv.logger import Logger, Fore


class EnvHandler(object):
    """
    Handle docknv environment files
    """

    @staticmethod
    def list_environments(project_path):
        """
        List environment configurations.

        @param project_path Project path
        """

        env_path = os.path.join(project_path, "envs")

        if not os.path.isdir(env_path):
            Logger.error("Env folder does not exist.")

        envs = os.listdir(env_path)
        envs_count = len(envs)
        if envs_count == 0:
            Logger.warn("No env file found.")
        else:
            Logger.info("Environment files listing:")

            for env_file in envs:
                if env_file.endswith(".env.py"):
                    name = env_file[:-7]
                    Logger.raw("  > {0}".format(name))

    @staticmethod
    def check_environment_file(project_path, name):
        """
        Check if an environment file exist.

        @param project_path Project path
        @param name         Environment file name
        @return True/False
        """

        env_path = os.path.join(project_path, "envs",
                                "".join((name, ".env.py")))
        return os.path.exists(env_path)

    @staticmethod
    def load_env_in_memory(project_path, name):
        """
        Load environment file in memory.

        @param project_path Project path
        @param name         Environment file name
        """

        env_path = os.path.join(project_path, "envs",
                                "".join((name, ".env.py")))

        if not os.path.isfile(env_path):
            raise RuntimeError("File `{0}` does not exist".format(env_path))
        Logger.info(
            "Loading environment configuration file `{0}`...".format(name))

        env_data = imp.load_source("envs", env_path)
        env_vars = [e for e in dir(env_data) if not e.startswith("__")]

        loaded_env = OrderedDict()
        for variable in env_vars:
            loaded_env[variable] = getattr(env_data, variable)

        Logger.info("Loaded environment:")
        for key in loaded_env:
            Logger.raw("  {0}".format(key), color=Fore.YELLOW, linebreak=False)
            Logger.raw(" = ", linebreak=False)
            Logger.raw(loaded_env[key], color=Fore.BLUE)

        return loaded_env

    @staticmethod
    def write_env_to_file(env, path):
        """
        Write environment to a file.

        @param env  Environment configuration data
        @param path Output file
        """

        Logger.info("Writing environment to file {0}...".format(path))

        with codecs.open(path, encoding="utf-8", mode="wt+") as handle:
            for value in env:
                handle.write("{0}={1}\n".format(value, env[value]))
