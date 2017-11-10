"""User handling."""

from __future__ import unicode_literals

import os
import shutil

from contextlib import contextmanager

from docknv.logger import Logger


def user_get_id():
    """
    Return the user ID.

    :rtype: User ID (int/str)
    """
    try:
        return os.geteuid()
    except Exception:
        import getpass
        return getpass.getuser()


def user_get_project_path(project_name, config_name=None):
    """
    Get a user project path.

    :param project_name:    Project name (str)
    :param config_name:     Config name (str?) (default: None)
    :rtype: Config path (str)
    """
    if config_name:
        return os.path.join(_get_docknv_path(), project_name, config_name)
    return os.path.join(_get_docknv_path(), project_name)


def user_get_docknv_config_file(project_name):
    """
    Get project config file from user path.

    :param project_name:     Project name (str)
    :rtype: Config path (str)
    """
    config_path = os.path.join(user_get_project_path(project_name), "docknv.yml")
    user_ensure_config_path_exists(project_name)
    return config_path


def user_get_file_from_project(project_name, path_to_file, config_name=None):
    """
    Get file from user project path.

    :param project_name:    Project name (str)
    :param path_to_file:    Path to file (str)
    :param config_name:     Config name (str?) (default: None)
    :rtype: File path (str)
    """
    if not config_name:
        return os.path.join(user_get_project_path(project_name), path_to_file)
    else:
        return os.path.join(user_get_project_path(project_name), config_name, path_to_file)


def user_ensure_config_path_exists(project_name):
    """
    Ensure the config path existence.

    :param project_name:     Project name (str)
    """
    user_config_path = _get_docknv_path()
    user_project_config_path = user_get_project_path(project_name)

    if not os.path.exists(user_config_path):
        os.makedirs(user_config_path)
    if not os.path.exists(user_project_config_path):
        os.makedirs(user_project_config_path)


def user_copy_file_to_config(project_name, path_to_file):
    """
    Copy file to the user config path.

    :param project_name:     Project name (str)
    :param path_to_file:     Path to file (str)
    """
    user_ensure_config_path_exists(project_name)

    config_path = user_get_project_path(project_name)
    file_name = os.path.basename(path_to_file)

    shutil.copyfile(path_to_file, os.path.join(config_path, file_name))


############
# Lock


def user_get_lock_file(project_path):
    """
    Get the user lock file.

    :param project_path:     Project path (str)
    :rtype: Lock file path (str)
    """
    return "{0}/.{1}.lock".format(project_path, user_get_id())


def user_check_lock(project_path):
    """
    Check the user lock file.

    :param project_path:     Project path (str)
    :rtype: bool
    """
    return os.path.exists(user_get_lock_file(project_path))


def user_enable_lock(project_path):
    """
    Enable user lock file.

    :param project_path:     Project path (str)
    :rtype: Success ? (bool)
    """
    lockfile = user_get_lock_file(project_path)
    if user_check_lock(project_path):
        return False

    with open(lockfile, mode="w") as handle:
        handle.write("$")

    return True


def user_disable_lock(project_path):
    """
    Disable user lock file.

    :param project_path:     Project path (str)
    """
    lockfile = user_get_lock_file(project_path)
    if user_check_lock(project_path):
        os.remove(lockfile)


@contextmanager
def user_try_lock(project_path):
    """
    Try to set the user lock.

    :param project_path:     Project path (str)

    **Context manager**
    """
    if not user_enable_lock(project_path):
        Logger.error("docknv is already running with your account. wait until completion.")
    else:
        try:
            yield
        except Exception:
            user_disable_lock(project_path)
            raise

    user_disable_lock(project_path)


@contextmanager
def user_temporary_copy_file(project_name, path_to_file):
    """
    Make a temporary copy of a user config file.

    :param project_name:     Project name (str)
    :param path_to_file:     Path to file (str)

    **Context manager**
    """
    path = user_get_file_from_project(project_name, path_to_file)

    generated_file_name = ".{0}.{1}".format(user_get_id(), os.path.basename(path))
    shutil.copyfile(path, generated_file_name)

    yield generated_file_name

    if os.path.exists(generated_file_name):
        os.remove(generated_file_name)


def user_clean_config_path(project_name, config_name=None):
    """
    Clean a user config path, with an optional config name.

    :param project_name:     Project name (str)
    :param config_name:      Config name (str?) (default: None)
    """
    from docknv.utils.prompt import prompt_yes_no

    folder_path = user_get_project_path(project_name, config_name)

    if prompt_yes_no("Are you sure you want to remove the user folder {0} ?".format(folder_path)):
        shutil.rmtree(folder_path)
        Logger.info("Folder `{0}` removed".format(folder_path))

##################


def _get_docknv_path():
    """
    Get the docknv path.

    :rtype: Config path (str)
    """
    return os.path.expanduser("~/.docknv")
