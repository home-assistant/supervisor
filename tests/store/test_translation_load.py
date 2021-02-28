"""Test loading add-translation."""
# pylint: disable=import-error,protected-access
import json
import os

from supervisor.coresys import CoreSys


def test_loading_traslations(coresys: CoreSys, tmp_path):
    """Test loading add-translation."""
    os.makedirs(tmp_path / "translations")
    # no transaltions
    assert coresys.store.data._read_addon_translations(tmp_path) == {}

    for file in ("en.json", "es.json"):
        with open(tmp_path / "translations" / file, "w") as lang_file:
            lang_file.write(json.dumps({"test": "test"}))

    translations = coresys.store.data._read_addon_translations(tmp_path)

    assert translations["en"]["test"] == "test"
    assert translations["es"]["test"] == "test"
