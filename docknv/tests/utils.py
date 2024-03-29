"""Test utilities."""

import tempfile
import shutil
from contextlib import contextmanager

from docknv.logger import Logger


@contextmanager
def using_temporary_directory(preserve=False):
    """
    Create a temporary directory.

    **Context manager**
    """
    directory = tempfile.mkdtemp()

    try:
        yield directory
    finally:
        if not preserve:
            shutil.rmtree(directory)


@contextmanager
def disable_logger():
    """
    Temporarily disable logger.

    **Context manager**
    """
    lvl = Logger.get_log_level()
    Logger.set_log_level("NONE")

    try:
        yield
    finally:
        Logger.set_log_level(lvl)


def copy_sample(sample, destination):
    """
    Copy a sample to a destination.

    :param sample:      Sample name (str)
    :param destination: Destination directory (str)
    :rtype: Output path (str)
    """
    output_path = "{0}/{1}".format(destination, sample)
    shutil.copytree("samples/{0}".format(sample), output_path)

    return output_path


def assert_cmd(cmd, value):
    """
    Assert a command.

    :param cmd:     Command (list)
    :param value:   Value (str)
    :rtype: True/False
    """
    return " ".join(cmd) == value
