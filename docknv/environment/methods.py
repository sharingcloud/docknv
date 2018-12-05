"""Environment methods."""

import os
import re
import copy
import six

from .exceptions import UnresolvableEnvironment

from docknv.utils.ioutils import io_open
from docknv.utils.serialization import yaml_ordered_load, yaml_ordered_dump

VARIABLE_DETECTION_RGX = re.compile(r'\${([a-zA-Z0-9_-]+)}')


def env_yaml_resolve_variables(environment):
    """
    Apply deep resolution.

    :raise UnresolvableEnvironment

    :param environment:  Environment (dict)
    :rtype: Resolved environment (dict)
    """
    depth_graph = env_yaml_generate_depth_graph(environment)
    resolved_env = copy.deepcopy(environment)
    known_values = {}

    for (key, _depth) in depth_graph:
        value = resolved_env[key]
        resolved_env[key] = env_yaml_deep_handle(key, value, known_values)
    return resolved_env


def env_yaml_deep_handle(key, value, known_values):
    """
    Deep handle.

    Known values will be modified.

    :param key:             Key (str)
    :param value:           Value (list|dict|str)
    :param known_values:    Known values (dict)
    :rtype: Data
    """
    if isinstance(value, list):
        output_list = []
        for i in range(len(value)):
            v = value[i]
            output = env_yaml_deep_handle(key, v, known_values)
            output_list.append(output)

        return output_list

    elif isinstance(value, dict):
        output_dict = {}
        for k in value:
            ks = env_yaml_deep_handle_str(k, known_values)

            v = value[k]
            vs = env_yaml_deep_handle(key, v, known_values)
            output_dict[ks] = vs

        return output_dict

    elif isinstance(value, six.string_types):
        parsed = env_yaml_deep_handle_str(value, known_values)
        known_values[key] = parsed
        return parsed

    elif isinstance(value, six.integer_types):
        known_values[key] = value
        return value

    elif isinstance(value, float):
        known_values[key] = value
        return value


def env_yaml_deep_handle_str(string_value, known_values):
    """
    Deep handle str.

    :param string_value:    String value
    :param known_values:    Known values
    :rtype: Handled string (str)
    """
    def _replace(match):
        var_name = match.group(1)
        if var_name in known_values:
            return str(known_values[var_name])

    return re.sub(VARIABLE_DETECTION_RGX, _replace, string_value)


def env_yaml_generate_depth_graph(environment):
    """
    Generate the environment depth graph.

    :raise UnresolvableEnvironment

    :param environment: Environment (dict)
    :rtype: Depth pairs (list)
    """
    env_distance = {}
    for key in environment:
        value = environment[key]

        max_depth = 0
        deps = env_yaml_get_dependencies(value)
        for dep in deps:
            if dep not in env_distance:
                raise UnresolvableEnvironment(key, dep)

            depth = env_distance[dep]
            if depth > max_depth:
                max_depth = depth

        env_distance[key] = max_depth + 1

    # Sort dictionary
    return sorted(six.iteritems(env_distance), key=lambda x: x[1])


def env_yaml_get_dependencies_str(str_value):
    """
    Get dependencies for a key in a string value.

    :param str_value:   String value
    :rtype: Dependencies
    """
    return re.findall(VARIABLE_DETECTION_RGX, str_value)


def env_yaml_get_dependencies(value):
    """
    Get dependencies for a key in environment.

    :param value: Value
    :rtype: Dependencies
    """
    def add_if_ne(ks, v):
        for k in ks:
            if k not in v:
                v.append(k)

    deps = []

    if isinstance(value, list):
        for i in range(len(value)):
            v = value[i]
            vs = env_yaml_get_dependencies(v)
            add_if_ne(vs, deps)

    elif isinstance(value, dict):
        for k in value:
            ks = env_yaml_get_dependencies_str(k)
            add_if_ne(ks, deps)

            v = value[k]
            vs = env_yaml_get_dependencies(v)
            add_if_ne(vs, deps)

    elif isinstance(value, six.string_types):
        return env_yaml_get_dependencies_str(value)

    return deps


def env_get_yaml_path(project_path, name):
    """
    Get YAML environment path.

    :param project_path:    Project path (str)
    :param name:            Environment name (str)
    :rtype: Absolute path to environment file (str)
    """
    return os.path.join(project_path, "envs", "".join((name, ".env.yml")))


def env_set_env_value(env_path, key, value):
    """
    Set environment value from file at `env_path`.

    :param env_path:    Environment path (str)
    :param key:         Key (str)
    :param value:       Value (any)
    """
    with io_open(env_path, mode="r") as handle:
        content = yaml_ordered_load(handle)

    if content["environment"] is None:
        content["environment"] = {}
    content["environment"][key] = value

    with io_open(env_path, mode="w") as handle:
        handle.write(yaml_ordered_dump(content))
