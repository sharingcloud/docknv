"""Docker wrapper tests."""

from docknv.docker_wrapper import exec_docker, exec_compose


def _check_cmd(list_cmd, value):
    assert " ".join(list_cmd) == value


def test_exec_docker():
    """Exec docker tests."""
    _check_cmd(exec_docker('.', ['toto']), 'docker toto')
    _check_cmd(exec_docker('.', ['cp', 'tutu', 'tata']), 'docker cp tutu tata')


def test_exec_compose():
    """Exec docker compose."""
    _check_cmd(
        exec_compose('.', 'toto.yml', ['start']),
        'docker-compose -f toto.yml --project-directory . start')
    _check_cmd(
        exec_compose('.', 'toto.yml', ['stop', 'toto'], pretty=True),
        'docker-compose -f toto.yml --project-directory . stop toto')
