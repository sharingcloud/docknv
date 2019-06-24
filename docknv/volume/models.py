"""Volume object."""

import os
import platform

from .methods import volume_generate_namespaced_root
from .exceptions import MalformedVolume


class Volume(object):
    """Volume object."""

    def __init__(self, host_path, container_path, mode="rw"):
        """
        Volume object constructor.

        :param host_path:        Host path (str)
        :param container_path:   Container path (str)
        :param mode:             Mode (str) (default: rw)
        """
        self.host_path = host_path
        self.container_path = container_path
        self.mode = mode

        self.is_absolute = self.host_path.startswith("/") or (
            ":" in self.host_path
        )
        self.is_relative = not self.is_absolute and (
            any(character in self.host_path for character in "/\\")
        )
        self.is_named = not self.is_absolute and not self.is_relative

    def get_namespaced_path(self, session, file_type, config_name):
        """
        Get a namespaced volume path.

        :param session:          User session
        :param file_type:        Type of file (str) (static/shared)
        :param config_name:      Config name (str)

        :rtype: Volume path (str)
        """
        return os.path.normpath(
            "{0}/{1}".format(
                volume_generate_namespaced_root(
                    session, file_type, config_name
                ),
                self.host_path,
            )
        )

    @classmethod
    def load_from_entry(cls, line, system=None):
        """
        Extract a Volume from a line string.

        :param line:    Line string (str)
        :param system:  Override system (str?)
        :rtype: Volume object data (VolumeObject)
        """
        if system:
            system_name = system
        else:
            system_name = platform.system()

        drive = ""
        if system_name == "Windows" and line[1] == ":":
            drive, line = line[:2], line[2:]

        split_line = line.split(":")
        len_split_line = len(split_line)

        if len_split_line == 3 or len_split_line == 2:
            split_line[0] = drive + split_line[0]
            return cls(*split_line)
        else:
            raise MalformedVolume(f"bad entry {line}")

    def __str__(self):
        """Str."""
        return ":".join((self.host_path, self.container_path, self.mode))
