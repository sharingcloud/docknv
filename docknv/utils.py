"""
docknv utilities
"""

from __future__ import print_function

import codecs
import os
import random
import shutil
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


def generate_config_name(config_list):
    """
    Generate a unique config name.
    :return: Config name
    """

    if os.path.isfile("/usr/share/dict/words"):
        success = False
        key = None

        while not success:
            word1 = get_random_word_from_dictionary()
            word2 = get_random_word_from_dictionary()
            key = "{0}_{1}".format(word1, word2)

            if key not in config_list:
                success = True

        return key

    return "config_{0}".format(len(config_list) + 1)


def get_random_word_from_dictionary():
    """
    Get a random word from a dictionary
    :return: Random word
    """

    with codecs.open("/usr/share/dict/words", encoding="utf-8", mode="rt") as handle:
        words = handle.readlines()

    return random.choice(words).lower()[:-1]


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
