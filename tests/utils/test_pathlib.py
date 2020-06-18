"""Test Pathlib functions."""

from pathlib import PurePath
from supervisor.utils.pathlib import is_excluded_by_filter


def test_is_excluded_by_filter_good():
    """Test exclude filter."""
    filter_globs = ["not/match", "/dev/xy"]
    test_list = [
        PurePath("test.txt"),
        PurePath("data/xy.blob"),
        PurePath("bla/blu/ble"),
        PurePath("data/../xy.blob"),
    ]

    for info in [is_excluded_by_filter(result, filter_globs) for result in test_list]:
        assert info is False


def test_is_excluded_by_filter_bad():
    """Test exclude filter."""
    filter_globs = ["*.txt", "data/*", "bla/blu/ble"]
    test_list = [
        PurePath("test.txt"),
        PurePath("data/xy.blob"),
        PurePath("bla/blu/ble"),
        PurePath("data/test_files/kk.txt"),
    ]

    for info in [is_excluded_by_filter(result, filter_globs) for result in test_list]:
        assert info is True
