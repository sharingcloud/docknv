"""Entry point."""

import sys
import traceback

from docknv.logger import Logger, LoggerError
from docknv.wrapper import FailedCommandExecution

from .shell import Shell
from .custom import MalformedCommand


def docknv_entry_point():
    """Entry point for docknv."""
    shell = Shell()

    try:
        return shell.run(sys.argv[1:])
    except BaseException as e:
        if isinstance(e, LoggerError):
            pass
        elif isinstance(e, SystemExit):
            pass
        elif isinstance(e, FailedCommandExecution) or (
            isinstance(e, MalformedCommand)
        ):
            Logger.error(str(e), crash=False)
            sys.exit(1)
        else:
            Logger.error(traceback.format_exc(), crash=False)
            sys.exit(1)
