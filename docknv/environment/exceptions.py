"""Environment exceptions."""


class UnresolvableEnvironment(Exception):
    """Unresolvable environment."""

    def __init__(self, key, dep):
        """Init."""
        message = f"unresolvable dependency {dep} for key {key}"
        super(UnresolvableEnvironment, self).__init__(message)


class MissingEnvironment(Exception):
    """Missing environment."""

    def __init__(self, name):
        """Init."""
        message = f"missing environment: {name}"
        super(MissingEnvironment, self).__init__(message)


class ExistingEnvironment(Exception):
    """Existing environment."""

    def __init__(self, name):
        """Init."""
        message = f"environment {name} already exists"
        super(ExistingEnvironment, self).__init__(message)
