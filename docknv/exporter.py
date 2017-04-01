import os
import re
import shutil
import copy

from .logger import Logger
from .yaml_utils import ordered_load, ordered_dump

from collections import OrderedDict

class Exporter(object):

    @staticmethod
    def _load_file(compose_file):
        # Load yml file
        if not os.path.exists(compose_file):
            Logger.error("Bad compose file: `{0}`".format(compose_file))

        with open(compose_file, mode="rt") as f:
            content = ordered_load(f.read())

        # Analyze services
        if "services" not in content:
            Logger.error("Missing `services` directive in compose file.")

        return content

    @staticmethod
    def clean(compose_file):
        Logger.info("Cleaning export...")

        content = Exporter._load_file(compose_file)
        services = content["services"]
        for service_name in services:
            service = services[service_name]
            if "volumes" not in service:
                Logger.info("No volume in service `{0}`".format(service_name))
                continue

            if "build" not in service:
                Logger.warn("Exporter only works with image builds, not direct pull.")
                continue

            # Build path detection
            build_path = service["build"]
            if isinstance(build_path, OrderedDict):
                build_path = build_path["context"]

            dockerfile_path = os.path.join(build_path, "Dockerfile")
            exported_path = os.path.join(build_path, "exported")
            if not os.path.exists(dockerfile_path):
                Logger.warn("Dockerfile not present in build path `{0}`".format(build_path))
                continue

            with open(dockerfile_path, mode="rt") as f:
                dockerfile_content = f.read()

            match = re.search(r'\# <docknv additions>', dockerfile_content)
            if match:
                # Already edited
                start, end = match.regs[0]
                dockerfile_content = dockerfile_content[:start]

                with open(dockerfile_path, mode="wt") as f:
                    f.write(dockerfile_content)

            if os.path.exists(exported_path):
                shutil.rmtree(exported_path)

    @staticmethod
    def export(compose_file, swarm=False, swarm_registry=None):
        Logger.info("Exporting compose file...")
        content = Exporter._load_file(compose_file)
        services = content["services"]

        if "networks" in content:
            if swarm:
                for network in content["networks"]:
                    content["networks"][network] = {"external": True}

        for service_name in services:
            service = services[service_name]

            # Swarm mode
            if swarm:
                if "image" in service:
                    Logger.info("Image is already present in service `{0}`".format(service_name))
                else:
                    config = swarm_registry if swarm_registry else "127.0.0.1:5000"
                    service["image"] = "{0}/{1}".format(config, service_name)

            if "volumes" not in service:
                Logger.info("No volume in service `{0}`".format(service_name))
                continue

            if "build" not in service:
                Logger.warn("Exporter only works with image builds, not direct pull.")
                continue

            # Build path detection
            build_path = service["build"]
            if isinstance(build_path, OrderedDict):
                build_path = build_path["context"]

            dockerfile_path = os.path.join(build_path, "Dockerfile")
            exported_path = os.path.join(build_path, "exported")
            if not os.path.exists(dockerfile_path):
                Logger.warn("Dockerfile not present in build path `{0}`".format(build_path))
                continue

            with open(dockerfile_path, mode="rt") as f:
                dockerfile_content = f.read()

            match = re.search(r'\# <docknv additions>', dockerfile_content)
            if match:
                # Already edited
                start, end = match.regs[0]
                dockerfile_content = dockerfile_content[:start]

            dockerfile_content += "# <docknv additions>\n"

            volumes = copy.copy(service["volumes"])
            for volume in service["volumes"]:
                volume_split = volume.split(":")
                host, container = volume_split[:2]s
                host_folder = os.path.basename(host)


                if host.endswith(".sock"):
                    Logger.info("Socket detected. Nothing to do.")
                elif host.startswith(".") or host.startswith("/"):
                    Logger.info("Path volume `{0}`".format(host))

                    # Copy local folder and edit dockerfile

                    if not os.path.exists(host):
                        Logger.error("The host volume path does not exist: `{0}`".format(host))

                    exported_final_path = os.path.join(exported_path, host_folder)

                    if not os.path.exists(exported_path):
                        os.mkdir(exported_path)

                    if os.path.exists(exported_final_path):
                        if os.path.isdir(exported_final_path):
                            shutil.rmtree(exported_final_path)
                        else:
                            os.remove(exported_final_path)

                    Logger.debug("Copying `{0}` to `{1}`...".format(host, exported_final_path))
                    if os.path.isdir(host):
                        shutil.copytree(host, exported_final_path)
                    else:
                        shutil.copy(host, exported_final_path)

                    dockerfile_content += "COPY ./exported/{0} {1}\n".format(host_folder, container)
                    volumes.remove(volume)

                else:
                    Logger.info("Named volume. Nothing to do")

            if len(volumes) == 0:
                del service["volumes"]
            else:
                service["volumes"] = volumes

            # Update Dockerfile
            with open(dockerfile_path, mode="wt+") as f:
                f.write(dockerfile_content)

        # Remove the volume directives from the compose file
        with open(compose_file, mode="wt") as f:
            f.write(ordered_dump(content, default_flow_style=False))

        Logger.info("Compose file successfully exported")
