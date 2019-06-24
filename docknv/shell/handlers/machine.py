"""Removed machine sub command."""

import argparse
import sys

from docknv.logger import Logger, Fore


def _init(subparsers):
    cmd = subparsers.add_parser(
        "machine", help="removed machine command, use `service` instead"
    )
    cmd.add_argument("args", nargs=argparse.REMAINDER)


def _handle(args):
    str_args = " ".join(args.args)
    Logger.raw(
        "`machine` command has been removed. use `service` instead.",
        color=Fore.YELLOW,
    )
    Logger.raw(f"example: `docknv service {str_args}`", color=Fore.YELLOW)
    sys.exit(1)
