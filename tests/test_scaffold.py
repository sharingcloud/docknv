"""Scaffolding tests."""

import os

import pytest

from docknv.utils.ioutils import io_open

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample,
)

from docknv.tests.mocking import (
    mock_input
)


from docknv.scaffolder import (
    scaffold_environment,
    scaffold_environment_copy,
    scaffold_image,
    scaffold_ignore,
    scaffold_config,
    scaffold_project,

    IGNORE_FILE_CONTENT,
    CONFIG_FILE_CONTENT
)

from docknv.environment import (
    env_get_yaml_path,
    Environment,
)

from docknv.image import (
    image_check_dockerfile,
    image_load_in_memory
)

from docknv.project import (
    MissingProject
)


def test_scaffold_environment():
    """Environment scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold new environment
        scaffold_environment(project_path, "toto")
        assert os.path.isfile(env_get_yaml_path(project_path, "toto"))
        content = Environment.load_from_project(project_path, "toto")
        assert len(content) == 0

        # Scaffold new environment with values
        scaffold_environment(project_path, "tata", {"POUET": 6})
        assert os.path.isfile(env_get_yaml_path(project_path, "tata"))
        content = Environment.load_from_project(project_path, "tata")
        assert len(content) == 1
        assert content["POUET"] == 6

        # Scaffold existing environment
        with mock_input("n"):
            scaffold_environment(project_path, "tata", {"POUET": 6})
        with mock_input("n"):
            scaffold_environment(project_path, "tata", {"POUET": 6})

        # Copy existing environment
        scaffold_environment_copy(project_path, "tata", "tutu")
        assert os.path.isfile(env_get_yaml_path(project_path, "tutu"))
        content = Environment.load_from_project(project_path, "tutu")
        assert len(content) == 1
        assert content["POUET"] == 6


def test_scaffold_image():
    """Image scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold new image
        scaffold_image(project_path, "postgres", "postgres")
        assert image_check_dockerfile(project_path, "postgres")
        content = image_load_in_memory(project_path, "postgres")
        assert content == "FROM postgres:latest\n"

        # Overwrite
        with mock_input("y"):
            scaffold_image(project_path, "postgres", "postgres")
        with mock_input("n"):
            scaffold_image(project_path, "postgres", "postgres")

        # Scaffold image version
        scaffold_image(project_path, "pouet", "ici/pouet", "2.1.1")
        assert image_check_dockerfile(project_path, "pouet")
        content = image_load_in_memory(project_path, "pouet")
        assert content == "FROM ici/pouet:2.1.1\n"

        # Scaffold in empty folder
        empty_folder = os.path.join(tempdir, "toto")
        os.makedirs(empty_folder)
        scaffold_image(empty_folder, "pouet", "ici/pouet")


def test_scaffold_ignore():
    """Ignorefile scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold ignore
        scaffold_ignore(project_path)
        ignorefile = os.path.join(project_path, ".gitignore")
        with io_open(ignorefile, mode="rt") as handle:
            content = handle.read()
        assert content == IGNORE_FILE_CONTENT

        with mock_input("y"):
            scaffold_ignore(project_path)
        with mock_input("n"):
            scaffold_ignore(project_path)

        with pytest.raises(MissingProject):
            scaffold_ignore("/a/b/c/d")


def test_scaffold_config():
    """Config scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold config
        scaffold_config(project_path)
        configfile = os.path.join(project_path, "config.yml")

        with io_open(configfile, mode="rt") as handle:
            content = handle.read()

        assert content == CONFIG_FILE_CONTENT


def test_scaffold_project():
    """Project scaffold tests."""
    with using_temporary_directory() as tempdir:
        # New playground
        project_path = os.path.join(tempdir, "playground")

        with mock_input("y"):
            scaffold_project(project_path)
        with mock_input("n"):
            scaffold_project(project_path)

        assert os.path.isfile(os.path.join(project_path, ".gitignore"))
        assert os.path.isfile(os.path.join(project_path, "config.yml"))
        assert os.path.isdir(os.path.join(project_path, "envs"))
        assert os.path.isdir(os.path.join(project_path, "composefiles"))
        assert os.path.isdir(os.path.join(project_path, "images"))
        assert os.path.isdir(os.path.join(project_path, "data"))
        assert os.path.isdir(os.path.join(project_path, "data", "files"))

        assert os.path.isfile(env_get_yaml_path(project_path, "default"))
