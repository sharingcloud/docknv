import argparse
import sys
import os
import re


class Shell(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="CompoDocker")
        self.parser.add_argument("-f", "--config", default="config.yml", help="compose config file")

        self.subparsers = self.parser.add_subparsers(help="command", dest="command")

        sub_compose = self.subparsers.add_parser("compose", help="compose actions")
        sub_compose_subparsers = sub_compose.add_subparsers(help="compose command", dest="compose_cmd")
        sub_compose_generate = sub_compose_subparsers.add_parser("generate", help="generate compose file")
        sub_compose_down = sub_compose_subparsers.add_parser("down", help="shutdown all")
        sub_compose_ps = sub_compose_subparsers.add_parser("ps", help="show active containers")
        sub_compose_daemon = sub_compose_subparsers.add_parser("daemon", help="run a container in background")
        sub_compose_daemon.add_argument("machine", help="machine name")
        sub_compose_run = sub_compose_subparsers.add_parser("run", help="run a command on a container")
        sub_compose_run.add_argument("machine", help="machine name")
        sub_compose_run.add_argument("run_command", nargs="?", default="", help="command")
        sub_compose_shell = sub_compose_subparsers.add_parser("shell", help="run shell")
        sub_compose_shell.add_argument("machine", help="machine name")
        sub_compose_shell.add_argument("shell", help="shell executable")
        sub_compose_stop = sub_compose_subparsers.add_parser("stop", help="stop a container")
        sub_compose_stop.add_argument("machine", help="machine name")
        sub_compose_restart = sub_compose_subparsers.add_parser("restart", help="restart a container")
        sub_compose_restart.add_argument("machine", help="machine name")

        sub_env = self.subparsers.add_parser("env", help="env actions")
        sub_env_subparsers = sub_env.add_subparsers(help="env command", dest="env_cmd")
        sub_env_generate = sub_env_subparsers.add_parser("generate", help="generate .env file")
        sub_env_generate.add_argument("env_file", help="environment file")
        sub_env_render = sub_env_subparsers.add_parser("render", help="render templates from env")
        sub_env_render.add_argument("env_file", help="environment file")
        sub_env_render.add_argument("folder", help="render templates inside folder")

        sub_schema = self.subparsers.add_parser("schema", help="schema actions")
        sub_schema_subparsers = sub_schema.add_subparsers(help="schema command", dest="schema_cmd")
        sub_schema_list = sub_schema_subparsers.add_parser("list", help="list schemas")
        sub_schema_build = sub_schema_subparsers.add_parser("build", help="build schema")
        sub_schema_build.add_argument("schema", help="schema name")

        sub_lifecycle = self.subparsers.add_parser("lifecycle", help="lifecycle actions")
        sub_lifecycle_subparsers = sub_lifecycle.add_subparsers(help="lifecycle command", dest="lifecycle_cmd")
        sub_lifecycle_list = sub_lifecycle_subparsers.add_parser("list", help="list lifecycles")
        sub_lifecycle_run = sub_lifecycle_subparsers.add_parser("run", help="run lifecycle")
        sub_lifecycle_run.add_argument("lifecycle", help="lifecycle name")

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
            elif args.compose_cmd == "ps":
                self._compose_ps(args)
            elif args.compose_cmd == "daemon":
                self._compose_daemon(args)
            elif args.compose_cmd == "run":
                self._compose_run(args)
            elif args.compose_cmd == "shell":
                self._compose_shell(args)
            elif args.compose_cmd == "stop":
                self._compose_stop(args)
            elif args.compose_cmd == "restart":
                self._compose_restart(args)

        elif command == "env":
            if args.env_cmd == "generate":
                self._generate_env(args)
            elif args.env_cmd == "render":
                self._render_templates(args)

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

        else:
            for p in self.post_parsers:
                if p(self, args):
                    break

    def _docker_compose_check(self):
        if not os.path.exists("./.docker-compose.yml"):
            print("[ERROR] Before building you should generate the docker-compose.yml file using the `compose generate` command.")
            sys.exit(1)

    ############################

    def _generate_compose(self, args):
        from .config_handler import ConfigHandler
        config = ConfigHandler(args.config)
        config.write_compose(".docker-compose.yml")

    def _compose_down(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.down()

    def _compose_ps(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.ps()

    def _compose_stop(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.stop(args.machine)

    def _compose_daemon(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.daemon(args.machine)

    def _compose_run(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.run(args.machine, args.run_command)

    def _compose_shell(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.shell(args.machine)

    def _compose_restart(self, args):
        self._docker_compose_check()

        from .config_handler import ConfigHandler
        c = ConfigHandler(args.config)
        c.compose_tool.restart(args.machine)

    ###########################

    def _generate_env(self, args):
        from .env_handler import EnvHandler
        env_vars = EnvHandler.load_env_in_memory(args.env_file)
        EnvHandler.write_env_to_file(env_vars, ".env")

    def _render_templates(self, args):
        from .env_handler import EnvHandler
        from .renderer import Renderer
        env_vars = EnvHandler.load_env_in_memory(args.env_file)
        Renderer.render_files(args.folder, env_vars)

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
