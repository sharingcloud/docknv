"""Shell."""

import argparse
import sys
import os
import imp

from docknv.version import __version__
from docknv.logger import Logger

from docknv.scaffolder import scaffold_environment, scaffold_environment_copy, scaffold_image, \
                              scaffold_link_composefile, scaffold_project
from docknv.environment_handler import env_list, env_show
from docknv.schema_handler import schema_list
from docknv.session_handler import session_show_configuration_list, session_remove_configuration, \
                                   session_update_environment
from docknv.project_handler import project_generate_compose, project_use_configuration, \
                                   project_update_configuration_schema, project_generate_compose_from_configuration, \
                                   project_get_active_configuration, project_clean_user_config_path
from docknv.user_handler import user_try_lock, user_disable_lock
from docknv.dockerfile_packer import dockerfile_packer
from docknv.command_handler import command_get_config, command_get_context

from docknv import lifecycle_handler


class Shell(object):
    """Shell entry-point."""

    def __init__(self):
        """Init."""
        self.parser = argparse.ArgumentParser(description="Docker w/ environments (docknv {0})".format(__version__))
        self.parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

        self.subparsers = self.parser.add_subparsers(dest="command", metavar="")
        self.post_parsers = []

        self._init_commands()

    def register_post_parser(self, fct, cfg, ctx):
        """
        Register a new parser function.

        :param fct  Parser function (fn)
        :param cfg  Configuration (dict)
        :param ctx  Context (dict)
        """
        self.post_parsers.append((fct, cfg, ctx))

    def run(self, args):
        """
        Start and read command-line arguments.

        :param args Arguments
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
        self._init_bundle_commands()
        self._init_swarm_commands()
        self._init_environment_commands()
        self._init_scaffold_commands()
        self._init_registry_commands()
        self._init_image_commands()
        self._init_network_commands()
        self._init_config_commands()
        self._init_volume_commands()
        self._init_user_commands()

    def _init_schema_commands(self):
        cmd = self.subparsers.add_parser(
            "schema", help="manage groups of machines at once (schema mode)")

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

    def _init_bundle_commands(self):
        cmd = self.subparsers.add_parser(
            "bundle", help="manage groups of configs at once (bundle mode)")

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

    def _init_registry_commands(self):
        cmd = self.subparsers.add_parser(
            "registry", help="start and stop registry")

        subs = cmd.add_subparsers(dest="registry_cmd", metavar="")

        start_cmd = subs.add_parser("start", help="start registry")
        start_cmd.add_argument(
            "-p", "--path", help="storage path", nargs="?", default=None)
        subs.add_parser("stop", help="stop registry")

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

    def _init_image_commands(self):
        pass

    def _init_swarm_commands(self):
        cmd = self.subparsers.add_parser(
            "swarm", help="deploy to swarm (swarm mode)")
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

    def _init_environment_commands(self):
        cmd = self.subparsers.add_parser("env", help="manage environments")
        subs = cmd.add_subparsers(dest="env_cmd", metavar="")

        show_cmd = subs.add_parser("show", help="show an environment file")
        show_cmd.add_argument(
            "env_name", help="environment file name (debug, etc.)")

        subs.add_parser("ls", help="list envs")

        use_cmd = subs.add_parser("use", help="set env and render templates")
        use_cmd.add_argument(
            "env_name", help="environment file name (debug, etc.)")

    def _init_volume_commands(self):
        cmd = self.subparsers.add_parser("volume", help="manage volumes")
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

    def _init_network_commands(self):
        cmd = self.subparsers.add_parser("network", help="manage networks")
        subs = cmd.add_subparsers(dest="network_cmd", metavar="")

        subs.add_parser("ls", help="list networks")

        create_overlay_cmd = subs.add_parser("create-overlay", help="create an overlay network to use with swarm")
        create_overlay_cmd.add_argument("name", help="network name")

        rm_cmd = subs.add_parser("rm", help="remove network")
        rm_cmd.add_argument("name", help="network name")

    def _init_user_commands(self):
        cmd = self.subparsers.add_parser(
            "user", help="manage user config files")
        subs = cmd.add_subparsers(dest="user_cmd", metavar="")

        clean_cmd = subs.add_parser("clean-config", help="clean user config files for this project")
        clean_cmd.add_argument("config_name", nargs="?", default=None)

        subs.add_parser("rm-lock", help="remove the user lockfile")

    def _parse_args(self, args):
        command = args.command

        if command == "scaffold":
            if args.scaffold_cmd == "project":
                scaffold_project(
                    args.project_path, args.project_name)

            elif args.scaffold_cmd == "image":
                scaffold_image(
                    ".", args.image_name, args.image_tag, args.image_version)

            elif args.scaffold_cmd == "env":
                if args.from_env:
                    scaffold_environment_copy(
                        ".", args.from_env, args.name)
                else:
                    scaffold_environment(".", args.name)

            elif args.scaffold_cmd == "link-compose":
                scaffold_link_composefile(
                    ".", args.composefile_name, unlink=False)
            elif args.scaffold_cmd == "unlink-compose":
                scaffold_link_composefile(
                    ".", args.composefile_name, unlink=True)

        elif command == "env":
            if args.env_cmd == "ls":
                env_list(".")

            elif args.env_cmd == "show":
                env_show(".", args.env_name)

        elif command == "schema":
            if args.schema_cmd == "build":
                lifecycle_handler.lifecycle_schema_build(
                    ".", args.no_cache, not args.do_not_push)

            elif args.schema_cmd == "start":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_schema_start(
                        ".", foreground=args.foreground)

            elif args.schema_cmd == "status":
                config = project_get_active_configuration(".")
                if not config:
                    Logger.warn(
                        "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
                else:
                    Logger.info("Current configuration: `{0}`".format(config))

            elif args.schema_cmd == "stop":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_schema_stop(".")

            elif args.schema_cmd == "restart":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_schema_restart(".", args.force)

            elif args.schema_cmd == "ps":
                lifecycle_handler.lifecycle_schema_ps(".")

            elif args.schema_cmd == "ls":
                schema_list(".")

        elif command == "machine":
            context = command_get_context(".")
            environment_name = context.environment_name

            if args.machine_cmd == "build":
                lifecycle_handler.lifecycle_machine_build(
                    ".", args.machine, args.no_cache, not args.do_not_push, environment_name)

            elif args.machine_cmd == "daemon":
                lifecycle_handler.lifecycle_machine_daemon(".", args.machine, args.run_command, environment_name)

            elif args.machine_cmd == "run":
                lifecycle_handler.lifecycle_machine_run(
                    ".", args.machine, args.run_command, environment_name)

            elif args.machine_cmd == "exec":
                lifecycle_handler.lifecycle_machine_exec(
                    ".", args.machine, args.run_command, args.no_tty, args.return_code, environment_name)

            elif args.machine_cmd == "shell":
                lifecycle_handler.lifecycle_machine_shell(
                    ".", args.machine, args.shell, environment_name, args.create)

            elif args.machine_cmd == "restart":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_machine_restart(
                        ".", args.machine, args.force, environment_name)

            elif args.machine_cmd == "stop":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_machine_stop(
                        ".", args.machine, environment_name)

            elif args.machine_cmd == "start":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_machine_start(
                        ".", args.machine, environment_name)

            elif args.machine_cmd == "push":
                lifecycle_handler.lifecycle_machine_push(
                    ".", args.machine, args.host_path, args.container_path, environment_name)

            elif args.machine_cmd == "pull":
                lifecycle_handler.lifecycle_machine_pull(
                    ".", args.machine, args.container_path, args.host_path, environment_name)

            elif args.machine_cmd == "logs":
                lifecycle_handler.lifecycle_machine_logs(
                    ".", args.machine, tail=args.tail, follow=args.follow, environment_name=environment_name)

            elif args.machine_cmd == "freeze":
                dockerfile_packer(".", args.machine)

        elif command == "bundle":
            if args.bundle_cmd == "start":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_bundle_start(".", args.configs)
            elif args.bundle_cmd == "stop":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_bundle_stop(".", args.configs)
            elif args.bundle_cmd == "restart":
                with user_try_lock("."):
                    lifecycle_handler.lifecycle_bundle_restart(".", args.configs, args.force)
            elif args.bundle_cmd == "ps":
                lifecycle_handler.lifecycle_bundle_ps(".", args.configs)
            elif args.bundle_cmd == "build":
                lifecycle_handler.lifecycle_bundle_build(
                    ".", args.configs, args.no_cache, not args.do_not_push)

        elif command == "registry":
            if args.registry_cmd == "start":
                lifecycle_handler.lifecycle_registry_start(args.path)
            elif args.registry_cmd == "stop":
                lifecycle_handler.lifecycle_registry_stop()

        elif command == "config":
            if args.config_cmd == "ls":
                session_show_configuration_list(".")

            elif args.config_cmd == "rm":
                session_remove_configuration(".", args.name)

            elif args.config_cmd == "generate":
                project_generate_compose(
                    ".", args.name, args.namespace, args.environment, args.config_name)

            elif args.config_cmd == "use":
                project_use_configuration(
                    ".", args.name)

            elif args.config_cmd == "change-schema":
                project_update_configuration_schema(
                    ".", args.config_name, args.schema_name)

                if args.update:
                    project_generate_compose_from_configuration(
                        ".", args.config_name)
                    project_use_configuration(".", args.config_name)

            elif args.config_cmd == "change-env":
                session_update_environment(
                    ".", args.config_name, args.environment)

                if args.update:
                    project_generate_compose_from_configuration(
                        ".", args.config_name)
                    project_use_configuration(
                        ".", args.config_name)

            elif args.config_cmd == "update":
                if args.name is None:
                    config = project_get_active_configuration(".")
                    if not config:
                        Logger.warn(
                            "No configuration selected. Use 'docknv config use [configuration]' to select a \
                            configuration.")
                    else:
                        project_generate_compose_from_configuration(".", config)
                        project_use_configuration(".", config)
                        if args.restart:
                            lifecycle_handler.lifecycle_schema_stop(".")
                            lifecycle_handler.lifecycle_schema_start(".")

                else:
                    project_generate_compose_from_configuration(
                        ".", args.name)

                    if args.set_current:
                        project_use_configuration(
                            ".", args.name)
                    if args.restart:
                        lifecycle_handler.lifecycle_schema_stop(".")
                        lifecycle_handler.lifecycle_schema_start(".")

            elif args.config_cmd == "status":
                config = project_get_active_configuration(".")
                if not config:
                    Logger.warn(
                        "No configuration selected. Use 'docknv config use [configuration]' to select a configuration.")
                else:
                    Logger.info("Current configuration: `{0}`".format(config))

        elif command == "volume":
            if args.volume_cmd == "ls":
                lifecycle_handler.lifecycle_volume_list(".")

            elif args.volume_cmd == "rm":
                lifecycle_handler.lifecycle_volume_remove(".", args.name)

        elif command == "user":
            if args.user_cmd == "clean-config":
                project_clean_user_config_path(".", args.config_name)
            elif args.user_cmd == "rm-lock":
                user_disable_lock(".")

        for parser, cfg, ctx in self.post_parsers:
            try:
                result = parser(self, args, cfg, ctx)
            except TypeError:
                result = parser(self, args)

            if result:
                break


def docknv_entry_point():
    """Main entry point."""
    current_dir = os.getcwd()
    commands_dir = os.path.join(current_dir, "commands")
    shell = Shell()

    if os.path.exists(commands_dir):
        for root, _, files in os.walk(commands_dir):
            for filename in files:
                if filename.endswith(".py"):
                    base_filename, ext = os.path.splitext(filename)
                    abs_f = os.path.join(root, filename)
                    src = imp.load_source("commands", abs_f)
                    if hasattr(src, "pre_parse") and hasattr(src, "post_parse"):
                        pre_parse = getattr(src, "pre_parse")
                        post_parse = getattr(src, "post_parse")

                        command_config = command_get_config(current_dir, base_filename)
                        command_context = command_get_context(current_dir)

                        try:
                            pre_parse(shell, command_config, command_context)
                        except TypeError:
                            pre_parse(shell)

                        shell.register_post_parser(post_parse, command_config, command_context)

    shell.run(sys.argv[1:])
