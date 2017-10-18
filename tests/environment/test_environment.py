"""Environment tests."""


def test_env_get_path():
    import os
    from docknv.environment_handler import _env_get_path

    assert _env_get_path(".", "toto") == os.path.join(".", "envs", "toto.env.py")


def test_env_detect_imports():
    from docknv.environment_handler import _env_detect_imports

    content = """
        ENV_TEST = "Test"
        ENV_TEST2 = "Test2"
    """

    assert len(_env_detect_imports(content)) == 0

    content = """
        # -*- test: app-test -*-
        ENV_TEST = "Test"
    """

    assert len(_env_detect_imports(content)) == 0

    content = """
        # -*- import: app-test -*-
        ENV_TEST = "Test"
    """

    imports = _env_detect_imports(content)
    assert len(imports) == 1
    assert "app-test" in imports


def test_env_load_in_memory():
    from docknv.environment_handler import env_load_in_memory
    config = env_load_in_memory("samples/sample01", "default")

    assert "TEST_VALUE" in config
    assert config["TEST_VALUE"] == "default"

    config = env_load_in_memory("samples/sample01", "inclusion")

    assert "TEST_VALUE" in config
    assert "TEST_ONE" in config
    assert config["TEST_VALUE"] == "inclusion"
    assert config["TEST_ONE"] == 1

    config = env_load_in_memory("samples/sample01", "inclusion2")

    assert "TEST_VALUE" in config
    assert "TEST_ONE" in config
    assert config["TEST_VALUE"] == "inclusion2"
    assert config["TEST_ONE"] == 1
