"""test json."""

import time
from typing import NamedTuple

from supervisor.utils.json import json_dumps, read_json_file, write_json_file


def test_file_permissions(tmp_path):
    """Test file permissions."""
    tempfile = tmp_path / "test.json"
    write_json_file(tempfile, {"test": "data"})
    assert tempfile.is_file()
    assert oct(tempfile.stat().st_mode)[-3:] == "600"


def test_new_file_permissions(tmp_path):
    """Test file permissions."""
    tempfile = tmp_path / "test.json"
    tempfile.write_text("test")
    assert oct(tempfile.stat().st_mode)[-3:] != "600"

    write_json_file(tempfile, {"test": "data"})
    assert oct(tempfile.stat().st_mode)[-3:] == "600"


def test_file_round_trip(tmp_path):
    """Test file permissions."""
    tempfile = tmp_path / "test.json"
    write_json_file(tempfile, {"test": "data"})
    assert tempfile.is_file()
    assert oct(tempfile.stat().st_mode)[-3:] == "600"
    assert read_json_file(tempfile) == {"test": "data"}


def test_json_dumps_float_subclass() -> None:
    """Test the json dumps a float subclass."""

    class FloatSubclass(float):
        """A float subclass."""

    assert json_dumps({"c": FloatSubclass(1.2)}) == '{"c":1.2}'


def test_json_dumps_tuple_subclass() -> None:
    """Test the json dumps a tuple subclass."""

    tt = time.struct_time((1999, 3, 17, 32, 44, 55, 2, 76, 0))

    assert json_dumps(tt) == "[1999,3,17,32,44,55,2,76,0]"


def test_json_dumps_named_tuple_subclass() -> None:
    """Test the json dumps a tuple subclass."""

    class NamedTupleSubclass(NamedTuple):
        """A NamedTuple subclass."""

        name: str

    nts = NamedTupleSubclass("a")

    assert json_dumps(nts) == '["a"]'
