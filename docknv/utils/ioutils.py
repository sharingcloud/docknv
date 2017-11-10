"""IO utils."""

import io
from contextlib import contextmanager

import six


@contextmanager
def io_open(filename, mode="r", encoding="utf-8", newline=None):
    """
    Universal open function for Python 2/3.

    :param filename: Filename (str)
    :param mode:     Mode (str) (default: 'r')
    :param encoding: Encoding (str) (default: utf-8)

    **Context manager**
    """
    if six.PY2:
        with io.open(filename, mode, encoding=encoding, newline=newline) as handle:
            yield handle
    else:
        with open(filename, mode, encoding=encoding, newline=newline) as handle:
            yield handle
