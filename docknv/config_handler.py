import yaml
import copy
import os
import shutil

from .compose import Compose
from .yaml_utils import merge_yaml, merge_yaml_two, ordered_load, ordered_dump
from .logger import Logger, Fore

################
# Constants

CURRENT_SCHEMA_FILENAME = "./.docknv_schema"

################

class ConfigHandler(object):
    """
    Handle the docknv config file.
    """

    def __init__(self, compose_file):
        self._load_config(compose_file)

    def _load_config(self, compose_file):
        compose_content = ""
        compose_file_path = os.path.realpath(compose_file)

        if os.path.isfile(compose_file_path):
            with open(compose_file_path, mode="rt") as f:
                compose_content = ordered_load(f.read())
        else:
            Logger.error("Bad compose file: {0}".format(compose_file_path))

        self.compose_file_path = compose_file_path
        self.compose_file_dir = os.path.dirname(compose_file_path)
        self.compose_content = compose_content
        self.namespace = compose_content.get("project_name", None)
        self.configuration = compose_content.get("configuration", {})

        if not self.namespace:
            compose_dir = os.path.basename(self.compose_file_dir)
            compose_dir = compose_dir.replace("-", "")
            self.namespace = compose_dir

        self.compose_tool = Compose(self.namespace)

    @staticmethod
    def validate_config(compose_file):
        """
        Validate the docknv config file.
        """

        compose_content = ""
        compose_file_path = os.path.realpath(compose_file)

        if os.path.isfile(compose_file_path):
            try:
                with open(compose_file_path, mode="rt") as f:
                    compose_content = ordered_load(f.read())
            except Exception as exc:
                Logger.error(
                    "Exception occured during the loading of `{0}`: {1}"
                        .format(compose_file_path, exc)
                )
        else:
            Logger.error("Unknown file: {0}".format(compose_file_path))

        # Validate data

        if "project_name" not in compose_content:
            Logger.error(
                "Missing `project_name` key in config file `{0}`"
                    .format(compose_file_path)
            )

        if "templates" not in compose_content:
            Logger.error(
                "Missing `templates` key in config file `{0}`"
                    .format(compose_file_path)
            )

        if "schemas" not in compose_content:
            Logger.error(
                "Missing `schemas` key in config file `{0}`"
                    .format(compose_file_path)
            )

    def generate_compose(self, schema=None):
        """
        Generate a Docker Compose file from the docknv config.yml
        """

        if "templates" not in self.compose_content:
            Logger.error("Missing `templates` section in compose config.")

        contents = []
        for template in self.compose_content["templates"]:
            template_content = ""

            # Relative to absolute
            if template[0] == ".":
                template = self.compose_file_dir + template[1:]

            if not os.path.isfile(template):
                Logger.error("Bad compose template file: {0}".format(template))
            else:
                Logger.info("Using template `{0}`...".format(template))

                with open(template, mode="rt") as f:
                    template_content = ordered_load(f.read())

            contents.append(template_content)

        merged = merge_yaml(contents)

        if schema:
            Logger.info("Using schema `{0}`...".format(schema))
            if not "schemas" in self.compose_content:
                Logger.error("Missing `schemas` section in compose config.")

            schemas = self.compose_content["schemas"]
            if schema not in schemas:
                Logger.error("Missing schema `{0}` in schemas section.".format(schema))

            schema_data = self.get_schema(schema)
            needed_volumes = schema_data.get("volumes", [])
            needed_services = schema_data.get("services", [])
            needed_networks = schema_data.get("networks", [])

            new_merged = copy.deepcopy(merged)
            to_remove = []
            if "volumes" in new_merged:
                for volume_name in new_merged["volumes"]:
                    if volume_name not in needed_volumes:
                        to_remove.append(volume_name)

            for x in to_remove:
                Logger.debug("- Removing volume {0}...".format(x))
                del new_merged["volumes"][x]

            to_remove = []
            if "networks" in new_merged:
                for network_name in new_merged["networks"]:
                    if network_name not in needed_networks:
                        to_remove.append(network_name)

            for x in to_remove:
                Logger.debug("- Removing network {0}...".format(x))
                del new_merged["networks"][x]

            to_remove = []
            for service_name in new_merged["services"]:
                if service_name not in needed_services:
                    to_remove.append(service_name)

            for x in to_remove:
                Logger.debug("- Removing service {0}...".format(x))
                del new_merged["services"][x]

            return new_merged

        else:
            return merged

    def write_compose(self, output_file, schema=None):
        """
        Write a Docker Compose file to disk
        """

        result = self.generate_compose(schema)

        Logger.info("Writing compose file to `{0}`...".format(output_file))

        with open(output_file, mode="wt+") as f:
            f.write(ordered_dump(result, default_flow_style=False))

    def make_static(self, path):
        """
        Substitute the Docker Compose environment variables with their current
        values from the local .env file.
        """

        if not os.path.isfile(".env"):
            Logger.error("Missing `.env` file. Please generate env using 'env use [environment]'")

        Logger.info("Generating static compose file using .env file...")

        os.system("docker-compose -f {0} config > {0}.out".format(path))
        shutil.copy("{0}.out".format(path), path)
        os.remove("{0}.out".format(path))

    ##############################

    ##############################
    # Schemas

    def get_current_schema(self):
        """
        Fetch the current schema from the docknv schema filename.
        """

        if os.path.isfile(CURRENT_SCHEMA_FILENAME):
            with open(CURRENT_SCHEMA_FILENAME, mode="rt") as f:
                schema = f.read()

            if self.check_schema(schema):
                return schema
            else:
                return None

        else:
            return None

    def set_current_schema(self, schema):
        """
        Set the current schema in the docknv schema filename.
        """

        if self.check_schema(schema):
            with open(CURRENT_SCHEMA_FILENAME, mode="wt+") as f:
                f.write(schema)

        else:
            Logger.error("Could not set unknown schema as current: `{0}`".format(schema))


    def get_schema(self, name):
        """
        Fetch information about one schema.
        """

        if "schemas" not in self.compose_content:
            Logger.error("Missing `schemas` section in compose config.")

        schemas = self.compose_content["schemas"]
        if name not in schemas:
            Logger.error("Missing schema `{0}` definition in compose config.".format(name))

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

    def check_schema(self, schema_name):
        """
        Check if a schema exist in the current compose file.
        """

        if "schemas" not in self.compose_content:
            Logger.error("Missing `schemas` section in compose config.")

        schemas = self.compose_content["schemas"]
        return schema_name in schemas

    def list_schemas(self):
        """
        List all the available schemas from the project.
        """

        if "schemas" not in self.compose_content:
            Logger.error("Missing `schemas` section in compose config.")

        schemas = self.compose_content["schemas"]
        for name in schemas:
            schema = self.get_schema(name)
            Logger.raw("Schema: " + name, color=Fore.GREEN)
            if "volumes" in schema:
                Logger.raw("  Volumes: ", color=Fore.BLUE)
                volumes = schema["volumes"]
                for volume in volumes:
                    Logger.raw("    " + volume)

            if "services" in schema:
                Logger.raw("  Services: ", color=Fore.BLUE)
                services = schema["services"]
                for service in services:
                    Logger.raw("    " + service)
            Logger.raw("")

    def build_schema(self, name):
        schema = self.get_schema(name)

        if "services" in schema:
            services = schema["services"]
            for service in services:
                self.compose_tool.build(service)

    ##############################
