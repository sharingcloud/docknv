"""Common handler code."""


def exec_handler(cmd_name, args, handlers):
    """
    Execute handler.

    :param cmd_name:    Command name (str)
    :param args:        Arguments (iterable)
    :param handlers:    Handlers (dict)
    :rtype: Status
    """
    command = getattr(args, cmd_name + "_cmd").replace("-", "_")
    handler = "_handle_" + command
    if handler in handlers:
        return handlers[handler](args)
