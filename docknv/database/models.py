"""Database handler models."""

import copy
import os
import shutil

from docknv.environment import Environment

from docknv.logger import Logger, Fore

from docknv.utils.ioutils import io_open
from docknv.utils.prompt import prompt_yes_no
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump

from docknv.user import (
    UserSession, user_get_username, user_get_username_from_id
)

from docknv.compose import ComposeDefinition

from .methods import (
    database_get_database_path
)

from .exceptions import (
    MissingConfiguration,
    PermissionDenied,
)


class Configuration(object):
    """Configuration."""

    def __init__(self, database, name, user, environment="default",
                 services=None, volumes=None, networks=None, namespace=None):
        """Init."""
        self.database = database
        self.name = name
        self.user = user
        self.environment = environment
        self.services = [x for x in services] if services else []
        self.volumes = [x for x in volumes] if volumes else []
        self.networks = [x for x in networks] if networks else []
        self.namespace = namespace

        self.environment_data = Environment.load_from_project(
            database.project_path, environment)

        self.session = UserSession.load_from_path(
            user, database.project.project_path)

    @classmethod
    def load_from_data(cls, database, name, data):
        """
        Load from data.

        :param database:    Database
        :param name:        Config name (str)
        :param data:        Data (dict)
        :rtype: Configuration
        """
        # Old format
        if "schema" in data:
            data = copy.deepcopy(data)
            collection = database.project.schemas
            schema = collection.get_schema(data["schema"])
            data["services"] = schema.services
            data["volumes"] = schema.volumes
            data["networks"] = schema.networks

            # Handle IDs
            if isinstance(data["user"], int):
                data["user"] = user_get_username_from_id(data["id"])

            # Default namespace
            if data["namespace"] == "default":
                data["namespace"] = None

        return cls(
            database,
            name=name,
            user=data["user"],
            environment=data["environment"],
            services=data.get("services", []),
            volumes=data.get("volumes", []),
            networks=data.get("networks", []),
            namespace=data.get("namespace", None))

    def get_path(self):
        """Get configuration path."""
        return self.session.get_paths().get_user_configuration_root(self.name)

    def get_composefile_path(self):
        """Get composefile path."""
        return self.session.get_paths().get_file_path(
            "docker-compose.yml", self.name)

    def generate_composefile(self):
        """Generate composefile."""
        project_path = self.database.project.project_path

        compose_def = ComposeDefinition.load_from_project(project_path)
        compose_def.apply_configuration(self)
        compose_def.save_to_path(self.get_composefile_path())

    def has_permission(self, user=None):
        """
        Check permission.

        :param user: Username
        """
        if user is None:
            user = user_get_username()
        return bool(user == self.user)

    def serialize(self):
        """Serialize."""
        return {
            "user": self.user,
            "environment": self.environment,
            "services": self.services,
            "volumes": self.volumes,
            "networks": self.networks,
            "namespace": self.namespace
        }

    def show(self):
        """Show."""
        name = self.name
        namespace = self.namespace
        environment = self.environment
        services = self.services
        networks = self.networks
        volumes = self.volumes
        user = self.user

        Logger.raw(
            f"- Configuration '{name}'\n"
            f"  Namespace: {namespace}\n"
            f"  Environment: {environment}\n"
            f"  Services: {services}\n"
            f"  Volumes: {volumes}\n"
            f"  Networks: {networks}\n"
            f"  User: {user}\n\n",
            color=Fore.BLUE)


class Database(object):
    """Database model."""

    def __init__(self, project, data=None):
        """Init."""
        self.project = project
        self.project_path = project.project_path
        self.configurations = {}

        data = data or {}

        # Check for "values" key
        if "values" in data:
            # Old version, convert to new format !
            for name, conf in data["values"].items():
                self.configurations[name] = \
                    Configuration.load_from_data(self, name, conf)

            # Save to new version
            self.save()

        else:
            # New version
            for name, conf in data.items():
                self.configurations[name] = \
                    Configuration.load_from_data(self, name, conf)

    def __len__(self):
        """Len."""
        return len(self.configurations)

    def __getitem__(self, idx):
        """Getitem."""
        return self.configurations[idx]

    def serialize(self):
        """Serialize database contents."""
        output = {}
        for confname, conf in self.configurations.items():
            output[confname] = conf.serialize()
        return output

    def includes_configuration(self, config_name):
        """
        Check if configuration exist.

        :param config_name: Config name (str)
        """
        return config_name in self.configurations

    def get_configuration(self, config_name):
        """
        Get configuration.

        :param config_name: Config name (str)
        """
        if not self.includes_configuration(config_name):
            raise MissingConfiguration(config_name)
        return self.configurations[config_name]

    def create_configuration(self, config):
        """
        Create configuration.

        :param config:  Configuration
        """
        # Generate composefile
        config.generate_composefile()

        self.configurations[config.name] = config

    def update_configuration(self, config):
        """
        Update configuration.

        :param config:  Configuration
        """
        config_name = config.name

        # Check if configuration exists
        config = self.get_configuration(config_name)

        # Check for permission
        if not config.has_permission():
            raise PermissionDenied(user_get_username())

        # Generate composefile
        config.generate_composefile()

    def remove_configuration(self, config_name, force=False):
        """
        Remove configuration.

        :param config_name: Configuration name (str)
        :param force:       Force (bool) (default: False)
        """
        # Check if configuration exists
        config = self.get_configuration(config_name)

        # Check for permission
        if not config.has_permission():
            raise PermissionDenied(user_get_username())

        choice = prompt_yes_no(
            f"/!\\ are you sure you want to remove "
            f"configuration `{config_name}` ?",
            force)

        if choice:
            # Active session for current user
            if self.project.session.get_current_configuration() == config_name:
                self.project.session.unset_current_configuration()
                self.project.session.save()

            # Remove configuration path.
            path = config.get_path()
            print(path)
            if os.path.exists(path):
                shutil.rmtree(path)

            # Remove database entry
            del self.configurations[config_name]

            # Write database
            self.save()

    def show_configuration_list(self):
        """Show configuration list."""
        len_values = len(self.configurations)
        if len_values == 0:
            Logger.warn(
                "no configuration found. "
                "use `docknv config create` to generate configurations.")
        else:
            Logger.info("known configurations:")
            for conf in self.configurations.values():
                conf.show()

    @classmethod
    def load_from_project(cls, project):
        """
        Load from project.

        :param project:    Project
        """
        project_path = project.project_path
        project_file_path = database_get_database_path(project_path)

        if os.path.isfile(project_file_path):
            with io_open(
                project_file_path, encoding="utf-8", mode="r"
            ) as handle:
                config_data = yaml_ordered_load(handle.read())
            return cls(project, config_data)

        return cls(project, {})

    def save(self):
        """Save."""
        project_file_path = database_get_database_path(self.project_path)

        with io_open(project_file_path, encoding="utf-8", mode="w") as handle:
            handle.write(yaml_ordered_dump(self.serialize()))
