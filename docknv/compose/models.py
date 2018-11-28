"""Compose models."""

import os

from docknv.utils.ioutils import io_open
from docknv.utils.serialization import (
    yaml_merge, yaml_ordered_load, yaml_ordered_dump
)

from docknv.template import renderer_render_compose_template

from .methods import composefile_get_composefile_paths
from .filtering import composefile_filter
from .namespacing import composefile_apply_namespace
from .resolution import (
    composefile_resolve_services, composefile_resolve_volumes
)

from .exceptions import MissingComposefile


class ComposeDefinition(object):
    """Compose definition."""

    def __init__(self, data=None):
        """Init."""
        self.content = data or {}

    @classmethod
    def load_from_path(cls, path):
        """
        Load from path.

        :param path:    Path (str)
        """
        if not os.path.isfile(path):
            raise MissingComposefile(path)

        with io_open(path, mode="r") as handle:
            content = yaml_ordered_load(handle.read())

        return cls(content)

    @classmethod
    def load_from_project(cls, project_path):
        """
        Load from project.

        :param project_path:    Project path (str)
        """
        paths = composefile_get_composefile_paths(project_path)
        composefile_content = {}

        for path in paths:
            with io_open(path, mode="r") as handle:
                content = yaml_ordered_load(handle.read())
                composefile_content = yaml_merge(
                    [composefile_content, content])

        return cls(composefile_content)

    def apply_configuration(self, config):
        """
        Apply configuration.

        - Filter services, volumes and networks.
        - Render composefile template
        - Resolve volumes
        - Resolve services
        - Apply namespaces

        :param config:  Configuration
        """
        content = self.content
        content = composefile_filter(content, config)
        content = renderer_render_compose_template(
            content, config.environment_data.data)
        content = composefile_resolve_services(content)
        content = composefile_resolve_volumes(content, config)
        content = composefile_apply_namespace(
            content, config.namespace, config.environment)

        self.content = content

    def get_services(self):
        """Get services."""
        return self.content.get("services", [])

    def get_volumes(self):
        """Get volumes."""
        return self.content.get("volumes", [])

    def get_networks(self):
        """Get networks."""
        return self.content.get("networks", [])

    def save_to_path(self, path):
        """
        Save content to path.

        :param path:    Path (str)
        """
        with io_open(path, mode="w") as handle:
            handle.write(yaml_ordered_dump(self.content))
