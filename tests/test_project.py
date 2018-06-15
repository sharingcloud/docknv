"""Project tests."""

from __future__ import unicode_literals
import os

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)


def test_project_read():
    """Test project read."""
    from docknv.project_handler import project_read

    with using_temporary_directory() as tempdir:
        # Copy playground
        project_path = copy_sample("sample01", tempdir)
        config = project_read(project_path)

        assert "composefiles/sample.yml" in config.composefiles
        assert "standard" in config.schemas
        assert "portainer" in config.schemas["standard"]["services"]


def test_project_generate_compose():
    """Test generate compose."""
    from docknv.project_handler import project_generate_compose
    from docknv.user_handler import user_get_username
    from docknv.session_handler import session_get_config_path

    with using_temporary_directory() as tempdir:
        # Copy playground
        uname = user_get_username()
        project_path = copy_sample("sample01", tempdir)
        os.environ["DOCKNV_USER_PATH"] = project_path
        session_path = session_get_config_path(project_path)

        project_generate_compose(project_path, "test", "hello", "default", "test")
        user_path = os.path.join(project_path, '.docknv', uname)

        assert os.path.isdir(session_path)
        assert os.path.isdir(user_path)

        assert os.path.isfile(
            os.path.join(user_path, "test", "environment.env"))
        assert os.path.isfile(
            os.path.join(user_path, "test", "docker-compose.yml"))
        assert os.path.isfile(
            os.path.join(session_path, ".docknv.yml"))
        assert not os.path.exists(
            os.path.join(user_path, "docker-compose.yml"))
