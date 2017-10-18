"""Volume handler."""


import platform


class VolumeObject(object):
    """Volume object entry."""

    def __init__(self, host_path, container_path, mode="rw"):
        """
        The VolumeObject constructor.

        :param host_path:        Host path (str)
        :param container_path:   Container path (str)
        :param mode:             Mode (str) (default: rw)
        """
        self.host_path = host_path
        self.container_path = container_path
        self.mode = mode

        self.is_absolute = False
        self.is_relative = False
        self.is_named = False

        self.update_filters()

    def update_filters(self):
        """Update filter values from host path, container path and mode."""
        # Filters
        self.is_absolute = self.host_path.startswith("/")
        self.is_relative = not self.is_absolute and any(character in self.host_path for character in "/\\")
        self.is_named = not self.is_absolute and not self.is_relative

    def generate_namespaced_volume_path(self, file_type, path, project_name, config_name):
        """
        Generate a namespaced volume path.

        :param file_type:        Type of file (str) (static/shared)
        :param path:             File path (str)
        :param project_name:     Project name (str)
        :param config_name:      Config name (str)

        :rtype: Volume path (str)
        """
        return "{0}/{1}".format(volume_generate_namespaced_path(file_type, project_name, config_name), path)

    def __str__(self):
        """Str."""
        return ":".join((self.host_path, self.container_path, self.mode))


def volume_generate_namespaced_path(file_type, project_name, config_name):
    """
    Generate a namespaced volume path.

    :param file_type:        Type of file (str) (static/shared)
    :param project_name:     Project name (str)
    :param config_name:      Config name (str)

    :rtype: Volume path (str)
    """
    from docknv.user_handler import user_get_project_config_name_path

    user_config_path = user_get_project_config_name_path(project_name, config_name)

    if file_type == "static":
        return "{0}/data/static".format(user_config_path)
    elif file_type == "shared":
        return "./data/global"


def volume_extract_from_line(line):
    """
    Extract a VolumeObject from a line string.

    :param line:     Line string (str)
    :rtype: Volume object data (VolumeObject)
    """
    system_name = platform.system()
    drive = ""
    if system_name == "Windows" and line[1] == ":":
        drive, line = line[:2], line[2:]

    split_line = line.split(":")
    len_split_line = len(split_line)

    if len_split_line == 3 or len_split_line == 2:
        split_line[0] = drive + split_line[0]
        return VolumeObject(*split_line)
    else:
        raise RuntimeError("Bad volume format: {0}".format(line))
