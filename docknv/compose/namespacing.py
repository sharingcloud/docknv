"""Composefile namespacing methods."""

from collections import OrderedDict
import copy

from docknv.volume import Volume


def composefile_apply_namespace(content, namespace=None,
                                environment="default"):
    """
    Apply namespace to compose content.

    :param content:          Content (dict)
    :param namespace:        Namespace name (str?)
    :param environment:      Environment file name (str) (default: default)
    :rtype: dict
    """
    if namespace is None:
        return content

    output_content = copy.deepcopy(content)

    # Volume replacement
    shared_volumes = set()
    new_volumes = OrderedDict()
    for volume in output_content["volumes"]:
        if isinstance(output_content["volumes"][volume], dict):
            if "shared" in output_content["volumes"][volume] and (
                output_content["volumes"][volume]["shared"]
            ):
                shared_volumes.add(volume)

        if volume in shared_volumes:
            continue

        new_key = "{0}_{1}_{2}".format(
            namespace, environment, volume)
        new_volumes[new_key] = volume

    # Cleanup shared mentions
    for key in shared_volumes:
        del output_content["volumes"][key]["shared"]

    for key in new_volumes:
        output_content["volumes"][key] = None
        del output_content["volumes"][new_volumes[key]]

    # Service replacement
    return _composefile_apply_namespace_replacement(
        output_content, namespace, environment, shared_volumes)


def _composefile_apply_namespace_replacement(output_content, namespace,
                                             environment, shared_volumes):
    # Service replacement
    new_keys_repl = OrderedDict()
    for key in output_content["services"]:
        new_key = "{0}_{1}".format(namespace, key)
        new_keys_repl[new_key] = key

        # Find volumes
        new_volumes = OrderedDict()
        if "volumes" in output_content["services"][key]:
            for volume in output_content["services"][key]["volumes"]:
                # Ignore empty volumes
                if volume == "":
                    continue

                volume_object = Volume.load_from_entry(volume)
                if volume_object.is_named:
                    if volume_object.host_path in shared_volumes:
                        continue

                    volume_object.host_path = "{0}_{1}_{2}".format(
                        namespace, environment, volume_object.host_path)

                    new_volumes[volume] = str(volume_object)

            # Apply new volumes/Remove old volumes
            for volume in new_volumes:
                new_v = new_volumes[volume]

                output_content["services"][key]["volumes"].append(new_v)
                output_content["services"][key]["volumes"].remove(volume)

    # Apply new services/Remove old services
    for key in new_keys_repl:
        output_content["services"][key] = \
            output_content["services"][new_keys_repl[key]]
        del output_content["services"][new_keys_repl[key]]

    return output_content
