"""Env sub commands."""

import subprocess

from docknv import environment_handler
from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("env", help="manage environments")
    subs = cmd.add_subparsers(dest="env_cmd", metavar="")

    subs.add_parser("ls", help="list envs")

    show_cmd = subs.add_parser("show", help="show an environment file")
    show_cmd.add_argument("env_name", help="environment file name")

    edit_cmd = subs.add_parser("edit", help="edit an environment file")
    edit_cmd.add_argument("env_name", help="environment file name")
    edit_cmd.add_argument("-e", "--editor", nargs="?", default="atom", help="editor to use (default: atom)")


def _handle(args):
    return exec_handler("env", args, globals())


def _handle_ls(args):
    return environment_handler.env_yaml_list(".")


def _handle_show(args):
    return environment_handler.env_yaml_show(".", args.env_name)


def _handle_edit(args):
    path = environment_handler.env_get_yaml_path(".", args.env_name)
    return subprocess.call([args.editor, path], shell=True)
