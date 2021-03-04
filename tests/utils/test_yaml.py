"""test yaml."""

import pytest

from supervisor.const import FILE_SUFFIX_CONFIGURATION
from supervisor.exceptions import ConfigurationFileError
from supervisor.utils.common import find_one_filetype, read_json_or_yaml_file
from supervisor.utils.json import write_json_file
from supervisor.utils.yaml import read_yaml_file, write_yaml_file


def test_reading_yaml(tmp_path):
    """Test reading YAML file."""
    tempfile = tmp_path / "test.yaml"
    write_yaml_file(tempfile, {"test": "test"})
    read = read_yaml_file(tempfile)
    assert read["test"] == "test"


def test_get_file_from_type(tmp_path):
    """Test get file from type."""
    tempfile = tmp_path / "test1.yaml"
    write_yaml_file(tempfile, {"test": "test"})
    found = find_one_filetype(tmp_path, "test1", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test1.yaml"

    tempfile = tmp_path / "test2.yml"
    write_yaml_file(tempfile, {"test": "test"})
    found = find_one_filetype(tmp_path, "test2", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test2.yml"

    tempfile = tmp_path / "test3.json"
    write_yaml_file(tempfile, {"test": "test"})
    found = find_one_filetype(tmp_path, "test3", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test3.json"

    tempfile = tmp_path / "test.config"
    write_yaml_file(tempfile, {"test": "test"})
    with pytest.raises(ConfigurationFileError):
        find_one_filetype(tmp_path, "test4", FILE_SUFFIX_CONFIGURATION)


def test_read_json_or_yaml_file(tmp_path):
    """Read JSON or YAML file."""
    tempfile = tmp_path / "test.json"
    write_json_file(tempfile, {"test": "test"})
    read = read_json_or_yaml_file(tempfile)
    assert read["test"] == "test"

    tempfile = tmp_path / "test.yaml"
    write_yaml_file(tempfile, {"test": "test"})
    read = read_json_or_yaml_file(tempfile)
    assert read["test"] == "test"
