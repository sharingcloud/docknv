"""Template tests."""

import os

import pytest

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)

from docknv.utils.ioutils import io_open

from docknv.project import Project
from docknv.template import (
    MissingTemplate, MalformedTemplate,
    renderer_render_template
)


CONFIG_DATA = """\
config:
    services: ["portainer", "pouet"]
    volumes: ["portainer"]
    networks: ["net"]
    environment: default
    user: test
    namespace:
"""


def test_template():
    """Template test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)
        project_config_root = os.path.join(project_path, ".docknv")
        session_file_path = os.path.join(project_config_root, ".docknv.yml")

        os.makedirs(project_config_root)
        with io_open(session_file_path, mode="w") as handle:
            handle.write(CONFIG_DATA)

        project = Project.load_from_path(project_path)
        config = project.database.get_configuration("config")

        # Missing template file
        with pytest.raises(MissingTemplate):
            renderer_render_template("toto.sh", config)

        # Creating file
        templates_path = os.path.join(project_path, "data", "files")
        with io_open(
            os.path.join(templates_path, "toto.sh"), mode="w"
        ) as handle:
            handle.write("...")

        # Malformed template file
        with pytest.raises(MalformedTemplate):
            renderer_render_template("toto.sh", config)
