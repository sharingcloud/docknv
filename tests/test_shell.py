"""Shell tests."""

import pytest

from docknv.shell import Shell

from docknv.utils.ioutils import NoEditorFound

from docknv.tests.mocking import mock_input
from docknv.tests.utils import using_temporary_directory, copy_sample


def test_shell():
    """Shell test."""
    shell = Shell()

    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        def run_shell(args=None):
            args = args or []
            shell.run(["--project", project_path, "--dry-run"] + args)

        with pytest.raises(SystemExit):
            run_shell([])

        # Config create
        run_shell(
            [
                "config",
                "create",
                "toto",
                "-e",
                "default",
                "-S",
                "portainer",
                "pouet",
                "-V",
                "portainer",
                "-N",
                "net",
            ]
        )

        # Start config
        run_shell(["config", "start"])
        # Stop config
        run_shell(["config", "stop"])
        # Restart config
        run_shell(["config", "restart"])
        run_shell(["config", "restart", "-f"])

        # Set config
        run_shell(["config", "set", "toto"])
        # Unset config
        run_shell(["config", "unset"])

        with mock_input("y"):
            # Remove config
            run_shell(["config", "rm", "toto"])

        # Status
        run_shell(["config", "status"])

        # Toto
        run_shell(
            [
                "config",
                "create",
                "toto",
                "-e",
                "default",
                "-S",
                "portainer",
                "pouet",
                "-V",
                "portainer",
                "-N",
                "net",
            ]
        )

        run_shell(["config", "status"])
        run_shell(["config", "update"])
        run_shell(["config", "ls"])
        run_shell(["config", "build"])
        run_shell(["config", "ps"])

        ########
        # Service

        run_shell(["service", "build", "portainer"])
        run_shell(["service", "start", "portainer"])
        run_shell(["service", "stop", "portainer"])
        run_shell(["service", "restart", "portainer"])
        run_shell(["service", "restart", "portainer", "-f"])
        run_shell(["service", "run", "portainer", "bash"])
        run_shell(["service", "run", "portainer", "-d", "bash"])
        run_shell(["service", "exec", "portainer", "bash"])
        run_shell(["service", "shell", "portainer"])
        run_shell(["service", "logs", "portainer"])
        run_shell(["service", "push", "portainer", "./a", "/b"])
        run_shell(["service", "pull", "portainer", "/a", "./b"])

        #######
        # Env

        run_shell(["env", "ls"])
        run_shell(["env", "show", "default"])

        try:
            run_shell(["env", "edit", "default"])
            run_shell(["env", "edit", "default", "-e", "vim"])
        except NoEditorFound:
            pass

        #########
        # Schemas

        run_shell(["schema", "ls"])

        ########
        # Scaffold

        run_shell(["scaffold", "project", f"{project_path}/toto"])
        run_shell(["scaffold", "image", "apzt", "otapti"])
        run_shell(["scaffold", "env", "tototo"])
        run_shell(["scaffold", "env", "totototo", "-i", "tototo"])

        ######
        # User

        try:
            run_shell(["user", "edit"])
            run_shell(["user", "edit", "-e", "vim"])
            run_shell(["user", "edit", "toto"])
        except NoEditorFound:
            pass

        run_shell(["user", "rm-lock"])

        with mock_input("y"):
            run_shell(["user", "clean", "toto"])
            run_shell(["user", "clean"])

        ########
        # Custom

        with pytest.raises(SystemExit):
            run_shell(["custom"])

        ########
        # Machine

        with pytest.raises(SystemExit):
            run_shell(["machine"])
        with pytest.raises(SystemExit):
            run_shell(["machine", "restart", "portainer"])


def test_commands():
    """Commands."""
    shell = Shell()

    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample02", tempdir)

        def run_shell(args=None):
            args = args or []
            shell.run(["--project", project_path, "--dry-run"] + args)

        with pytest.raises(SystemExit):
            run_shell(["custom"])

        with pytest.raises(SystemExit):
            run_shell(["custom", "notebook"])

        run_shell(
            [
                "config",
                "create",
                "toto",
                "-e",
                "default",
                "-S",
                "ipython",
                "pouet",
                "-N",
                "net",
            ]
        )

        run_shell(["custom", "notebook", "password"])
