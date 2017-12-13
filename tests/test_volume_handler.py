"""Volume handler tests."""

from __future__ import unicode_literals

import pytest

from docknv.volume_handler import volume_extract_from_line


def test_extract_bad_format():
    """Should raise an exception when extracting volume from bad string."""
    with pytest.raises(RuntimeError):
        volume_extract_from_line("pouet")


def test_extract_correct():
    """Should work on this extraction examples."""
    obj = volume_extract_from_line("./local:/local")

    assert obj.is_relative, "Should be relative"
    assert not obj.is_absolute, "Should not be absolute"
    assert not obj.is_named, "Should not be named"
    assert obj.host_path == "./local"
    assert obj.container_path == "/local"
    assert obj.mode == "rw", "Should set default volume to 'rw'"

    obj = volume_extract_from_line("/abs:/abs:ro")

    assert not obj.is_relative, "Should not be relative"
    assert obj.is_absolute, "Should be absolute"
    assert not obj.is_named, "Should not be named"
    assert obj.host_path == "/abs"
    assert obj.container_path == "/abs"
    assert obj.mode == "ro"

    obj = volume_extract_from_line("pouet:/pouet:rw")

    assert not obj.is_relative, "Should not be relative"
    assert not obj.is_absolute, "Should not be absolute"
    assert obj.is_named, "Should be named"
    assert obj.host_path == "pouet"
    assert obj.container_path == "/pouet"
    assert obj.mode == "rw"
