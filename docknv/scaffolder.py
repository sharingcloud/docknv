"""Scaffolder methods."""

from __future__ import print_function
from __future__ import unicode_literals

import os

from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump
from docknv.utils.prompt import prompt_yes_no
from docknv.utils.ioutils import io_open

from docknv.logger import Logger


def scaffold_project(project_path, project_name=None):
    """
    Scaffold a Docknv project.

    :param project_path:     Project path (str)
    :param project_name:     Project name (str?) (default: None)
    """
    project_name = project_name if project_name else os.path.basename(project_path)
    paths = ["envs", "data", "composefiles", "images"]
    data_paths = ["files"]

    if os.path.exists(project_path):
        choice = prompt_yes_no(
            "/!\\ WARNING: The project path `{0}` already exists. Overwrite all ?".format(project_path)
        )

        if not choice:
            print("Nothing done.")
            return

    # Main folder
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    # Ignore file
    scaffold_ignore(project_path, force=True)

    # Create paths
    for path in paths:
        joined_path = os.path.join(project_path, path)
        if not os.path.exists(joined_path):
            os.makedirs(joined_path)

    for path in data_paths:
        joined_path = os.path.join(project_path, "data", path)
        if not os.path.exists(joined_path):
            os.makedirs(joined_path)

    # Create config file
    scaffold_config(project_path, project_name)

    # Create default env
    scaffold_environment(project_path, "default")

    Logger.info("New project `{0}` initialized in `{1}`".format(project_name, project_path))


def scaffold_config(project_path, project_name=None):
    """
    Scaffold a basic config file.

    :param project_path:     Project path (str)
    :param project_name:     Project name (str?) (default: None)
    """
    config_content = "project_name: {0}\n\nschemas:\ncomposefiles:".format(project_name)

    joined_path = os.path.join(project_path, "config.yml")
    with io_open(joined_path, encoding="utf-8", mode="wt") as handle:
        handle.write(config_content)

    Logger.info("Configuration file created.")


def scaffold_environment(project_path, env_name, env_content=None):
    """
    Scaffold an environment.

    :param project_path:     Project path (str)
    :param env_name:         Environment name (str)
    :param env_content:      Environment content (str?) (default: None)
    """
    from docknv.environment_handler import env_write_to_file

    env_content = env_content if env_content else {}
    env_path = os.path.join(project_path, "envs",
                            "".join((env_name, ".env.py")))
    if os.path.exists(env_path):
        choice = prompt_yes_no(
            "/!\\ WARNING: The environment file `{0}` already exists. Overwrite ?".format(env_name)
        )

        if not choice:
            print("Nothing done.")
            return

    # Create file
    with io_open(env_path, encoding="utf-8", mode="wt+") as handle:
        handle.write("")

    # Write env to file
    env_content_len = len(env_content)
    if env_content_len > 0:
        env_write_to_file(env_content, env_path)
    else:
        Logger.info("Empty environment file `{0}` created.".format(env_name))


def scaffold_environment_copy(project_path, env_name_source, env_name_dest):
    """
    Copy an environment.

    :param project_path:     Project path (str)
    :param env_name_source:  Source environment name (str)
    :param env_name_dest:    Destination environment name (str)
    """
    if env_name_source == env_name_dest:
        Logger.error('Source environment name and destination environment name cannot be the same.')

    env_path_source = os.path.join(project_path, "envs", "".join((env_name_source, ".env.py")))
    env_path_dest = os.path.join(project_path, "envs", "".join((env_name_dest, ".env.py")))

    if not os.path.exists(env_path_source):
        Logger.error("Missing environment file `{0}`.".format(env_name_source))

    if os.path.exists(env_path_dest):
        choice = prompt_yes_no(
            "/!\\ WARNING: The environment file `{0}` already exists. Overwrite ?".format(env_name_dest)
        )

        if not choice:
            print("Nothing done.")
            return

    # Loading source env
    source_content = []
    with io_open(env_path_source, encoding='utf-8', mode='r') as handle:
        source_content = handle.readlines()

    with io_open(env_path_dest, encoding='utf-8', mode="wt+") as handle:
        handle.write('# -*- import: {0} -*-\n\n'.format(env_name_source))
        for line in source_content:
            if not line.startswith('#') and not line.startswith('"""') and line != '\n':
                handle.write('# ')
            handle.write(line)

    Logger.info("Environment file `{0}` copied to `{1}`".format(env_name_source, env_name_dest))


def scaffold_link_composefile(project_path, compose_file_name, unlink=False):
    """
    Link/Unlink a compose file in a project.

    :param compose_file_name:    Compose file name (str)
    :param project_path:         Project path (str)
    :param unlink:               Unlink if true, else link (bool) (default: False)
    """
    config_file = os.path.join(project_path, "config.yml")
    compose_file = os.path.join(project_path, "composefiles", compose_file_name)

    if not os.path.exists(config_file):
        Logger.error("Config file `{0}` does not exist.".format(config_file))

    if not os.path.exists(compose_file):
        Logger.error("Compose file `{0}` does not exist.".format(compose_file))

    with io_open(config_file, encoding="utf-8", mode="rt") as handle:
        content = yaml_ordered_load(handle.read())

    if "composefiles" not in content:
        Logger.error("Missing `composefiles` section in config.yml.")

    composefiles = content["composefiles"] if content["composefiles"] else []
    compose_file_path = "./composefiles/" + compose_file_name

    if unlink:
        if compose_file_path in composefiles:
            composefiles.remove(compose_file_path)
            Logger.info("Compose file `{0}` unlinked from config.yml".format(compose_file_name))
        else:
            Logger.warn("Missing compose file entry `{0}` in config.yml".format(compose_file_path))
    else:
        if compose_file_path in composefiles:
            Logger.warn("Compose file entry `{0}` already present in config.yml. Ignoring.".format(compose_file_path))
        else:
            composefiles.append(compose_file_path)
            Logger.info("Compose file `{0}` linked in config.yml".format(compose_file_name))

    content["composefiles"] = composefiles

    with io_open(config_file, encoding="utf-8", mode="wt") as handle:
        handle.write(yaml_ordered_dump(content))


def scaffold_ignore(project_path, force=False):
    """
    Scaffold an ignore file.

    :param project_path:     Project path (str)
    :param force:            No prompt user (bool) (default: False)
    """
    file_content = "rendered/\n__pyc__/\n*.pyc\n*.docknv*"
    ignore_file = os.path.join(project_path, ".gitignore")

    if os.path.exists(ignore_file):
        choice = prompt_yes_no("/!\\ WARNING: The .gitignore file already exists. Overwrite ?", force)

        if not choice:
            print("Nothing done.")
            return

    if not os.path.exists(project_path):
        Logger.error("Project path `{0}` does not exist.".format(project_path))

    with io_open(ignore_file, encoding="utf-8", mode="wt") as handle:
        handle.write(file_content)

    Logger.info("Ignore file created.")


def scaffold_image(project_path, image_name, image_url, image_tag="latest"):
    """
    Scaffold an image Dockerfile.

    :param project_path:     Project path (str)
    :param image_name:       Image name (str)
    :param image_url:        Image URL (str)
    :param image_tag:        Image tag (str) (default: latest)
    """
    image_url = image_url if image_url else image_name
    image_path = os.path.join(project_path, "images")

    if not os.path.exists(image_path):
        os.makedirs(image_path)

    local_image_path = os.path.join(image_path, image_name)
    if not os.path.exists(local_image_path):
        os.makedirs(local_image_path)

    dockerfile_path = os.path.join(local_image_path, "Dockerfile")
    if os.path.exists(dockerfile_path):
        choice = prompt_yes_no(
            "/!\\ WARNING: The Dockerfile `{0}` already exists. Overwrite ?".format(dockerfile_path)
        )

        if not choice:
            print("Nothing done.")
            return

    generated_dockerfile = "FROM {0}:{1}\n".format(image_url, image_tag)

    with io_open(dockerfile_path, encoding="utf-8", mode="wt") as handle:
        handle.write(generated_dockerfile)

    Logger.info("Dockerfile generated for image `{0}`, using `{1}:{2}`".format(
        image_name, image_url, image_tag))
