"""Template exceptions."""


class MalformedTemplate(Exception):
    """Malformed template."""

    def __init__(self, cause):
        """Init."""
        message = f"Malformed template: {cause}"
        super(MalformedTemplate, self).__init__(message)


class MissingTemplate(Exception):
    """Missing template."""

    def __init__(self, path):
        """Init."""
        message = f"Missing template: {path}"
        super(MissingTemplate, self).__init__(message)
