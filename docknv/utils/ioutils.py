"""IO utils."""

import io
import os
from contextlib import contextmanager

from whichcraft import which
import six

EDITORS = ["code", "atom", "vim", "emacs", "nano"]


class NoEditorFound(Exception):
    """No editor found."""

    def __init__(self, editors):
        """Init."""
        editors_str = " ".join(editors)
        message = (
            f"none of the following editors has been found: {editors_str}"
        )
        super(NoEditorFound, self).__init__(message)


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
        with io.open(
            filename, mode, encoding=encoding, newline=newline
        ) as handle:
            yield handle
    else:
        with open(
            filename, mode, encoding=encoding, newline=newline
        ) as handle:
            yield handle


def check_for_command(command):
    """
    Check for command.

    :param command: Command (str)
    :rtype: True/False
    """
    return which(command) is not None


def get_editor_executable(override=None):
    """
    Get editor executable.

    Can be overridden with parameter.

    :param override:    Override editor (str?) (default: None)
    """
    editors_to_test = [os.environ.get("EDITOR", "")] + EDITORS
    if override:
        editors_to_test = [override] + editors_to_test

    # Filtering
    editors_to_test = [e for e in editors_to_test if e != ""]

    for editor in editors_to_test:
        if check_for_command(editor):
            return editor

    raise NoEditorFound(editors_to_test)
