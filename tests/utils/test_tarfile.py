"""Test Tarfile functions."""

import attr

from pathlib import PurePath
from supervisor.utils.tar import secure_path, _is_excluded_by_filter


@attr.s
class TarInfo:
    """Fake TarInfo."""

    name: str = attr.ib()


def test_secure_path():
    """Test Secure Path."""
    test_list = [
        TarInfo("test.txt"),
        TarInfo("data/xy.blob"),
        TarInfo("bla/blu/ble"),
        TarInfo("data/../xy.blob"),
    ]
    assert test_list == list(secure_path(test_list))


def test_not_secure_path():
    """Test Not secure path."""
    test_list = [
        TarInfo("/test.txt"),
        TarInfo("data/../../xy.blob"),
        TarInfo("/bla/blu/ble"),
    ]
    assert [] == list(secure_path(test_list))


def test_is_excluded_by_filter_good():
    """Test exclude filter."""
    filter_list = ["not/match", "/dev/xy"]
    test_list = [
        PurePath("test.txt"),
        PurePath("data/xy.blob"),
        PurePath("bla/blu/ble"),
        PurePath("data/../xy.blob"),
    ]

    for path_object in test_list:
        assert _is_excluded_by_filter(path_object, filter_list) is False


def test_is_exclude_by_filter_bad():
    """Test exclude filter."""
    filter_list = ["*.txt", "data/*", "bla/blu/ble"]
    test_list = [
        PurePath("test.txt"),
        PurePath("data/xy.blob"),
        PurePath("bla/blu/ble"),
        PurePath("data/test_files/kk.txt"),
    ]

    for path_object in test_list:
        assert _is_excluded_by_filter(path_object, filter_list) is True
