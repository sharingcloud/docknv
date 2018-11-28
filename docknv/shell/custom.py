"""Custom shell."""

import argparse
import os
import sys

from docknv.project import Project


class MalformedCommand(Exception):
    """Malformed command."""

    def __init__(self, cause):
        """Init."""
        message = f"malformed command: {cause}"
        super(MalformedCommand, self).__init__(message)


class CustomShell(object):
    """Custom shell entry-point."""

    def __init__(self):
        """Init."""
        self.parser = argparse.ArgumentParser(
            description="docknv custom commands")
        self.parser.add_argument(
            '-v', '--verbose', action='store_true', help='verbose mode')
        self.parser.add_argument(
            '-p', '--project', help='project path', default='.')
        self.parser.add_argument(
            '--dry-run', help='dry run', action="store_true")

        self.subparsers = self.parser.add_subparsers(
            dest="command", metavar="")
        self.post_parsers = []

    def register_post_parser(self, fct):
        """
        Register a new parser function.

        :param fct:         Parser function (fn)
        """
        self.post_parsers.append(fct)

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

    def parse_args(self, args):
        """
        Parse command-line args.

        :param args:    Arguments (iterable)
        """
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
                else:
                    pass

        return handle_parsers(self, args)


def handle_parsers(shell, args):
    """
    Handle parsers.

    :param shell:   Shell
    :param args:    Arguments
    :rtype: Exit code (int)
    """
    # Absolute path
    args.project = os.path.abspath(args.project)

    # Get project and current config
    project = Project.load_from_path(args.project)
    current_config = project.get_current_configuration()
    if current_config:
        config = project.database.get_configuration(current_config)
    else:
        config = None

    for parser in shell.post_parsers:
        parser(shell, args, project, config)
