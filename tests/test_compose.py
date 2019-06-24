"""Compose tests."""

import os

import pytest

from docknv.utils.ioutils import io_open

from docknv.compose import ComposeDefinition, MissingComposefile
from docknv.project import Project

from docknv.tests.utils import using_temporary_directory, copy_sample

CONFIG_DATA = """\
config:
    services: ["portainer", "pouet"]
    volumes: ["portainer"]
    networks: ["net"]
    environment: default
    user: test
    namespace:
config2:
    services: ["portainer", "pouet"]
    volumes: []
    networks: []
    environment: default
    user: test
    namespace: pouet
"""


def test_compose():
    """Compose test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)
        project_config_root = os.path.join(project_path, ".docknv")
        session_file_path = os.path.join(project_config_root, ".docknv.yml")

        os.makedirs(project_config_root)
        with io_open(session_file_path, mode="w") as handle:
            handle.write(CONFIG_DATA)

        project = Project.load_from_path(project_path)
        database = project.database

        compose = ComposeDefinition.load_from_project(project_path)
        assert len(compose.get_networks()) == 1
        assert len(compose.get_volumes()) == 1
        assert len(compose.get_services()) == 3

        test_path = os.path.join(project_path, "test.yml")
        compose.save_to_path(test_path)
        composeclone = ComposeDefinition.load_from_path(test_path)

        with pytest.raises(MissingComposefile):
            ComposeDefinition.load_from_path(
                os.path.join(project_path, "test2.yml")
            )

        assert compose.content == composeclone.content

        # Filter configuration
        conf = database.get_configuration("config")
        compose.apply_configuration(conf)
        assert len(compose.get_services()) == 2

        # Namespace
        conf2 = database.get_configuration("config2")
        compose = ComposeDefinition.load_from_project(project_path)
        compose.apply_configuration(conf2)
        assert len(compose.get_services()) == 2
