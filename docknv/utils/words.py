"""
Words utilities
"""

import os
import codecs
import random


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
