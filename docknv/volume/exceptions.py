"""Volume exceptions."""


class MalformedVolume(Exception):
    """Malformed volume."""

    def __init__(self, cause):
        """Init."""
        message = f"malformed volume: {cause}"
        super(MalformedVolume, self).__init__(message)
