"""Lifecycle tests."""

import os

import pytest

from docknv.database import MissingActiveConfiguration
from docknv.project import Project

from docknv.utils.ioutils import io_open
from docknv.tests.utils import using_temporary_directory, copy_sample

CONFIG_DATA = """\
config:
    services: ["portainer", "pouet"]
    volumes: ["portainer"]
    networks: ["net"]
    environment: default
    user: test
    namespace:
config2:
    services: ["portainer", "pouet"]
    volumes: []
    networks: []
    environment: default
    user: test
    namespace: pouet
"""


def test_lifecycle():
    """Lifecycle test."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)
        project_config_root = os.path.join(project_path, ".docknv")
        session_file_path = os.path.join(project_config_root, ".docknv.yml")

        os.makedirs(project_config_root)
        with io_open(session_file_path, mode="w") as handle:
            handle.write(CONFIG_DATA)

        project = Project.load_from_path(project_path)
        lifecycle = project.lifecycle

        # Should raise, no active configuration
        with pytest.raises(MissingActiveConfiguration):
            lifecycle.config.start(dry_run=True)

        # Active tests
        project.set_current_configuration("config")
        lifecycle.config.start(dry_run=True)
        lifecycle.config.stop(dry_run=True)
        lifecycle.config.restart(dry_run=True)
        lifecycle.config.restart(force=True, dry_run=True)

        # Manual tests
        lifecycle.config.start(["config", "config2"], dry_run=True)

        # Service tests
        lifecycle.service.start("portainer", dry_run=True)
        lifecycle.service.stop("portainer", dry_run=True)
        lifecycle.service.restart("portainer", dry_run=True)
        lifecycle.service.restart("portainer", force=True, dry_run=True)
        lifecycle.service.execute("portainer", ["toto"], dry_run=True)
        lifecycle.service.execute("portainer", ["toto", "tutu"], dry_run=True)
        lifecycle.service.shell("portainer", dry_run=True)
        lifecycle.service.shell("portainer", shell="/bin/sh", dry_run=True)
        lifecycle.service.logs("portainer", dry_run=True)
        lifecycle.service.attach("portainer", dry_run=True)
        lifecycle.service.build("portainer", dry_run=True)

        # Update config
        lifecycle.config.update(dry_run=True)
        lifecycle.config.update("config2", dry_run=True)
        lifecycle.config.update(restart=True, dry_run=True)
        lifecycle.config.build(dry_run=True)

        lifecycle.config.update(environment="default", dry_run=True)
        lifecycle.config.update(services=[], dry_run=True)
        lifecycle.config.update(volumes=[], dry_run=True)
        lifecycle.config.update(networks=[], dry_run=True)
        lifecycle.config.update(namespace="", dry_run=True)
        lifecycle.config.update(namespace="hello", dry_run=True)

        # Create config
        lifecycle.config.create(name="tutu", services=["portainer"])
        lifecycle.config.ps(dry_run=True)
