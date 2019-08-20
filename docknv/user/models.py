"""User models."""

from contextlib import contextmanager
import os
import shutil
import time

from docknv.logger import Logger

from docknv.utils.ioutils import io_open
from docknv.utils.prompt import prompt_yes_no
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump

from .exceptions import ProjectLocked

LOCKFILE_CONTENT = "$"


class UserLock(object):
    """User lock."""

    def __init__(self, username, project_path):
        """Init."""
        self.username = username
        self.project_path = project_path

    def get_file(self):
        """Get lock file."""
        return f"{self.project_path}/.{self.username}.lock"

    @property
    def is_enabled(self):
        """Is lock enabled."""
        return os.path.exists(self.get_file())

    def lock(self):
        """Enable lock."""
        lockfile = self.get_file()
        if self.is_enabled:
            return False

        with open(lockfile, mode="w") as handle:
            handle.write(LOCKFILE_CONTENT)

        return True

    def unlock(self):
        """Disable lock."""
        lockfile = self.get_file()
        if self.is_enabled:
            try:
                os.remove(lockfile)
            except FileNotFoundError:
                # Already removed
                pass

        return True

    @contextmanager
    def try_lock(self, timeout=0):
        """
        Try to set the user lock.

        if timeout == 0:
            - Do not wait, raise on lock failure
        elif timeout > 0:
            - Try to lock until timeout
        else:
            - Try to lock until it is possible

        :param timeout: Timeout in seconds
        """
        start_time = time.time()
        message_shown = False

        while True:
            if self.lock():
                # OK, go!
                break
            else:
                if timeout == 0:
                    raise ProjectLocked(self.project_path)
                elif timeout > 0:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        raise ProjectLocked(self.project_path)

            # Sleep for 1 seconds
            time.sleep(1)

            if timeout == -1 and not message_shown:
                if time.time() - start_time > 3:
                    Logger.info(
                        f"Waiting for lockfile... If you know what you are doing, remove the file {self.get_file()}."
                    )
                    message_shown = True

        try:
            yield
        except BaseException as exc:
            self.unlock()
            raise exc

        self.unlock()


class UserPaths(object):
    """User paths."""

    def __init__(self, username, project_path):
        """Init."""
        self.username = username
        self.project_path = project_path

    def get_project_root(self):
        """Get project root."""
        return os.path.join(self.project_path, ".docknv")

    def get_user_root(self):
        """Get user root."""
        return os.path.join(self.project_path, ".docknv", self.username)

    def get_user_configuration_root(self, config_name):
        """
        Get configuration root.

        :param config_name: Config name (str)
        """
        return os.path.join(self.get_user_root(), config_name)

    def get_user_session_file_path(self):
        """Get user session file."""
        return os.path.join(self.get_user_root(), "docknv.yml")

    def get_file_path(self, path, config_name=None):
        """
        Get file from user root or user config.

        :param path:        File path (str)
        :param config_name: Config name (str?)
        """
        if not config_name:
            return os.path.join(self.get_user_root(), path)
        else:
            return os.path.join(
                self.get_user_configuration_root(config_name), path
            )


class UserSession(object):
    """User session."""

    def __init__(self, username, project_path):
        """Init."""
        self.username = username
        self.project_path = project_path
        self.session_data = {"current": None}

        self.lock = UserLock(username, project_path)
        self.paths = UserPaths(username, project_path)

    def get_lock(self):
        """Get project lock."""
        return self.lock

    def get_paths(self):
        """Get project paths."""
        return self.paths

    def set_current_configuration(self, config_name):
        """
        Set current configuration.

        :param config_name: Config name (str)
        """
        self.session_data["current"] = config_name

    def unset_current_configuration(self):
        """Unset current configuration."""
        self.session_data["current"] = None

    def get_current_configuration(self):
        """Get current configuration."""
        return self.session_data["current"]

    @classmethod
    def load_from_path(cls, username, project_path):
        """
        Load user session from path.

        :param username:        Username (str)
        :param project_path:    Project path (str)
        """
        session = cls(username, project_path)

        # Ensure config paths exists
        project_root = session.get_paths().get_project_root()
        if not os.path.exists(project_root):
            os.makedirs(project_root)
        user_root = session.get_paths().get_user_root()
        if not os.path.exists(user_root):
            os.makedirs(user_root)

        session_file = session.get_paths().get_user_session_file_path()
        if not os.path.exists(session_file):
            session.session_data = {"current": None}
        else:
            with io_open(session_file, mode="r") as handle:
                session.session_data = yaml_ordered_load(handle.read())

        return session

    def save(self):
        """Save session."""
        session_file = self.get_paths().get_user_session_file_path()
        with io_open(session_file, mode="w") as handle:
            handle.write(yaml_ordered_dump(self.session_data))

    def remove_path(self, config_name=None, force=False):
        """
        Remove path.

        :param config_name: Config name (str?)
        :param force:       Force (bool) (default: False)
        """
        if config_name:
            user_config_root = self.get_paths().get_user_configuration_root(
                config_name
            )
        else:
            user_config_root = self.get_paths().get_user_root()

        if not os.path.exists(user_config_root):
            Logger.info(
                f"user configuration folder {user_config_root} "
                f"does not exist"
            )
        else:
            if prompt_yes_no(
                f"/!\\ are you sure you want to remove the "
                f"user folder {user_config_root}?",
                force,
            ):
                shutil.rmtree(user_config_root)
                Logger.info(
                    f"user configuration folder `{user_config_root}` "
                    f"removed"
                )
