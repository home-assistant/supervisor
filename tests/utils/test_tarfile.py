"""Test Tarfile functions."""

import attr
import pytest

from hassio.utils.tar import secure_path, exclude_filter


@attr.s
class TarInfo:
    """Fake TarInfo"""

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


def test_exclude_filter_good():
    """Test exclude filter."""
    filter_funct = exclude_filter(["not/match", "/dev/xy"])
    test_list = [
        TarInfo("test.txt"),
        TarInfo("data/xy.blob"),
        TarInfo("bla/blu/ble"),
        TarInfo("data/../xy.blob"),
    ]

    assert test_list == [filter_funct(result) for result in test_list]


def test_exclude_filter_bad():
    """Test exclude filter."""
    filter_funct = exclude_filter(["*.txt", "data/*", "bla/blu/ble"])
    test_list = [
        TarInfo("test.txt"),
        TarInfo("data/xy.blob"),
        TarInfo("bla/blu/ble"),
        TarInfo("data/test_files/kk.txt"),
    ]

    for info in [filter_funct(result) for result in test_list]:
        assert info is None
