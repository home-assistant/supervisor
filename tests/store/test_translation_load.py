"""Test loading add-translation."""
# pylint: disable=import-error,protected-access
import json
import os

from ruamel.yaml import YAML

from supervisor.coresys import CoreSys

_YAML = YAML()
_YAML.allow_duplicate_keys = True


def test_loading_traslations(coresys: CoreSys, tmp_path):
    """Test loading add-translation."""
    os.makedirs(tmp_path / "translations")
    # no transaltions
    assert coresys.store.data._read_addon_translations(tmp_path) == {}

    for file in ("en.json", "es.json"):
        with open(tmp_path / "translations" / file, "w") as lang_file:
            lang_file.write(json.dumps({"configuration": {"test": "test"}}))

    for file in ("no.yaml", "de.yaml"):
        _YAML.dump(
            {"configuration": {"test": "test"}}, tmp_path / "translations" / file
        )

    translations = coresys.store.data._read_addon_translations(tmp_path)

    assert translations["en"]["configuration"]["test"] == "test"
    assert translations["es"]["configuration"]["test"] == "test"
    assert translations["no"]["configuration"]["test"] == "test"
    assert translations["de"]["configuration"]["test"] == "test"
