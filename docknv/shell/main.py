"""Entry poiny."""

import os
import sys
import traceback


def docknv_entry_point():
    """Entry point for docknv."""
    from docknv.command_handler import command_get_context
    from docknv.logger import Logger, LoggerError

    from .shell import Shell, register_handlers

    current_dir = os.getcwd()
    commands_dir = os.path.join(current_dir, "commands")
    commands_context = command_get_context(current_dir)
    shell = Shell()

    try:
        if os.path.exists(commands_dir):
            register_handlers(shell, current_dir, commands_dir, commands_context)

    except BaseException as e:
        Logger.error(e, crash=False)

    try:
        return shell.run(sys.argv[1:])
    except BaseException as e:
        if not isinstance(e, LoggerError):
            Logger.error(traceback.format_exc(), crash=False)
