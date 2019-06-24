"""Notebook commands helper."""

from docknv.logger import Logger


def pre_parse(shell):
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


def post_parse(shell, args, project, context):
    """Post parse."""
    if args.command == "notebook":
        config = project.get_command_parameters("notebook")
        service_name = config.get("service", None)
        if service_name is None:
            Logger.error(
                "ipython machine name is not configured in `config.yml`."
            )

        if args.notebook_cmd == "password":
            Logger.info("generating notebook password...")
            cmd = 'python -c "from IPython.lib import passwd; print(passwd())"'
            project.lifecycle.service.run(
                service_name, cmd, dry_run=args.dry_run
            )
