"""Scaffold sub commands."""

from docknv import scaffolder
from docknv.shell.common import exec_handler


def _handle(args):
    return exec_handler("scaffold", args, globals())


def _handle_project(args):
    return scaffolder.scaffold_project(args.project_path, args.project_name)


def _handle_image(args):
    return scaffolder.scaffold_image(".", args.image_name, args.image_tag, args.image_version)


def _handle_env(args):
    if args.from_env:
        return scaffolder.scaffold_environment_copy(".", args.from_env, args.name)
    else:
        return scaffolder.scaffold_environment(".", args.name)


def _handle_link_compose(args):
    return scaffolder.scaffold_link_composefile(".", args.composefile_name, unlink=False)


def _handle_unlink_compose(args):
    return scaffolder.scaffold_link_composefile(".", args.composefile_name, unlink=True)
