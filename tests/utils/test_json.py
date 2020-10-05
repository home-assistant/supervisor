"""test json."""
from pathlib import Path

from supervisor.utils.json import write_json_file


def test_file_permissions(tmp_path):
    """Test file permissions."""
    tempfile = Path(tmp_path, "test.json")
    write_json_file(tempfile, {"test": "data"})
    assert tempfile.is_file()
    assert oct(tempfile.stat().st_mode)[-3:] == "600"


def test_new_file_permissions(tmp_path):
    """Test file permissions."""
    tempfile = Path(tmp_path, "test.json")
    tempfile.write_text("test")
    assert oct(tempfile.stat().st_mode)[-3:] != "600"

    write_json_file(tempfile, {"test": "data"})
    assert oct(tempfile.stat().st_mode)[-3:] == "600"
