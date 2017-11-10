"""Scaffold sub commands."""

from docknv import scaffolder
from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("scaffold", help="scaffolding")
    subs = cmd.add_subparsers(dest="scaffold_cmd", metavar="")

    project_cmd = subs.add_parser("project", help="scaffold a new docknv project")
    project_cmd.add_argument("project_path", help="project path")

    image_cmd = subs.add_parser("image", help="scaffold an image Dockerfile")
    image_cmd.add_argument("image_name", help="image name")
    image_cmd.add_argument("image_tag",
                           help="image tag (Docker style path)",
                           nargs="?",
                           default=None)
    image_cmd.add_argument("image_version",
                           help="image version (default: latest)",
                           nargs="?",
                           default="latest")

    env_cmd = subs.add_parser("env", help="scaffold an environment file")
    env_cmd.add_argument("name", help="environment file name")
    env_cmd.add_argument("-i", "--inherit", nargs="?", default=None, help="inherit from existing environment")


def _handle(args):
    return exec_handler("scaffold", args, globals())


def _handle_project(args):
    return scaffolder.scaffold_project(args.project_path, args.project_name)


def _handle_image(args):
    return scaffolder.scaffold_image(".", args.image_name, args.image_tag, args.image_version)


def _handle_env(args):
    if args.inherit:
        return scaffolder.scaffold_environment_copy(".", args.inherit, args.name)
    else:
        return scaffolder.scaffold_environment(".", args.name)
