"""Environment models."""

from collections import OrderedDict
import json
import os

from docknv.logger import Logger, Fore
from docknv.project.exceptions import MalformedProject

from docknv.utils.serialization import yaml_ordered_load
from docknv.utils.ioutils import (
    io_open
)

from .methods import (
    env_get_yaml_path,
    env_yaml_resolve_variables
)

from .exceptions import (
    MissingEnvironment,
    ExistingEnvironment,
    UnresolvableEnvironment,
)

ENV_EXTENSION = ".env.yml"
ENV_OFFSET = len(ENV_EXTENSION)


class EnvironmentCollection(object):
    """Environment collection."""

    def __init__(self, project_path, environments=None):
        """
        Init.

        :param project_path:    Project path (str)
        :param environments:    Environments (dict)
        """
        self.project_path = project_path
        self.environments = environments

    def __len__(self):
        return len(self.environments)

    @classmethod
    def load_from_project(cls, project_path):
        """
        Load environments from projects.

        :param project_path:    Project path (str)
        """
        env_path = os.path.join(project_path, "envs")
        if not os.path.isdir(env_path):
            raise MalformedProject("missing envs folder")

        return cls(
            project_path, {
                f[:-ENV_OFFSET]: Environment.load_from_project(
                    project_path, f[:-ENV_OFFSET])
                for f in os.listdir(env_path)
                if f.endswith(".env.yml")})

    def get_environment(self, name):
        """
        Get environment from project.

        :param name:    Name (str)
        """
        if not self.includes_environment(name):
            raise MissingEnvironment(name)
        return self.environments[name]

    def get_environment_path(self, name):
        """
        Get environment path.

        :param name:    Name (str)
        """
        if not self.includes_environment(name):
            raise MissingEnvironment(name)
        return env_get_yaml_path(self.project_path, name)

    def includes_environment(self, name):
        """
        Is environment in list.

        :param name:    Name (str)
        """
        return name in self.environments

    def create_inherited_environment(self, source_name, target_name):
        """
        Create inherited environment.

        :param source_name:     Environment name to clone.
        :param target_name:     Target environment.
        """
        # Error checking
        if not self.includes_environment(source_name):
            raise MissingEnvironment(source_name)
        if self.includes_environment(target_name):
            raise ExistingEnvironment(target_name)

        target_path = env_get_yaml_path(self.project_path, target_name)
        with open(target_path, mode="w") as handle:
            handle.write(
                f"# Environment: {target_name}\n"
                "\n"
                f"imports: [{source_name}]\n"
                "environment:\n"
                "   # Add entries here\n"
            )

        self.environments[target_name] = Environment.load_from_project(
            self.project_path, target_name)
        return self.environments[target_name]

    def show_environments(self):
        """Show environments."""
        if len(self.environments) == 0:
            Logger.warn("no env file found")
        else:
            for name in self.environments.keys():
                Logger.raw(f"- Environment: {name}")


class Environment(object):
    """Environment."""

    def __init__(self, name, data=None):
        """
        Init.

        :param project_path:    Project path (str)
        :param name:            Name (str)
        :param data:            Data (dict)
        """
        self.name = name
        self.data = data or {}

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return self.data.__contains__(key)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    @classmethod
    def load_from_project(cls, project_path, name):
        """
        Load from project.

        :param project_path:    Project path (str)
        :param name:            Environment name (str)
        """
        imported = set()

        def _load(project_path, name):
            path = env_get_yaml_path(project_path, name)
            if not os.path.isfile(path):
                raise MissingEnvironment(name)

            loaded_env = OrderedDict()
            with io_open(path, mode="r") as handle:
                env_content = yaml_ordered_load(handle.read())

            # Detect imports
            imports = []
            if "imports" in env_content:
                for entry in env_content["imports"]:
                    imports.append(entry)

            for imported_env in imports:
                # Ignore self-import
                if imported_env == name:
                    continue
                # Ignore already imported envs
                if imported_env in imported:
                    continue

                # Save imported
                imported.add(imported_env)

                # Load imported environments
                result = _load(project_path, imported_env)
                for key, value in result.data.items():
                    loaded_env[key] = value

            # Load environment
            if env_content.get("environment", None):
                for key in env_content["environment"]:
                    loaded_env[key] = env_content["environment"][key]

            return Environment(name, loaded_env)

        env = _load(project_path, name)

        # Resolve environment
        try:
            loaded_env = env_yaml_resolve_variables(env.data)
            env.data = loaded_env
        except UnresolvableEnvironment as exc:
            Logger.warn(f"unresolvable environment: {name}")
            Logger.warn(f"  details: {str(exc)}")

        return env

    def export_as_key_values(self):
        """
        Export environment as key-values file content.

        :rtype: Key-values content (str)
        """
        export_string = ""
        for key, value in self.data.items():
            if isinstance(value, str):
                value = value.replace("\n", "\\n")
            elif value is None:
                value = ""
            else:
                value = json.dumps(value)
            export_string += key + "=" + value + "\n"

        return export_string

    def save_key_values_to_path(self, path):
        """
        Save export to path.

        :param path:    Path (str)
        """
        with io_open(path, mode="w") as handle:
            handle.write(self.export_as_key_values())

    def show(self):
        """Show."""
        Logger.raw(f"- Environment: {self.name}")
        for key, value in self.data.items():
            Logger.raw(f"  {key}", color=Fore.YELLOW, linebreak=False)
            Logger.raw(" = ", linebreak=False)
            Logger.raw(value, color=Fore.BLUE)
