"""Test loading add-translation."""

# pylint: disable=import-error,protected-access
import os
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.store.data import _read_addon_translations
from supervisor.utils.common import write_json_or_yaml_file


def test_loading_traslations(coresys: CoreSys, tmp_path: Path):
    """Test loading add-translation."""
    os.makedirs(tmp_path / "translations")
    # no transaltions
    assert _read_addon_translations(tmp_path) == {}

    for file in ("en.json", "es.json"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {"configuration": {"test": {"name": "test", "test": "test"}}},
        )

    for file in ("no.yaml", "de.yaml"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {
                "configuration": {"test": {"name": "test", "test": "test"}},
                "network": {"80/tcp": "Webserver port"},
            },
        )

    translations = _read_addon_translations(tmp_path)

    assert translations["en"]["configuration"]["test"]["name"] == "test"
    assert translations["es"]["configuration"]["test"]["name"] == "test"
    assert translations["no"]["configuration"]["test"]["name"] == "test"
    assert translations["de"]["configuration"]["test"]["name"] == "test"

    assert "test" not in translations["en"]["configuration"]["test"]

    assert translations["no"]["network"]["80/tcp"] == "Webserver port"


def test_translation_file_failure(
    coresys: CoreSys, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Test translations load if one fails."""
    os.makedirs(tmp_path / "translations")
    write_json_or_yaml_file(
        tmp_path / "translations" / "en.json",
        {"configuration": {"test": {"name": "test", "test": "test"}}},
    )
    fail_path = tmp_path / "translations" / "de.json"
    with fail_path.open("w") as de_file:
        de_file.write("not json")

    translations = _read_addon_translations(tmp_path)

    assert translations["en"]["configuration"]["test"]["name"] == "test"
    assert f"Can't read translations from {fail_path.as_posix()}" in caplog.text
