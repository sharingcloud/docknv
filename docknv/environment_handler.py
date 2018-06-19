"""Environment files handler."""

from __future__ import unicode_literals

import os
import re
import copy
import imp
import json
import six

from collections import OrderedDict

from docknv.logger import Logger, Fore
from docknv.utils.ioutils import io_open
from docknv.utils.prompt import prompt_yes_no
from docknv.utils.serialization import yaml_ordered_dump, yaml_ordered_load

IMPORT_DETECTION_RGX = re.compile(r'-\*-\s*import:\s*([a-zA-Z0-9_-]*)\s*-\*-')
VARIABLE_DETECTION_RGX = re.compile(r'\${([a-zA-Z0-9_-]+)}')


class UnresolvableEnvironment(Exception):
    """Unresolvable environment."""

    def __init__(self, key, dependency):
        """Init."""
        message = "Unresolvable dependency {dep} for key {key}".format(
            dep=dependency,
            key=key
        )

        super(UnresolvableEnvironment, self).__init__(message)


def env_yaml_list(project_path):
    """
    List environment configurations.

    :param project_path:     Project path (str)
    """
    env_path = os.path.join(project_path, "envs")

    if not os.path.isdir(env_path):
        Logger.error("'envs' folder does not exist.")

    envs = [f for f in os.listdir(env_path) if f.endswith(".env.yml")]
    envs_count = len(envs)
    if envs_count == 0:
        Logger.warn("No env file found.")
    else:
        Logger.info("Environment files listing:")
        for env_file in envs:
            name = env_file[:-8]
            Logger.raw("  > {0}".format(name))


def env_yaml_show(project_path, name):
    """
    Print an environment file.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    """
    loaded_env = env_yaml_load_in_memory(project_path, name)
    loaded_env = env_yaml_resolve_variables(loaded_env)

    Logger.info("Showing environment file `{0}`:".format(name))
    for key in loaded_env:
        Logger.raw("  {0}".format(key), color=Fore.YELLOW, linebreak=False)
        Logger.raw(" = ", linebreak=False)
        Logger.raw(loaded_env[key], color=Fore.BLUE)


def env_yaml_check_file(project_path, name):
    """
    Check if an environment file exist.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    :rtype: bool
    """
    env_path = env_get_yaml_path(project_path, name)
    return os.path.exists(env_path)


def env_yaml_load_in_memory(project_path, name):
    """
    Load YAML environment file in memory.

    :param project_path:    Project path (str)
    :param name:            Environment file name (str)
    :rtype: Environment data (dict)
    """
    env_path = env_get_yaml_path(project_path, name)
    if not os.path.isfile(env_path):
        raise RuntimeError("File `{0}` does not exist".format(env_path))

    loaded_env = OrderedDict()
    env_content = _env_yaml_read_file_content(env_path)

    # Load imports
    imported_environments = _env_yaml_detect_imports(env_content)
    for imported_env in imported_environments:
        if imported_env == name:
            continue

        result = env_yaml_load_in_memory(project_path, imported_env)
        for key in result:
            loaded_env[key] = result[key]

    # Load environment
    if env_content.get("environment", None):
        for key in env_content["environment"]:
            loaded_env[key] = env_content["environment"][key]

    return loaded_env


def env_yaml_key_value_export(env_data):
    """
    Export YAML data as key/value.

    :param env_data:    Environment data (dict)
    :rtype: Key value string (str)
    """
    export_string = ""
    for key in env_data:
        value = env_data[key]
        if isinstance(value, str):
            value = value.replace("\n", "\\n")
        else:
            value = json.dumps(value)
        export_string += key + "=" + value + "\n"

    return export_string


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
        if var_name not in known_values:
            Logger.warn("[ENV] Unknown environment variable {0}. It may not have been resolved yet.".format(var_name))
        else:
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


def env_yaml_inherits(source_name):
    """
    Inherit a YAML environment.

    :param source_name:     Source name (str)
    :rtype: YAML data (dict)
    """
    return {
        "imports": [source_name],
        "environment": {}
    }


def env_yaml_write_to_file(env, path):
    """
    Write YAML environment to a file.

    :param env:      Environment configuration data (dict)
    :param path:     Output file (str)
    """
    Logger.info("Writing YAML environment to file {0}...".format(path))

    with io_open(path, encoding="utf-8", mode="wt+") as handle:
        handle.write(yaml_ordered_dump(env))


def env_get_yaml_path(project_path, name):
    """
    Get YAML environment path.

    :param project_path:    Project path (str)
    :param name:            Environment name (str)
    :rtype: Absolute path to environment file (str)
    """
    return os.path.join(project_path, "envs", "".join((name, ".env.yml")))


def env_yaml_convert(project_path, name):
    """
    Convert a Python environment file to a YAML environment file.

    It will create a new [name].env.yml.

    :param project_path:    Project path (str)
    :param name:            Environment name (str)
    :rtype: Absolute path to YAML environment file (str), YAML data (dict)
    """
    # Loading Python env
    py_env = {}
    py_env_path = env_get_py_path(project_path, name)

    if not os.path.isfile(py_env_path):
        raise RuntimeError("File `{0}` does not exist".format(py_env_path))

    yaml_env_path = env_get_yaml_path(project_path, name)

    if os.path.isfile(yaml_env_path):
        choice = prompt_yes_no("/!\\ The environment file `{0}` already exists. Your Python file might already have been converted. Are you sure to continue ?".format( # noqa
            yaml_env_path
        ))
        if not choice:
            return

    py_env_data = imp.load_source("envs", py_env_path)
    py_env_vars = [e for e in dir(py_env_data) if not e.startswith("__")]
    for variable in py_env_vars:
        py_env[variable] = getattr(py_env_data, variable)

    # Imports
    py_env_content = _env_py_read_file_content(py_env_path)
    py_imported_environments = _env_py_detect_imports(py_env_content)

    yaml_data = {"imports": py_imported_environments, "environment": py_env}
    if len(py_imported_environments) == 0:
        del yaml_data["imports"]

    with io_open(yaml_env_path, mode="wt") as handle:
        handle.write(yaml_ordered_dump(yaml_data))

    Logger.info("Python environment `{0}.env.py` has been converted to `{0}.env.yml`".format(name))
    return yaml_env_path, yaml_data

##############
# LEGACY


def env_py_load_in_memory(project_path, name):
    """
    Load Python environment file in memory.

    :param project_path:     Project path (str)
    :param name:             Environment file name (str)
    :rtype: Environment data (dict)
    """
    env_path = env_get_py_path(project_path, name)

    if not os.path.isfile(env_path):
        raise RuntimeError("File `{0}` does not exist".format(env_path))

    loaded_env = OrderedDict()

    # Detect imports
    env_content = _env_py_read_file_content(env_path)
    imported_environments = _env_py_detect_imports(env_content)
    for imported_env in imported_environments:
        if imported_env == name:
            continue

        result = env_py_load_in_memory(project_path, imported_env)
        for key in result:
            loaded_env[key] = result[key]

    # Loading variables
    env_data = imp.load_source("envs", env_path)
    env_vars = [e for e in dir(env_data) if not e.startswith("__")]
    for variable in env_vars:
        loaded_env[variable] = getattr(env_data, variable)

    return loaded_env


def env_get_py_path(project_path, name):
    """
    Get Python environment path.

    :param project_path:    Project path (str)
    :param name:            Environment name (str)
    :rtype: Absolute path to environment file (str)
    """
    return os.path.join(project_path, "envs", "".join((name, ".env.py")))

##############
# PRIVATE


def _env_yaml_detect_imports(env_content):
    imports = []
    if "imports" in env_content:
        for entry in env_content["imports"]:
            imports.append(entry)

    return imports


def _env_yaml_read_file_content(env_path):
    with io_open(env_path, mode='r', encoding='utf-8') as handle:
        return yaml_ordered_load(handle.read())


def _env_py_detect_imports(env_content):
    """
    Detect imports in an environment file.

    :param env_content:  Environment file content (str)
    :rtype: Detected imports (iterable)
    """
    detected_imports = []
    for match in IMPORT_DETECTION_RGX.finditer(env_content):
        detected_imports.append(match.groups()[0])

    return detected_imports


def _env_py_read_file_content(env_path):
    """
    Open and read environment file content.

    :param env_path:     Environment file path (str)
    :rtype: Environment file content (str)
    """
    with io_open(env_path, mode='r', encoding='utf-8') as handle:
        return handle.read()
