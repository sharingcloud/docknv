"""Composefile preprocessor."""

import copy
import os
import shutil

from collections import OrderedDict

from slugify import slugify

from docknv.logger import Logger
from docknv.utils.paths import create_path_or_replace, create_path_tree
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump
from docknv.utils.ioutils import io_open

from docknv.user_handler import (
    user_get_file_from_project
)
from docknv.template_renderer import renderer_render_template
from docknv.volume_handler import (
    volume_extract_from_line, volume_generate_namespaced_path
)


def composefile_read(project_path, compose_file_path):
    """
    Read a compose file.

    :raise LoggerError

    :param project_path:         Project path (str)
    :param compose_file_path:    Compose file path (str)

    :rtype: File content (dict)
    """
    real_path = os.path.join(project_path, compose_file_path)

    if not os.path.exists(real_path):
        Logger.error(
            "Compose file `{0}` does not exist.".format(compose_file_path))

    with io_open(real_path, encoding="utf-8", mode="r") as handle:
        content = yaml_ordered_load(handle.read())

    return content


def composefile_multiple_read(project_path, compose_file_paths):
    """
    Read multiple compose files.

    :raise LoggerError

    :param project_path:         Project path (str)
    :param compose_file_paths:   Compose file paths (str)

    :rtype: List of file contents (iterable)
    """
    return [composefile_read(project_path, path)
            for path in compose_file_paths if path]


def composefile_write(compose_content, output_path):
    """
    Write compose content to a file.

    :param compose_content:  Compose content (dict)
    :param output_path:      Output path (str)
    """
    with io_open(output_path, encoding="utf-8", mode="w") as handle:
        handle.write(yaml_ordered_dump(compose_content))

    Logger.debug("Compose content written to file `{0}`".format(output_path))


def composefile_filter(merged_content, schema_configuration):
    """
    Filter composefile content using a schema configuration.

    :param merged_content:           Compose file content (dict)
    :param schema_configuration:     Schema configuration (str)
    :rtype: Filtered content (dict)
    """
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
        new_merged = _composefile_filter_volumes(new_merged, needed_volumes)
        new_merged = _composefile_filter_networks(new_merged, needed_networks)
        new_merged = _composefile_filter_services(new_merged, needed_services)

        return new_merged


def _composefile_filter_volumes(content, needed):
    to_remove = []
    if "volumes" in content:
        for volume_name in content["volumes"]:
            if volume_name not in needed:
                to_remove.append(volume_name)

    for value in to_remove:
        Logger.debug("- Removing volume {0}...".format(value))
        del content["volumes"][value]

    return content


def _composefile_filter_services(content, needed):
    to_remove = []
    for service_name in content["services"]:
        if service_name not in needed:
            to_remove.append(service_name)

    for value in to_remove:
        Logger.debug("- Removing service {0}...".format(value))
        del content["services"][value]

    return content


def _composefile_filter_networks(content, needed):
    to_remove = []
    if "networks" in content:
        for network_name in content["networks"]:
            if network_name not in needed:
                to_remove.append(network_name)

    for value in to_remove:
        Logger.debug("- Removing network {0}...".format(value))
        del content["networks"][value]

    return content


def composefile_apply_namespace(compose_content, namespace="default", environment="default"):
    """
    Apply namespace to compose content.

    :param compose_content:  Compose content (dict)
    :param namespace:        Namespace name (str) (default: default)
    :param environment:      Environment file name (str) (default: default)
    :rtype: dict
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
    return _composefile_apply_namespace_replacement(output_content, namespace, environment, shared_volumes)


def _composefile_apply_namespace_replacement(output_content, namespace, environment, shared_volumes):
    # Service replacement
    new_keys_repl = OrderedDict()
    for key in output_content["services"]:
        new_key = "{0}_{1}".format(namespace, key)
        new_keys_repl[new_key] = key

        # Find volumes
        new_volumes = OrderedDict()
        if "volumes" in output_content["services"][key]:
            for volume in output_content["services"][key]["volumes"]:
                # Ignore empty volumes
                if volume == "":
                    continue

                volume_object = volume_extract_from_line(volume)
                if volume_object.is_named:
                    if volume_object.host_path in shared_volumes:
                        continue

                    volume_object.host_path = "{0}_{1}_{2}".format(
                        namespace, environment, volume_object.host_path)

                    new_volumes[volume] = str(volume_object)

            # Apply new volumes/Remove old volumes
            for volume in new_volumes:
                new_v = new_volumes[volume]

                Logger.debug("Namespacing volume '{0}' to '{1}'...".format(volume, new_v))
                output_content["services"][key]["volumes"].append(new_v)
                output_content["services"][key]["volumes"].remove(volume)

    # Apply new services/Remove old services
    for key in new_keys_repl:
        old_s = new_keys_repl[key]

        Logger.debug("Namespacing service '{0}' to '{1}'...".format(old_s, key))
        output_content["services"][key] = output_content["services"][new_keys_repl[key]]
        del output_content["services"][new_keys_repl[key]]

    return output_content


def composefile_handle_service_tags(compose_content, registry_url):
    """
    Handle service tags.

    :param project_path:        Project path (str)
    :param compose_content:     Compose content (dict)
    :param registry_url:        Registry URL (str)
    :rtype dict
    """
    Logger.debug("Handling service tags...")
    output_content = copy.deepcopy(compose_content)

    if "services" in output_content:
        for service_name in output_content["services"]:
            service_data = output_content["services"][service_name]

            if "tag" in service_data:
                Logger.debug("Handling tag for service `{0}`...".format(service_name))
                service_tag = service_data["tag"]

                # TODO
                # service_data["image"] = "/".join([registry_url, service_tag])

                service_data["image"] = service_tag
                del service_data["tag"]

    return output_content


def composefile_resolve_volumes(project_path, compose_content, config_name, namespace="default", environment="default",
                                environment_data=None):
    """
    Resolve volumes and Jinja templates path using namespacing.

    :param project_path:     Project path (str)
    :param compose_content:  Compose content (dict)
    :param project_name:     Project name (str)
    :param namespace:        Namespace name (str) (default: default)
    :param environment:      Environment file name (str) (default: default)
    :param environment_data: Environment data (str?) (default: None)
    :rtype: dict
    """
    Logger.debug("Resolving volumes...")
    output_content = copy.deepcopy(compose_content)

    # Cleaning static files
    create_path_or_replace(
        volume_generate_namespaced_path(
            project_path, "static", config_name)
    )

    if "services" in output_content:
        for service_name in output_content["services"]:
            service_data = output_content["services"][service_name]

            # Set environment
            if "env_file" not in service_data:
                service_data["env_file"] = [
                    user_get_file_from_project(project_path, 'environment.env', config_name)
                ]

            Logger.debug(
                "Resolving volumes for service `{0}`...".format(service_name))

            final_volumes = []
            if "volumes" in service_data and isinstance(service_data["volumes"], dict):
                volumes_data = service_data["volumes"]

                # Templates
                final_volumes = _composefile_resolve_template_volumes(project_path, config_name, environment_data,
                                                                      volumes_data, final_volumes)

                # Static files
                final_volumes = _composefile_resolve_static_volumes(project_path, config_name,
                                                                    volumes_data, final_volumes)

                # Shared files
                final_volumes = _composefile_resolve_shared_volumes(project_path, volumes_data, final_volumes)

                # Standard volumes
                final_volumes = _composefile_resolve_standard_volumes(volumes_data, final_volumes)

            service_data["volumes"] = final_volumes

            _composefile_resolve_networks(service_data, namespace)

    return output_content


def _get_files_to_copy(data_path, output_path):
    files_to_copy = []
    if os.path.isfile(data_path):
        files_to_copy.append((data_path, output_path))
    else:
        base_root = data_path
        for root, folders, filenames in os.walk(data_path):
            sub_part = root.replace(base_root, "")
            if len(sub_part) > 0:
                sub_part = sub_part[1:]

            for filename in filenames:
                full_path = os.path.normpath(os.path.join(root, filename))
                full_output_path = os.path.normpath(os.path.join(output_path, sub_part, filename))
                files_to_copy.append((full_path, full_output_path))

    return files_to_copy


def _composefile_resolve_static_volumes(project_path, config_name, volumes_data, output_volumes):
    if "static" in volumes_data:
        for static_def in volumes_data["static"]:
            # Ignore empty volumes
            if static_def == "":
                continue

            volume_object = volume_extract_from_line(static_def)

            # Create dirs & copy
            output_path = volume_object.generate_namespaced_volume_path("static", volume_object.host_path,
                                                                        project_path, config_name)

            data_path = os.path.normpath(os.path.join(project_path, "data", "files", volume_object.host_path))

            # Get files to copy
            files_to_copy = _get_files_to_copy(data_path, output_path)

            # Copy !
            for file_to_copy, output_path_to_copy in files_to_copy:
                Logger.debug(
                    "Copying static content from `{0}` to `{1}`...".format(file_to_copy, output_path_to_copy))
                create_path_tree(os.path.dirname(output_path_to_copy))

                if os.path.isdir(file_to_copy):
                    try:
                        os.mkdir(file_to_copy)
                    except Exception:
                        pass
                else:
                    shutil.copy2(file_to_copy, output_path_to_copy)

            volume_object.host_path = output_path
            output_volumes.append(str(volume_object))

        del volumes_data["static"]

    return output_volumes


def _composefile_resolve_shared_volumes(project_path, volumes_data, output_volumes):
    if "shared" in volumes_data:
        for shared_def in volumes_data["shared"]:
            # Ignore empty volumes
            if shared_def == "":
                continue

            volume_object = volume_extract_from_line(shared_def)

            data_path = os.path.join(project_path, "data", "files", volume_object.host_path)
            Logger.debug("Detecting shared content at `{0}`...".format(data_path))

            volume_object.host_path = data_path
            output_volumes.append(str(volume_object))

        del volumes_data["shared"]

    return output_volumes


def _composefile_resolve_template_volumes(project_path, config_name, environment_data, volumes_data, output_volumes):

    # Jinja templates
    if "templates" in volumes_data:
        for template_def in volumes_data["templates"]:
            # Ignore empty volumes
            if template_def == "":
                continue

            volume_object = volume_extract_from_line(template_def)
            template_path = volume_object.host_path

            # Render template
            rendered_path = renderer_render_template(project_path, template_path, config_name, environment_data)
            volume_object.host_path = rendered_path
            output_volumes.append(str(volume_object))

        del volumes_data["templates"]

    return output_volumes


def _composefile_resolve_standard_volumes(volumes_data, output_volumes):
    if "standard" in volumes_data:
        for standard_def in volumes_data["standard"]:
            # Ignore empty volumes
            if standard_def == "":
                continue

            output_volumes.append(standard_def)

        del volumes_data["standard"]

    return output_volumes


def _composefile_resolve_networks(service_data, namespace):
    if "networks" in service_data:
        for network_name in service_data["networks"]:
            network = service_data["networks"][network_name]
            if isinstance(network, dict) and "aliases" in network:
                new_aliases = []
                for alias in network["aliases"]:
                    if namespace == "default":
                        new_alias = slugify(alias)
                    else:
                        new_alias = slugify("-".join([namespace, alias]))

                    new_aliases.append(new_alias)

                network["aliases"] = new_aliases
