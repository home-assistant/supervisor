"""Test common."""

import pytest

from supervisor.exceptions import ConfigurationFileError
from supervisor.utils.common import find_one_filetype


def test_not_found(tmp_path):
    """Test default."""
    with pytest.raises(ConfigurationFileError):
        find_one_filetype(tmp_path, "test", [".json"])
