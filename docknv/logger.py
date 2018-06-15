"""Simple logger."""

from __future__ import print_function

import time
import sys

import colorama
import six

from colorama import Fore, Style

INIT_TIME = time.time()
VERBOSE = True

colorama.init()


class LoggerError(Exception):
    """Logger error."""


class Logger(object):
    """Simple logger."""

    LOGGER_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "NONE"]
    current_level = "DEBUG"

    @staticmethod
    def set_log_level(value):
        """
        Set the current log level.

        :param value:   Value (str)
        """
        Logger.current_level = value

    @staticmethod
    def get_log_level():
        """
        Get the current log level.

        :rtype: Current log level (str)
        """
        return Logger.current_level

    @staticmethod
    def log(msg_type, message, color):
        """
        Write a standard log entry.

        :param msg_type:     Message type (str)
        :param message:      Message content (str)
        :param color:        Message color (color)
        """
        if Logger._is_active(msg_type):
            current_time = time.time() - INIT_TIME
            logged_str = "{0}[{1}] [{2}] {3}{4}".format(
                color,
                Logger._round_time(current_time),
                msg_type,
                message,
                Style.RESET_ALL
            )

            if six.PY2:
                logged_str = logged_str.decode('utf-8', errors='replace') # noqa
            print(logged_str)

    @staticmethod
    def info(message, color=Fore.GREEN):
        """
        Info log.

        :param message:      Message content (str)
        :param color:        Message color (color) (default: GREEN)
        """
        Logger.log("INFO", message, color)

    @staticmethod
    def error(message, color=Fore.RED, crash=True):
        """
        Error log.

        If 'crash', exit program.

        :param message:      Message content (str)
        :param color:        Message color (color) (default: RED)
        :param crash:        Crash the program (bool) (default: True)
        """
        Logger.log("ERROR", message, color)
        if crash:
            raise LoggerError(message)

    @staticmethod
    def debug(message, color=Fore.CYAN):
        """
        Debug log.

        :param message:      Message content (str)
        :param color:        Message color (color) (default: CYAN)
        """
        Logger.log("DEBUG", message, color)

    @staticmethod
    def warn(message, color=Fore.YELLOW):
        """
        Warn log.

        :param message:      Message content (str)
        :param color:        Message color (color) (default: YELLOW)
        """
        Logger.log("WARN", message, color)

    @staticmethod
    def raw(message, color=None, linebreak=True):
        """
        Raw log. No line break.

        :param message:      Message content (str)
        :param color:        Message color (color?) (default: None)
        :param linebreak:    Insert linebreak (bool) (default: True)
        """
        if color:
            message = "{0}{1}{2}".format(color, message, Style.RESET_ALL)

        if six.PY2:
            message = unicode(message) # noqa

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

    @staticmethod
    def _is_active(level):
        if level not in Logger.LOGGER_LEVELS:
            raise RuntimeError("Bad log level value: {0}".format(level))

        idx = Logger.LOGGER_LEVELS.index(level)
        curr_idx = Logger.LOGGER_LEVELS.index(Logger.current_level)
        return idx >= curr_idx
