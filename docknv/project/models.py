"""Project data."""

from contextlib import contextmanager
import os

from docknv.user import UserSession, user_get_username
from docknv.database import Database, MissingActiveConfiguration
from docknv.schema import SchemaCollection
from docknv.lifecycle import ProjectLifecycle

from docknv.utils.ioutils import io_open
from docknv.utils.serialization import yaml_ordered_load

from .methods import (
    project_get_name_from_path,
    project_get_config_path,
    project_is_valid,
)

from .exceptions import (
    MissingProject,
)


class Project(object):
    """Project."""

    def __init__(self, project_path, config_data):
        """
        Project data constructor.

        :param project_path:     Project path (str)
        :param config_data:      Config data (dict)
        """
        self.project_path = project_path
        self.project_name = project_get_name_from_path(project_path)
        self.schemas = SchemaCollection.load_from_data(
            config_data.get("schemas", []))
        self.config_data = config_data

        self.session = UserSession.load_from_path(
            user_get_username(), project_path)
        self.database = Database.load_from_project(self)
        self.lifecycle = ProjectLifecycle(self)

    def __repr__(self):
        """Repr."""
        import pprint
        return pprint.pformat({
            "project_path": self.project_path,
            "project_name": self.project_name,
            "schemas": self.schemas,
            "config_data": self.config_data
        }, indent=4)

    def get_command_parameters(self, command=None):
        """
        Get command parameters.

        :param command: Command (str?)
        """
        data = self.config_data.get('commands', None)
        if not data:
            return {}

        # Return all parameters
        if command is None:
            return data
        else:
            command_data = data.get(command)
            if not command_data:
                return {}

            return command_data

    def set_current_configuration(self, config_name):
        """
        Set current configuration.

        :param config_name: Config name (str?)
        """
        if config_name is not None:
            self.database.get_configuration(config_name)

        self.session.set_current_configuration(config_name)
        self.session.save()

    def ensure_current_configuration(self):
        """Ensure current configuration."""
        active_conf = self.get_current_configuration()
        if active_conf:
            return self.database.get_configuration(active_conf)
        else:
            raise MissingActiveConfiguration()

    @contextmanager
    def using_temporary_configuration(self, config_name):
        """
        Use a temporary configuration.

        :param config_name: Config name (str)
        """
        old_config = self.get_current_configuration()
        self.set_current_configuration(config_name)
        yield
        self.set_current_configuration(old_config)

    def unset_current_configuration(self):
        """Unset current configuration."""
        self.session.unset_current_configuration()
        self.session.save()

    def get_current_configuration(self):
        """Get current configuration."""
        return self.session.get_current_configuration()

    @staticmethod
    def validate_path(project_path):
        """
        Validate project path.

        :param project_path:    Project path
        """
        return project_is_valid(project_path)

    @classmethod
    def load_from_path(cls, project_path):
        """
        Load from project path.

        :param project_path:    Project path
        """
        project_file_path = project_get_config_path(project_path)

        if os.path.isfile(project_file_path):
            with io_open(
                project_file_path, encoding="utf-8", mode="r"
            ) as handle:
                config_data = yaml_ordered_load(handle.read())
        else:
            raise MissingProject(project_path)

        return cls(project_path, config_data)
