"""
Shell
"""

import argparse
import sys

from docknv.v2.schema_handler import SchemaHandler
from docknv.v2.scaffolder import Scaffolder
from docknv.v2.lifecycle_handler import LifecycleHandler
from docknv.v2.config_handler import ConfigHandler

from docknv.logger import Logger, Fore


class Shell(object):
    """
    Shell entry-point
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Docker w/ environments")
        self.parser.add_argument(
            "-f", "--config", default="config.yml", help="compose config file")

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
        build_cmd = subs.add_parser("build", help="build machines from schema")

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

        restart_cmd = subs.add_parser("restart", help="restart a container")
        restart_cmd.add_argument("machine", help="machine name")

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
                Scaffolder.scaffold_environment(".", args.name)

            elif args.scaffold_cmd == "link-compose":
                Scaffolder.scaffold_link_composefile(
                    ".", args.composefile_name, unlink=False)
            elif args.scaffold_cmd == "unlink-compose":
                Scaffolder.scaffold_link_composefile(
                    ".", args.composefile_name, unlink=True)

        elif command == "schema":
            if args.schema_cmd == "build":
                LifecycleHandler.build_schema(".")

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
                LifecycleHandler.build_machine(".", args.machine)

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
                    ".", args.machine)

            elif args.machine_cmd == "logs":
                LifecycleHandler.logs_machine(
                    ".", args.machine, tail=args.tail)

        elif command == "config":
            if args.config_cmd == "ls":
                ConfigHandler.list_known_configurations(".")

            elif args.config_cmd == "generate":
                SchemaHandler.generate_compose(
                    ".", args.name, args.namespace, args.environment, args.config_name)

            elif args.config_cmd == "use":
                ConfigHandler.use_composefile_configuration(
                    ".", args.name)

            elif args.config_cmd == "update":
                SchemaHandler.generate_compose_from_configuration(
                    ".", args.name)

            elif args.config_cmd == "status":
                config = ConfigHandler.get_current_config(".")
                if not config:
                    Logger.warn("No configuration selected.")
                else:
                    Logger.info("Current configuration: `{0}`".format(config))

        # if command == "scaffold" and args.scaffold_cmd == "project":
        #     Scaffolder.scaffold_project(args.project_path, args.project_name)
        #     return

        # elif command == "schema" and args.schema_cmd == "build":
        #     SchemaHandler.build_schema(".", args.name, args.namespace, args.environment)
        #     return

        # # Validation
        # ConfigHandler.validate_config(args.config)

        # config = ConfigHandler(
        #     args.config, args.namespace if "namespace" in args else "default")
        # compose = config.compose_tool
        # compose_file = ".docker-compose.yml"

        # if command == "machine":
        #     if args.machine_cmd == "daemon":
        #         compose.daemon(args.machine)

        #     elif args.machine_cmd == "run":
        #         compose.run(args.machine, args.run_command)

        #     elif args.machine_cmd == "shell":
        #         compose.shell(args.machine)

        #     elif args.machine_cmd == "stop":
        #         compose.stop(args.machine)

        #     elif args.machine_cmd == "restart":
        #         compose.restart(args.machine)

        #     elif args.machine_cmd == "exec":
        #         compose.execute(args.machine, args.exec_command,
        #                         not args.no_tty, args.return_code)

        #     elif args.machine_cmd == "logs":
        #         compose.logs(args.machine)

        #     elif args.machine_cmd == "copy":
        # compose.copy(args.machine, args.container_path, args.host_path)

        #     elif args.machine_cmd == "push":
        # compose.push(args.machine, args.host_path, args.container_path)

        #     elif args.machine_cmd == "build":
        #         compose.build(args.machine)

        # elif command == "volume":
        #     if args.volume_cmd == "ls":
        #         compose.list_volumes()

        #     elif args.volume_cmd == "rm":
        #         compose.remove_volume(args.name)

        # elif command == "nfs":
        #     if args.nfs_cmd == "ls":
        #         compose.list_nfs_volumes(config)

        #     elif args.nfs_cmd == "rm":
        #         compose.remove_nfs_volume(config, args.name)

        #     elif args.nfs_cmd == "create":
        #         compose.create_nfs_volume(config, args.name)

        # elif command == "env":
        #     if args.env_cmd == "ls":
        #         EnvHandler.list_envs()

        #     elif args.env_cmd == "use":
        #         filename = "./envs/{0}.env.py".format(args.env_name)
        #         if not os.path.isfile(filename):
        #             Logger.error(
        #                 "Bad env file: {0} does not exist.".format(filename))
        #         sharedfolder = "./shared"
        #         if not os.path.isdir(sharedfolder):
        #             Logger.error(
        #                 "Bad shared folder: {0} does not exist.".format(sharedfolder))

        #         env_vars = EnvHandler.load_env_in_memory(filename)
        #         Renderer.render_files(sharedfolder, env_vars)
        #         EnvHandler.write_env_to_file(env_vars, ".env")

        # elif command == "scaffold":
        #     if args.scaffold_cmd == "image":
        #         Scaffolder.scaffold_image(
        #             args.image_name, args.image_tag, args.image_version)

        #     elif args.scaffold_cmd == "env":
        #         Scaffolder.scaffold_environment(".", args.name)

        #     elif args.scaffold_cmd == "link-compose":
        #         Scaffolder.scaffold_link_composefile(
        #             args.composefile_name, unlink=False)
        #     elif args.scaffold_cmd == "unlink-compose":
        #         Scaffolder.scaffold_link_composefile(
        #             args.composefile_name, unlink=True)

        # elif command == "schema":
        #     if args.schema_cmd == "ls":
        #         config.list_schemas()

        #     if args.schema_cmd == "down":
        #         self._use_schema(config, args)
        #         compose.down()

        #     elif args.schema_cmd == "up":
        #         self._use_schema(config, args)
        #         compose.up()

        #     elif args.schema_cmd == "ps":
        #         self._use_schema(config, args)
        #         compose.list_processes()

        #     elif args.schema_cmd == "restart":
        #         self._use_schema(config, args)
        #         compose.reup()

            # elif args.schema_cmd == "build":
            #     self._use_schema(config, args)
            #     config.build_schema(args.schema)

        # elif command == "export":
            # if args.clean:
                # Exporter.clean(config, compose_file)
                # Logger.info("Generating new compose file...")
                # config.write_compose(compose_file, config.get_current_schema())
                # if args.build:
                # config.build_schema(config.get_current_schema())
            # else:
                # Exporter.export(config, compose_file,
                # args.swarm, args.swarm_registry)
                # if args.build:
                # config.build_schema(config.get_current_schema())

        # elif command == "swarm":
        #     if args.swarm_cmd == "push":
        #         compose.push_stack()

        #     elif args.swarm_cmd == "up":
        #         compose.deploy_stack()

        #     elif args.swarm_cmd == "down":
        #         compose.rm_stack()

        #     elif args.swarm_cmd == "ls":
        #         compose.service_list()

        #     elif args.swarm_cmd == "ps":
        #         compose.service_ps(args.machine)

        # elif command == "network":
        #     if args.network_cmd == "create-overlay":
        #         compose.create_overlay_network(args.name)

        #     elif args.network_cmd == "ls":
        #         compose.list_networks()

        #     elif args.network_cmd == "rm":
        #         compose.remove_network(args.name)

        # else:
        #     for p in self.post_parsers:
        #         if p(self, args):
        #             break
