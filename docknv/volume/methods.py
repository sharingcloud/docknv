"""Volume methods."""

import os


def volume_generate_namespaced_root(session, file_type, config_name):
    """
    Generate a namespaced volume root.

    :param session:          User session
    :param file_type:        Type of file (str) (static/shared)
    :param config_name:      Config name (str)

    :rtype: Volume path (str)
    """
    user_config_path = session.get_paths().get_user_configuration_root(
        config_name
    )

    if file_type == "static":
        return os.path.normpath("{0}/data/static".format(user_config_path))
    elif file_type == "shared":
        return os.path.normpath("./data/global")
