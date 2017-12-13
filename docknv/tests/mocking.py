"""Mocking utility."""

from __future__ import unicode_literals

import sys
from contextlib import contextmanager

try:
    from io import StringIO
except ImportError:
    # Python 2
    from StringIO import StringIO

import six
import mock


@contextmanager
def using_temporary_stdout():
    """
    Temporarily change the stdout.

    **Context manager**
    """
    old_stdout = sys.stdout
    logger = StringIO()

    sys.stdout = logger
    yield logger
    sys.stdout = old_stdout


@contextmanager
def mock_input(value):
    """
    Mock input for a value.

    :param value:    Value (str)

    **Context manager**
    """
    if six.PY2:
        with mock.patch("__builtin__.raw_input", return_value=value):
            yield
    else:
        with mock.patch("builtins.input", return_value=value):
            yield
