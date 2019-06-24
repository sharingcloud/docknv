"""User methods."""

import os


def user_get_username():
    """
    Return the user username.

    :rtype: Username (str)
    """
    if os.environ.get("DOCKNV_TEST_USERNAME"):
        return "test"

    import getpass

    return getpass.getuser()


def user_get_username_from_id(user_id):
    """
    Get username from ID.

    :param user_id: User ID (int)
    """
    import pwd

    return pwd.getpwuid(user_id)[0]
