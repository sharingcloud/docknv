import os
import shutil


from .logger import Logger

class NFSHandler(object):

    @staticmethod
    def list_namespace_volumes(path, namespace):
        if not NFSHandler.do_namespace_exist(path, namespace):
            NFSHandler.create_namespace(path, namespace)

        dirs = os.listdir(os.path.join(path, namespace))
        if len(dirs) == 0:
            Logger.info("No volumes found in namespace `{0}`".format(namespace))
        else:
            Logger.info("Volumes for namespace `{0}`:".format(namespace))
            for d in dirs:
                Logger.raw("  - {0}".format(d))

    @staticmethod
    def list_namespaces(path):
        if not os.path.isdir(path):
            Logger.error("Path `{0}` does not exist.".format(path))

        dirs = os.listdir(path)
        print(dirs)

    @staticmethod
    def do_volume_exist(path, namespace, name):
        if not NFSHandler.do_namespace_exist(path, namespace):
            NFSHandler.create_namespace(path, namespace)

        return os.path.isdir(os.path.join(os.path.join(path, namespace), name))

    @staticmethod
    def do_namespace_exist(path, namespace):
        return os.path.isdir(os.path.join(path, namespace))

    @staticmethod
    def create_namespace(path, namespace):
        if NFSHandler.do_namespace_exist(path, namespace):
            Logger.info("Volume namespace `{0}` already exist.".format(namespace))
        else:
            Logger.info("Creating volume namespace `{0}`...".format(namespace))
            os.makedirs(os.path.join(path, namespace))

    @staticmethod
    def remove_namespace(path, namespace):
        if NFSHandler.do_namespace_exist(path, namespace):
            Logger.info("Deleting volume namespace `{0}`...".format(namespace))
            shutil.rmtree(os.path.join(path, namespace))
        else:
            Logger.error("Volume namespace `{0}` does not exist.".format(namespace))

    @staticmethod
    def remove_volume(path, namespace, name):
        if NFSHandler.do_volume_exist(path, namespace, name):
            Logger.info("Removing volume `{0}` from namespace `{1}`...".format(name, namespace))
            shutil.rmtree(os.path.join(os.path.join(path, namespace), name))
        else:
            Logger.error("Volume `{0}` from namespace `{1}` does not exist.".format(name, namespace))

    @staticmethod
    def create_volume(path, namespace, name):
        if not NFSHandler.do_namespace_exist(path, namespace):
            NFSHandler.create_namespace(path, namespace)

        if NFSHandler.do_volume_exist(path, namespace, name):
            Logger.info("Volume `{0}` from namespace `{1}` already exist.".format(name, namespace))
        else:
            Logger.info("Creating volume `{0}` from namespace `{1}`...".format(name, namespace))
            os.makedirs(os.path.join(os.path.join(path, namespace), name))
