"""Diff system."""

from __future__ import unicode_literals

import os
import json

import six


def get_files_last_modification_time(path):
    """
    For each file in path, recursively, get its last modification time as a timestamp.

    :param path:    Path (str)
    :rtype: Time dict (dict)
    """
    result = {}
    if os.path.isfile(path):
        result[path] = os.path.getmtime(path)

    elif os.path.isdir(path):
        for root, folders, files in os.walk(path):
            for filename in files:
                full_path = os.path.join(root, filename)
                if os.path.isfile(full_path):
                    result[full_path] = os.path.getmtime(full_path)

    return result


def save_last_modification_time(stream, results):
    """
    Save last modification time.

    :param stream:  Stream (io)
    :param results: Time dict (dict)
    """
    stream.write(json.dumps(results))


def read_last_modification_time(stream):
    """
    Read last modification time.

    :param stream:  Stream (io)
    :rtype: Time dict (dict)
    """
    return json.loads(stream.read())


def concat_diffs(old_time_data, new_time_data):
    """
    Concat diffs.

    :param old_time_data:   Old time data (dict)
    :param new_time_data:   New time data (dict)
    :rtype: Time diff concat (dict)
    """
    output = {}
    output.update(old_time_data)
    output.update(new_time_data)
    return output


def diff_modification_time(old_time_data, new_time_data):
    """
    Check diff between two time datas.

    :param old_time_data:   Old time data (dict)
    :param new_time_data:   New time data (dict)
    :rtype: Time diff dict (dict)
    """
    result = {}

    for filename, new_time in six.iteritems(new_time_data):
        if filename in old_time_data:
            old_time = old_time_data[filename]
            if old_time == new_time:
                continue
            else:
                result[filename] = new_time
        else:
            result[filename] = new_time

    return result
