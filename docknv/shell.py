import argparse
import sys
import os
import re

from .logger import Logger


class Shell(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Docker and eNVironments")
        self.parser.add_argument("-f", "--config", default="config.yml", help="compose config file")

        self.subparsers = self.parser.add_subparsers(help="command", dest="command")

        sub_compose = self.subparsers.add_parser("compose", help="compose actions")
        sub_compose_subparsers = sub_compose.add_subparsers(help="compose command", dest="compose_cmd")
        sub_compose_generate = sub_compose_subparsers.add_parser("generate", help="generate compose file")
        sub_compose_generate.add_argument("schema", nargs="?", help="schema name to generate")
        sub_compose_build = sub_compose_subparsers.add_parser("build", help="build needed containers")
        sub_compose_down = sub_compose_subparsers.add_parser("down", help="shutdown all")
        sub_compose_up = sub_compose_subparsers.add_parser("up", help="start all")
        sub_compose_ps = sub_compose_subparsers.add_parser("ps", help="show active containers")
        sub_compose_export = sub_compose_subparsers.add_parser("export", help="export the compose file for production")
        sub_compose_export.add_argument("--swarm", action="store_true", help="prepare swarm mode by setting image names")
        sub_compose_export.add_argument("--swarm-registry", nargs="?", default="127.0.0.1:5000", help="swarm registry URL")
        sub_compose_clean_export = sub_compose_subparsers.add_parser("export-clean", help="clean the compose export and generate a new compose file")
        sub_compose_clean_export.add_argument("schema", nargs="?", help="new schema to generate")
        sub_compose_reup = sub_compose_subparsers.add_parser("restart", help="restart all stack")
        sub_compose_static = sub_compose_subparsers.add_parser("static", help="make the compose file static")

        sub_swarm = self.subparsers.add_parser("swarm", help="swarm actions")
        sub_swarm_subparsers = sub_swarm.add_subparsers(help="swarm command", dest="swarm_cmd")
        sub_swarm_push = sub_swarm_subparsers.add_parser("push", help="push stack to swarm")
        sub_swarm_up = sub_swarm_subparsers.add_parser("up", help="deploy stack to swarm")
        sub_swarm_down = sub_swarm_subparsers.add_parser("down", help="shutdown stack")

        sub_machine = self.subparsers.add_parser("machine", help="machine actions")
        sub_machine_subparsers = sub_machine.add_subparsers(help="machine command", dest="machine_cmd")
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

        sub_volume = self.subparsers.add_parser("volume", help="volume actions")
        sub_volume_subparsers = sub_volume.add_subparsers(help="volume command", dest="volume_cmd")
        sub_volume_list = sub_volume_subparsers.add_parser("list", help="list volumes")
        sub_volume_remove = sub_volume_subparsers.add_parser("remove", help="remove volume")
        sub_volume_remove.add_argument("name", help="volume name")

        sub_env = self.subparsers.add_parser("env", help="env actions")
        sub_env_subparsers = sub_env.add_subparsers(help="env command", dest="env_cmd")
        # sub_env_generate = sub_env_subparsers.add_parser("generate", help="generate .env file")
        # sub_env_generate.add_argument("env_file", help="environment file")
        # sub_env_render = sub_env_subparsers.add_parser("render", help="render templates from env")
        # sub_env_render.add_argument("env_file", help="environment file")
        # sub_env_render.add_argument("folder", help="render templates inside folder")
        sub_env_use = sub_env_subparsers.add_parser("use", help="set env and render templates")
        sub_env_use.add_argument("env_name", help="environment file name (debug, etc.)")

        sub_schema = self.subparsers.add_parser("schema", help="schema actions")
        sub_schema_subparsers = sub_schema.add_subparsers(help="schema command", dest="schema_cmd")
        sub_schema_list = sub_schema_subparsers.add_parser("list", help="list schemas")
        # sub_schema_build = sub_schema_subparsers.add_parser("build", help="build schema")
        # sub_schema_build.add_argument("schema", help="schema name")

        # sub_lifecycle = self.subparsers.add_parser("lifecycle", help="lifecycle actions")
        # sub_lifecycle_subparsers = sub_lifecycle.add_subparsers(help="lifecycle command", dest="lifecycle_cmd")
        # sub_lifecycle_list = sub_lifecycle_subparsers.add_parser("list", help="list lifecycles")
        # sub_lifecycle_run = sub_lifecycle_subparsers.add_parser("run", help="run lifecycle")
        # sub_lifecycle_run.add_argument("lifecycle", help="lifecycle name")

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
        function_name = "_" + re.sub(r'-', '_', command)

        if command == "compose":
            if args.compose_cmd == "generate":
                self._generate_compose(args)
            elif args.compose_cmd == "down":
                self._compose_down(args)
            elif args.compose_cmd == "up":
                self._compose_up(args)
            elif args.compose_cmd == "ps":
                self._compose_ps(args)
            elif args.compose_cmd == "export":
                self._compose_export(args)
            elif args.compose_cmd == "export-clean":
                self._compose_export_clean(args)
            elif args.compose_cmd == "build":
                self._compose_build(args)
            elif args.compose_cmd == "restart":
                self._compose_reup(args)
            elif args.compose_cmd == "static":
                self._compose_static(args)

        elif command == "machine":
            if args.machine_cmd == "daemon":
                self._machine_daemon(args)
            elif args.machine_cmd == "run":
                self._machine_run(args)
            elif args.machine_cmd == "shell":
                self._machine_shell(args)
            elif args.machine_cmd == "stop":
                self._machine_stop(args)
            elif args.machine_cmd == "restart":
                self._machine_restart(args)
            elif args.machine_cmd == "exec":
                self._machine_exec(args)
            elif args.machine_cmd == "logs":
                self._machine_logs(args)
            elif args.machine_cmd == "copy":
                self._machine_copy(args)

        elif command == "volume":
            if args.volume_cmd == "list":
                self._list_volumes(args)
            elif args.volume_cmd == "remove":
                self._remove_volume(args)

        elif command == "env":
            if args.env_cmd == "generate":
                self._generate_env(args)
            elif args.env_cmd == "render":
                self._render_templates(args)
            elif args.env_cmd == "use":
                self._use_env(args)

        elif command == "schema":
            if args.schema_cmd == "list":
                self._list_schemas(args)
            elif args.schema_cmd == "build":
                self._build_schema(args)

        elif command == "lifecycle":
            if args.lifecycle_cmd == "list":
                self._list_lifecycles(args)
            elif args.lifecycle_cmd == "run":
                self._run_lifecycle(args)

        elif command == "swarm":
            if args.swarm_cmd == "push":
                self._push_swarm(args)
            elif args.swarm_cmd == "up":
                self._up_swarm(args)
            elif args.swarm_cmd == "down":
                self._down_swarm(args)

        else:
            for p in self.post_parsers:
                if p(self, args):
                    break

    def _docker_compose_check(self):
        if not os.path.exists("./.docker-compose.yml"):
            Logger.error("Before building you should generate the docker-compose.yml file using the `compose generate` command.")

    ############################

    def _generate_compose(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.write_compose(".docker-compose.yml", args.schema)

    def _compose_down(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.down()

    def _compose_build(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.build_all()

    def _compose_up(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.up()

    def _compose_ps(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.ps()

    def _machine_stop(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.stop(args.machine)

    def _machine_daemon(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.daemon(args.machine)

    def _machine_run(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.run(args.machine, args.run_command)

    def _machine_shell(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.shell(args.machine)

    def _machine_restart(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.restart(args.machine)

    def _machine_exec(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.execute(args.machine, args.exec_command, not args.no_tty, args.return_code)

    def _machine_logs(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.logs(args.machine)

    def _machine_copy(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.copy(args.machine, args.container_path, args.host_path)

    def _compose_export(self, args):
        self._docker_compose_check()

        from .exporter import Exporter
        Exporter.export(".docker-compose.yml", args.swarm, args.swarm_registry)

    def _compose_export_clean(self, args):
        self._docker_compose_check()

        from .exporter import Exporter
        Exporter.clean(".docker-compose.yml")

        # Generate new compose
        Logger.info("Generating new compose file...")
        self._generate_compose(args)

    def _compose_reup(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.reup()

    def _compose_static(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.make_static(".docker-compose.yml")

    def _push_swarm(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.compose_tool.push_stack()

    def _up_swarm(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.compose_tool.deploy_stack()

    def _down_swarm(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.compose_tool.rm_stack()

    ###########################

    def _list_volumes(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.compose_tool.list_volumes()

    def _remove_volume(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.compose_tool.remove_volume(args.name)

    def _generate_env(self, args):
        from .env_handler import EnvHandler
        env_vars = EnvHandler.load_env_in_memory(args.env_file)
        EnvHandler.write_env_to_file(env_vars, ".env")

    def _render_templates(self, args):
        from .env_handler import EnvHandler
        from .renderer import Renderer
        env_vars = EnvHandler.load_env_in_memory(args.env_file)
        Renderer.render_files(args.folder, env_vars)
        EnvHandler.write_env_to_file(env_vars, ".env")

    def _use_env(self, args):
        from .env_handler import EnvHandler
        from .renderer import Renderer

        fname = "./envs/{0}.env.py".format(args.env_name)
        if not os.path.isfile(fname):
            Logger.error("Bad env file: {0} does not exist.".format(fname))

        sfolder = "./shared"
        if not os.path.isdir(sfolder):
            Logger.error("Bad shared folder: {0} does not exist.".format(sfolder))

        env_vars = EnvHandler.load_env_in_memory(fname)
        Renderer.render_files(sfolder, env_vars)
        EnvHandler.write_env_to_file(env_vars, ".env")

    def _list_schemas(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.list_schemas()

    def _build_schema(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.build_schema(args.schema)

    def _run_lifecycle(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.run_lifecycle(args.lifecycle)

    def _list_lifecycles(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.list_lifecycles()
