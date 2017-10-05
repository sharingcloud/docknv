"""User handling."""

import os
import shutil

from contextlib import contextmanager

from docknv.logger import Logger


def user_current_is_root():
    """
    Check if the user is root.

    :return bool
    """
    return os.geteuid() == 0


def user_current_get_id():
    """
    Return the user ID.

    :return User ID (int/str)
    """
    try:
        return os.geteuid()
    except Exception:
        import getpass
        return getpass.getuser()


def user_get_config_path():
    """
    Get the docknv user config path.

    :return Config path (str)
    """
    return os.path.expanduser("~/.docknv")


def user_get_project_config_path(project_name):
    """
    Get the docknv user config path for a project.

    :param project_name     Project name (str)
    :return Config path (str)
    """
    return os.path.join(user_get_config_path(), project_name)


def user_get_project_config_name_path(project_name, config_name):
    """
    Get the docknv user config path for a project and a config.

    :param project_name     Project name (str)
    :param config_name      Config name (str)
    :return Config path (str)
    """
    return os.path.join(user_get_config_path(), project_name, config_name)


def user_get_project_config_file_path(project_name):
    """
    Get project config file from user path.

    :param project_name     Project name (str)
    :return Config path (str)
    """
    config_path = os.path.join(user_get_project_config_path(project_name), "docknv.yml")
    user_ensure_config_path_exists(project_name)
    return config_path


def user_get_project_file_path(project_name, path_to_file):
    """
    Get project file from config path.

    :param project_name     Project name (str)
    :param path_to_file     Path to file (str)
    :return File path (str)
    """
    return os.path.join(user_get_project_config_path(project_name), path_to_file)


def user_create_project_config_path(project_name):
    """
    Create a docknv config path for a project.

    :param project_name     Project name (str)
    """
    user_ensure_config_path_exists(project_name)


def user_ensure_config_path_exists(project_name):
    """
    Ensure the config path existence.

    :param project_name     Project name (str)
    """
    user_config_path = user_get_config_path()
    user_project_config_path = user_get_project_config_path(project_name)

    if not os.path.exists(user_config_path):
        os.makedirs(user_config_path)
    if not os.path.exists(user_project_config_path):
        os.makedirs(user_project_config_path)


def user_copy_file_to_config_path(project_name, path_to_file):
    """
    Copy file to the user config path.

    :param project_name     Project name (str)
    :param path_to_file     Path to file (str)
    """
    user_ensure_config_path_exists(project_name)

    config_path = user_get_project_config_path(project_name)
    file_name = os.path.basename(path_to_file)

    shutil.copyfile(path_to_file, os.path.join(config_path, file_name))


def user_get_lock_file(project_path):
    """
    Get the user lock file.

    :param project_path     Project path (str)
    :return Lock file path (str)
    """
    return "{0}/.{1}.lock".format(project_path, user_current_get_id())


def user_check_lock(project_path):
    """
    Check the user lock file.

    :param project_path     Project path (str)
    :return bool
    """
    return os.path.exists(user_get_lock_file(project_path))


def user_enable_lock(project_path):
    """
    Enable user lock file.

    :param project_path     Project path (str)
    :return Success ? (bool)
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

    :param project_path     Project path (str)
    """
    lockfile = user_get_lock_file(project_path)
    if user_check_lock(project_path):
        os.remove(lockfile)


@contextmanager
def user_try_lock(project_path):
    """
    Try to set the user lock.

    :param project_path     Project path (str)
    :coroutine
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

    :param project_name     Project name (str)
    :param path_to_file     Path to file (str)
    :coroutine
    """
    path = user_get_project_file_path(project_name, path_to_file)

    generated_file_name = ".{0}.{1}".format(user_current_get_id(), os.path.basename(path))
    shutil.copyfile(path, generated_file_name)

    yield generated_file_name

    if os.path.exists(generated_file_name):
        os.remove(generated_file_name)


def user_clean_config_path(project_name, config_name=None):
    """
    Clean a user config path, with an optional config name.

    :param project_name     Project name (str)
    :param config_name      Config name (str?) (default: None)
    """
    from docknv.utils.prompt import prompt_yes_no

    if config_name:
        folder_path = user_get_project_config_name_path(project_name, config_name)
    else:
        folder_path = user_get_project_config_path(project_name)

    if prompt_yes_no("Are you sure you want to remove the user folder {0} ?".format(folder_path)):
        shutil.rmtree(folder_path)
        Logger.info("Folder `{0}` removed".format(folder_path))
