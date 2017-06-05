"""
Jinja template renderer
"""

import os
import codecs

from jinja2 import Template

from docknv.logger import Logger
from docknv import yaml_utils


class TemplateRenderer(object):
    """
    Jinja template renderer
    """

    @staticmethod
    def render_template_inplace(content, environment_data=None):
        """
        Render a Jinja template in-place, using environment data.

        @param content          Template content
        @param environment_data Environment data
        """

        environment_data = environment_data if environment_data else {}

        Logger.debug("Rendering template in-place...")

        string_content = yaml_utils.ordered_dump(content)

        template = Template(string_content)
        template_output = template.render(**environment_data)

        Logger.debug("Template rendered.")

        return template_output

    @staticmethod
    def render_template(project_path, template_path, namespace="default", environment="default", environment_data=None):
        """
        Render a Jinja template, using a namespace and environment.

        @param project_path     Project path
        @param template_path    Template path
        @param namespace        Namespace name
        @param environment_name Environment file name
        @param environment_data Environment data
        """

        environment_data = environment_data if environment_data else {}
        templates_path = os.path.join(project_path, "templates")
        data_path = os.path.join(project_path, "data")

        real_template_path = os.path.join(templates_path, template_path)

        if not os.path.exists(real_template_path):
            Logger.error(
                "Template `{0}` does not exist.".format(template_path))
        if not template_path.endswith(".j2"):
            Logger.error(
                "Bad Jinja template file: `{0}`. It should end with '.j2'.".format(template_path))

        Logger.debug("Rendering template `{0}`...".format(template_path))

        # Creating tree
        local_path = os.path.join(data_path, "local")
        namespace_path = os.path.join(local_path, namespace)
        environment_path = os.path.join(namespace_path, environment)
        tpl_output_path = os.path.join(environment_path, "templates")
        destination_path = os.path.join(
            tpl_output_path, os.path.dirname(template_path))

        for path in (local_path, namespace_path, environment_path, tpl_output_path, destination_path):
            if not os.path.exists(path):
                os.makedirs(path)

        # Loading template
        with codecs.open(real_template_path, encoding="utf-8", mode="rt") as handle:
            template = Template(handle.read())

        # Rendering template
        file_output = os.path.join(
            destination_path, os.path.basename(template_path)[:-3])
        rendered_template = template.render(**environment_data)
        with codecs.open(file_output, encoding="utf-8", mode="wt") as handle:
            handle.write(rendered_template)

        Logger.info("Template `{0}` rendered to `{1}`.".format(
            template_path, file_output))

        return file_output
