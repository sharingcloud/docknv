"""Image handler test."""

import os

from docknv.image import (
    image_get_dockerfile_path,
    image_check_dockerfile,
    image_load_in_memory
)


def test_image_get_dockerfile_path():
    """Get dockerfile path."""
    # Simple test
    assert image_get_dockerfile_path(".", "test") == os.path.join(
        ".", "images", "test", "Dockerfile")
    assert image_get_dockerfile_path("samples/sample01", "portainer") == \
        os.path.join("samples/sample01", "images", "portainer", "Dockerfile")

    # Structured test
    assert image_get_dockerfile_path(".", "app/test") == os.path.join(
        ".", "images", "app/test", "Dockerfile")


def test_image_check_dockerfile():
    """Check dockerfile."""
    assert image_check_dockerfile("samples/sample01", "portainer")
    assert not image_check_dockerfile("samples/sample01", "pouet")


def test_image_load_in_memory():
    """Load in memory."""
    assert not image_load_in_memory("samples/sample01", "pouet")
    assert image_load_in_memory("samples/sample01", "portainer") == \
        "FROM portainer/portainer:latest\n"
    assert image_load_in_memory("samples/sample01", "app/hello-world") == \
        "FROM hello-world:latest\n"
