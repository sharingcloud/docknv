"""
YAML utilities
"""

import copy
from collections import OrderedDict

import six
import yaml


def yaml_merge(contents):
    """
    Merge two YAML dict together
    """

    len_contents = len(contents)
    if len_contents == 1:
        return contents[0]
    elif len_contents == 0:
        return None
    else:
        src1 = contents[0]
        for src2 in contents[1:]:
            src1 = _merge_yaml_two(src1, src2)
        return src1


def yaml_ordered_load(stream, loader_class=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Load ordered YAML content
    """

    class OrderedLoader(loader_class):
        """
        Ordered loader
        """

    def _construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _construct_mapping)

    return yaml.load(stream, OrderedLoader)


def yaml_ordered_dump(data, stream=None, dumper_class=yaml.Dumper, **kwds):
    """
    Dump ordered YAML content
    """

    class OrderedDumper(dumper_class):
        """
        Ordered dumper
        """

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)

    return yaml.dump(data, stream, OrderedDumper, **kwds)


# PRIVATE ##########


def _merge_yaml_two(src1, src2):
    dst = copy.deepcopy(src1)

    if isinstance(src1, dict) and isinstance(src2, dict):
        for key, value in six.iteritems(src2):
            if key not in src1:
                dst[key] = value
            else:
                dst[key] = _merge_yaml_two(dst[key], src2[key])

    if isinstance(src1, list) and isinstance(src2, list):
        for key in src2:
            if key not in src1:
                dst.append(key)

    return dst
