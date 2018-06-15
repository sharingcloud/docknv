"""User handler tests."""

from __future__ import unicode_literals
import os

from docknv.tests.utils import (
    using_temporary_directory,
)


def test_get_local_docknv_path():
    """Get local docknv path."""
    from docknv.user_handler import user_get_username, user_get_local_docknv_path

    with using_temporary_directory() as tempdir:
        project_folder = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_folder

        uname = user_get_username()
        user_path = user_get_local_docknv_path(project_folder)
        assert user_path == os.path.join(
            project_folder, ".docknv", uname
        )


def test_get_config_path():
    """Get config path."""
    from docknv.user_handler import user_get_username, user_get_config_path

    with using_temporary_directory() as tempdir:
        project_folder = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_folder

        uname = user_get_username()
        proj_path = user_get_config_path(project_folder, "tutu")
        assert proj_path == os.path.join(
            project_folder, ".docknv", uname, "tutu")


def test_get_docknv_config_file():
    """Get docknv config file."""
    from docknv.user_handler import user_get_username, user_get_docknv_config_file

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        uname = user_get_username()
        docknv_path = user_get_docknv_config_file(project_path)
        assert docknv_path == os.path.join(
            project_path, ".docknv", uname, "docknv.yml")


def test_get_old_docknv_path():
    """Get old docknv path."""
    from docknv.user_handler import user_get_old_docknv_path

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH_OLD"] = project_path

        old_path = user_get_old_docknv_path("toto")

        assert old_path == os.path.join(
            project_path, "toto"
        )


def test_get_file_from_project():
    """Get file from project."""
    from docknv.user_handler import user_get_username, user_get_file_from_project

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path
        uname = user_get_username()

        file_path = user_get_file_from_project(project_path, "tutu.txt")
        assert file_path == os.path.join(
            project_path, ".docknv", uname, "tutu.txt")

        file_path = user_get_file_from_project(project_path, "tutu.txt", "tata")
        assert file_path == os.path.join(
            project_path, ".docknv", uname, "tata", "tutu.txt")


def test_ensure_config_path_exists():
    """Ensure config path exists."""
    from docknv.user_handler import user_get_username, user_ensure_config_path_exists
    uname = user_get_username()

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        user_ensure_config_path_exists(project_path)
        config_path = os.path.join(
            project_path, ".docknv", uname
        )

        assert os.path.exists(config_path)
        assert os.path.isdir(config_path)

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        user_ensure_config_path_exists(project_path, "config")
        config_path = os.path.join(
            project_path, ".docknv", uname, "config"
        )

        assert os.path.exists(config_path)
        assert os.path.isdir(config_path)


def test_read_write_docknv_config():
    """Read/Write docknv config."""
    from docknv.user_handler import (
        user_read_docknv_config,
        user_write_docknv_config
    )

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        config = user_read_docknv_config(project_path)
        assert config == {}

    with using_temporary_directory() as tempdir:
        os.environ["DOCKNV_USER_PATH"] = tempdir

        config = {"toto": "tutu"}
        user_write_docknv_config(project_path, config)

        read_config = user_read_docknv_config(project_path)
        assert read_config == config


def test_copy_file_to_config():
    """Copy file to config."""
    from docknv.user_handler import (
        user_get_username,
        user_copy_file_to_config
    )

    with using_temporary_directory() as tempdir:
        project_path = tempdir
        test_file = os.path.join(tempdir, "toto.txt")

        with open(test_file, mode="wt") as handle:
            handle.write("toto")

        os.environ["DOCKNV_USER_PATH"] = project_path
        user_copy_file_to_config(project_path, test_file)

        assert os.path.isfile(
            os.path.join(
                project_path, ".docknv", user_get_username(), "toto.txt"
            )
        )

        user_copy_file_to_config(project_path, test_file, "tutu")

        assert os.path.isfile(
            os.path.join(
                project_path, ".docknv", user_get_username(), "tutu", "toto.txt"
            )
        )


def test_migrate_config():
    """Migrate config."""
    from docknv.user_handler import (
        user_get_username,
        user_migrate_config
    )

    with using_temporary_directory() as tempdir:
        old_path = os.path.join(tempdir, "old")
        new_path = os.path.join(tempdir, "new")

        os.makedirs(old_path)
        os.makedirs(os.path.join(old_path, "toto"))
        os.makedirs(os.path.join(old_path, "toto", "tutu"))
        os.makedirs(new_path)

        os.environ["DOCKNV_USER_PATH"] = new_path
        os.environ["DOCKNV_USER_PATH_OLD"] = old_path

        user_migrate_config(new_path, "toto", force=True)

        # <proj>/.docknv/<user>/tutu
        output_path = os.path.join(new_path, ".docknv", user_get_username(), "tutu")
        assert os.path.isdir(output_path)
        assert not os.path.isdir(os.path.join(old_path, "toto"))
