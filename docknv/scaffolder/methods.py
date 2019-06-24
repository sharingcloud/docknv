"""Scaffolder methods."""

import os

from docknv.project import MissingProject

from docknv.environment import env_get_yaml_path, EnvironmentCollection

from docknv.utils.prompt import prompt_yes_no
from docknv.utils.serialization import yaml_ordered_dump
from docknv.utils.ioutils import io_open


IGNORE_FILE_CONTENT = """
__pyc__/
*.pyc
/*.docker-compose.yml
/.docknv.yml
.DS_Store
"""

CONFIG_FILE_CONTENT = """
composefiles:
commands:
schemas:
"""


def scaffold_project(project_path, force=False):
    """
    Scaffold a docknv project.

    :param project_path:     Project path (str)
    :param force:            Force? (bool) (default: False)
    """
    paths = ["envs", "data", "composefiles", "images"]
    data_paths = ["files"]

    if os.path.exists(project_path):
        choice = prompt_yes_no(
            "/!\\ WARNING: The project path `{0}` already exists. "
            "Overwrite all ?".format(project_path),
            force=force,
        )

        if not choice:
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
    scaffold_config(project_path)

    # Create default env
    scaffold_environment(project_path, "default")


def scaffold_config(project_path):
    """
    Scaffold a basic config file.

    :param project_path:     Project path (str)
    """
    joined_path = os.path.join(project_path, "config.yml")
    with io_open(joined_path, encoding="utf-8", mode="wt") as handle:
        handle.write(CONFIG_FILE_CONTENT)


def scaffold_environment(
    project_path, env_name, env_content=None, force=False
):
    """
    Scaffold an environment.

    :param project_path:     Project path (str)
    :param env_name:         Environment name (str)
    :param env_content:      Environment content (str?) (default: None)
    :param force:            Force? (bool) (default: False)
    """
    env_content = env_content if env_content else {}
    env_path = env_get_yaml_path(project_path, env_name)
    if os.path.exists(env_path):
        choice = prompt_yes_no(
            "/!\\ WARNING: The environment file `{0}` already exists. "
            "Overwrite ?".format(env_name),
            force=force,
        )

        if not choice:
            return

    # Create file
    with io_open(env_path, mode="w") as handle:
        handle.write(yaml_ordered_dump({"environment": {}}))

    # Write env to file
    env_content_len = len(env_content)
    if env_content_len > 0:
        with io_open(env_path, mode="w") as handle:
            handle.write(yaml_ordered_dump({"environment": env_content}))


def scaffold_environment_copy(
    project_path, env_name_source, env_name_dest, force=False
):
    """
    Copy an environment.

    :param project_path:     Project path (str)
    :param env_name_source:  Source environment name (str)
    :param env_name_dest:    Destination environment name (str)
    :param force:            Force? (bool) (default: False)
    """
    env_collection = EnvironmentCollection.load_from_project(project_path)
    env_collection.create_inherited_environment(env_name_source, env_name_dest)


def scaffold_ignore(project_path, force=False):
    """
    Scaffold an ignore file.

    :param project_path:     Project path (str)
    :param force:            No prompt user (bool) (default: False)
    """
    ignore_file = os.path.join(project_path, ".gitignore")

    if os.path.exists(ignore_file):
        choice = prompt_yes_no(
            "/!\\ WARNING: The .gitignore file already exists. Overwrite ?",
            force=force,
        )

        if not choice:
            return

    if not os.path.exists(project_path):
        raise MissingProject(project_path)

    with io_open(ignore_file, encoding="utf-8", mode="wt") as handle:
        handle.write(IGNORE_FILE_CONTENT)


def scaffold_image(
    project_path, image_name, image_url, image_tag="latest", force=False
):
    """
    Scaffold an image Dockerfile.

    :param project_path:     Project path (str)
    :param image_name:       Image name (str)
    :param image_url:        Image URL (str)
    :param image_tag:        Image tag (str) (default: latest)
    :param force:            Force? (bool) (default: False)
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
            "/!\\ WARNING: The Dockerfile `{0}` already exists. "
            "Overwrite ?".format(dockerfile_path),
            force=force,
        )

        if not choice:
            return

    generated_dockerfile = "FROM {0}:{1}\n".format(image_url, image_tag)

    with io_open(dockerfile_path, encoding="utf-8", mode="wt") as handle:
        handle.write(generated_dockerfile)
