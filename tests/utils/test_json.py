"""test json."""
from pathlib import Path
from tempfile import TemporaryDirectory

from supervisor.utils.json import write_json_file


def test_file_permissions():
    """Test file permissions."""
    with TemporaryDirectory() as temp_dir:
        tempfile = Path(temp_dir + "test.json")
        write_json_file(tempfile, {"test": "data"})
        assert tempfile.is_file()
        assert oct(tempfile.stat().st_mode)[-3:] == "600"


def test_new_file_permissions():
    """Test file permissions."""
    with TemporaryDirectory() as temp_dir:
        tempfile = Path(temp_dir + "test.json")
        tempfile.write_text("test")
        assert oct(tempfile.stat().st_mode)[-3:] != "600"

        write_json_file(tempfile, {"test": "data"})
        assert oct(tempfile.stat().st_mode)[-3:] == "600"
