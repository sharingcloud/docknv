"""Logger tests."""

import pytest

from docknv.tests.mocking import using_temp_stdout

from docknv.logger import Logger, Fore


def test_log():
    """Simple logger tests."""
    with using_temp_stdout() as stdout:
        # Info
        Logger.info("Pouet")
        assert "[INFO]" in stdout.getvalue()
        print("Should be an info message")

    with using_temp_stdout() as stdout:
        # Warn
        Logger.warn("Pouet")
        assert "[WARN]" in stdout.getvalue()
        print("Should be a warn message")

    with using_temp_stdout() as stdout:
        # Debug
        Logger.debug("Pouet")
        assert "[DEBUG]" in stdout.getvalue()
        print("Should be a debug message")

    with using_temp_stdout() as stdout:
        # Raw
        Logger.raw("Pouet pouet")
        assert stdout.getvalue().endswith("\n")
        print("Should end with a newline")

    with using_temp_stdout() as stdout:
        Logger.raw("Pouet", color=Fore.BLUE)
        assert stdout.getvalue().startswith("\x1b[34m")
        print("Should start with blue color")

    with using_temp_stdout() as stdout:
        Logger.raw("Pouet pouet", linebreak=False)
        assert not stdout.getvalue().endswith("\n")
        print("Should not end with a newline")

    with using_temp_stdout() as stdout:
        # Error
        Logger.error("Pouet", crash=False)
        with pytest.raises(RuntimeError):
            Logger.error("Pouet", crash=True)
