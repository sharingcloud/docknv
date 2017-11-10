"""Scaffolding tests."""

import os

from docknv.utils.ioutils import io_open

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample,
    disable_logger
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

from docknv.environment_handler import (
    env_yaml_check_file,
    env_yaml_load_in_memory
)

from docknv.image_handler import (
    image_check_dockerfile,
    image_load_in_memory
)


def test_scaffold_environment():
    """Environment scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold new environment
        with disable_logger():
            scaffold_environment(project_path, "toto")
            assert env_yaml_check_file(project_path, "toto")
            content = env_yaml_load_in_memory(project_path, "toto")
            assert len(content) == 0

        # Scaffold new environment with values
        with disable_logger():
            scaffold_environment(project_path, "tata", {"POUET": 6})
            assert env_yaml_check_file(project_path, "tata")
            content = env_yaml_load_in_memory(project_path, "tata")
            assert len(content) == 1
            assert content["POUET"] == 6

        # Copy existing environment
        with disable_logger():
            scaffold_environment_copy(project_path, "tata", "tutu")
            assert env_yaml_check_file(project_path, "tutu")
            content = env_yaml_load_in_memory(project_path, "tutu")
            assert len(content) == 1
            assert content["POUET"] == 6


def test_scaffold_image():
    """Image scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold new image
        with disable_logger():
            scaffold_image(project_path, "postgres", "postgres")
            assert image_check_dockerfile(project_path, "postgres")
            content = image_load_in_memory(project_path, "postgres")
            assert content == "FROM postgres:latest\n"

        # Scaffold image version
        with disable_logger():
            scaffold_image(project_path, "pouet", "ici/pouet", "2.1.1")
            assert image_check_dockerfile(project_path, "pouet")
            content = image_load_in_memory(project_path, "pouet")
            assert content == "FROM ici/pouet:2.1.1\n"


def test_scaffold_ignore():
    """Ignorefile scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold ignore
        with disable_logger():
            scaffold_ignore(project_path, force=True)
            ignorefile = os.path.join(project_path, ".gitignore")

            with io_open(ignorefile, mode="rt") as handle:
                content = handle.read()

            assert content == IGNORE_FILE_CONTENT


def test_scaffold_config():
    """Config scaffold tests."""
    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)

        # Scaffold config
        with disable_logger():
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
        os.makedirs(project_path)

        with disable_logger():
            with mock_input("y"):
                scaffold_project(project_path)

            assert os.path.isfile(os.path.join(project_path, ".gitignore"))
            assert os.path.isfile(os.path.join(project_path, "config.yml"))
            assert os.path.isdir(os.path.join(project_path, "envs"))
            assert os.path.isdir(os.path.join(project_path, "composefiles"))
            assert os.path.isdir(os.path.join(project_path, "images"))
            assert os.path.isdir(os.path.join(project_path, "data"))
            assert os.path.isdir(os.path.join(project_path, "data", "files"))

            assert env_yaml_check_file(project_path, "default")
