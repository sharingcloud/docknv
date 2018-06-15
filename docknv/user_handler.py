"""User handling."""

import os
import shutil

from contextlib import contextmanager

from docknv.utils.prompt import prompt_yes_no
from docknv.utils.ioutils import io_open
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump
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


def user_get_username():
    """
    Return the user username.

    :rtype: Username (str)
    """
    import getpass
    return getpass.getuser()


def user_get_config_path(project_path, config_name):
    """
    Get a user configuration path for a project.

    :param project_path:    Project path (str)
    :param config_name:     Config name (str)
    :rtype: Config path (str)
    """
    return os.path.join(
        user_get_local_docknv_path(project_path),
        config_name)


def user_get_docknv_config_file(project_path):
    """
    Get project config file from user path.

    :param project_path:     Project path (str)
    :rtype: Config path (str)
    """
    config_file_path = os.path.join(
        user_get_local_docknv_path(project_path),
        "docknv.yml")
    return config_file_path


def user_get_file_from_project(project_path, path_to_file, config_name=None):
    """
    Get file from user project path.

    :param project_path:    Project path (str)
    :param path_to_file:    Path to file (str)
    :param config_name:     Config name (str?) (default: None)
    :rtype: File path (str)
    """
    if not config_name:
        return os.path.join(
            user_get_local_docknv_path(project_path), path_to_file)
    else:
        return os.path.join(
            user_get_local_docknv_path(project_path), config_name, path_to_file)


def user_read_docknv_config(project_path):
    """
    Read the docknv.yml config file for a project.

    :param project_path:    Project path (str)
    :rtype: YAML content (dict)
    """
    user_ensure_config_path_exists(project_path)

    docknv_config_path = user_get_docknv_config_file(project_path)
    if not os.path.exists(docknv_config_path):
        return {}

    else:
        with io_open(docknv_config_path, mode="rt") as handle:
            return yaml_ordered_load(handle.read())


def user_write_docknv_config(project_path, docknv_config):
    """
    Write docknv.yml config content for a project.

    :param project_path:    Project path (str)
    :param docknv_config:   docknv config (dict)
    """
    user_ensure_config_path_exists(project_path)

    docknv_config_path = user_get_docknv_config_file(project_path)
    with io_open(docknv_config_path, mode="wt") as handle:
        handle.write(yaml_ordered_dump(docknv_config))


def user_copy_file_to_config(project_path, path_to_file, config_name=None):
    """
    Copy file to the user session path.

    :param project_path:     Project path (str)
    :param path_to_file:     Path to file (str)
    :param config_name:      Config name (str?)
    """
    user_ensure_config_path_exists(project_path, config_name)

    if config_name:
        user_path = user_get_config_path(project_path, config_name)
    else:
        user_path = user_get_local_docknv_path(project_path)

    file_name = os.path.basename(path_to_file)
    dest_path = os.path.join(user_path, file_name)

    Logger.debug('Copying {src} to {dst}'.format(src=file_name, dst=dest_path))
    shutil.copyfile(path_to_file, dest_path)


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
        except BaseException:
            user_disable_lock(project_path)
            raise

    user_disable_lock(project_path)


@contextmanager
def user_temporary_copy_file(project_path, path_to_file, config_name=None):
    """
    Make a temporary copy of a user config file.

    :param project_path:     Project path (str)
    :param path_to_file:     Path to file (str)
    :param config_name:      Config name (str?) (default: None)

    **Context manager**
    """
    path = user_get_file_from_project(project_path, path_to_file, config_name)

    generated_file_name = ".{0}.{1}".format(user_get_id(), os.path.basename(path))
    shutil.copyfile(path, generated_file_name)

    yield generated_file_name

    if os.path.exists(generated_file_name):
        os.remove(generated_file_name)


def user_clean_config_path(project_path, config_name=None):
    """
    Clean a user config path, with an optional config name.

    :param project_path:     Project path (str)
    :param config_name:      Config name (str?) (default: None)
    """
    if config_name:
        user_config_path = user_get_config_path(project_path, config_name)
    else:
        user_config_path = user_get_local_docknv_path(project_path)

    if not os.path.exists(user_config_path):
        Logger.info("User configuration folder {0} does not exist.".format(user_config_path))
    else:
        if prompt_yes_no("/!\\ Are you sure you want to remove the user folder {0} ?".format(user_config_path)):
            shutil.rmtree(user_config_path)
            Logger.info("User configuration folder `{0}` removed".format(user_config_path))


def user_get_local_docknv_path(project_path):
    """
    Get local docknv path for a user.

    :param project_path:    Project path (str)
    :rtype: Local docknv path.
    """
    from docknv.session_handler import session_get_config_path

    uname = user_get_username()
    config_path = session_get_config_path(project_path)

    return os.path.join(
        config_path,
        uname
    )


def user_get_old_docknv_path(project_name):
    """
    Get old docknv path for a user.

    :param project_name:    Project name (str)
    :rtype: Old docknv path.
    """
    return os.path.realpath(
        os.path.join(
            os.environ.get("DOCKNV_USER_PATH_OLD", os.path.expanduser("~/.docknv")),
            project_name
        )
    )


def user_migrate_config(project_path, project_name, force=False):
    """
    Migrate user configuration.

    :param project_path:    Project path
    """
    old_path = user_get_old_docknv_path(project_name)
    new_path = user_get_local_docknv_path(project_path)

    if not os.path.exists(old_path):
        Logger.error(
            "Old configuration path `{0}` does not exist.".format(old_path))

    choice = prompt_yes_no(
        "/!\\ Are you sure to migrate old configuration `{0}` to `{1}`?".format(
            old_path, new_path
        ),
        force)

    if not choice:
        return

    if os.path.exists(new_path):
        choice = prompt_yes_no(
            "/!\\ Path `{0}` will be removed. Are you sure to continue?".format(
                new_path), force)
        if not choice:
            return

        shutil.rmtree(new_path)

    shutil.copytree(old_path, new_path)
    shutil.rmtree(old_path)


def user_ensure_config_path_exists(project_path, config_name=None):
    """
    Ensure that the user config path exists.

    :param project_path:    Project path (str)
    :param config_name:     Config name (str)
    """
    from docknv.session_handler import session_get_config_path
    global_session_path = session_get_config_path(project_path)
    user_session_path = user_get_local_docknv_path(project_path)

    if not os.path.exists(global_session_path):
        os.makedirs(global_session_path)
    if not os.path.exists(user_session_path):
        os.makedirs(user_session_path)

    if config_name:
        user_config_path = user_get_config_path(project_path, config_name)
        if not os.path.exists(user_config_path):
            os.makedirs(user_config_path)
