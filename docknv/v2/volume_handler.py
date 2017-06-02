"""
Volume handler
"""


class VolumeHandler(object):
    """
    Volume handler
    """

    class VolumeObject(object):
        """
        Volume object entry
        """

        def __init__(self, host_path, container_path, mode="rw"):
            self.host_path = host_path
            self.container_path = container_path
            self.mode = mode

            self.update_filters()

        def update_filters(self):
            """
            Update filter values from host path, container path and mode.
            """

            # Filters
            self.is_absolute = self.host_path.startswith("/")
            self.is_relative = not self.is_absolute and any(
                character in self.host_path for character in "/\\")
            self.is_named = not self.is_absolute and not self.is_relative

        def generate_namespaced_path(self, type, path, namespace, environment):
            """
            Generate a namespaced path.

            @param type         Type of file (static/shared)
            @param path         File path
            @param namespace    Current namespace name
            @param environment  Current environment file name

            @return Path
            """

            if type == "static":
                return "./data/local/{0}/{1}/static/{2}".format(namespace, environment, path)
            elif type == "shared":
                return "./data/global/{0}".format(path)

        def __str__(self):
            return ":".join((self.host_path, self.container_path, self.mode))

    @staticmethod
    def extract_from_line(line):
        """
        Extract a VolumeObject from a line string.

        @param line Line string
        """

        split_line = line.split(":")
        len_split_line = len(split_line)

        if len_split_line == 3 or len_split_line == 2:
            return VolumeHandler.VolumeObject(*split_line)
        else:
            raise RuntimeError("Bad volume format: {0}".format(line))
