"""Command handler tests."""

from docknv import command_handler


def test_command_get_config():
    CONFIG = {
        "commands": {
            "test": {
                "var1": 5
            },
            "test2": {
                "var2": 7,
                "var3": "coucou"
            }
        }
    }

    assert command_handler.command_get_config(CONFIG, "pouet") == {}
    assert command_handler.command_get_config(CONFIG, "test") == {"var1": 5}
    assert command_handler.command_get_config(CONFIG, "test2") == {"var2": 7, "var3": "coucou"}
