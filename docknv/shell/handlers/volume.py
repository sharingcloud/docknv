"""Volume sub commands."""

from docknv import lifecycle_handler

from docknv.shell.common import exec_handler


def _init(subparsers):
    cmd = subparsers.add_parser("volume", help="manage volumes")
    subs = cmd.add_subparsers(dest="volume_cmd", metavar="")

    subs.add_parser("ls", help="list volumes")

    rm_cmd = subs.add_parser("rm", help="remove volume")
    rm_cmd.add_argument("name", help="volume name")

    # TODO: NFS handling
    # subs.add_parser("nfs-ls", help="list NFS volumes")
    #
    # nfs_rm_cmd = subs.add_parser("nfs-rm", help="remove NFS volume")
    # nfs_rm_cmd.add_argument("name", help="NFS volume name")
    #
    # nfs_create_cmd = subs.add_parser("nfs-create", help="create a NFS volume")
    # nfs_create_cmd.add_argument("name", help="NFS volume name")


def _handle(args):
    return exec_handler("volume", args, globals())


def _handle_ls(args):
    return lifecycle_handler.lifecycle_volume_list(args.context)


def _handle_rm(args):
    return lifecycle_handler.lifecycle_volume_remove(args.context, args.name)
