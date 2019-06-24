"""Environment tests."""

import os
import shutil

import pytest

from docknv.environment import (
    Environment,
    EnvironmentCollection,
    MissingEnvironment,
    ExistingEnvironment,
)

from docknv.project import MalformedProject

from docknv.tests.utils import using_temporary_directory, copy_sample


def test_environment():
    """Environment test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # Simple
        envdefault = Environment.load_from_project(project_path, "default")
        assert "PORTAINER_OUTPUT_PORT" in envdefault
        assert envdefault["PORTAINER_OUTPUT_PORT"] == 9000
        assert envdefault["TEST_VALUE"] == "default"
        assert len(envdefault) == 11

        # Error
        with pytest.raises(MissingEnvironment):
            Environment.load_from_project(project_path, "toto")

        # Import
        env = Environment.load_from_project(project_path, "inclusion")
        assert env["TEST_VALUE"] == "inclusion"
        assert env["TEST_ONE"] == 1
        assert env["TEST_ONE_2"] == "toto:1"

        # Neg values
        assert env["TEST_NEG_ONE"] == 0
        assert env["TEST_NEG_BOOL1"] is False
        assert env["TEST_NEG_BOOL2"] is True
        assert env["TEST_NEG_ONE_2"] == env["TEST_ONE_2"]

        # Inheritance
        env = Environment.load_from_project(project_path, "inclusion2")
        assert env["TEST_VALUE"] == "inclusion2"
        assert env["TEST_ONE"] == 2
        assert env["TEST_ONE_2"] == "toto:2"

        # Loop test
        env = Environment.load_from_project(project_path, "inclusion-loop")
        assert env["POUET"] == "loop"

        # Multiple loop test
        env = Environment.load_from_project(project_path, "inclusion-loop-mul")
        assert env["POUET"] == "pouet"

        # Show
        env.show()

        # Key-value export
        envdefault.export_as_key_values()


def test_collection():
    """Collection test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # Load
        collection = EnvironmentCollection.load_from_project(project_path)
        assert len(collection) == 8

        # Show
        collection.show_environments()

        # Error get
        with pytest.raises(MissingEnvironment):
            collection.get_environment("toto")
        with pytest.raises(MissingEnvironment):
            collection.get_environment_path("toto")

        # Inheritance
        default_env = collection.get_environment("default")
        env = collection.create_inherited_environment("default", "default2")
        assert os.path.isfile(
            os.path.join(project_path, "envs", "default2.env.yml")
        )

        assert len(collection) == 9
        assert env.name == "default2"
        assert len(env) == len(default_env)

        # Inheritance errors
        with pytest.raises(MissingEnvironment):
            collection.create_inherited_environment("pouet", "pouet2")
        with pytest.raises(ExistingEnvironment):
            collection.create_inherited_environment("default", "default")
        with pytest.raises(ExistingEnvironment):
            collection.create_inherited_environment("inclusion", "default")


def test_collection_error():
    """Collection test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # Remove envs
        shutil.rmtree(os.path.join(project_path, "envs"))

        # Load
        with pytest.raises(MalformedProject):
            EnvironmentCollection.load_from_project(project_path)

        # Create envs
        os.makedirs(os.path.join(project_path, "envs"))
        collection = EnvironmentCollection.load_from_project(project_path)

        # Show
        collection.show_environments()
