"""String utils."""


def parse_str(value):
    """Convert a string value to int or bool, if possible.

    Args:
        value (str): String value

    Returns:
        {int,bool}?: Value, or None
    """
    try:
        bool_value = str(value).lower()
        if bool_value == "true":
            return True
        elif bool_value == "false":
            return False
    except (ValueError, TypeError):
        return None

    try:
        int_value = int(value)
        return int_value
    except (ValueError, TypeError):
        return None
