from collections import OrderedDict
import os
from typing import Optional

from docknv.logger import Logger, Fore


class MissingImage(Exception):
    """Missing image."""

    def __init__(self, image_name: str):
        """Init."""
        message = f"Missing image {image_name}"
        super(MissingImage, self).__init__(message)


class Image(object):
    """Image."""

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def show(self):
        """Show image."""
        Logger.raw(f"- {self.name} ", color=Fore.GREEN, linebreak=False)
        Logger.raw(f"({self.path})")


class ImageCollection(object):
    """Image collection."""

    def __init__(self, images):
        self.images = images

    def __len__(self):
        return len(self.images)

    def get_image(self, image_name: str) -> Optional[Image]:
        """Get image by name.

        Args:
            image_name (str): Image name

        Returns:
            Optional[Image]: Image instance
        """
        if image_name not in self.images:
            raise MissingImage(image_name)
        return self.images[image_name]

    @classmethod
    def load_from_project(cls, project: "Project") -> "ImageCollection":
        """Load images from project.

        Args:
            project (Project): Project instance

        Returns:
            ImageCollection: Collection
        """
        image_path = os.path.join(project.project_path, "images")
        images = {}
        ordered_images = OrderedDict()
        if os.path.exists(image_path):
            for root, _folders, files in os.walk(image_path):
                if "Dockerfile" in files:
                    image_name = os.path.basename(root)
                    image_path = root.replace(project.project_path + "/", "./")
                    images[image_name] = Image(image_name, image_path)

        for key in sorted(images):
            ordered_images[key] = images[key]

        return cls(ordered_images)

    def show(self):
        """Show collection."""
        for image in self.images.values():
            image.show()
