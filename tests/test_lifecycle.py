"""Lifecycle handler tests."""

from __future__ import unicode_literals
import os

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample,
    assert_cmd
)

from docknv import lifecycle_handler

from docknv.user_handler import user_get_file_from_project
from docknv.project_handler import project_generate_compose, project_use_configuration


def _prepare_project(tempdir):
    user_path = os.path.join(tempdir, "user")
    os.makedirs(user_path)
    os.environ["DOCKNV_USER_PATH"] = user_path

    project_path = copy_sample("sample01", tempdir)
    project_generate_compose(project_path, "hello", "test", "default", "test")
    project_generate_compose(project_path, "hello", "test2", "default", "test2")
    project_use_configuration(project_path, "test")
    return project_path


def test_lifecycle_schema_build():
    """Test lifecycle schema build."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename = user_get_file_from_project("sample01", "docker-compose.yml", "test")

        # Schema build no-cache, push
        build_cmd, push_cmd = lifecycle_handler.lifecycle_schema_build(
            project_path, no_cache=True, push_to_registry=True)

        expected_build_cmd, expected_push_cmd = (
            'docker-compose -f {0} --project-directory {1} build test_hello-world --no-cache'.format(
                config_filename, project_path),
            'docker-compose -f {0} --project-directory {1} push test_hello-world'.format(
                config_filename, project_path))

        assert assert_cmd(build_cmd, expected_build_cmd)
        assert assert_cmd(push_cmd, expected_push_cmd)

        # Schema build w/ cache, no push
        build_cmd = lifecycle_handler.lifecycle_schema_build(
            project_path, no_cache=False, push_to_registry=False)
        assert len(build_cmd) == 1
        build_cmd = build_cmd[0]

        expected_build_cmd = (
            'docker-compose -f {0} --project-directory {1} build test_hello-world'.format(
                config_filename, project_path))

        assert assert_cmd(build_cmd, expected_build_cmd)


def test_lifecycle_schema_start():
    """Test lifecycle schema start."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename = user_get_file_from_project("sample01", "docker-compose.yml", "test")

        # Schema start
        cmd = lifecycle_handler.lifecycle_schema_start(project_path)

        expected_cmd = (
            'docker-compose -f {0} --project-directory {1} up -d'.format(
                config_filename, project_path)
        )

        assert assert_cmd(cmd, expected_cmd)


def test_lifecycle_schema_stop():
    """Test lifecycle schema stop."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename = user_get_file_from_project("sample01", "docker-compose.yml", "test")

        # Schema stop
        cmd = lifecycle_handler.lifecycle_schema_stop(project_path)

        expected_cmd = (
            'docker-compose -f {0} --project-directory {1} down'.format(
                config_filename, project_path)
        )

        assert assert_cmd(cmd, expected_cmd)


def test_lifecycle_schema_restart():
    """Test lifecycle schema restart."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename = user_get_file_from_project("sample01", "docker-compose.yml", "test")

        # Schema restart
        cmd = lifecycle_handler.lifecycle_schema_restart(project_path, force=False)

        expected_cmd = (
            'docker-compose -f {0} --project-directory {1} restart'.format(
                config_filename, project_path)
        )

        assert assert_cmd(cmd, expected_cmd)

        # Schema restart force
        stop_cmd, start_cmd = lifecycle_handler.lifecycle_schema_restart(project_path, force=True)

        expected_stop_cmd, expected_start_cmd = (
            'docker-compose -f {0} --project-directory {1} down'.format(
                config_filename, project_path),
            'docker-compose -f {0} --project-directory {1} up -d'.format(
                config_filename, project_path)
        )

        assert assert_cmd(stop_cmd, expected_stop_cmd)
        assert assert_cmd(start_cmd, expected_start_cmd)


# BUNDLE ###########


def test_lifecycle_bundle_start():
    """Test lifecycle bundle start."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename1 = user_get_file_from_project("sample01", "docker-compose.yml", "test")
        config_filename2 = user_get_file_from_project("sample01", "docker-compose.yml", "test2")

        # Bundle start
        cmds = lifecycle_handler.lifecycle_bundle_start(project_path, ["test", "test2"])

        expected_cmds = (
            'docker-compose -f {0} --project-directory {1} up -d'.format(
                config_filename1, project_path),
            'docker-compose -f {0} --project-directory {1} up -d'.format(
                config_filename2, project_path)
        )

        for i in range(len(cmds)):
            assert assert_cmd(cmds[i], expected_cmds[i])


def test_lifecycle_bundle_stop():
    """Test lifecycle bundle stop."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename1 = user_get_file_from_project("sample01", "docker-compose.yml", "test")
        config_filename2 = user_get_file_from_project("sample01", "docker-compose.yml", "test2")

        # Bundle start
        cmds = lifecycle_handler.lifecycle_bundle_stop(project_path, ["test", "test2"])

        expected_cmds = (
            'docker-compose -f {0} --project-directory {1} down'.format(
                config_filename1, project_path),
            'docker-compose -f {0} --project-directory {1} down'.format(
                config_filename2, project_path)
        )

        for i in range(len(cmds)):
            assert assert_cmd(cmds[i], expected_cmds[i])


def test_lifecycle_bundle_restart():
    """Test lifecycle bundle restart."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename1 = user_get_file_from_project("sample01", "docker-compose.yml", "test")
        config_filename2 = user_get_file_from_project("sample01", "docker-compose.yml", "test2")

        # Bundle restart force
        cmds = lifecycle_handler.lifecycle_bundle_restart(project_path, ["test", "test2"], force=True)
        expected_cmds = (
            (
                'docker-compose -f {0} --project-directory {1} down'.format(
                    config_filename1, project_path),
                'docker-compose -f {0} --project-directory {1} up -d'.format(
                    config_filename1, project_path)
            ),
            (
                'docker-compose -f {0} --project-directory {1} down'.format(
                    config_filename2, project_path),
                'docker-compose -f {0} --project-directory {1} up -d'.format(
                    config_filename2, project_path)
            )
        )

        for i in range(len(cmds)):
            assert assert_cmd(cmds[i][0], expected_cmds[i][0])
            assert assert_cmd(cmds[i][1], expected_cmds[i][1])

        # Bundle restart no-force
        cmds = lifecycle_handler.lifecycle_bundle_restart(project_path, ["test", "test2"])
        expected_cmds = (
            'docker-compose -f {0} --project-directory {1} restart'.format(
                config_filename1, project_path),
            'docker-compose -f {0} --project-directory {1} restart'.format(
                config_filename2, project_path)
        )

        for i in range(len(cmds)):
            assert assert_cmd(cmds[i], expected_cmds[i])


def test_lifecycle_bundle_build():
    """Test lifecycle bundle build."""
    with using_temporary_directory() as tempdir:
        project_path = _prepare_project(tempdir)
        config_filename1 = user_get_file_from_project("sample01", "docker-compose.yml", "test")
        config_filename2 = user_get_file_from_project("sample01", "docker-compose.yml", "test2")

        # Bundle start
        cmds = lifecycle_handler.lifecycle_bundle_build(project_path, ["test", "test2"], push_to_registry=True)

        expected_cmds = (
            (
                'docker-compose -f {0} --project-directory {1} build test_hello-world'.format(
                    config_filename1, project_path),
                'docker-compose -f {0} --project-directory {1} push test_hello-world'.format(
                    config_filename1, project_path)
            ),
            (
                'docker-compose -f {0} --project-directory {1} build test2_hello-world'.format(
                    config_filename2, project_path),
                'docker-compose -f {0} --project-directory {1} push test2_hello-world'.format(
                    config_filename2, project_path)
            )
        )

        for i in range(len(cmds)):
            assert assert_cmd(cmds[i][0], expected_cmds[i][0])
            assert assert_cmd(cmds[i][1], expected_cmds[i][1])

# MACHINE ##########
