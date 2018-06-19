"""Environment handler tests."""

from __future__ import unicode_literals

import os
import pytest
from collections import OrderedDict

from docknv.logger import LoggerError

from docknv.environment_handler import (
    env_yaml_load_in_memory,
    env_yaml_resolve_variables,
    env_yaml_inherits,
    env_get_yaml_path,
    env_get_py_path,
    env_yaml_convert,
    env_yaml_key_value_export,
    env_yaml_list,
    env_yaml_get_dependencies,
    env_yaml_get_dependencies_str,
    env_yaml_generate_depth_graph,

    UnresolvableEnvironment
)

from docknv.tests.utils import (
    using_temporary_directory,
    copy_sample
)


def test_env_get_yaml_path():
    """Test get yaml path."""
    assert env_get_yaml_path(".", "toto") == os.path.join(".", "envs", "toto.env.yml")


def test_yaml_environment():
    """Environment test."""
    config = env_yaml_load_in_memory("samples/sample01", "default")

    assert "TEST_VALUE" in config
    assert config["TEST_VALUE"] == "default"
    assert config["VAR_SUB_TEST"] == "${VAR_TEST}"
    assert config["CONCAT_EXAMPLE"] == "Hello ${VAR_SUB_TEST}"
    assert config["DOUBLE_CONCAT_EXAMPLE"] == "${VAR_TEST} + ${VAR_TEST} = ${VAR_TEST}${VAR_TEST}"

    configEmpty = env_yaml_load_in_memory("samples/sample01", "inclusion-empty")
    assert config == configEmpty

    config = env_yaml_load_in_memory("samples/sample01", "inclusion")

    assert "TEST_VALUE" in config
    assert "TEST_ONE" in config
    assert config["TEST_VALUE"] == "inclusion"
    assert config["TEST_ONE"] == 1
    assert config["TEST_ONE_2"] == "toto:${TEST_ONE}"
    assert config["VAR_TEST"] == "hi"
    assert config["VAR_SUB_TEST"] == "${VAR_TEST}"

    config = env_yaml_load_in_memory("samples/sample01", "inclusion2")

    assert "TEST_VALUE" in config
    assert "TEST_ONE" in config
    assert config["TEST_VALUE"] == "inclusion2"
    assert config["TEST_ONE"] == 1
    assert config["VAR_TEST"] == "hi"
    assert config["VAR_SUB_TEST"] == "pouet"
    assert config["CONCAT_EXAMPLE"] == "Hello ${VAR_SUB_TEST}"
    assert config["DOUBLE_CONCAT_EXAMPLE"] == "${VAR_TEST} + ${VAR_TEST} = ${VAR_TEST}${VAR_TEST}"
    assert config["ARRAY_EXAMPLE"] == ["coucou", "${VAR_TEST}", "${VAR_TEST}"]
    assert config["DICT_EXAMPLE"]["key1"] == "${VAR_TEST}"
    assert config["COMPLEX_EXAMPLE"][0]["pouet"] == "${VAR_TEST}"
    assert config["COMPLEX_EXAMPLE"][0]["arr"][0] == "${VAR_TEST}"


def test_yaml_resolve_variables():
    """Variable resolution test."""
    config = env_yaml_load_in_memory("samples/sample01", "default")
    resolved_env = env_yaml_resolve_variables(config)

    assert resolved_env["TEST_VALUE"] == "default"
    assert resolved_env["VAR_SUB_TEST"] == "toto"
    assert resolved_env["CONCAT_EXAMPLE"] == "Hello toto"
    assert resolved_env["DOUBLE_CONCAT_EXAMPLE"] == "toto + toto = totototo"
    assert resolved_env["ARRAY_EXAMPLE"] == ["coucou", "toto", "toto"]
    assert resolved_env["DICT_EXAMPLE"]["key1"] == "toto"
    assert resolved_env["COMPLEX_EXAMPLE"][0]["pouet"] == "toto"
    assert resolved_env["COMPLEX_EXAMPLE"][0]["arr"][0] == "toto"

    config = env_yaml_load_in_memory("samples/sample01", "inclusion")
    resolved_env = env_yaml_resolve_variables(config)

    assert resolved_env["VAR_TEST"] == "hi"
    assert resolved_env["VAR_SUB_TEST"] == "hi"
    assert resolved_env["CONCAT_EXAMPLE"] == "Hello hi"
    assert resolved_env["DOUBLE_CONCAT_EXAMPLE"] == "hi + hi = hihi"

    config = env_yaml_load_in_memory("samples/sample01", "inclusion2")
    resolved_env = env_yaml_resolve_variables(config)

    assert resolved_env["VAR_TEST"] == "hi"
    assert resolved_env["VAR_SUB_TEST"] == "pouet"
    assert resolved_env["CONCAT_EXAMPLE"] == "Hello pouet"
    assert resolved_env["DOUBLE_CONCAT_EXAMPLE"] == "hi + hi = hihi"


def test_yaml_convert():
    """Convert a Python environment file in YAML."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        old_default = env_get_py_path(project_path, "old-default")
        old_test = env_get_py_path(project_path, "old-test")

        assert os.path.exists(old_default)
        assert os.path.exists(old_test)

        new_default = env_get_yaml_path(project_path, "old-default")
        new_test = env_get_yaml_path(project_path, "old-test")

        assert not os.path.exists(new_default)
        assert not os.path.exists(new_test)

        converted_default, default_yaml_data = env_yaml_convert(project_path, "old-default")
        converted_test, test_yaml_data = env_yaml_convert(project_path, "old-test")

        assert converted_default == new_default
        assert converted_test == new_test

        assert "imports" in test_yaml_data
        assert "old-default" in test_yaml_data["imports"]

        assert "imports" not in default_yaml_data


def test_yaml_list():
    """List."""
    with using_temporary_directory() as tempdir:
        project_path = copy_sample("sample01", tempdir)

        # OK test
        env_yaml_list(project_path)

        # Non existing test
        toto_path = os.path.join(project_path, 'toto')
        with pytest.raises(LoggerError):
            env_yaml_list(toto_path)

        # Empty test
        toto_env_path = os.path.join(toto_path, 'envs')
        os.makedirs(toto_env_path)
        env_yaml_list(toto_path)


def test_yaml_inherits():
    """Inheritance test."""
    result = env_yaml_inherits("test")
    assert "test" in result["imports"]
    assert result["environment"] == {}


def test_yaml_key_value_export():
    """Key/Value export test."""
    config = env_yaml_load_in_memory("samples/sample01", "inclusion")
    resolved_env = env_yaml_resolve_variables(config)
    export = env_yaml_key_value_export(resolved_env)

    assert "VAR_SUB_TEST=hi" in export
    assert "ARRAY_EXAMPLE=[\"coucou\", \"hi\", \"hi\"]" in export


def test_yaml_generate_depth_graph():
    """Generate depth graph."""
    input_yml = OrderedDict([
        ("A", 1),
        ("B", "${A}"),
        ("C", "${A}"),
        ("D", "${C}"),
        ("E", "${D}"),
        ("F", "${C}"),
        ("G", "${F}${A}")
    ])

    output = [
        ("A", 1),
        ("B", 2),
        ("C", 2),
        ("D", 3),
        ("F", 3),
        ("E", 4),
        ("G", 4)
    ]

    pairs = env_yaml_generate_depth_graph(input_yml)
    for x in output:
        assert x in pairs
    for x in pairs:
        assert x in output


def test_yaml_deep_resolution():
    """YAML deep resolution."""
    input_yml = OrderedDict([
        ("A", 1),
        ("B", "${A}"),
        ("C", "${A}"),
        ("D", "${C}"),
        ("E", "${D}"),
        ("F", "${C}"),
        ("G", "${F}${A}")
    ])

    output_yml = [
        ("A", 1),
        ("B", "1"),
        ("C", "1"),
        ("D", "1"),
        ("E", "1"),
        ("F", "1"),
        ("G", "11")
    ]

    resolved_yml = env_yaml_resolve_variables(input_yml)
    for k, v in output_yml:
        assert k in resolved_yml
        assert resolved_yml[k] == v


def test_yaml_get_dependencies_str():
    """YAML get dependencies str."""
    input_yml = "Toto ${A} ${tutu} + ${hello}"
    result = ["A", "tutu", "hello"]

    assert env_yaml_get_dependencies_str(input_yml) == result


def test_yaml_get_dependencies():
    """YAML get dependencies."""
    input_yml = OrderedDict([
        ("Toto ${A}", OrderedDict([
            ("Tutu", ["A ${B}", "C", "D ${D}"]),
            ("Tutu ${Tutu}", OrderedDict([
                ("tutu", "${A}"),
                ("toto ${to}", [])
            ]))
        ]))
    ])

    result = ["A", "B", "D", "Tutu", "to"]

    assert env_yaml_get_dependencies(input_yml) == result


def test_yaml_deep_resolution_fail():
    """YAML deep resolution fail."""
    input_yml = OrderedDict([
        ("H", "${TOTO}"),
        ("TOTO", 1)
    ])

    with pytest.raises(UnresolvableEnvironment):
        env_yaml_resolve_variables(input_yml)
