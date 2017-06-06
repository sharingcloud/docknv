"""
Compose file handler
"""

import os
import copy
import shutil
import codecs

from collections import OrderedDict

from docknv import yaml_utils, utils
from docknv.logger import Logger

from docknv.v2.template_renderer import TemplateRenderer
from docknv.v2.volume_handler import VolumeHandler


class ComposeHandler(object):
    """
    Compose file handler
    """

    @staticmethod
    def load_compose_file(project_path, compose_file_path):
        """
        Load a compose file.

        @param project_path         Project path
        @param compose_file_path    Compose file path

        @return File content
        """

        real_path = os.path.join(project_path, compose_file_path)

        if not os.path.exists(real_path):
            Logger.error(
                "Compose file `{0}` does not exist.".format(compose_file_path))

        with codecs.open(real_path, encoding="utf-8", mode="rt") as handle:
            content = yaml_utils.ordered_load(handle.read())

        return content

    @staticmethod
    def load_multiple_compose_files(project_path, compose_file_paths):
        """
        Load multiple compose files.

        @param project_path         Project path
        @param compose_file_paths   Compose file paths

        @return List of file contents
        """

        return filter(None, [
            ComposeHandler.load_compose_file(project_path, path) for path in compose_file_paths])

    @staticmethod
    def filter_content_with_schema(compose_files_content, schema_configuration):
        """
        Filter multiple compose files content from a schema configuration.

        @param compose_files_content    Compose file content
        @param schema_configuration     Schema configuration
        """

        merged_content = yaml_utils.merge_yaml(compose_files_content)
        all_schema = schema_configuration["name"] == "all"

        if all_schema:
            Logger.info("Using all services, volumes and networks...")
            return merged_content

        else:
            Logger.info("Using schema `{0}`...".format(
                schema_configuration["name"]))

            schema_data = schema_configuration["config"]
            needed_volumes = schema_data.get("volumes", [])
            needed_services = schema_data.get("services", [])
            needed_networks = schema_data.get("networks", [])

            new_merged = copy.deepcopy(merged_content)
            to_remove = []
            if "volumes" in new_merged:
                for volume_name in new_merged["volumes"]:
                    if volume_name not in needed_volumes:
                        to_remove.append(volume_name)

            for value in to_remove:
                Logger.debug("- Removing volume {0}...".format(value))
                del new_merged["volumes"][value]

            to_remove = []
            if "networks" in new_merged:
                for network_name in new_merged["networks"]:
                    if network_name not in needed_networks:
                        to_remove.append(network_name)

            for value in to_remove:
                Logger.debug("- Removing network {0}...".format(value))
                del new_merged["networks"][value]

            to_remove = []
            for service_name in new_merged["services"]:
                if service_name not in needed_services:
                    to_remove.append(service_name)

            for value in to_remove:
                Logger.debug("- Removing service {0}...".format(value))
                del new_merged["services"][value]

            return new_merged

    @staticmethod
    def apply_namespace(compose_content, namespace="default", environment="default"):
        """
        Apply namespace to compose content.

        @param compose_content  Compose content
        @param namespace        Namespace name
        @param environment      Environment file name
        """

        output_content = copy.deepcopy(compose_content)

        if namespace == "default":
            Logger.info("No namespace applied. Default namespace in use.")
            return output_content

        Logger.info("Using namespace `{0}`...".format(namespace))

        # Volume replacement
        shared_volumes = set()
        new_volumes = OrderedDict()
        for volume in output_content["volumes"]:
            if isinstance(output_content["volumes"][volume], dict):
                if "shared" in output_content["volumes"][volume] and output_content["volumes"][volume]["shared"]:
                    shared_volumes.add(volume)

            if volume in shared_volumes:
                continue

            new_key = "{0}_{1}_{2}".format(
                namespace, environment, volume)
            new_volumes[new_key] = volume

        # Cleanup shared mentions
        for key in shared_volumes:
            Logger.debug("Shared named volume detected: {0}".format(key))
            del output_content["volumes"][key]["shared"]

        for key in new_volumes:
            output_content["volumes"][key] = None
            del output_content["volumes"][new_volumes[key]]

        # Service replacement
        new_keys_repl = OrderedDict()
        for key in output_content["services"]:
            new_key = "{0}_{1}".format(namespace, key)
            new_keys_repl[new_key] = key

            # Find volumes
            new_volumes = OrderedDict()
            if "volumes" in output_content["services"][key]:
                for volume in output_content["services"][key]["volumes"]:
                    volume_object = VolumeHandler.extract_from_line(volume)
                    if volume_object.is_named:
                        if volume_object.host_path in shared_volumes:
                            continue

                        volume_object.host_path = "{0}_{1}_{2}".format(
                            namespace, environment, volume_object.host_path)

                        new_volumes[volume] = str(volume_object)

                # Apply new volumes/Remove old volumes
                for volume in new_volumes:
                    new_v = new_volumes[volume]

                    Logger.debug(
                        "Namespacing volume '{0}' to '{1}'...".format(volume, new_v))

                    output_content["services"][key]["volumes"].append(
                        new_v)
                    output_content["services"][key]["volumes"].remove(
                        volume)

        # Apply new services/Remove old services
        for key in new_keys_repl:
            old_s = new_keys_repl[key]

            Logger.debug(
                "Namespacing service '{0}' to '{1}'...".format(old_s, key))

            output_content["services"][key] = output_content["services"][new_keys_repl[key]]
            del output_content["services"][new_keys_repl[key]]

        return output_content

    @staticmethod
    def resolve_compose_content(compose_content, environment_data=None):
        """
        Resolve compose content.

        @param compose_content  Compose content
        @param environment_data Environment data
        """

        Logger.info("Resolving compose content...")
        output_content = copy.deepcopy(compose_content)

        template_result = TemplateRenderer.render_template_inplace(
            output_content, environment_data)

        return yaml_utils.ordered_load(template_result)

    @staticmethod
    def resolve_volumes(project_path, compose_content, namespace="default", environment="default", environment_data=None):
        """
        Resolve volumes, using namespacing.
        Resolve Jinja templates paths.

        @param project_path     Project path
        @param compose_content  Compose content
        @param namespace        Namespace name
        @param environment      Environment file name
        @param environment_data Environment data
        """

        Logger.info("Resolving volumes...")
        output_content = copy.deepcopy(compose_content)

        # Cleaning static files
        utils.create_path_or_replace(
            VolumeHandler.generate_namespaced_path(
                "static", namespace, environment)
        )

        if "services" in output_content:
            for service_name in output_content["services"]:

                Logger.debug(
                    "Resolving volumes for service `{0}`...".format(service_name))

                service_data = output_content["services"][service_name]
                final_volumes = []

                if "volumes" in service_data and isinstance(service_data["volumes"], dict):
                    volumes_data = service_data["volumes"]

                    # Jinja templates
                    if "templates" in volumes_data:
                        for template_def in volumes_data["templates"]:
                            volume_object = VolumeHandler.extract_from_line(
                                template_def)
                            template_path = volume_object.host_path

                            # Render template
                            rendered_path = TemplateRenderer.render_template(
                                project_path, template_path, namespace, environment, environment_data)
                            volume_object.host_path = rendered_path
                            final_volumes.append(str(volume_object))

                        del volumes_data["templates"]

                    # Static files
                    if "static" in volumes_data:
                        for static_def in volumes_data["static"]:
                            volume_object = VolumeHandler.extract_from_line(
                                static_def)

                            # Create dirs & copy
                            output_path = volume_object.generate_namespaced_volume_path(
                                "static", volume_object.host_path, namespace, environment)

                            data_path = os.path.join(
                                project_path, "data", "global", volume_object.host_path)

                            Logger.debug("Copying static content from `{0}` to `{1}`...".format(
                                data_path, output_path))

                            # Copy !
                            if os.path.isfile(data_path):
                                utils.create_path_tree(
                                    os.path.dirname(output_path))

                                shutil.copy(
                                    data_path, output_path)
                            else:
                                try:
                                    shutil.copytree(
                                        data_path, output_path)
                                except OSError:
                                    pass

                            volume_object.host_path = output_path
                            final_volumes.append(str(volume_object))

                        del volumes_data["static"]

                    # Shared files
                    if "shared" in volumes_data:
                        for shared_def in volumes_data["shared"]:
                            volume_object = VolumeHandler.extract_from_line(
                                shared_def)

                            data_path = os.path.join(
                                project_path, "data", "global", volume_object.host_path)

                            Logger.debug("Detecting shared content at `{0}`...".format(
                                data_path))

                            volume_object.host_path = data_path
                            final_volumes.append(str(volume_object))

                        del volumes_data["shared"]

                    # Standard volumes
                    if "standard" in volumes_data:
                        for standard_def in volumes_data["standard"]:
                            final_volumes.append(standard_def)

                        del volumes_data["standard"]

                service_data["volumes"] = final_volumes

                if "networks" in service_data:
                    for network_name in service_data["networks"]:
                        network = service_data["networks"][network_name]
                        if isinstance(network, dict) and "aliases" in network:
                            new_aliases = []
                            for alias in network["aliases"]:
                                new_aliases.append(
                                    "{0}_{1}".format(namespace, alias))

                            network["aliases"] = new_aliases

        return output_content

    @staticmethod
    def write_compose_content_to_file(compose_content, output_path):
        """
        Write compose content to a file.

        @param compose_content  Compose content
        @param output_path      Output path
        """

        with codecs.open(output_path, encoding="utf-8", mode="wt") as handle:
            handle.write(yaml_utils.ordered_dump(compose_content))

        Logger.info(
            "Compose content written to file `{0}`".format(output_path))
