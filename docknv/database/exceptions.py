"""Database exceptions."""


class MissingActiveConfiguration(Exception):
    """Missing active configuration."""

    def __init__(self):
        """Init."""
        message = f"no active configuration set"
        super(MissingActiveConfiguration, self).__init__(message)


class MissingConfiguration(Exception):
    """Missing configuration."""

    def __init__(self, name):
        """Init."""
        message = f"Unknown configuration {name}"
        super(MissingConfiguration, self).__init__(message)


class PermissionDenied(Exception):
    """Permission denied."""

    def __init__(self, user=None):
        """Init."""
        message = f"Permission denied for user {user}"
        super(PermissionDenied, self).__init__(message)
