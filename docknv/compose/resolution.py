"""Composefile resolution methods."""

import copy
import os
import shutil

from slugify import slugify

from docknv.utils.paths import create_path_or_replace, create_path_tree

from docknv.template import renderer_render_template
from docknv.volume import Volume, volume_generate_namespaced_root


def composefile_resolve_services(content):
    """
    Resolve services.

    :param compose_content:     Compose content (dict)
    :rtype: dict
    """
    output_content = copy.deepcopy(content)

    if "services" in output_content:
        for service_name in output_content["services"]:
            service_data = output_content["services"][service_name]

            if "tag" in service_data:
                service_tag = service_data["tag"]

                service_data["image"] = service_tag
                del service_data["tag"]

            # Handle ports
            if "ports" in service_data:
                # Remove empty ports
                new_ports = []
                for port in service_data["ports"]:
                    if port != "":
                        new_ports.append(port)

                # If no port remain, clean 'ports' section
                if len(new_ports) == 0:
                    del service_data["ports"]
                else:
                    service_data["ports"] = new_ports

    return output_content


def composefile_resolve_volumes(content, config):
    """
    Resolve volumes and Jinja templates path using namespacing.

    :param content:     Compose content (dict)
    :param config:      Config
    :rtype: dict
    """
    output_content = copy.deepcopy(content)
    session = config.session
    config_name = config.name

    # Cleaning static files
    create_path_or_replace(
        volume_generate_namespaced_root(session, "static", config.name)
    )

    if "services" in output_content:
        for service_name in output_content["services"]:
            service_data = output_content["services"][service_name]

            # Set environment
            if "env_file" not in service_data:
                service_data["env_file"] = [
                    session.get_paths().get_file_path(
                        "environment.env", config_name
                    )
                ]

            final_volumes = []
            if "volumes" in service_data and (
                isinstance(service_data["volumes"], dict)
            ):
                volumes_data = service_data["volumes"]

                # Templates
                final_volumes = _composefile_resolve_template_volumes(
                    volumes_data, config, final_volumes
                )

                # Static files
                final_volumes = _composefile_resolve_static_volumes(
                    volumes_data, config, final_volumes
                )

                # Shared files
                final_volumes = _composefile_resolve_shared_volumes(
                    volumes_data, config, final_volumes
                )

                # Standard volumes
                final_volumes = _composefile_resolve_standard_volumes(
                    volumes_data, final_volumes
                )

            service_data["volumes"] = final_volumes

            _composefile_resolve_networks(service_data, config.namespace)

    return output_content


def _composefile_resolve_static_volumes(volumes, config, output):
    if "static" in volumes:
        for static_def in volumes["static"]:
            # Ignore empty volumes
            if static_def == "":
                continue

            volume_object = Volume.load_from_entry(static_def)

            # Create dirs & copy
            output_path = volume_object.get_namespaced_path(
                config.session, "static", config.name
            )

            data_path = os.path.normpath(
                os.path.join(
                    config.database.project_path,
                    "data",
                    "files",
                    volume_object.host_path,
                )
            )

            # Get files to copy
            files_to_copy = _get_files_to_copy(data_path, output_path)

            # Copy !
            for file_to_copy, output_path_to_copy in files_to_copy:
                create_path_tree(os.path.dirname(output_path_to_copy))

                if os.path.isdir(file_to_copy):
                    try:
                        os.mkdir(file_to_copy)
                    except Exception:
                        pass
                else:
                    shutil.copy2(file_to_copy, output_path_to_copy)

            volume_object.host_path = output_path
            output.append(str(volume_object))

        del volumes["static"]

    return output


def _composefile_resolve_shared_volumes(volumes, config, output):
    if "shared" in volumes:
        for shared_def in volumes["shared"]:
            # Ignore empty volumes
            if shared_def == "":
                continue

            volume_object = Volume.load_from_entry(shared_def)

            data_path = os.path.join(
                config.database.project_path,
                "data",
                "files",
                volume_object.host_path,
            )

            volume_object.host_path = data_path
            output.append(str(volume_object))

        del volumes["shared"]

    return output


def _composefile_resolve_template_volumes(volumes, config, output):
    # Jinja templates
    if "templates" in volumes:
        for template_def in volumes["templates"]:
            # Ignore empty volumes
            if template_def == "":
                continue

            volume_object = Volume.load_from_entry(template_def)
            template_path = volume_object.host_path

            # Render template
            rendered_path = renderer_render_template(template_path, config)
            volume_object.host_path = rendered_path
            output.append(str(volume_object))

        del volumes["templates"]

    return output


def _composefile_resolve_standard_volumes(volumes, output):
    if "standard" in volumes:
        for standard_def in volumes["standard"]:
            # Ignore empty volumes
            if standard_def == "":
                continue

            output.append(standard_def)

        del volumes["standard"]

    return output


def _composefile_resolve_networks(services, namespace):
    if "networks" in services:
        for network_name in services["networks"]:
            network = services["networks"][network_name]
            if isinstance(network, dict) and "aliases" in network:
                new_aliases = []
                for alias in network["aliases"]:
                    if namespace is None:
                        new_alias = slugify(alias)
                    else:
                        new_alias = slugify("-".join([namespace, alias]))

                    new_aliases.append(new_alias)

                network["aliases"] = new_aliases


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
                full_output_path = os.path.normpath(
                    os.path.join(output_path, sub_part, filename)
                )
                files_to_copy.append((full_path, full_output_path))

    return files_to_copy
