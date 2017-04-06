import argparse
import sys
import os
import re

from .logger import Logger, Fore
from .config_handler import ConfigHandler
from .renderer import Renderer
from .env_handler import EnvHandler
from .exporter import Exporter


class Shell(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Docker and eNVironments")
        self.parser.add_argument("-f", "--config", default="config.yml", help="compose config file")

        self.subparsers = self.parser.add_subparsers(dest="command", metavar="")

        sub_compose = self.subparsers.add_parser("compose", help="manage current machines lifecycle (compose mode)")
        sub_compose_subparsers = sub_compose.add_subparsers(dest="compose_cmd", metavar="")
        sub_compose_down = sub_compose_subparsers.add_parser("down", help="shutdown all")
        sub_compose_up = sub_compose_subparsers.add_parser("up", help="start all")
        sub_compose_ps = sub_compose_subparsers.add_parser("ps", help="show active containers")
        sub_compose_reup = sub_compose_subparsers.add_parser("restart", help="restart all stack")

        sub_schema = self.subparsers.add_parser("schema", help="manage groups of machines at once (schema mode)")
        sub_schema_subparsers = sub_schema.add_subparsers(dest="schema_cmd", metavar="")
        sub_schema_generate = sub_schema_subparsers.add_parser("generate", help="generate compose file for current schema")
        sub_schema_list = sub_schema_subparsers.add_parser("ls", help="list schemas")
        sub_schema_use = sub_schema_subparsers.add_parser("use", help="set a current schema")
        sub_schema_use.add_argument("schema", help="schema name")
        sub_schema_status = sub_schema_subparsers.add_parser("status", help="get current schema")
        sub_schema_build = sub_schema_subparsers.add_parser("build", help="build current schema")
        sub_schema_export = sub_schema_subparsers.add_parser("export", help="export the schema for production")
        sub_schema_export.add_argument("--swarm", action="store_true", help="prepare swarm mode by setting image names")
        sub_schema_export.add_argument("--swarm-registry", nargs="?", default="127.0.0.1:5000", help="swarm registry URL")
        sub_schema_export.add_argument("--build", action="store_true", help="rebuild new images")
        sub_schema_clean_export = sub_schema_subparsers.add_parser("export-clean", help="clean the schema export and generate a new compose file")
        sub_schema_clean_export.add_argument("--build", action="store_true", help="rebuild new images")
        sub_schema_static = sub_schema_subparsers.add_parser("static", help="make the compose file static")

        sub_machine = self.subparsers.add_parser("machine", help="manage one machine at a time (machine mode)")
        sub_machine_subparsers = sub_machine.add_subparsers(dest="machine_cmd", metavar="")
        sub_machine_daemon = sub_machine_subparsers.add_parser("daemon", help="run a container in background")
        sub_machine_daemon.add_argument("machine", help="machine name")
        sub_machine_run = sub_machine_subparsers.add_parser("run", help="run a command on a container")
        sub_machine_run.add_argument("machine", help="machine name")
        sub_machine_run.add_argument("run_command", nargs="?", default="", help="command")
        sub_machine_shell = sub_machine_subparsers.add_parser("shell", help="run shell")
        sub_machine_shell.add_argument("machine", help="machine name")
        sub_machine_shell.add_argument("shell", nargs="?", default="/bin/bash", help="shell executable")
        sub_machine_stop = sub_machine_subparsers.add_parser("stop", help="stop a container")
        sub_machine_stop.add_argument("machine", help="machine name")
        sub_machine_restart = sub_machine_subparsers.add_parser("restart", help="restart a container")
        sub_machine_restart.add_argument("machine", help="machine name")
        sub_machine_exec = sub_machine_subparsers.add_parser("exec", help="execute a command on a running container")
        sub_machine_exec.add_argument("machine", help="machine name")
        sub_machine_exec.add_argument("exec_command", help="command to execute")
        sub_machine_exec.add_argument("-n", "--no-tty", action="store_true", help="disable tty")
        sub_machine_exec.add_argument("-r", "--return-code", action="store_true", help="return code")
        sub_machine_logs = sub_machine_subparsers.add_parser("logs", help="show logs")
        sub_machine_logs.add_argument("machine", help="machine name")
        sub_machine_copy = sub_machine_subparsers.add_parser("copy", help="copy file")
        sub_machine_copy.add_argument("machine", help="machine name")
        sub_machine_copy.add_argument("container_path", help="container path")
        sub_machine_copy.add_argument("host_path", help="host path")
        sub_machine_build = sub_machine_subparsers.add_parser("build", help="build a machine")
        sub_machine_build.add_argument("machine", help="machine name")

        sub_swarm = self.subparsers.add_parser("swarm", help="deploy to swarm (swarm mode)")
        sub_swarm_subparsers = sub_swarm.add_subparsers(dest="swarm_cmd", metavar="")
        sub_swarm_push = sub_swarm_subparsers.add_parser("push", help="push stack to swarm")
        sub_swarm_up = sub_swarm_subparsers.add_parser("up", help="deploy stack to swarm")
        sub_swarm_down = sub_swarm_subparsers.add_parser("down", help="shutdown stack")
        sub_swarm_list = sub_swarm_subparsers.add_parser("ls", help="list current services")
        sub_swarm_ps = sub_swarm_subparsers.add_parser("ps", help="get service info")

        sub_network = self.subparsers.add_parser("network", help="manage networks")
        sub_network_subparsers = sub_network.add_subparsers(dest="network_cmd", metavar="")
        sub_network_create_overlay = sub_network_subparsers.add_parser("create-overlay", help="create an overlay network to use with swarm")
        sub_network_create_overlay.add_argument("name", help="network name")
        sub_network_list = sub_network_subparsers.add_parser("ls", help="list networks")
        sub_network_remove = sub_network_subparsers.add_parser("rm", help="remove network")
        sub_network_remove.add_argument("name", help="network name")

        sub_volume = self.subparsers.add_parser("volume", help="manage volumes")
        sub_volume_subparsers = sub_volume.add_subparsers(dest="volume_cmd", metavar="")
        sub_volume_list = sub_volume_subparsers.add_parser("ls", help="list volumes")
        sub_volume_remove = sub_volume_subparsers.add_parser("rm", help="remove volume")
        sub_volume_remove.add_argument("name", help="volume name")

        sub_env = self.subparsers.add_parser("env", help="manage environments")
        sub_env_subparsers = sub_env.add_subparsers(dest="env_cmd", metavar="")
        sub_env_use = sub_env_subparsers.add_parser("use", help="set env and render templates")
        sub_env_use.add_argument("env_name", help="environment file name (debug, etc.)")
        sub_env_ls = sub_env_subparsers.add_parser("ls", help="list envs")

        self.post_parsers = []

    def register_post_parser(self, fct):
        self.post_parsers.append(fct)

    def run(self, args):
        if len(args) == 0:
            self.parser.print_help()
            sys.exit(1)

        self._parse_args(self.parser.parse_args(args))

    def _parse_args(self, args):
        command = args.command

        # Validation
        ConfigHandler.validate_config(args.config)

        config = ConfigHandler(args.config)
        compose = config.compose_tool
        compose_file = ".docker-compose.yml"

        if command == "compose":
            self._docker_compose_check()

            if args.compose_cmd == "down":
                compose.down()

            elif args.compose_cmd == "up":
                compose.up()

            elif args.compose_cmd == "ps":
                compose.ps()

            elif args.compose_cmd == "restart":
                compose.reup()

        elif command == "machine":
            self._docker_compose_check()

            if args.machine_cmd == "daemon":
                compose.daemon(args.machine)

            elif args.machine_cmd == "run":
                compose.run(args.machine, args.run_command)

            elif args.machine_cmd == "shell":
                compose.shell(args.machine)

            elif args.machine_cmd == "stop":
                compose.stop(args.machine)

            elif args.machine_cmd == "restart":
                compose.restart(args.machine)

            elif args.machine_cmd == "exec":
                compose.execute(args.machine, args.exec_command, not args.no_tty, args.return_code)

            elif args.machine_cmd == "logs":
                compose.logs(args.machine)

            elif args.machine_cmd == "copy":
                compose.copy(args.machine, args.container_path, args.host_path)

            elif args.machine_cmd == "build":
                compose.build(args.machine)

        elif command == "volume":
            if args.volume_cmd == "ls":
                compose.list_volumes()

            elif args.volume_cmd == "rm":
                compose.remove_volume(args.name)

        elif command == "env":
            if args.env_cmd == "ls":
                EnvHandler.list_envs()

            elif args.env_cmd == "use":
                filename = "./envs/{0}.env.py".format(args.env_name)
                if not os.path.isfile(filename):
                    Logger.error("Bad env file: {0} does not exist.".format(filename))
                sharedfolder = "./shared"
                if not os.path.isdir(sharedfolder):
                    Logger.error("Bad shared folder: {0} does not exist.".format(sharedfolder))

                env_vars = EnvHandler.load_env_in_memory(filename)
                Renderer.render_files(sharedfolder, env_vars)
                EnvHandler.write_env_to_file(env_vars, ".env")

        elif command == "schema":
            if args.schema_cmd == "ls":
                config.list_schemas()

            elif args.schema_cmd == "generate":
                self._schema_check()
                config.write_compose(compose_file, config.get_current_schema())

            elif args.schema_cmd == "export":
                self._schema_check()
                Exporter.export(config, compose_file, args.swarm, args.swarm_registry)
                if args.build:
                    config.build_schema(config.get_current_schema())

            elif args.schema_cmd == "export-clean":
                self._schema_check()
                Exporter.clean(config, compose_file)
                Logger.info("Generating new compose file...")
                config.write_compose(compose_file, config.get_current_schema())
                if args.build:
                    config.build_schema(config.get_current_schema())

            elif args.schema_cmd == "use":
                config.set_current_schema(args.schema)
                Logger.raw("Schema set: `{0}`".format(args.schema), Fore.GREEN)

            elif args.schema_cmd == "static":
                config.make_static(compose_file)

            elif args.schema_cmd == "status":
                schema = config.get_current_schema()
                if not schema:
                    Logger.raw("No schema selected. Use `schema use [schema]` to use a schema, `schema ls` to list schemas.", Fore.YELLOW)
                else:
                    Logger.raw("Current schema: `{0}`".format(schema), Fore.GREEN)

            elif args.schema_cmd == "build":
                self._docker_compose_check()
                self._schema_check()

                config.build_schema(config.get_current_schema())

        elif command == "swarm":
            self._docker_compose_check()

            if args.swarm_cmd == "push":
                compose.push_stack()

            elif args.swarm_cmd == "up":
                compose.deploy_stack()

            elif args.swarm_cmd == "down":
                compose.rm_stack()

            elif args.swarm_cmd == "ls":
                compose.service_list()

            elif args.swarm_cmd == "ps":
                compose.service_ps(args.machine)

        elif command == "network":
            if args.network_cmd == "create-overlay":
                compose.create_overlay_network(args.name)

            elif args.network_cmd == "ls":
                compose.list_networks()

            elif args.network_cmd == "rm":
                compose.remove_network(args.name)

        else:
            for p in self.post_parsers:
                if p(self, args):
                    break

    def _docker_compose_check(self):
        if not os.path.exists("./.docker-compose.yml"):
            Logger.error("Before building you should generate the compose file using the `schema generate` command.")

    def _schema_check(self):
        if not os.path.exists("./.docknv_schema"):
            Logger.error("Before using schemas you should set the current schema using `schema use [schema]`")
