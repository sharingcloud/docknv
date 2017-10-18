"""Handle docknv environment files."""

from __future__ import unicode_literals

import os
import imp
import re

from collections import OrderedDict

from docknv.logger import Logger, Fore
from docknv.utils.ioutils import io_open

IMPORT_DETECTION_RGX = re.compile(r'-\*-\s*import:\s*([a-zA-Z0-9_-]*)\s*-\*-')


def env_list(project_path):
    """
    List environment configurations.

    :param project_path:     Project path (str)
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


def env_show(project_path, name):
    """
    Print an environment file.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    """
    loaded_env = env_load_in_memory(project_path, name)

    Logger.info("Showing environment file `{0}`:".format(name))
    for key in loaded_env:
        Logger.raw("  {0}".format(key), color=Fore.YELLOW, linebreak=False)
        Logger.raw(" = ", linebreak=False)
        Logger.raw(loaded_env[key], color=Fore.BLUE)


def env_check_file(project_path, name):
    """
    Check if an environment file exist.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    :rtype: bool
    """
    env_path = os.path.join(project_path, "envs",
                            "".join((name, ".env.py")))
    return os.path.exists(env_path)


def env_load_in_memory(project_path, name):
    """
    Load environment file in memory.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    :rtype: Environment data (dict)
    """
    env_path = _env_get_path(project_path, name)

    if not os.path.isfile(env_path):
        raise RuntimeError("File `{0}` does not exist".format(env_path))

    loaded_env = OrderedDict()

    # Detect imports
    env_content = _env_read_file_content(env_path)
    imported_environments = _env_detect_imports(env_content)
    for imported_env in imported_environments:
        if imported_env == name:
            continue

        result = env_load_in_memory(project_path, imported_env)
        for key in result:
            loaded_env[key] = result[key]

    # Loading variables
    env_data = imp.load_source("envs", env_path)
    env_vars = [e for e in dir(env_data) if not e.startswith("__")]
    for variable in env_vars:
        loaded_env[variable] = getattr(env_data, variable)

    return loaded_env


def env_write_to_file(env, path):
    """
    Write environment to a file.

    :param env:      Environment configuration data (dict)
    :param path:     Output file (str)
    """
    Logger.info("Writing environment to file {0}...".format(path))

    with io_open(path, encoding="utf-8", mode="wt+") as handle:
        for value in env:
            handle.write("{0} = {1}\n".format(value, env[value]))


##############
# PRIVATE


def _env_get_path(project_path, name):
    """
    Return environment path from project path and environment name.

    :param project_path:     Project path (str)
    :param name:             Environment name (str)
    :rtype: Environment file path (str)
    """
    return os.path.join(project_path, "envs", "".join((name, ".env.py")))


def _env_detect_imports(env_content):
    """
    Detect imports in an environment file.

    :param env_content:  Environment file content (str)
    :rtype: Detected imports (iterable)
    """
    detected_imports = []
    for match in IMPORT_DETECTION_RGX.finditer(env_content):
        detected_imports.append(match.groups()[0])

    return detected_imports


def _env_read_file_content(env_path):
    """
    Open and read environment file content.

    :param env_path:     Environment file path (str)
    :rtype: Environment file content (str)
    """
    with io_open(env_path, mode='r', encoding='utf-8') as handle:
        return handle.read()
