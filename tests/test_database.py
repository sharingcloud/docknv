"""Database tests."""

import os

import pytest

from docknv.database import (
    Configuration, MissingConfiguration, PermissionDenied
)

from docknv.project import (
    Project
)

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)

from docknv.utils.ioutils import (
    io_open
)

from docknv.utils.serialization import (
    yaml_ordered_load
)


def test_empty_database():
    """Empty db test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        project = Project.load_from_path(project_path)
        database = project.database
        assert len(database) == 0

        database.show_configuration_list()
        database.save()


def test_database():
    """Database test."""
    database_file = """\
first:
    services:
        - ser1
        - ser2
    networks:
        - net1
    volumes:
        - vol1
    environment: default
    user: test
    namespace:
second:
    services:
        - ser3
    networks: []
    volumes: []
    environment: default
    user: tost
    namespace: hello\
    """

    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # Create directory
        os.makedirs(os.path.join(project_path, ".docknv"))
        with open(
            os.path.join(project_path, ".docknv", ".docknv.yml"),
            mode="w"
        ) as handle:
            handle.write(database_file)

        project = Project.load_from_path(project_path)
        database = project.database
        assert len(database) == 2

        first = database.get_configuration("first")
        os.makedirs(first.get_path())
        assert os.path.exists(first.get_path())

        config = Configuration(
            database,
            "toto",
            user="test",
            environment="default",
            services=["toto"],
            volumes=[],
            networks=[],
            namespace=None
        )
        database.create_configuration(config)

        assert len(database) == 3

        assert database["first"].has_permission()
        assert not database["second"].has_permission()
        assert database["toto"].has_permission()

        assert database.includes_configuration("first")
        assert not database.includes_configuration("pouet")

        first = database.get_configuration("first")
        first.environment = "test1"
        database.update_configuration(first)

        # Unknown name should fail
        first.name = "test1"
        with pytest.raises(MissingConfiguration):
            database.update_configuration(first)
        first.name = "first"

        # Second edit should fail
        second = database.get_configuration("second")
        second.environment = "erg"
        with pytest.raises(PermissionDenied):
            database.update_configuration(second)

        # Pouet does not exist
        with pytest.raises(MissingConfiguration):
            database.get_configuration("pouet")

        # Serialization test
        database.serialize()
        # Show test
        database.show_configuration_list()
        # Save test
        database.save()

        # Paths test
        assert first.get_path() == os.path.join(
            project_path, ".docknv", "test", "first")
        assert second.get_path() == os.path.join(
            project_path, ".docknv", "tost", "second")
        assert first.get_composefile_path() == os.path.join(
            project_path, ".docknv", "test", "first", "docker-compose.yml")
        assert second.get_composefile_path() == os.path.join(
            project_path, ".docknv", "tost", "second", "docker-compose.yml")

        # Removal test
        project.session.set_current_configuration("first")
        database.remove_configuration("first", force=True)
        assert project.session.get_current_configuration() is None
        assert len(database) == 2

        with pytest.raises(MissingConfiguration):
            database.remove_configuration("pouet", force=True)
        with pytest.raises(PermissionDenied):
            database.remove_configuration("second", force=True)

        assert len(database) == 2


def test_old_database():
    """Test old database."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample03", tempdir)

        # Values key should be present
        db_file = os.path.join(project_path, ".docknv", ".docknv.yml")
        with io_open(db_file) as handle:
            data = yaml_ordered_load(handle.read())
            assert "values" in data

        project = Project.load_from_path(project_path)
        assert len(project.database) == 2

        with io_open(db_file) as handle:
            data = yaml_ordered_load(handle.read())
            assert "values" not in data
