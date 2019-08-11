"""Custom commands."""

import argparse
import imp
import os

from docknv.shell.custom import CustomShell, MalformedCommand
from docknv.logger import Logger

from docknv.project import project_is_valid


def _init(subparsers):
    cmd = subparsers.add_parser("custom", help="custom commands")
    cmd.add_argument("-c", "--config", help="configuration name", default=None)
    cmd.add_argument("args", nargs=argparse.REMAINDER)


def _handle(args):
    project_path = args.project

    if not project_is_valid(project_path):
        Logger.warn("no custom commands found")
        return

    commands_dir = os.path.join(project_path, "commands")
    if not os.path.exists(commands_dir):
        Logger.warn("no custom commands found")
        return

    shell = CustomShell()

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
                    pre_parse = src.pre_parse
                    post_parse = src.post_parse
                    error = None

                    try:
                        pre_parse(shell)
                    except BaseException as exc:
                        error = exc

                    if error:
                        raise MalformedCommand(
                            f"{base_filename} - {str(error)}"
                        )

                    shell.register_post_parser(post_parse)

    # Pass arguments to custom shell
    cmd_args = ["--project", project_path]
    if args.verbose:
        cmd_args += ["-v"]
    if args.dry_run:
        cmd_args += ["--dry-run"]
    if args.config:
        cmd_args += ["-c", args.config]
    cmd_args += args.args

    shell.run(cmd_args)
