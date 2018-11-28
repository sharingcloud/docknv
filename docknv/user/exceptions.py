"""User exceptions."""


class ProjectLocked(Exception):
    """Project is locked."""

    def __init__(self, project):
        """Init."""
        message = f"current project {project} is currently locked " \
                  f"by another execution."

        super(ProjectLocked, self).__init__(message)
