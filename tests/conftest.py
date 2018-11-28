"""Conftest."""

import os


def pytest_configure(config):
    """Configure."""
    os.environ["DOCKNV_FAKE_WRAPPER"] = '1'
    os.environ["DOCKNV_TEST_ID"] = '1'
    os.environ["DOCKNV_TEST_USERNAME"] = '1'
