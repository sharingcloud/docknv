"""
Utils tests
"""

import unittest
import mock
import six

from contextlib import contextmanager

from docknv.utils import prompt_yes_no, create_path_tree


class TestUtils(unittest.TestCase):
    """
    Utils tests
    """

    @staticmethod
    @contextmanager
    def mock_input(value):
        if six.PY2:
            with mock.patch("__builtin__.raw_input", return_value=value):
                yield
        else:
            with mock.patch("builtins.input", return_value=value):
                yield

    def test_prompt_yes_no(self):
        """
        Test prompt_yes_no function
        """

        with TestUtils.mock_input("y"):
            self.assertTrue(prompt_yes_no("Pouet", force=False))
            self.assertTrue(prompt_yes_no("Pouet", force=True))

        with TestUtils.mock_input("n"):
            self.assertFalse(prompt_yes_no("Pouet", force=False))
            self.assertTrue(prompt_yes_no("Pouet", force=True))

    def test_create_path_tree(self):
        """
        Test create_path_tree function
        """

        with mock.patch("os.path.exists", return_value=False):
            with mock.patch("os.makedirs"):
                create_path_tree("./pouet")
