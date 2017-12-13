"""Network sub commands."""

# TODO: Complete


def _init(subparsers):
    cmd = subparsers.add_parser("network", help="manage networks")
    subs = cmd.add_subparsers(dest="network_cmd", metavar="")

    subs.add_parser("ls", help="list networks")

    create_overlay_cmd = subs.add_parser("create-overlay", help="create an overlay network to use with swarm")
    create_overlay_cmd.add_argument("name", help="network name")

    rm_cmd = subs.add_parser("rm", help="remove network")
    rm_cmd.add_argument("name", help="network name")
