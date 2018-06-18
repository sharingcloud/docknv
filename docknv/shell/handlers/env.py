"""Env sub commands."""

import subprocess

from docknv import environment_handler
from docknv.logger import Logger
from docknv.shell.common import exec_handler
from docknv.utils.ioutils import get_editor_executable


def _init(subparsers):
    cmd = subparsers.add_parser("env", help="manage environments")
    subs = cmd.add_subparsers(dest="env_cmd", metavar="")

    subs.add_parser("ls", help="list envs")

    show_cmd = subs.add_parser("show", help="show an environment file")
    show_cmd.add_argument("env_name", help="environment file name")

    edit_cmd = subs.add_parser("edit", help="edit an environment file")
    edit_cmd.add_argument("env_name", help="environment file name")
    edit_cmd.add_argument("-e", "--editor", nargs="?", default=None, help="editor to use (default: auto-detect)")

    convert_cmd = subs.add_parser("convert", help="convert an old Python environment to the new format")
    convert_cmd.add_argument("env_name", help="environment file name")

    inherit_cmd = subs.add_parser("create-from", help='create an environment file from another')
    inherit_cmd.add_argument("env_name", help="environment file name")
    inherit_cmd.add_argument("from_env", help="source environment name")


def _handle(args):
    return exec_handler("env", args, globals())


def _handle_ls(args):
    environment_handler.env_yaml_list(args.context)


def _handle_show(args):
    environment_handler.env_yaml_show(args.context, args.env_name)


def _handle_edit(args):
    editor = get_editor_executable(args.editor)
    path = environment_handler.env_get_yaml_path(args.context, args.env_name)
    return subprocess.call([editor, path], shell=True)


def _handle_convert(args):
    environment_handler.env_yaml_convert(args.context, args.env_name)


def _handle_create_from(args):
    if not environment_handler.env_yaml_check_file(args.context, args.from_env):
        Logger.error("Missing environment file `{0}`".format(args.from_env))

    inherited = environment_handler.env_yaml_inherits(args.from_env)
    dest_env = environment_handler.env_get_yaml_path(args.context, args.env_name)
    environment_handler.env_yaml_write_to_file(inherited, dest_env)
