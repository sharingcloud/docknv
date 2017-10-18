"""Environment tests."""


def test_env_get_path():
    import os
    from docknv.environment_handler import _env_get_path

    assert _env_get_path(".", "toto") == os.path.join(".", "envs", "toto.env.py")
