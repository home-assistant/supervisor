"""Test common."""
from pathlib import Path

import pytest

from supervisor.exceptions import ConfigurationFileError
from supervisor.utils.common import find_one_filetype


def test_not_found(tmp_path):
    """Test default."""
    with pytest.raises(ConfigurationFileError):
        find_one_filetype(tmp_path, "test", [".json"])


def test_with_found(tmp_path):
    """Test default."""
    test_file = Path(tmp_path, "test.json")
    test_file.write_text("found")

    assert find_one_filetype(tmp_path, "test", [".json"]) == test_file
