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

    with using_temporary_directory() as tempdir:
        # Copy playground
        user_path = os.path.join(tempdir, "user")
        os.makedirs(user_path)
        os.environ["DOCKNV_USER_PATH"] = user_path

        project_path = copy_sample("sample01", tempdir)
        project_generate_compose(project_path, "hello", "test", "default", "test")

        assert os.path.exists(os.path.join(user_path, "sample01", "test", "environment.env"))
        assert os.path.exists(os.path.join(user_path, "sample01", "test", "docker-compose.yml"))
        assert not os.path.exists(os.path.join(user_path, "sample01", "docker-compose.yml"))
