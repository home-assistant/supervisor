"""Test loading add-translation."""
# pylint: disable=import-error,protected-access
import os

from supervisor.coresys import CoreSys
from supervisor.utils.common import write_json_or_yaml_file


def test_loading_traslations(coresys: CoreSys, tmp_path):
    """Test loading add-translation."""
    os.makedirs(tmp_path / "translations")
    # no transaltions
    assert coresys.store.data._read_addon_translations(tmp_path) == {}

    for file in ("en.json", "es.json"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {"configuration": {"test": {"name": "test", "test": "test"}}},
        )

    for file in ("no.yaml", "de.yaml"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {"configuration": {"test": {"name": "test", "test": "test"}}},
        )

    translations = coresys.store.data._read_addon_translations(tmp_path)

    assert translations["en"]["configuration"]["test"]["name"] == "test"
    assert translations["es"]["configuration"]["test"]["name"] == "test"
    assert translations["no"]["configuration"]["test"]["name"] == "test"
    assert translations["de"]["configuration"]["test"]["name"] == "test"

    assert "test" not in translations["en"]["configuration"]["test"]
