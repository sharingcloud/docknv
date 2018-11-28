"""Volume tests."""

import pytest

from docknv.volume import Volume, MalformedVolume
from docknv.user import UserSession


def test_extract_bad_format():
    """Should raise an exception when extracting volume from bad string."""
    with pytest.raises(MalformedVolume):
        Volume.load_from_entry("pouet")


def test_extract_correct():
    """Should work on this extraction examples."""
    obj = Volume.load_from_entry("./local:/local")

    assert obj.is_relative, "Should be relative"
    assert not obj.is_absolute, "Should not be absolute"
    assert not obj.is_named, "Should not be named"
    assert obj.host_path == "./local"
    assert obj.container_path == "/local"
    assert obj.mode == "rw", "Should set default volume to 'rw'"

    obj = Volume.load_from_entry("/abs:/abs:ro")

    assert not obj.is_relative, "Should not be relative"
    assert obj.is_absolute, "Should be absolute"
    assert not obj.is_named, "Should not be named"
    assert obj.host_path == "/abs"
    assert obj.container_path == "/abs"
    assert obj.mode == "ro"

    obj = Volume.load_from_entry("pouet:/pouet:rw")

    assert not obj.is_relative, "Should not be relative"
    assert not obj.is_absolute, "Should not be absolute"
    assert obj.is_named, "Should be named"
    assert obj.host_path == "pouet"
    assert obj.container_path == "/pouet"
    assert obj.mode == "rw"

    # str check
    str(obj) == "pouet:/pouet:rw"

    # Windows check
    obj = Volume.load_from_entry("C:/toto:/toto:ro", system="Windows")
    assert obj.is_absolute


def test_namespace():
    """Namespace tests."""
    obj = Volume.load_from_entry("toto:/toto:rw")
    session = UserSession("test", "/project")

    assert obj.get_namespaced_path(session, "static", "config") == \
        "/project/.docknv/test/config/data/static/toto"

    assert obj.get_namespaced_path(session, "shared", "config") == \
        "data/global/toto"
