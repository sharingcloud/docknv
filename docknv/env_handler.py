import os
import imp
import pprint

from .logger import Logger, Fore

class EnvHandler(object):

    @staticmethod
    def list_envs():
        if not os.path.isdir("./envs"):
            Logger.error("Env folder does not exist.")

        Logger.info("Environment files listing:")

        for f in os.listdir("./envs"):
            if f.endswith(".env.py"):
                name = f[:-7]
                print("  > {0}".format(name))

    @staticmethod
    def load_env_in_memory(path):
        if not os.path.isfile(path):
            raise RuntimeError("File `{0}` does not exist".format(path))
        Logger.info("Loading environment configuration file {0}...".format(path))

        env_data = imp.load_source("envs", path)
        env_vars = [e for e in dir(env_data) if not e.startswith("__")]

        loaded_env = {}
        for v in env_vars:
                loaded_env[v] = getattr(env_data, v)

        pprint.pprint(loaded_env)

        return loaded_env

    @staticmethod
    def write_env_to_file(env, path):
        Logger.info("Writing environment to file {0}...".format(path))

        with open(path, mode="wt+") as f:
            for v in env:
                f.write("{0}={1}\n".format(v, env[v]))
