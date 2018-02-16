"""Docker wrapper tests."""

from docknv.docker_wrapper import exec_docker, exec_compose
from docknv.tests.utils import assert_cmd


def test_exec_docker():
    """Exec docker tests."""
    assert assert_cmd(exec_docker('.', ['toto']), 'docker toto')
    assert assert_cmd(exec_docker('.', ['cp', 'tutu', 'tata']), 'docker cp tutu tata')


def test_exec_compose():
    """Exec docker compose."""
    assert assert_cmd(
        exec_compose('.', 'toto.yml', ['start']),
        'docker-compose -f toto.yml --project-directory . start')
    assert assert_cmd(
        exec_compose('.', 'toto.yml', ['stop', 'toto'], pretty=True),
        'docker-compose -f toto.yml --project-directory . stop toto')
