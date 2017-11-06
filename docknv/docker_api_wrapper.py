"""Docker API wrapper."""


from contextlib import contextmanager

import docker


def text_ellipse(s, maxlen):
    """
    Apply ellipse on text at `maxlen`.

    :param s:       Text (str)
    :param maxlen:  Max length (int)
    :rtype: Text (str)
    """
    return s[:maxlen] + (s[maxlen:] and '..')


@contextmanager
def using_docker_client():
    """
    Open a Docker client.

    :coroutine:
    """
    yield docker.from_env()


def docker_ps(client, config_name=None):
    """
    Get running container infos.

    :param client:      Client (Client)
    :param config_name: Config name (str)
    :rtype: Info list (iterable)
    """
    containers = client.containers.list()
    status_lines = []
    for container in containers:
        attrs = container.attrs
        state = attrs["State"]
        status_lines.append({
            "name": attrs["Name"][1:],
            "status": state["Status"],
            "ports": " ".join(list(attrs["NetworkSettings"]["Ports"].keys()))
        })

    return status_lines
