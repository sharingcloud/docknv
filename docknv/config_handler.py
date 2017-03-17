import yaml
import copy
import os

from .compose import Compose
from .yaml_utils import merge_yaml, merge_yaml_two, ordered_load, ordered_dump
from .logger import Logging, Fore

class ConfigHandler(object):
    def __init__(self, compose_file):
        self._load_config(compose_file)

    def _load_config(self, compose_file):
        compose_content = ""
        compose_file_path = os.path.realpath(compose_file)

        if os.path.isfile(compose_file_path):
            with open(compose_file_path, mode="rt") as f:
                compose_content = ordered_load(f.read())
        else:
            Logging.error("Bad compose file: {0}".format(compose_file_path))

        self.compose_file_path = compose_file_path
        self.compose_file_dir = os.path.dirname(compose_file_path)
        self.compose_content = compose_content
        self.namespace = compose_content.get("project_name", os.path.basename(self.compose_file_dir))

        self.compose_tool = Compose(self.namespace)

    def generate_compose(self):
        if "templates" not in self.compose_content:
            Logging.error("Missing `templates` section in compose config.")

        contents = []
        for template in self.compose_content["templates"]:
            template_content = ""

            # Relative to absolute
            if template[0] == ".":
                template = self.compose_file_dir + template[1:]

            if not os.path.isfile(template):
                Logging.error("Bad compose template file: {0}".format(template))
            else:
                Logging.info("Using template `{0}`...".format(template)

                with open(template, mode="rt") as f:
                    template_content = ordered_load(f.read())

            contents.append(template_content)

        return merge_yaml(contents)

    def write_compose(self, output_file):
        result = self.generate_compose()

        Logging.info("Writing compose file to `{0}`...".format(output_file))

        with open(output_file, mode="wt+") as f:
            f.write(ordered_dump(result, default_flow_style=False))

    ##############################
    ##############################

    def list_lifecycles(self):
        if "lifecycles" not in self.compose_content:
            Logging.error("Missing `lifecycles` section in compose config.")

        lifecycles = self.compose_content["lifecycles"]
        for name in lifecycles:
            lifecycle = self.get_lifecycle(name)
            schema_name = lifecycle["schema"]
            schema = self.get_schema(schema_name)
            all_action = lifecycle["action"]
            handlers = lifecycle.get("handlers", {})

            Logging.raw("Lifecycle: " + name, color=Fore.GREEN)
            Logging.raw("  Schema: " + schema_name)
            Logging.raw("  Global action: " + all_action)

            handlers_specs = [k for k in handlers.keys() if k != "ALL"]
            if len(handlers_specs) > 0:
                Logging.raw("  Custom actions:")
                for k in handlers_specs:
                    command = handlers[k]
                    Logging.raw("    {0}: {1}".format(k, command))

            Logging.raw("")

    def get_lifecycle(self, name):
        if "lifecycles" not in self.compose_content:
            Logging.error("Missing `lifecycles` section in compose config.")

        lifecycles = self.compose_content["lifecycles"]
        if name not in lifecycles:
            Logging.error("Missing lifecycle `{0}` definition in compose config.".format(name))

        lifecycle = lifecycles[name]
        return lifecycle

    def run_lifecycle(self, name):
        lifecycle = self.get_lifecycle(name)

        if not "schema" in lifecycle:
            Logging.error("Missing `schema` section in lifecycle `{0}`".format(name))

        schema_name = lifecycle["schema"]
        schema = self.get_schema(schema_name)
        handlers = lifecycle.get("handlers", {})
        all_action = lifecycle["action"]

        for service in schema["services"]:
            # Custom handler ?
            if service in handlers:
                command = handlers[service]
                self.compose_tool.run(service, command)

            if all_action == "start":
                self.compose_tool.daemon(service)
            elif all_action == "stop":
                self.compose_tool.stop(service)

        if all_action == "stop":
            if "networks" in schema:
                for network in schema["networks"]:
                    full_network_name = self.namespace + "_" + network
                    self.compose_tool.remove_network(full_network_name)

    ##############################
    ##############################

    def get_schema(self, name):
        if "schemas" not in self.compose_content:
            Logging.error("Missing `schemas` section in compose config.")

        schemas = self.compose_content["schemas"]
        if name not in schemas:
            Logging.error("Missing schema `{0}` definition in compose config.".format(name))

        schema = schemas[name]

        # Inclusions
        if "includes" in schema:
            includes = schema["includes"]
            include_schemas = [self.get_schema(include_name) for include_name in includes]

            current_schema = copy.deepcopy(schema)
            del current_schema["includes"]
            include_schemas.append(current_schema)

            schema = merge_yaml(include_schemas)

        return schema

    def list_schemas(self):
        if "schemas" not in self.compose_content:
            Logging.error("Missing `schemas` section in compose config.")

        schemas = self.compose_content["schemas"]
        for name in schemas:
            schema = self.get_schema(name)
            Logging.raw("Schema: " + name, color=Fore.GREEN)
            if "volumes" in schema:
                Logging.raw("  Volumes: ", color=Fore.BLUE)
                volumes = schema["volumes"]
                for volume in volumes:
                    Logging.raw("    " + volume)

            if "services" in schema:
                Logging.raw("  Services: ", color=Fore.BLUE)
                services = schema["services"]
                for service in services:
                    Logging.raw("    " + service)
            Logging.raw("")

    def build_schema(self, name):
        schema = self.get_schema(name)

        if "volumes" in schema:
            volumes = schema["volumes"]
            for volume in volumes:
                self.compose_tool.create_volume(volume)

        if "services" in schema:
            services = schema["services"]
            for service in services:
                self.compose_tool.build(service)
