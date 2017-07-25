"""
Path utilities
"""

import os
import shutil


def create_path_or_replace(path_to_create):
    """
    Create or replace path.

    @param path_to_create   Path to create
    """

    if os.path.exists(path_to_create):
        shutil.rmtree(path_to_create)

    create_path_tree(path_to_create)


def create_path_tree(path_to_create):
    """
    Create a path tree if folders does not exist.

    @param path_to_create   Path to create
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
