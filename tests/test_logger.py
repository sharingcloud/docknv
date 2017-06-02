"""
Logger tests
"""

import sys
import unittest

from StringIO import StringIO
from contextlib import contextmanager

from docknv.logger import Logger, Fore


class TestLogger(unittest.TestCase):
    """
    Logger tests
    """

    @staticmethod
    @contextmanager
    def using_temp_stdout():
        """
        Temporary change the stdout
        """

        old_stdout = sys.stdout
        logger = StringIO()

        sys.stdout = logger
        yield logger
        sys.stdout = old_stdout

    def test_log(self):
        """
        Simple logger tests
        """

        with TestLogger.using_temp_stdout() as stdout:
            # Info
            Logger.info("Pouet")
            self.assertTrue("[INFO]" in stdout.getvalue(),
                            "Should be an info message")

        with TestLogger.using_temp_stdout() as stdout:
            # Warn
            Logger.warn("Pouet")
            self.assertTrue("[WARN]" in stdout.getvalue(),
                            "Should be a warn message")

        with TestLogger.using_temp_stdout() as stdout:
            # Debug
            Logger.debug("Pouet")
            self.assertTrue("[DEBUG]" in stdout.getvalue(),
                            "Should be a debug message")

        with TestLogger.using_temp_stdout() as stdout:
            # Raw
            Logger.raw("Pouet pouet")
            self.assertTrue(stdout.getvalue().endswith(
                "\n"), "Should end with a newline")

        with TestLogger.using_temp_stdout() as stdout:
            Logger.raw("Pouet", color=Fore.BLUE)
            self.assertTrue(stdout.getvalue().startswith(
                "\x1b[34m"), "Should start with blue color")

        with TestLogger.using_temp_stdout() as stdout:
            Logger.raw("Pouet pouet", linebreak=False)
            self.assertTrue(not stdout.getvalue().endswith(
                "\n"), "Should not end with a newline")

        with TestLogger.using_temp_stdout() as stdout:
            # Error
            Logger.error("Pouet", crash=False)
            with self.assertRaises(RuntimeError):
                Logger.error("Pouet", crash=True)
