"""
Shell
"""

import argparse
import sys

from docknv.v2.schema_handler import SchemaHandler
from docknv.v2.scaffolder import Scaffolder
from docknv.v2.lifecycle_handler import LifecycleHandler
from docknv.v2.config_handler import ConfigHandler
from docknv.v2.env_handler import EnvHandler

from docknv.version import __version__

from docknv.logger import Logger, Fore


class Shell(object):
    """
    Shell entry-point
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Docker w/ environments (docknv {0})".format(__version__))
        self.parser.add_argument(
            "-f", "--config", default="config.yml", help="compose config file")
        self.parser.add_argument('-v', '--version', action='version',
                                 version='%(prog)s ' + __version__)

        self.subparsers = self.parser.add_subparsers(
            dest="command", metavar="")
        self.post_parsers = []

        self._init_commands()

    def register_post_parser(self, fct):
        """
        Register a new parser function

        @param fct  Parser function
        """
        self.post_parsers.append(fct)

    def run(self, args):
        """
        Start and read command-line arguments.
        """

        args_count = len(args)
        if args_count == 0:
            self.parser.print_help()
            sys.exit(1)

        elif args_count == 1:
            self.parser.parse_args(args + ["-h"])
            sys.exit(1)

        self._parse_args(self.parser.parse_args(args))

    # PRIVATE METHODS ##########

    ################
    # INIT COMMANDS

    def _init_commands(self):
        self._init_schema_commands()
        self._init_machine_commands()
        self._init_swarm_commands()
        self._init_environment_commands()
        self._init_scaffold_commands()
        self._init_registry_commands()
        self._init_image_commands()
        self._init_network_commands()
        self._init_config_commands()
        self._init_volume_commands()

    def _init_schema_commands(self):
        cmd = self.subparsers.add_parser(
            "schema", help="manage groups of machines at once (schema mode)")

        subs = cmd.add_subparsers(dest="schema_cmd", metavar="")

        ls_cmd = subs.add_parser("ls", help="list schemas")

        ps_cmd = subs.add_parser("ps", help="list schema processes")
        start_cmd = subs.add_parser("start", help="boot machines from schema")
        start_cmd.add_argument(
            "-f", "--foreground", action="store_true", help="start in foreground")
        stop_cmd = subs.add_parser(
            "stop", help="shutdown machines from schema")
        restart_cmd = subs.add_parser(
            "restart", help="restart machines from schema")
        restart_cmd.add_argument(
            "-f", "--force", action="store_true", help="force restart")
        build_cmd = subs.add_parser("build", help="build machines from schema")
        build_cmd.add_argument(
            "-p", "--push", help="push to registry", action="store_true")

    def _init_registry_commands(self):
        cmd = self.subparsers.add_parser(
            "registry", help="start and stop registry")

        subs = cmd.add_subparsers(dest="registry_cmd", metavar="")

        start_cmd = subs.add_parser("start", help="start registry")
        start_cmd.add_argument(
            "-p", "--path", help="storage path", nargs="?", default=None)
        stop_cmd = subs.add_parser("stop", help="stop registry")

    def _init_machine_commands(self):
        cmd = self.subparsers.add_parser(
            "machine", help="manage one machine at a time (machine mode)"
        )

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
            "-p", "--push", help="push to registry", action="store_true")

    def _init_scaffold_commands(self):
        cmd = self.subparsers.add_parser("scaffold", help="scaffolding")
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

    def _init_config_commands(self):
        cmd = self.subparsers.add_parser(
            "config", help="configuration management"
        )

        subs = cmd.add_subparsers(dest="config_cmd", metavar="")

        use_cmd = subs.add_parser("use", help="use configuration")
        use_cmd.add_argument("name", help="configuration name")

        status_cmd = subs.add_parser(
            "status", help="show current configuration")

        generate_cmd = subs.add_parser(
            "generate", help="generate docker compose file using configuration")
        generate_cmd.add_argument(
            "name", help="schema name", nargs="?", default="all")
        generate_cmd.add_argument(
            "-n", "--namespace", help="namespace name", nargs="?", default="default")
        generate_cmd.add_argument(
            "-e", "--environment", help="environment file name", nargs="?", default="default")
        generate_cmd.add_argument(
            "-c", "--config-name", help="configuration nickname", nargs="?", default=None)

        ls_cmd = subs.add_parser("ls", help="list known configurations")

        update_cmd = subs.add_parser(
            "update", help="update a known configuration")
        update_cmd.add_argument("name", help="configuration name")
        update_cmd.add_argument(
            "-s", "--set-current", action="store_true", help="set this configuration as current")

        remove_cmd = subs.add_parser(
            "rm", help="remove a known configuration")
        remove_cmd.add_argument("name", help="configuration name")

    def _init_image_commands(self):
        pass

    def _init_swarm_commands(self):
        cmd = self.subparsers.add_parser(
            "swarm", help="deploy to swarm (swarm mode)")
        subs = cmd.add_subparsers(dest="swarm_cmd", metavar="")

        push_cmd = subs.add_parser("push", help="push stack to swarm")

        up_cmd = subs.add_parser("up", help="deploy stack to swarm")

        down_cmd = subs.add_parser("down", help="shutdown stack")

        ls_cmd = subs.add_parser("ls", help="list current services")

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

    def _init_environment_commands(self):
        cmd = self.subparsers.add_parser("env", help="manage environments")
        subs = cmd.add_subparsers(dest="env_cmd", metavar="")

        show_cmd = subs.add_parser("show", help="show an environment file")
        show_cmd.add_argument(
            "env_name", help="environment file name (debug, etc.)")

        ls_cmd = subs.add_parser("ls", help="list envs")

        use_cmd = subs.add_parser("use", help="set env and render templates")
        use_cmd.add_argument(
            "env_name", help="environment file name (debug, etc.)")

    def _init_volume_commands(self):
        cmd = self.subparsers.add_parser("volume", help="manage volumes")
        subs = cmd.add_subparsers(dest="volume_cmd", metavar="")

        ls_cmd = subs.add_parser("ls", help="list volumes")

        rm_cmd = subs.add_parser("rm", help="remove volume")
        rm_cmd.add_argument("name", help="volume name")

        nfs_ls_cmd = subs.add_parser("nfs-ls", help="list NFS volumes")

        nfs_rm_cmd = subs.add_parser("nfs-rm", help="remove NFS volume")
        nfs_rm_cmd.add_argument("name", help="NFS volume name")

        nfs_create_cmd = subs.add_parser(
            "nfs-create", help="create a NFS volume")
        nfs_create_cmd.add_argument("name", help="NFS volume name")

    def _init_network_commands(self):
        cmd = self.subparsers.add_parser("network", help="manage networks")
        subs = cmd.add_subparsers(dest="network_cmd", metavar="")

        ls_cmd = subs.add_parser("ls", help="list networks")

        create_overlay_cmd = subs.add_parser("create-overlay",
                                             help="create an overlay network to use with swarm")
        create_overlay_cmd.add_argument("name", help="network name")

        rm_cmd = subs.add_parser("rm", help="remove network")
        rm_cmd.add_argument("name", help="network name")

    def _use_schema(self, config, args):
        Logger.raw("Using schema `{0}`".format(args.schema), Fore.GREEN)

        config.write_compose(".docker-compose.yml", args.schema)
        if "build" in args and args.build:
            config.build_schema(args.schema)

    def _parse_args(self, args):
        command = args.command

        if command == "scaffold":
            if args.scaffold_cmd == "project":
                Scaffolder.scaffold_project(
                    args.project_path, args.project_name)

            elif args.scaffold_cmd == "image":
                Scaffolder.scaffold_image(
                    ".", args.image_name, args.image_tag, args.image_version)

            elif args.scaffold_cmd == "env":
                if args.from_env:
                    Scaffolder.scaffold_environment_copy(
                        ".", args.from_env, args.name)
                else:
                    Scaffolder.scaffold_environment(".", args.name)

            elif args.scaffold_cmd == "link-compose":
                Scaffolder.scaffold_link_composefile(
                    ".", args.composefile_name, unlink=False)
            elif args.scaffold_cmd == "unlink-compose":
                Scaffolder.scaffold_link_composefile(
                    ".", args.composefile_name, unlink=True)

        elif command == "env":
            if args.env_cmd == "ls":
                EnvHandler.list_environments(".")

            elif args.env_cmd == "show":
                EnvHandler.show_environment(".", args.env_name)

        elif command == "schema":
            if args.schema_cmd == "build":
                LifecycleHandler.build_schema(".", args.push)

            elif args.schema_cmd == "start":
                LifecycleHandler.start_schema(
                    ".", foreground=args.foreground)

            elif args.schema_cmd == "stop":
                LifecycleHandler.stop_schema(".")

            elif args.schema_cmd == "restart":
                LifecycleHandler.restart_schema(".")

            elif args.schema_cmd == "ps":
                LifecycleHandler.ps_schema(".")

            elif args.schema_cmd == "ls":
                SchemaHandler.list_schemas(".")

        elif command == "machine":
            if args.machine_cmd == "build":
                LifecycleHandler.build_machine(".", args.machine, args.push)

            elif args.machine_cmd == "daemon":
                LifecycleHandler.daemon_machine(
                    ".", args.machine, args.run_command)

            elif args.machine_cmd == "run":
                LifecycleHandler.run_machine(
                    ".", args.machine, args.run_command)

            elif args.machine_cmd == "exec":
                LifecycleHandler.exec_machine(
                    ".", args.machine, args.run_command, args.no_tty, args.return_code)

            elif args.machine_cmd == "shell":
                LifecycleHandler.shell_machine(
                    ".", args.machine, args.shell)

            elif args.machine_cmd == "restart":
                LifecycleHandler.restart_machine(
                    ".", args.machine, args.force)

            elif args.machine_cmd == "stop":
                LifecycleHandler.stop_machine(
                    ".", args.machine)

            elif args.machine_cmd == "start":
                LifecycleHandler.start_machine(
                    ".", args.machine)

            elif args.machine_cmd == "push":
                LifecycleHandler.push_machine(
                    ".", args.machine, args.host_path, args.container_path)

            elif args.machine_cmd == "pull":
                LifecycleHandler.pull_machine(
                    ".", args.machine, args.container_path, args.host_path)

            elif args.machine_cmd == "logs":
                LifecycleHandler.logs_machine(
                    ".", args.machine, tail=args.tail)

        elif command == "registry":
            if args.registry_cmd == "start":
                LifecycleHandler.start_registry(args.path)
            elif args.registry_cmd == "stop":
                LifecycleHandler.stop_registry()

        elif command == "config":
            if args.config_cmd == "ls":
                ConfigHandler.list_known_configurations(".")

            elif args.config_cmd == "rm":
                ConfigHandler.remove_config(".", args.name)

            elif args.config_cmd == "generate":
                SchemaHandler.generate_compose(
                    ".", args.name, args.namespace, args.environment, args.config_name)

            elif args.config_cmd == "use":
                ConfigHandler.use_composefile_configuration(
                    ".", args.name)

            elif args.config_cmd == "update":
                SchemaHandler.generate_compose_from_configuration(
                    ".", args.name)

                if args.set_current:
                    ConfigHandler.use_composefile_configuration(
                        ".", args.name)

            elif args.config_cmd == "status":
                config = ConfigHandler.get_current_config(".")
                if not config:
                    Logger.warn(
                        "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
                else:
                    Logger.info("Current configuration: `{0}`".format(config))

        elif command == "volume":
            if args.volume_cmd == "ls":
                LifecycleHandler.list_volumes(".")

            elif args.volume_cmd == "rm":
                LifecycleHandler.remove_volume(".", args.name)

        for parser in self.post_parsers:
            if parser(self, args):
                break
