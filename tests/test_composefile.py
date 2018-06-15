"""Composefile tests."""

import pytest

from docknv.logger import LoggerError
from docknv.composefile_handler import composefile_read

from docknv.tests.utils import (
    using_temporary_directory
)


def test_composefile_load():
    """Test composefile load."""
    with using_temporary_directory() as tempdir:
        # Should raise on error
        with pytest.raises(LoggerError):
            composefile_read(tempdir, 'toto.yml')