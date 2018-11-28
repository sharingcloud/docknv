"""Shell class."""

import os
import sys
import argparse
import importlib

from docknv.logger import Logger
from docknv.version import __version__

STANDARD_COMMANDS = (
    "config", "service", "env", "schema",
    "user", "scaffold", "custom"
)


class Shell(object):
    """Shell entry-point."""

    def __init__(self):
        """Init."""
        self.parser = argparse.ArgumentParser(
            description="Docker w/ environments (docknv v.{0})".format(
                __version__))
        self.parser.add_argument(
            '--version', action='version', version='%(prog)s ' + __version__)
        self.parser.add_argument(
            '-v', '--verbose', action='store_true', help='verbose mode')
        self.parser.add_argument(
            '-p', '--project', help='project path', default='.')
        self.parser.add_argument(
            '--dry-run', help='dry run', action="store_true")

        self.subparsers = self.parser.add_subparsers(
            dest="command", metavar="")
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
        # Verbose mode activation
        if args.verbose:
            Logger.set_log_level("DEBUG")
        else:
            Logger.set_log_level("INFO")

        # Command detection
        if args.command is None:
            self.parser.print_help()
            sys.exit(1)

        # Command help detection
        if args.command is not None:
            cmd = args.command
            subcmd_name = "{0}_cmd".format(cmd)
            if cmd in self.subparsers.choices:
                subpar = self.subparsers.choices[cmd]
                if hasattr(args, subcmd_name):
                    if getattr(args, subcmd_name) is None:
                        subpar.print_help()
                        sys.exit(1)

        return handle_parsers(self, args)


def handle_parsers(shell, args):
    """
    Handle parsers.

    :param shell:   Shell
    :param args:    Arguments
    :rtype: Exit code (int)
    """
    # Exit code
    exit_code = 0

    # Absolute path
    args.project = os.path.abspath(args.project)

    module = importlib.import_module(
        "docknv.shell.handlers." + args.command)
    exit_code = getattr(module, "_handle")(args)

    return exit_code
