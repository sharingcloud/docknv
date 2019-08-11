"""Entry point."""

import sys
import traceback

from docknv.logger import Logger, LoggerError
from docknv.wrapper import FailedCommandExecution, StoppedCommandExecution

from .custom import MalformedCommand
from .shell import Shell


def docknv_entry_point():
    """Entry point for docknv."""
    shell = Shell()

    try:
        return shell.run(sys.argv[1:])
    except BaseException as e:
        if isinstance(e, (LoggerError, SystemExit)):
            sys.exit(1)
        elif isinstance(
            e,
            (
                FailedCommandExecution,
                StoppedCommandExecution,
                MalformedCommand,
            ),
        ):
            Logger.error(str(e), crash=False)
            sys.exit(1)
        else:
            Logger.error(traceback.format_exc(), crash=False)
            sys.exit(1)
