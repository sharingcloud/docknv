"""Scaffold sub commands."""

from docknv.scaffolder import (
    scaffold_project,
    scaffold_image,
    scaffold_environment,
    scaffold_environment_copy,
)

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("scaffold", help="scaffolding")
    subs = cmd.add_subparsers(dest="scaffold_cmd", metavar="")

    # Project
    project_cmd = subs.add_parser(
        "project", help="scaffold a new docknv project"
    )
    project_cmd.add_argument("project_path", help="project path")

    # Image
    image_cmd = subs.add_parser("image", help="scaffold an image Dockerfile")
    image_cmd.add_argument("image_name", help="image name")
    image_cmd.add_argument("image_url", help="image url (Docker style path)")
    image_cmd.add_argument(
        "image_tag",
        help="image tag (default: latest)",
        nargs="?",
        default="latest",
    )

    # Environment
    env_cmd = subs.add_parser("env", help="scaffold an environment file")
    env_cmd.add_argument("name", help="environment file name")
    env_cmd.add_argument(
        "-i",
        "--inherit",
        nargs="?",
        default=None,
        help="inherit from existing environment",
    )


def _handle(args):
    return exec_handler("scaffold", args, globals())


def _handle_project(args):
    scaffold_project(args.project_path)


def _handle_image(args):
    scaffold_image(
        args.project, args.image_name, args.image_url, args.image_tag
    )


def _handle_env(args):
    if args.inherit:
        return scaffold_environment_copy(args.project, args.inherit, args.name)
    else:
        return scaffold_environment(args.project, args.name)
