"""Entry poiny."""

import os
import sys
import traceback


def _extract_context():
    args = sys.argv
    path = os.getcwd()
    for c in ("-C", "--context"):
        try:
            idx = args.index(c)
        except ValueError:
            continue

        if idx == len(args) - 1:
            continue
        else:
            # Return next argument
            return args[idx + 1]

    return path


def docknv_entry_point():
    """Entry point for docknv."""
    from docknv.command_handler import command_get_context
    from docknv.logger import Logger, LoggerError

    from .shell import Shell, register_handlers

    current_dir = os.path.abspath(_extract_context())
    if not os.path.isdir(current_dir):
        Logger.error("Wrong context folder: {0}".format(current_dir), crash=False)
        return

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
        if isinstance(e, LoggerError):
            pass
        elif isinstance(e, SystemExit):
            pass
        else:
            Logger.error(traceback.format_exc(), crash=False)
