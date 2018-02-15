"""Command handler tests."""

from __future__ import unicode_literals

import os

from docknv import command_handler

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

    assert command_handler.command_get_config(CONFIG, "pouet") == {}
    assert command_handler.command_get_config(CONFIG, "test") == {"var1": 5}
    assert command_handler.command_get_config(CONFIG, "test2") == {"var2": 7, "var3": "coucou"}


def test_command_get_context():
    """Command get context."""
    with using_temporary_directory() as tempdir:
        user_path = os.path.join(tempdir, "user")
        os.makedirs(user_path)
        os.environ["DOCKNV_USER_PATH"] = user_path

        project_path = copy_sample("sample01", tempdir)
        command_handler.command_get_context(project_path)

        assert os.path.exists(os.path.join(user_path, 'sample01', 'docknv.yml'))
