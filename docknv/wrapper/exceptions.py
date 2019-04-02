"""Wrapper exceptions."""


class FailedCommandExecution(Exception):
    """Failed command execution."""

    def __init__(self, cause):
        """Init."""
        message = f"failed command execution: {cause}"
        super(FailedCommandExecution, self).__init__(message)


class StoppedCommandExecution(Exception):
    """Stopped command execution."""

    def __init__(self, cause):
        """Init."""
        message = f"stopped command execution: {cause}"
        super(StoppedCommandExecution, self).__init__(message)
