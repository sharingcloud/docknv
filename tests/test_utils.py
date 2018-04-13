"""Utils tests."""

from __future__ import unicode_literals

import mock

from docknv.tests.mocking import mock_input

from docknv.utils.prompt import prompt_yes_no
from docknv.utils.paths import create_path_tree, get_lower_basename


def test_prompt_yes_no():
    """Test prompt_yes_no function."""
    with mock_input("y"):
        assert prompt_yes_no("Pouet", force=False)
        assert prompt_yes_no("Pouet", force=True)

    with mock_input("n"):
        assert not prompt_yes_no("Pouet", force=False)
        assert prompt_yes_no("Pouet", force=True)


def test_create_path_tree():
    """Test create_path_tree function."""
    with mock.patch("os.path.exists", return_value=False):
        with mock.patch("os.makedirs"):
            create_path_tree("./pouet")


def test_get_lower_basename():
    """Test get_lower_basename."""
    import platform
    if platform.system() == 'Windows':
        assert get_lower_basename("C:\\Users\\Pouet\\MyFolderName") == "myfoldername"
    else:
        assert get_lower_basename("/hello/Folder/FolderName") == "foldername"
