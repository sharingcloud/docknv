"""Utils tests."""

import mock

from docknv.tests.mocking import mock_input

from docknv.utils.prompt import prompt_yes_no
from docknv.utils.paths import create_path_tree


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
