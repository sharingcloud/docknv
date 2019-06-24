"""Jinja template renderer."""

import os
import copy

from jinja2 import Template

from docknv.utils.serialization import yaml_ordered_dump, yaml_ordered_load
from docknv.utils.ioutils import io_open

from .exceptions import MalformedTemplate, MissingTemplate


def renderer_render_compose_template(compose_content, environment_data=None):
    """
    Resolve compose content.

    :param compose_content:      Compose content (dict)
    :param environment_data:     Environment data (dict?) (default: None)
    :rtype: Template data (dict)
    """
    output_content = copy.deepcopy(compose_content)

    template_result = renderer_render_template_inplace(
        output_content, environment_data
    )

    return yaml_ordered_load(template_result)


def renderer_render_template_inplace(content, environment_data=None):
    """
    Render a Jinja template in-place, using environment data.

    :param content:              Template content (dict)
    :param environment_data:     Environment data (dict?) (default: None)
    :rtype: Template data (str)
    """
    environment_data = environment_data if environment_data else {}
    string_content = yaml_ordered_dump(content)

    template = Template(string_content)
    template_output = template.render(**environment_data)

    return template_output


def renderer_render_template(template_path, config):
    """
    Render a Jinja template, using a namespace and environment.

    :param template_path:        Template path (str)
    :param config:               Configuration
    :rtype: File output name (str)
    """
    config_path = config.session.get_paths().get_user_configuration_root(
        config.name
    )
    environment_data = config.environment_data.data
    templates_path = os.path.join(
        config.database.project_path, "data", "files"
    )

    real_template_path = os.path.join(templates_path, template_path)

    if not os.path.exists(real_template_path):
        raise MissingTemplate(real_template_path)
    if not template_path.endswith(".j2"):
        raise MalformedTemplate(f"bad extension: {template_path}")

    # Creating tree
    local_path = os.path.join(config_path, "data")
    tpl_output_path = os.path.join(local_path, "templates")
    destination_path = os.path.join(
        tpl_output_path, os.path.dirname(template_path)
    )

    for path in (local_path, tpl_output_path, destination_path):
        if not os.path.exists(path):
            os.makedirs(path)

    # Loading template
    with io_open(real_template_path, encoding="utf-8", mode="r") as handle:
        template = Template(handle.read())

    # Rendering template
    file_output = os.path.join(
        destination_path, os.path.basename(template_path)[:-3]
    )
    rendered_template = template.render(**environment_data)

    # Newline handle
    newline = None
    if template_path.endswith(".sh.j2"):
        newline = "\n"

    with io_open(
        file_output, encoding="utf-8", mode="w", newline=newline
    ) as handle:
        handle.write(rendered_template)

    return file_output
