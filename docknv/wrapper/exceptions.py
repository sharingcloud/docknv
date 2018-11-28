"""Wrapper exceptions."""


class FailedCommandExecution(Exception):
    """Failed command execution."""

    def __init__(self, cause):
        """Init."""
        message = f"failed command execution: {cause}"
        super(FailedCommandExecution, self).__init__(message)
