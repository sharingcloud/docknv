"""
docknv utilities
"""

from __future__ import print_function
import os
import shutil
import six
import sys
import imp


def get_input():
    """
    Return the user input
    """

    if six.PY2:
        return raw_input()
    else:
        return input()


def prompt_yes_no(message, force=False):
    """
    Prompt the user for a yes/no answer.

    @param message  Message to display
    @param force    Force choice to True
    """

    if force:
        return True

    choice = "_"

    while choice not in "yYnN":
        print(message + " (Y/N)", end=" ")
        choice = get_input()

    if choice in "yY":
        return True
    else:
        return False


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
        if not os.path.exists(current):
            os.makedirs(current)

