"""Environment handler tests."""

import os

from docknv.environment_handler import (
    env_yaml_load_in_memory,
    env_yaml_resolve_variables,
    env_yaml_inherits,
    env_get_yaml_path
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


def test_yaml_inherits():
    """Inheritance test."""
    result = env_yaml_inherits({}, "test")
    assert "test" in result["imports"]
    assert result["environment"] == {}
