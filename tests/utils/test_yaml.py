"""test yaml."""
import json

from ruamel.yaml import YAML as _YAML

from supervisor.const import FILE_SUFFIX_CONFIGURATION
from supervisor.utils import find_one_filetype, read_json_or_yaml_file, yaml

YAML = _YAML()


def test_reading_yaml(tmp_path):
    """Test reading YAML file."""
    tempfile = tmp_path / "test.yaml"
    YAML.dump({"test": "test"}, tempfile)
    yaml.read_yaml_file(tempfile)


def test_get_file_from_type(tmp_path):
    """Test get file from type."""
    tempfile = tmp_path / "test1.yaml"
    YAML.dump({"test": "test"}, tempfile)
    found = find_one_filetype(tmp_path, "test1", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test1.yaml"

    tempfile = tmp_path / "test2.yml"
    YAML.dump({"test": "test"}, tempfile)
    found = find_one_filetype(tmp_path, "test2", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test2.yml"

    tempfile = tmp_path / "test3.json"
    YAML.dump({"test": "test"}, tempfile)
    found = find_one_filetype(tmp_path, "test3", FILE_SUFFIX_CONFIGURATION)
    assert found.parts[-1] == "test3.json"

    tempfile = tmp_path / "test.config"
    YAML.dump({"test": "test"}, tempfile)
    found = find_one_filetype(tmp_path, "test4", FILE_SUFFIX_CONFIGURATION)
    assert not found


def test_read_json_or_yaml_file(tmp_path):
    """Read JSON or YAML file."""
    tempfile = tmp_path / "test.json"
    with open(tempfile, "w") as outfile:
        json.dump({"test": "test"}, outfile)
    read = read_json_or_yaml_file(tempfile)
    assert read["test"] == "test"

    tempfile = tmp_path / "test.yaml"
    YAML.dump({"test": "test"}, tempfile)
    read = read_json_or_yaml_file(tempfile)
    assert read["test"] == "test"
