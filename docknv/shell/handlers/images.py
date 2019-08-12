"""Images sub commands."""

from docknv.shell.common import exec_handler, load_project


def _init(subparsers):
    cmd = subparsers.add_parser("images", help="manage images")
    subs = cmd.add_subparsers(dest="images_cmd", metavar="")

    # Ls
    subs.add_parser("ls", help="list images")
    build_cmd = subs.add_parser("build", help="build image")
    build_cmd.add_argument("image", help="image name")
    build_cmd.add_argument("tag_name", help="image tag name")
    build_cmd.add_argument("tag_version", help="image tag version")
    build_cmd.add_argument("-b", "--build-args", nargs="+", help="build args")
    build_cmd.add_argument(
        "--no-cache", help="build without cache", action="store_true"
    )


def _handle(args):
    return exec_handler("images", args, globals())


def _handle_ls(args):
    project = load_project(args.project)
    project.images.show()


def _handle_build(args):
    project = load_project(args.project)
    project.lifecycle.image.build(
        args.image,
        args.tag_name,
        args.tag_version,
        build_args=args.build_args,
        no_cache=args.no_cache,
        dry_run=args.dry_run,
    )
