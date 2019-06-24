"""Composefile methods."""

import os


def composefile_get_composefile_paths(project_path):
    """
    Read composefiles from project.

    :param project_path:    Project path (str)
    :rtype: Composefile path list
    """
    from docknv.project.exceptions import MalformedProject

    composefiles_path = os.path.join(project_path, "composefiles")
    if not os.path.isdir(composefiles_path):
        raise MalformedProject("missing 'composefiles' folder in project")

    return [
        os.path.join(project_path, "composefiles", d)
        for d in os.listdir(composefiles_path)
    ]
