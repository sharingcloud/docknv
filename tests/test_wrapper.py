"""Wrapper tests."""

import pytest

from docknv.wrapper import (
    exec_process,
    exec_process_with_output,
    exec_docker,
    exec_compose,
    FailedCommandExecution,
)


def test_wrapper():
    """Wrapper test."""
    ret = exec_process(["one", "two"], dry_run=True)
    assert ret == ["one", "two"]

    ret = exec_process(["echo", "toto"])
    assert ret == 0

    # Unknown
    with pytest.raises(FailedCommandExecution):
        exec_process(["ioaouroazuoriuaoiuroi"])

    # Return code != 0
    with pytest.raises(FailedCommandExecution):
        exec_process(["ls", "/a/b/c/d"])


def test_wrapper_with_output():
    """Output test."""
    ret = exec_process_with_output(["ls"])
    assert ret == 0

    ret = exec_process_with_output(["ls"], outfilter=lambda *args: True)
    assert ret == 0

    with pytest.raises(FailedCommandExecution):
        exec_process_with_output(["ls"], outfilter=lambda *args: 0 / 0)

    with pytest.raises(FailedCommandExecution):
        exec_process_with_output(["ls", "/a/b/c/d"])


def test_docker():
    """Docker test."""
    ret = exec_docker("/project", ["run", "-ti", "toto"], dry_run=True)
    assert ret == ["docker", "run", "-ti", "toto"]


def test_compose():
    """Compose test."""
    ret = exec_compose("/project", "./toto.yml", ["start"], dry_run=True)
    assert ret == [
        "docker-compose",
        "-f",
        "./toto.yml",
        "--project-directory",
        "/project",
        "start",
    ]

    ret = exec_compose(
        "/project", "./toto.yml", ["start"], pretty=True, dry_run=True
    )
    assert ret == [
        "docker-compose",
        "-f",
        "./toto.yml",
        "--project-directory",
        "/project",
        "start",
    ]
