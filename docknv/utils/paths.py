"""Path utilities."""

import os
import shutil


def get_lower_basename(path):
    """
    Get the basename of a path, lowercased.

    :param path:    Path (str)
    :rtype: Lowercase basename (str)
    """
    return os.path.basename(os.path.normpath(os.path.abspath(path))).lower()


def create_path_or_replace(path_to_create):
    """
    Create or replace path.

    :param path_to_create:   Path to create (str)
    """
    if os.path.exists(path_to_create):
        shutil.rmtree(path_to_create)

    create_path_tree(path_to_create)


def create_path_tree(path_to_create):
    """
    Create a path tree if folders does not exist.

    :param path_to_create:   Path to create (str)
    """
    current = ""
    for path in path_to_create.split("/"):
        current = os.path.join(current, path)
        # Root
        if current == "":
            current = "/"
            continue

        if not os.path.exists(current):
            os.makedirs(current)
