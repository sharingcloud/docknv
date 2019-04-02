"""Wrapper methods."""

import subprocess

from docknv.logger import Logger

from .exceptions import FailedCommandExecution, StoppedCommandExecution


def exec_process(args, cwd=None, shell=False, dry_run=False):
    """
    Execute a process.

    :param args:    Arguments (list)
    :param cwd:     Working directory (str?)
    :param shell:   Shell? (bool) (default: False)
    :param dry_run: Dry run? (bool) (default: False)
    :rtype: Arguments or return code
    """
    if dry_run:
        return args

    try:
        Logger.debug(f"executing command {args}...")
        rc = subprocess.call(args, cwd=cwd, shell=shell)
    except KeyboardInterrupt:
        raise StoppedCommandExecution("CTRL+C")
    except BaseException as exc:
        raise FailedCommandExecution(str(exc))

    if rc != 0:
        raise FailedCommandExecution(f"bad return code: {rc}")
    return rc


def exec_process_with_output(args, cwd=None, outfilter=None, dry_run=False):
    """
    Execute a process with output.

    :param args:        Arguments (list)
    :param cwd:         Working directory (str?)
    :param outfilter:   Output filter func (fn?)
    :param dry_run:     Dry run? (bool) (default: False)
    :rtype: Arguments or return code and output
    """
    if dry_run:
        return args

    try:
        proc = subprocess.Popen(
            " ".join(args), cwd=cwd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True, universal_newlines=True)

        while True:
            out = proc.stdout.readline()
            if out == '' and proc.poll() is not None:
                break
            if out:
                out = out.strip()
                if outfilter and outfilter(args, out):
                    print(out)

        rc = proc.poll()
    except KeyboardInterrupt:
        raise StoppedCommandExecution("CTRL+C")
    except BaseException as exc:
        raise FailedCommandExecution(str(exc))

    if rc != 0:
        raise FailedCommandExecution(f"bad return code: {rc}")
    return rc
