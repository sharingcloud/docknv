"""Notebook commands helper."""

from docknv.lifecycle_handler import (
    lifecycle_machine_run
)

from docknv.logger import Logger


def pre_parse(shell, config, context):
    """
    Pre-parse.

    :param shell    Shell (shell)
    :param config   Configuration (dict)
    :param context  Context (dict)
    """
    subparsers = shell.subparsers

    cmd = subparsers.add_parser("notebook", help="execute notebook actions")
    subs = cmd.add_subparsers(dest="notebook_cmd", metavar="")

    subs.add_parser("password", help="generate a IPython notebook passwd")


def post_parse(shell, args, config, context):
    """
    Post-parse.

    :param shell    Shell (shell)
    :param args     Arguments (*)
    :param config   Command config (dict)
    :param context  Current context (dict)
    """
    if args.command == "notebook":
        machine_name = config.get('machine', None)
        if machine_name is None:
            Logger.error('IPython machine name is not configured in `config.yml`.')

        if args.notebook_cmd == "password":
            Logger.info("Generating notebook password...")
            cmd = 'python -c "from IPython.lib import passwd; print(passwd())"'
            lifecycle_machine_run(".", machine_name, cmd)
            return True

    return False
