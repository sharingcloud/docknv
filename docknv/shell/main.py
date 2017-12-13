"""Handler main functions."""

from __future__ import unicode_literals

import os
import sys
import imp
import argparse
import importlib

from docknv.logger import Logger
from docknv.version import __version__
from docknv.project_handler import project_read

STANDARD_COMMANDS = (
    "machine", "config", "bundle", "env", "schema",
    "volume", "user", "scaffold", "registry"
)


class Shell(object):
    """Shell entry-point."""

    def __init__(self):
        """Init."""
        self.parser = argparse.ArgumentParser(description="Docker w/ environments (docknv {0})".format(__version__))
        self.parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
        self.parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

        self.subparsers = self.parser.add_subparsers(dest="command", metavar="")
        self.post_parsers = []

        self.init_parsers()

    def register_post_parser(self, fct, cfg, ctx):
        """
        Register a new parser function.

        :param fct:  Parser function (fn)
        :param cfg:  Configuration (dict)
        :param ctx:  Context (dict)
        """
        self.post_parsers.append((fct, cfg, ctx))

    def run(self, args):
        """
        Start and read command-line arguments.

        :param args: Arguments
        """
        args_count = len(args)
        if args_count == 0:
            self.parser.print_help()
            sys.exit(1)

        elif args_count == 1:
            self.parser.parse_args(args + ["-h"])
            sys.exit(1)

        return self.parse_args(self.parser.parse_args(args))

    def init_parsers(self):
        """Initialize each parsers."""
        for cmd in STANDARD_COMMANDS:
            module = importlib.import_module("docknv.shell.handlers." + cmd)
            getattr(module, "_init")(self.subparsers)

    def parse_args(self, args):
        """
        Parse command-line args.

        :param args:    Arguments (iterable)
        """
        exit_code = 0

        # Verbose mode activation
        if args.verbose:
            Logger.set_log_level("DEBUG")
        else:
            Logger.set_log_level("INFO")

        if args.command in STANDARD_COMMANDS:
            module = importlib.import_module("docknv.shell.handlers." + args.command)
            exit_code = getattr(module, "_handle")(args)
        else:
            for parser, cfg, ctx in self.post_parsers:
                try:
                    # New args passing
                    result = parser(self, args, cfg, ctx)
                except TypeError:
                    # Old args passing
                    result = parser(self, args)

                try:
                    ok, exit_code = result
                except TypeError:
                    ok, exit_code = result, 0

                if ok:
                    break

        return exit_code


def _register_handlers(shell, current_dir, commands_dir, commands_context):
    from docknv import command_handler

    project_data = project_read(current_dir)
    config_data = project_data.config_data

    for root, _, files in os.walk(commands_dir):
        for filename in files:
            if filename.endswith(".py"):
                # Ignore __init__.py
                if filename == "__init__.py":
                    continue

                base_filename, ext = os.path.splitext(filename)
                abs_f = os.path.join(root, filename)

                # Ignore __pycache__
                if "__pycache__" in abs_f:
                    continue

                src = imp.load_source("commands", abs_f)
                if hasattr(src, "pre_parse") and hasattr(src, "post_parse"):
                    pre_parse = getattr(src, "pre_parse")
                    post_parse = getattr(src, "post_parse")

                    command_config = command_handler.command_get_config(config_data, base_filename)

                    try:
                        pre_parse(shell, command_config, commands_context)
                    except TypeError:
                        pre_parse(shell)

                    shell.register_post_parser(post_parse, command_config, commands_context)


def docknv_entry_point():
    """Entry point for docknv."""
    from docknv import command_handler

    current_dir = os.getcwd()
    commands_dir = os.path.join(current_dir, "commands")
    commands_context = command_handler.command_get_context(current_dir)
    shell = Shell()

    try:
        if os.path.exists(commands_dir):
            _register_handlers(shell, current_dir, commands_dir, commands_context)

    except BaseException as e:
        Logger.error(e, crash=False)

    return shell.run(sys.argv[1:])
