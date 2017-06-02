"""
Simple logger
"""

from __future__ import print_function

import time
import sys

import colorama

from colorama import Fore, Style

INIT_TIME = time.time()
VERBOSE = True

colorama.init()


class Logger(object):
    """
    Simple logger
    """

    @staticmethod
    def log(msg_type, message, color):
        """
        Standard log
        """

        current_time = time.time() - INIT_TIME
        print(color + "[{0}] [{1}] {2}".format(Logger._round_time(current_time),
                                               msg_type, message) + Style.RESET_ALL)

    @staticmethod
    def info(message, color=Fore.GREEN):
        """
        Info log
        """

        Logger.log("INFO", message, color)

    @staticmethod
    def error(message, color=Fore.RED, crash=True):
        """
        Error log
        If 'crash', exit program
        """
        Logger.log("ERROR", message, color)
        if crash:
            raise RuntimeError(message)

    @staticmethod
    def debug(message, color=Fore.CYAN):
        """
        Debug log
        """
        Logger.log("DEBUG", message, color)

    @staticmethod
    def warn(message, color=Fore.YELLOW):
        """
        Warn log
        """
        Logger.log("WARN", message, color)

    @staticmethod
    def raw(message, color=None, linebreak=True):
        """
        Raw log. No line break.
        """
        if color:
            message = "{0}{1}{2}".format(color, message, Style.RESET_ALL)

        if linebreak:
            print(message)
        else:
            sys.stdout.write(message)

    @staticmethod
    def _round_time(seconds):
        string_seconds = str(float(seconds))
        length = 4

        prev_part, next_part = string_seconds.split(".")
        next_part_length = len(next_part)

        if next_part_length > length:
            next_part = next_part[:length]

        return ".".join([prev_part, next_part])
