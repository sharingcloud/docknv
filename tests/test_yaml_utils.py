"""YAML utils tests."""

from docknv.utils.serialization import (
    yaml_ordered_load,
    yaml_ordered_dump,
    yaml_merge,
)


def test_load():
    """Test ordered_load function."""
    content = """
one:
    two: [a, b, c]
    three: 1
    four:
        - a
        - b
        - c
two:
    - pouet
aaa:
"""

    loaded = yaml_ordered_load(content)
    keys = list(loaded.keys())

    assert keys[0] == "one"
    assert keys[1] == "two"


def test_dump():
    """Test ordered_dump function."""
    content = {
        "one": {"two": ["a", "b", "c"], "three": 1, "four": ["a", "b", "c"]},
        "two": ["pouet"],
        "aaa": None,
    }

    dump = yaml_ordered_dump(content)
    assert dump.startswith("aaa: null\n")


def test_merge():
    """Test merge function."""
    content1 = {
        "one": ["a"],
        "two": {"a": 1},
        "three": {"a": ["A"], "b": {"c": None}},
    }

    content2 = {"one": ["b"], "two": {"b": 2}, "four": ["4"]}

    merge = yaml_merge((content1, content2))

    assert "three" in merge
    assert "four" in merge

    merge_solo = yaml_merge((content1,))

    assert merge_solo == content1
    assert yaml_merge(()) is None
