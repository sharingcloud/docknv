"""Composefile filter methods."""

import copy


def composefile_filter(content, config):
    """
    Filter composefile content using a configuration.

    :param content:     Compose file content (dict)
    :param config:      Configuration (dict)
    :rtype: Filtered content (dict)
    """
    needed_volumes = config.volumes
    needed_services = config.services
    needed_networks = config.networks

    new_merged = copy.deepcopy(content)
    _composefile_filter_volumes(new_merged, needed_volumes)
    _composefile_filter_networks(new_merged, needed_networks)
    _composefile_filter_services(new_merged, needed_services)

    return new_merged


def _composefile_filter_volumes(content, needed):
    to_remove = []
    if "volumes" in content:
        for volume_name in content["volumes"]:
            if volume_name not in needed:
                to_remove.append(volume_name)

    for value in to_remove:
        del content["volumes"][value]

    return content


def _composefile_filter_services(content, needed):
    to_remove = []
    for service_name in content["services"]:
        if service_name not in needed:
            to_remove.append(service_name)

    for value in to_remove:
        del content["services"][value]

    return content


def _composefile_filter_networks(content, needed):
    to_remove = []
    if "networks" in content:
        for network_name in content["networks"]:
            if network_name not in needed:
                to_remove.append(network_name)

    for value in to_remove:
        del content["networks"][value]

    return content
