"""Docker API wrapper."""

from __future__ import unicode_literals

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

    **Context manager**
    """
    yield docker.from_env()


def docker_ps(client, project_name, namespace_name=None):
    """
    Get running container infos.

    :param client:          Client (Client)
    :param namespace_name:  Namespace name (str)
    :rtype: Info list (iterable)
    """
    containers = client.containers.list()
    status_lines = []

    container_filter = project_name + "_"
    if namespace_name:
        container_filter += namespace_name + "_"

    for container in containers:
        attrs = container.attrs
        state = attrs["State"]

        container_name = attrs["Name"][1:]
        if not container_name.startswith(container_filter):
            continue

        status_lines.append({
            "name": container_name,
            "status": state["Status"],
            "ports": " - ".join(list(attrs["NetworkSettings"]["Ports"].keys()))
        })

    return status_lines
