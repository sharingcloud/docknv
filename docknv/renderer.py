import os
import re

from .logger import Logger, Fore

class Renderer(object):

    CONTENT_RGX = re.compile(r'\${(.*?)}', re.MULTILINE)

    @staticmethod
    def replace_match(result, env):
        group = result.group(1)
        if group not in env:
            return ""

        replace = env[group]
        if isinstance(replace, list):
            replace = ", ".join([repr(t) for t in replace])

        return str(replace)

    @staticmethod
    def render_file(path, env):
        if not os.path.isfile(path):
            raise RuntimeError("File `{0}` does not exist".format(path))

        with open(path, mode="rt") as f:
            content = f.read()

        result = re.sub(Renderer.CONTENT_RGX, lambda x: Renderer.replace_match(x, env), content)

        dest_file = path[:-4]
        with open(dest_file, mode="wt+") as f:
            f.write(result)

        Logger.info("Rendering {0} => {1}".format(path, dest_file))

    @staticmethod
    def render_files(folder, env):
        if not os.path.isdir(folder):
            raise RuntimeError("Folder `{0}` does not exist".format(folder))

        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".tpl"):
                    Renderer.render_file(os.path.join(root, f), env)
