"""User handler tests."""

import os

import pytest

from docknv.tests.utils import using_temporary_directory

from docknv.user import (
    UserSession, ProjectLocked, user_get_username)


def test_real_ids():
    """Real IDs."""
    os.environ.pop("DOCKNV_TEST_ID")
    os.environ.pop("DOCKNV_TEST_USERNAME")

    assert user_get_username() != 'test'

    os.environ["DOCKNV_TEST_ID"] = "1"
    os.environ["DOCKNV_TEST_USERNAME"] = "1"


def test_session_paths():
    """Session paths."""
    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        session = UserSession.load_from_path(user_get_username(), project_path)
        paths = session.get_paths()

        assert paths.get_project_root() == \
            os.path.join(project_path, ".docknv")
        assert paths.get_user_root() == \
            os.path.join(project_path, ".docknv", "test")
        assert paths.get_user_configuration_root("toto") == \
            os.path.join(project_path, ".docknv", "test", "toto")
        assert paths.get_file_path("tutu") == \
            os.path.join(project_path, ".docknv", "test", "tutu")
        assert paths.get_file_path("tutu", "toto") == \
            os.path.join(project_path, ".docknv", "test", "toto", "tutu")


def test_session_config():
    """Session config."""
    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        session = UserSession.load_from_path(user_get_username(), project_path)

        # No configuration set
        assert session.get_current_configuration() is None

        # Setting one configuration
        session.set_current_configuration("pouet")
        assert session.get_current_configuration() == "pouet"

        # Unset
        session.unset_current_configuration()
        assert session.get_current_configuration() is None


def test_session_existing():
    """Session tests."""
    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        session_file = os.path.join(project_path, ".docknv", "test",
                                    "docknv.yml")
        os.makedirs(os.path.dirname(session_file))

        with open(session_file, mode="w") as handle:
            handle.write("current:")

        session = UserSession.load_from_path(user_get_username(), project_path)
        assert "current" in session.session_data
        assert session.session_data["current"] is None

        # Save
        session.save()

        # Remove
        session.remove_path(force=True)
        session.remove_path(force=True)
        session.remove_path("toto", force=True)


def test_session_lock():
    """Session lock."""
    with using_temporary_directory() as tempdir:
        project_path = tempdir
        os.environ["DOCKNV_USER_PATH"] = project_path

        session = UserSession.load_from_path(user_get_username(), project_path)
        lock = session.get_lock()

        assert lock.get_file() == f"{project_path}/.test.lock"

        # Lock should be disabled
        assert not lock.is_enabled
        # Unlocking should work
        assert lock.unlock()
        # Locking should work
        assert lock.lock()
        # Lock should be enabled
        assert lock.is_enabled

        # Lockfile should contain a $
        with open(lock.get_file(), mode="r") as handle:
            assert handle.read() == "$"

        # Relocking should return False
        assert not lock.lock()
        # But unlocking should work
        assert lock.unlock()
        # And is should be disabled
        assert not lock.is_enabled

        # And the file should not exist
        with pytest.raises(IOError):
            with open(lock.get_file(), mode="r") as handle:
                pass

        # Try-lock test
        with lock.try_lock():
            # Lock should be enabled
            assert lock.is_enabled

        # Now, lock should be disabled
        assert not lock.is_enabled

        # Second try-lock test
        assert lock.lock()
        with pytest.raises(ProjectLocked):
            with lock.try_lock():
                pass
        assert lock.is_enabled

        # Third try-lock test
        assert lock.unlock()
        with pytest.raises(RuntimeError):
            with lock.try_lock():
                assert lock.is_enabled
                # Raise exception
                raise RuntimeError("oops")

        # Should be unlocked
        assert not lock.is_enabled
