"""Shell parsers."""


def init_parsers(subparsers):
    """
    Initialize parsers.

    :param subparsers:  Subparsers
    """
    _init_schema_commands(subparsers)
    _init_machine_commands(subparsers)
    _init_bundle_commands(subparsers)
    _init_swarm_commands(subparsers)
    _init_environment_commands(subparsers)
    _init_scaffold_commands(subparsers)
    _init_registry_commands(subparsers)
    _init_image_commands(subparsers)
    _init_network_commands(subparsers)
    _init_config_commands(subparsers)
    _init_volume_commands(subparsers)
    _init_user_commands(subparsers)


def _init_schema_commands(subparsers):
    cmd = subparsers.add_parser("schema", help="manage groups of machines at once (schema mode)")
    subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

    subs.add_parser("ls", help="list schemas")
    subs.add_parser("ps", help="list schema processes")
    subs.add_parser("stop", help="shutdown machines from schema")
    subs.add_parser("status", help="get current config name")

    start_cmd = subs.add_parser("start", help="boot machines from schema")
    start_cmd.add_argument(
        "-f", "--foreground", action="store_true", help="start in foreground")
    restart_cmd = subs.add_parser(
        "restart", help="restart machines from schema")
    restart_cmd.add_argument(
        "-f", "--force", action="store_true", help="force restart")
    build_cmd = subs.add_parser("build", help="build machines from schema")
    build_cmd.add_argument(
        "-n", "--no-cache", help="no cache", action="store_true")
    build_cmd.add_argument(
        "-d", "--do-not-push", help="do not push to registry", action="store_true")


def _init_bundle_commands(subparsers):
    cmd = subparsers.add_parser("bundle", help="manage groups of configs at once (bundle mode)")
    subs = cmd.add_subparsers(dest="bundle_cmd", metavar="")

    start_cmd = subs.add_parser("start", help="boot machines from schemas")
    start_cmd.add_argument("configs", nargs="+")

    stop_cmd = subs.add_parser(
        "stop", help="shutdown machines from schemas")
    stop_cmd.add_argument("configs", nargs="+")

    restart_cmd = subs.add_parser(
        "restart", help="restart machines from schemas")
    restart_cmd.add_argument("-f", "--force", help="force restart")
    restart_cmd.add_argument("configs", nargs="+")

    ps_cmd = subs.add_parser("ps", help="list schemas processes")
    ps_cmd.add_argument("configs", nargs="+")

    build_cmd = subs.add_parser(
        "build", help="build machines from schemas")
    build_cmd.add_argument("configs", nargs="+")
    build_cmd.add_argument(
        "-n", "--no-cache", help="no cache", action="store_true")
    build_cmd.add_argument(
        "-d", "--do-not-push", help="do not push to registry", action="store_true")


def _init_registry_commands(subparsers):
    cmd = subparsers.add_parser("registry", help="start and stop registry")
    subs = cmd.add_subparsers(dest="registry_cmd", metavar="")

    start_cmd = subs.add_parser("start", help="start registry")
    start_cmd.add_argument(
        "-p", "--path", help="storage path", nargs="?", default=None)
    subs.add_parser("stop", help="stop registry")


def _init_machine_commands(subparsers):
    cmd = subparsers.add_parser("machine", help="manage one machine at a time (machine mode)")
    subs = cmd.add_subparsers(dest="machine_cmd", metavar="")

    daemon_cmd = subs.add_parser(
        "daemon", help="run a container in background")
    daemon_cmd.add_argument("machine", help="machine name")
    daemon_cmd.add_argument(
        "run_command", help="command to run", nargs="?", default="")

    run_cmd = subs.add_parser("run", help="run a command on a container")
    run_cmd.add_argument("machine", help="machine name")
    run_cmd.add_argument(
        "run_command", help="command to run", nargs="?", default="")

    shell_cmd = subs.add_parser("shell", help="run shell")
    shell_cmd.add_argument("machine", help="machine name")
    shell_cmd.add_argument(
        "shell", help="shell executable", default="/bin/bash", nargs="?")
    shell_cmd.add_argument(
        "-c", "--create", help="create the container if it does not exist", action="store_true")

    stop_cmd = subs.add_parser("stop", help="stop a container")
    stop_cmd.add_argument("machine", help="machine name")

    start_cmd = subs.add_parser("start", help="start a container")
    start_cmd.add_argument("machine", help="machine name")

    restart_cmd = subs.add_parser("restart", help="restart a container")
    restart_cmd.add_argument("machine", help="machine name")
    restart_cmd.add_argument(
        "-f", "--force", action="store_true", help="force restart")

    exec_cmd = subs.add_parser(
        "exec", help="execute command on a running container")
    exec_cmd.add_argument("machine", help="machine name")
    exec_cmd.add_argument("run_command", help="command to run")
    exec_cmd.add_argument(
        "-t", "--no-tty", help="disable tty", action="store_true")
    exec_cmd.add_argument("-r", "--return-code",
                          help="forward ret code", action="store_true")

    logs_cmd = subs.add_parser("logs", help="show container logs")
    logs_cmd.add_argument("machine", help="machine name")
    logs_cmd.add_argument("--tail", type=int,
                          help="tail logs", default=0)
    logs_cmd.add_argument(
        "-f", "--follow", help="follow logs", action="store_true", default=False)

    pull_cmd = subs.add_parser("pull", help="pull a file from a container")
    pull_cmd.add_argument("machine", help="machine name")
    pull_cmd.add_argument("container_path", help="container path")
    pull_cmd.add_argument("host_path", help="host path")

    push_cmd = subs.add_parser("push", help="push a file to a container")
    push_cmd.add_argument("machine", help="machine name")
    push_cmd.add_argument("host_path", help="host path")
    push_cmd.add_argument("container_path", help="container path")

    build_cmd = subs.add_parser("build", help="build a machine")
    build_cmd.add_argument("machine", help="machine name")
    build_cmd.add_argument(
        "-d", "--do-not-push", help="do not push to registry", action="store_true")
    build_cmd.add_argument(
        "-n", "--no-cache", help="build without cache", action="store_true")

    freeze_cmd = subs.add_parser("freeze", help="freeze a machine")
    freeze_cmd.add_argument("machine", help="machine name")


def _init_scaffold_commands(subparsers):
    cmd = subparsers.add_parser("scaffold", help="scaffolding")
    subs = cmd.add_subparsers(dest="scaffold_cmd", metavar="")

    project_cmd = subs.add_parser(
        "project", help="scaffold a new docknv project")
    project_cmd.add_argument("project_path", help="project path")
    project_cmd.add_argument(
        "project_name", help="project name", default=None, nargs="?")

    image_cmd = subs.add_parser(
        "image", help="scaffold an image Dockerfile")
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
    env_cmd.add_argument(
        "-f", "--from-env", nargs="?", default=None, help="copy from existing environment")

    composefile_link_cmd = subs.add_parser(
        "link-compose", help="link a composefile to the project")
    composefile_link_cmd.add_argument(
        "composefile_name", help="composefile name (without path)")

    composefile_unlink_cmd = subs.add_parser(
        "unlink-compose", help="unlink a composefile from the project")
    composefile_unlink_cmd.add_argument(
        "composefile_name", help="composefile name (without path)")


def _init_config_commands(subparsers):
    cmd = subparsers.add_parser("config", help="configuration management")
    subs = cmd.add_subparsers(dest="config_cmd", metavar="")

    use_cmd = subs.add_parser("use", help="use configuration")
    use_cmd.add_argument("name", help="configuration name")

    subs.add_parser("unset", help="unset configuration")
    subs.add_parser("status", help="show current configuration")
    subs.add_parser("ls", help="list known configurations")

    generate_cmd = subs.add_parser(
        "generate", help="generate docker compose file using configuration")
    generate_cmd.add_argument(
        "name", help="schema name")
    generate_cmd.add_argument(
        "-n", "--namespace", help="namespace name", nargs="?", default="default")
    generate_cmd.add_argument(
        "-e", "--environment", help="environment file name", nargs="?", default="default")
    generate_cmd.add_argument(
        "-c", "--config-name", help="configuration nickname", nargs="?", default=None)

    update_cmd = subs.add_parser(
        "update", help="update a known configuration")
    update_cmd.add_argument("name", help="configuration name", nargs="?", default=None)
    update_cmd.add_argument(
        "-s", "--set-current", action="store_true", help="set this configuration as current")
    update_cmd.add_argument(
        "-r", "--restart", action="store_true", help="restart current schema"
    )

    change_schema_cmd = subs.add_parser(
        "change-schema", help="change a configuration schema")
    change_schema_cmd.add_argument(
        "config_name", help="configuration name")
    change_schema_cmd.add_argument("schema_name", help="schema name")
    change_schema_cmd.add_argument(
        "-u", "--update", action="store_true", help="auto-update configuration")

    change_env_cmd = subs.add_parser(
        "change-env", help="change a configuration environment file")
    change_env_cmd.add_argument(
        "config_name", help="configuration name")
    change_env_cmd.add_argument("environment", help="environment name")
    change_env_cmd.add_argument(
        "-u", "--update", action="store_true", help="auto-update configuration")

    remove_cmd = subs.add_parser(
        "rm", help="remove a known configuration")
    remove_cmd.add_argument("name", help="configuration name")


def _init_image_commands(subparsers):
    pass


def _init_swarm_commands(subparsers):
    cmd = subparsers.add_parser("swarm", help="deploy to swarm (swarm mode)")
    subs = cmd.add_subparsers(dest="swarm_cmd", metavar="")

    subs.add_parser("push", help="push stack to swarm")
    subs.add_parser("up", help="deploy stack to swarm")
    subs.add_parser("down", help="shutdown stack")
    subs.add_parser("ls", help="list current services")

    ps_cmd = subs.add_parser("ps", help="get service info")
    ps_cmd.add_argument("machine",
                        help="machine name")

    export_cmd = subs.add_parser(
        "export", help="export schema for production")
    export_cmd.add_argument("schema",
                            help="schema name")
    export_cmd.add_argument("--clean",
                            action="store_true",
                            help="clean the export.")
    export_cmd.add_argument("--swarm",
                            action="store_true",
                            help="prepare swarm mode by setting image names")
    export_cmd.add_argument("--swarm-registry",
                            nargs="?",
                            default="127.0.0.1:5000",
                            help="swarm registry URL")
    export_cmd.add_argument("--build",
                            action="store_true",
                            help="rebuild new images")


def _init_environment_commands(subparsers):
    cmd = subparsers.add_parser("env", help="manage environments")
    subs = cmd.add_subparsers(dest="env_cmd", metavar="")

    show_cmd = subs.add_parser("show", help="show an environment file")
    show_cmd.add_argument(
        "env_name", help="environment file name (debug, etc.)")

    subs.add_parser("ls", help="list envs")

    use_cmd = subs.add_parser("use", help="set env and render templates")
    use_cmd.add_argument(
        "env_name", help="environment file name (debug, etc.)")


def _init_volume_commands(subparsers):
    cmd = subparsers.add_parser("volume", help="manage volumes")
    subs = cmd.add_subparsers(dest="volume_cmd", metavar="")

    subs.add_parser("ls", help="list volumes")

    rm_cmd = subs.add_parser("rm", help="remove volume")
    rm_cmd.add_argument("name", help="volume name")

    subs.add_parser("nfs-ls", help="list NFS volumes")

    nfs_rm_cmd = subs.add_parser("nfs-rm", help="remove NFS volume")
    nfs_rm_cmd.add_argument("name", help="NFS volume name")

    nfs_create_cmd = subs.add_parser(
        "nfs-create", help="create a NFS volume")
    nfs_create_cmd.add_argument("name", help="NFS volume name")


def _init_network_commands(subparsers):
    cmd = subparsers.add_parser("network", help="manage networks")
    subs = cmd.add_subparsers(dest="network_cmd", metavar="")

    subs.add_parser("ls", help="list networks")

    create_overlay_cmd = subs.add_parser("create-overlay", help="create an overlay network to use with swarm")
    create_overlay_cmd.add_argument("name", help="network name")

    rm_cmd = subs.add_parser("rm", help="remove network")
    rm_cmd.add_argument("name", help="network name")


def _init_user_commands(subparsers):
    cmd = subparsers.add_parser("user", help="manage user config files")
    subs = cmd.add_subparsers(dest="user_cmd", metavar="")

    clean_cmd = subs.add_parser("clean-config", help="clean user config files for this project")
    clean_cmd.add_argument("config_name", nargs="?", default=None)

    subs.add_parser("rm-lock", help="remove the user lockfile")
