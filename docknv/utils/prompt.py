"""
Prompt utilities
"""

from __future__ import print_function

import six


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
