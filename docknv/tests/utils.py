"""Test utilities."""

from __future__ import unicode_literals

import tempfile
import shutil
from contextlib import contextmanager

from docknv.logger import Logger


@contextmanager
def using_temporary_directory():
    """
    Create a temporary directory.

    **Context manager**
    """
    directory = tempfile.mkdtemp()
    yield directory
    shutil.rmtree(directory)


@contextmanager
def disable_logger():
    """
    Temporarily disable logger.

    **Context manager**
    """
    lvl = Logger.get_log_level()
    Logger.set_log_level("NONE")
    yield
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
