"""Logger tests."""

import pytest

from docknv.tests.mocking import using_temporary_stdout
from docknv.logger import Logger, Fore, LoggerError

import six


def test_log():
    """Simple logger tests."""
    with using_temporary_stdout() as stdout:
        # Info
        Logger.info("Pouet")
        assert "[INFO]" in stdout.getvalue(), "Should be an info message"

    with using_temporary_stdout() as stdout:
        # Warn
        Logger.warn("Pouet")
        assert "[WARN]" in stdout.getvalue(), "Should be a warn message"

    with using_temporary_stdout() as stdout:
        # Debug
        Logger.debug("Pouet")
        assert "[DEBUG]" in stdout.getvalue(), "Should be a debug message"

    with using_temporary_stdout() as stdout:
        # Raw
        Logger.raw("Pouet pouet")
        assert stdout.getvalue().endswith("\n"), "Should end with a newline"

    with using_temporary_stdout() as stdout:
        Logger.raw("Pouet", color=Fore.BLUE)
        assert stdout.getvalue().startswith("\x1b[34m"), \
            "Should start with blue color"

    with using_temporary_stdout() as stdout:
        Logger.raw("Pouet pouet", linebreak=False)
        assert not stdout.getvalue().endswith("\n"), \
            "Should not end with a newline"

    with using_temporary_stdout() as stdout:
        Logger.info("H\x82h\x82 hoho")

        if six.PY2:
            res = "H\x82h\x82 hoho".decode('utf-8', errors='replace')
        else:
            res = "H\x82h\x82 hoho"

        assert res in stdout.getvalue(), "Should work"

    with using_temporary_stdout() as stdout:
        # Error
        Logger.error("Pouet", crash=False)
        with pytest.raises(LoggerError):
            Logger.error("Pouet", crash=True)
