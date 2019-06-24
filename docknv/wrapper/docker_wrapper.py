"""Docker commands wrapper."""

from .methods import exec_process, exec_process_with_output


def exec_docker(project_path, args, dry_run=False):
    """
    Execute a Docker command.

    :param project_path:     Project path (str)
    :param args:             Arguments (...)
    :param dry_run:          Dry run? (bool) (default: False)
    """
    cmd = ["docker"] + [str(a) for a in args if a != ""]
    return exec_process(cmd, cwd=project_path, dry_run=dry_run)


def exec_compose(
    project_path, composefile_path, args, pretty=False, dry_run=False
):
    """
    Execute a Docker Compose command.

    :param project_path:     Project path (str)
    :param composefile_path: Composefile path (str)
    :param args:             Arguments (...)
    :param pretty:           Pretty filtering ? (default: False) (bool)
    :param dry_run:          Dry run? (bool) (default: False)
    """
    cmd = [
        "docker-compose",
        "-f",
        composefile_path,
        "--project-directory",
        project_path,
    ]
    cmd += [str(a) for a in args if a != ""]

    if pretty:
        exec_process_with_output(
            cmd, project_path, _pretty_handler, dry_run=dry_run
        )

    return exec_process(cmd, cwd=project_path, dry_run=dry_run)


def _pretty_handler(args, line):
    action = args[0]
    if not _pretty_handler_common(line):
        return False

    if action in ["start", "stop", "restart", "up", "down"]:
        if not _pretty_handler_lifecycle(line):
            return False
        if not _pretty_handler_network(line):
            return False

    return True


def _pretty_handler_common(line):
    # Ignore swarm warning
    if "Compose does not support 'deploy'" in line:
        return False

    elif line.startswith("Found orphan containers"):
        return False

    elif line == "":
        return False

    return True


def _pretty_handler_network(line):
    if line.startswith("Network") and line.endswith("not found."):
        return False

    elif line.startswith("network") and line.endswith("has active endpoints"):
        return False

    elif line.startswith("Removing network"):
        return False

    return True


def _pretty_handler_lifecycle(line):
    if line.startswith("\x1b"):
        return False

    return True
