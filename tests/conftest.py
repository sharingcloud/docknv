"""Conftest."""

import os


def pytest_configure(config):
    """Configure."""
    os.environ["DOCKNV_FAKE_WRAPPER"] = '1'
