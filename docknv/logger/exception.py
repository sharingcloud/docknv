"""Logger exceptions."""


class LoggerError(Exception):
    """Logger error."""

    def __init__(self, cause):
        """Init."""
        message = f"Logger error: {cause}"
        super(LoggerError, self).__init__(message)
