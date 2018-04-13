"""Swarm sub commands."""

# TODO: Complete


def _init(subparsers):
    cmd = subparsers.add_parser("swarm", help="deploy to swarm (swarm mode)")
    subs = cmd.add_subparsers(dest="swarm_cmd", metavar="")

    subs.add_parser("push", help="push stack to swarm")
    subs.add_parser("up", help="deploy stack to swarm")
    subs.add_parser("down", help="shutdown stack")
    subs.add_parser("ls", help="list current services")

    ps_cmd = subs.add_parser("ps", help="get service info")
    ps_cmd.add_argument("machine",
                        help="machine name")

    export_cmd = subs.add_parser("export", help="export schema for production")
    export_cmd.add_argument("schema", help="schema name")
    export_cmd.add_argument("--clean", action="store_true", help="clean the export.")
    export_cmd.add_argument("--swarm", action="store_true", help="prepare swarm mode by setting image names")
    export_cmd.add_argument("--swarm-registry", nargs="?", default="127.0.0.1:5000", help="swarm registry URL")
    export_cmd.add_argument("--build", action="store_true", help="rebuild new images")
