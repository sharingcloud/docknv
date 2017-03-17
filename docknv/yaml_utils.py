import copy
import six
import yaml

from collections import OrderedDict

def merge_yaml(contents):
    if len(contents) == 1:
        return contents[0]
    elif len(contents) == 0:
        return None
    else:
        src1 = contents[0]
        for src2 in contents[1:]:
            src1 = merge_yaml_two(src1, src2)
        return src1

def merge_yaml_two(src1, src2):
    dst = copy.deepcopy(src1)

    if isinstance(src1, dict) and isinstance(src2, dict):
        for k, v in six.iteritems(src2):
            if k not in src1:
                dst[k] = v
            else:
                dst[k] = merge_yaml_two(dst[k], src2[k])

    if isinstance(src1, list) and isinstance(src2, list):
        for k in src2:
            if k not in src1:
                dst.append(k)

    return dst

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)
