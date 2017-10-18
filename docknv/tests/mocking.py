"""Mocking utility."""

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
def using_temp_stdout():
    """
    Temporary change the stdout.

    **Coroutine**
    """
    old_stdout = sys.stdout
    logger = StringIO()

    sys.stdout = logger
    yield logger
    sys.stdout = old_stdout


@contextmanager
def mock_input(value):
    """
    Mocking input for a value.

    :param value:    Value (str)
    **Coroutine**
    """
    if six.PY2:
        with mock.patch("__builtin__.raw_input", return_value=value):
            yield
    else:
        with mock.patch("builtins.input", return_value=value):
            yield
