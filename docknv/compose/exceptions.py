"""Compose exceptions."""


class MissingComposefile(Exception):
    """Missing composefile."""

    def __init__(self, path):
        """Init."""
        message = f"Missing composefile: {path}"
        super(MissingComposefile, self).__init__(message)
