"""Project exceptions."""


class MissingProject(Exception):
    """Missing project."""

    def __init__(self, path):
        """Init."""
        message = f"Missing project at path {path}"
        super(MissingProject, self).__init__(message)


class MalformedProject(Exception):
    """Malformed project."""

    def __init__(self, cause):
        """Init."""
        message = f"Malformed project: {cause}"
        super(MalformedProject, self).__init__(message)
