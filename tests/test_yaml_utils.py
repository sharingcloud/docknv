"""
YAML utils tests
"""

import unittest
import mock
import six

from docknv import yaml_utils


class TestYAMLUtils(unittest.TestCase):
    """
    YAML utils tests
    """

    def test_load(self):
        """
        Test ordered_load function
        """

        content = """
one:
    two: [a, b, c]
    three: 1
    four:
        - a
        - b
        - c
two:
    - pouet
aaa:
"""

        loaded = yaml_utils.ordered_load(content)

        self.assertEqual(loaded.keys()[0], "one")
        self.assertEqual(loaded.keys()[1], "two")

    def test_dump(self):
        """
        Test ordered_dump function
        """

        content = {
            "one": {
                "two": ["a", "b", "c"],
                "three": 1,
                "four": ["a", "b", "c"]
            },
            "two": ["pouet"],
            "aaa": None
        }

        dump = yaml_utils.ordered_dump(content)
        self.assertTrue(dump.startswith("aaa: null\n"))

    def test_merge(self):
        """
        Test merge function
        """

        content1 = {
            "one": ["a"],
            "two": {
                "a": 1
            },
            "three": {
                "a": ["A"],
                "b": {
                    "c": None
                }
            }
        }

        content2 = {
            "one": ["b"],
            "two": {
                "b": 2
            },
            "four": ["4"]
        }

        merge = yaml_utils.merge_yaml((content1, content2))

        self.assertIn("three", merge)
        self.assertIn("four", merge)

        merge_solo = yaml_utils.merge_yaml((content1,))

        self.assertEqual(merge_solo, content1)
        self.assertIsNone(yaml_utils.merge_yaml(()))
