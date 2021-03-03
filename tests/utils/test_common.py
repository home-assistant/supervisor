"""Test common."""
from supervisor.utils.common import find_one_filetype


def test_default(tmp_path):
    """Test default."""
    filepath = find_one_filetype(tmp_path, "test", [".json"], "test.json")
    assert filepath == tmp_path / "test.json"


def test_none(tmp_path):
    """Test default."""
    filepath = find_one_filetype(tmp_path, "test", [".json"])
    assert filepath is None
