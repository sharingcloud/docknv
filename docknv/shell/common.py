"""Common handler code."""

from docknv.project import Project


def exec_handler(cmd_name, args, handlers):
    """
    Execute handler.

    :param cmd_name:    Command name (str)
    :param args:        Arguments (iterable)
    :param handlers:    Handlers (dict)
    :rtype: Status
    """
    command = getattr(args, cmd_name + "_cmd").replace("-", "_")
    handler = "_handle_" + command
    if handler in handlers:
        return handlers[handler](args)


def load_project(project_path):
    """
    Load project.

    :param project_path:    Project path (str)
    """
    project = Project.load_from_path(project_path)
    return project
