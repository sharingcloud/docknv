import time
import colorama
import sys

INIT_TIME = time.time()

from colorama import Fore, Style
colorama.init()


def _round_time(t):
    s = str(float(t))
    l = 4

    pr, po = s.split(".")
    lpo = len(po)

    if lpo > l:
        po = po[:l]
    elif lpo < l:
        po = po + ("0" * (l - lpo))

    return ".".join(pr, po)


class Logger(object):

    @staticmethod
    def log(msg_type, message, color):
        t = time.time() - init_time
        print(color + "[{0}] [{1}] {2}".format(_round_time(t), msg_type, message))

    @staticmethod
    def info(message, color=Fore.GREEN):
        Logger.log("INFO", message, color)

    @staticmethod
    def error(message, color=Fore.RED, crash=True):
        Logger.log("ERROR", message, color)
        if crash:
            sys.exit(1)

    @staticmethod
    def debug(message, color=Fore.CYAN):
        Logger.log("DEBUG", message, color)

    @staticmethod
    def warn(message, color=Fore.YELLOW):
        Logger.log("DEBUG", message, color)

    @staticmethod
    def raw(message, color=None):
        if color:
            message = color + message + Style.RESET_ALL
        print(message)
