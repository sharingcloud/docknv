"""
Volume handler tests
"""

import unittest

from docknv.volume_handler import VolumeHandler


class TestVolumeHandler(unittest.TestCase):
    """
    Volume handler tests
    """

    def test_extract_bad_format(self):
        """
        Should raise an exception when extracting volume from bad string.
        """
        with self.assertRaises(RuntimeError):
            VolumeHandler.extract_from_line("pouet")

    def test_extract_correct(self):
        """
        Should work on this extraction examples.
        """
        obj = VolumeHandler.extract_from_line("./local:/local")

        self.assertTrue(obj.is_relative, "Should be relative")
        self.assertFalse(obj.is_absolute, "Should not be absolute")
        self.assertFalse(obj.is_named, "Should not be named")
        self.assertEqual(obj.host_path, "./local")
        self.assertEqual(obj.container_path, "/local")
        self.assertEqual(obj.mode, "rw", "Should set default volume to 'rw'")

        obj = VolumeHandler.extract_from_line("/abs:/abs:ro")

        self.assertFalse(obj.is_relative, "Should not be relative")
        self.assertTrue(obj.is_absolute, "Should be absolute")
        self.assertFalse(obj.is_named, "Should not be named")
        self.assertEqual(obj.host_path, "/abs")
        self.assertEqual(obj.container_path, "/abs")
        self.assertEqual(obj.mode, "ro")

        obj = VolumeHandler.extract_from_line("pouet:/pouet:rw")

        self.assertFalse(obj.is_relative, "Should not be relative")
        self.assertFalse(obj.is_absolute, "Should not be absolute")
        self.assertTrue(obj.is_named, "Should be named")
        self.assertEqual(obj.host_path, "pouet")
        self.assertEqual(obj.container_path, "/pouet")
        self.assertEqual(obj.mode, "rw")
