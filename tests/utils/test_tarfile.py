"""Test Tarfile functions."""
from pathlib import Path, PurePath
import shutil
from tempfile import TemporaryDirectory

import attr

from supervisor.utils.tar import (
    SecureTarFile,
    _is_excluded_by_filter,
    atomic_contents_add,
    secure_path,
)


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


def test_create_pure_tar():
    """Test to create a tar file without encryption."""
    with TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)

        # Prepair test folder
        temp_orig = temp.joinpath("orig")
        fixture_data = Path(__file__).parents[1].joinpath("fixtures/tar_data")
        shutil.copytree(fixture_data, temp_orig, symlinks=True)

        # Create Tarfile
        temp_tar = temp.joinpath("backup.tar")
        with SecureTarFile(temp_tar, "w") as tar_file:
            atomic_contents_add(
                tar_file, temp_orig, excludes=[], arcname=".",
            )

        assert temp_tar.exists()

        # Restore
        temp_new = temp.joinpath("new")
        with SecureTarFile(temp_tar, "r") as tar_file:
            tar_file.extractall(path=temp_new, members=tar_file)

        assert temp_new.is_dir()
        assert temp_new.joinpath("test_symlink").is_symlink()
        assert temp_new.joinpath("test1").is_dir()
        assert temp_new.joinpath("test1/script.sh").is_file()
        assert temp_new.joinpath("test1/script.sh").stat().st_mode == 33261
        assert temp_new.joinpath("README.md").is_file()
