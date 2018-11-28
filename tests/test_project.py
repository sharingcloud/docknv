"""Project tests."""

import os

import pytest

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)

from docknv.project import Project, MissingProject
from docknv.database import MissingActiveConfiguration


def test_project():
    """Test project."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # Path validation
        assert Project.validate_path(project_path)
        assert not Project.validate_path(os.path.join(project_path, "toto"))

        # Project load
        proj = Project.load_from_path(project_path)
        repr(proj)
        assert len(proj.schemas) == 2

        # Ensure current config
        with pytest.raises(MissingActiveConfiguration):
            proj.ensure_current_configuration()

        # Project load error
        with pytest.raises(MissingProject):
            Project.load_from_path(os.path.join(project_path, "toto"))

        # Get current config
        assert proj.get_current_configuration() is None

        # Create config
        proj.lifecycle.config.create("toto")

        # Set current config
        proj.set_current_configuration("toto")
        assert proj.get_current_configuration() == "toto"

        # Unset
        proj.unset_current_configuration()
        assert proj.get_current_configuration() is None

        # Temporary set
        with proj.using_temporary_configuration("toto"):
            assert proj.get_current_configuration() == "toto"
        assert proj.get_current_configuration() is None

        # Command config
        assert proj.get_command_parameters() == {}


def test_project2():
    """Test project2."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample02", tempdir)
        proj = Project.load_from_path(project_path)

        # Command config
        assert proj.get_command_parameters() == \
            {"notebook": {"service": "ipython"}}
        assert proj.get_command_parameters("notebook") == \
            {"service": "ipython"}
        assert proj.get_command_parameters("tutu") == {}
