"""Environment handler tests."""

from __future__ import unicode_literals

import os

from docknv.environment_handler import (
    env_yaml_load_in_memory,
    env_yaml_resolve_variables,
    env_yaml_inherits,
    env_get_yaml_path,
    env_get_py_path,
    env_yaml_convert
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


def test_yaml_inherits():
    """Inheritance test."""
    result = env_yaml_inherits({}, "test")
    assert "test" in result["imports"]
    assert result["environment"] == {}
