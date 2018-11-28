"""Misc tests."""

from docknv import version


def test_version():
    """Test version."""
    str(version.VERSION)
    str(version.__version__)
