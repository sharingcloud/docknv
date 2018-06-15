"""Command handler tests."""

from __future__ import unicode_literals

import os

from docknv.command_handler import (
    command_get_config,
    command_get_context
)

from docknv.user_handler import (
    user_get_docknv_config_file
)

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)


def test_command_get_config():
    """Command get config."""
    CONFIG = {
        "commands": {
            "test": {
                "var1": 5
            },
            "test2": {
                "var2": 7,
                "var3": "coucou"
            }
        }
    }

    assert command_get_config(CONFIG, "pouet") == {}
    assert command_get_config(CONFIG, "test") == {"var1": 5}
    assert command_get_config(CONFIG, "test2") == {"var2": 7, "var3": "coucou"}


def test_command_get_context():
    """Command get context."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        os.environ["DOCKNV_USER_PATH"] = project_path
        user_config_file_path = user_get_docknv_config_file(project_path)

        command_get_context(project_path)
        assert os.path.exists(user_config_file_path)
