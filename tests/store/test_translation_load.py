"""Test loading add-translation."""

# pylint: disable=import-error,protected-access
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.store.data import _read_app_translations
from supervisor.utils.common import write_json_or_yaml_file


def test_loading_traslations(coresys: CoreSys, tmp_path: Path):
    """Test loading add-translation."""
    (tmp_path / "translations").mkdir(parents=True)
    # no translations
    assert _read_app_translations(tmp_path) == {}

    for file in ("en.json", "es.json"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {
                "configuration": {
                    "test": {
                        "name": "test",
                        "description": "test",
                        "test": "test",
                        "fields": {"test2": {"name": "test2"}},
                    }
                }
            },
        )

    for file in ("no.yaml", "de.yaml"):
        write_json_or_yaml_file(
            tmp_path / "translations" / file,
            {
                "configuration": {"test": {"name": "test", "test": "test"}},
                "network": {"80/tcp": "Webserver port"},
            },
        )

    translations = _read_app_translations(tmp_path)

    assert translations["en"]["configuration"]["test"]["name"] == "test"
    assert translations["es"]["configuration"]["test"]["name"] == "test"
    assert translations["no"]["configuration"]["test"]["name"] == "test"
    assert translations["de"]["configuration"]["test"]["name"] == "test"

    assert translations["en"]["configuration"]["test"]["description"] == "test"
    assert translations["es"]["configuration"]["test"]["description"] == "test"

    assert (
        translations["en"]["configuration"]["test"]["fields"]["test2"]["name"]
        == "test2"
    )
    assert (
        translations["es"]["configuration"]["test"]["fields"]["test2"]["name"]
        == "test2"
    )

    assert "test" not in translations["en"]["configuration"]["test"]

    assert translations["no"]["network"]["80/tcp"] == "Webserver port"


def test_translation_file_failure(
    coresys: CoreSys, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Test translations load if one fails."""
    (tmp_path / "translations").mkdir(parents=True)
    write_json_or_yaml_file(
        tmp_path / "translations" / "en.json",
        {"configuration": {"test": {"name": "test", "test": "test"}}},
    )
    fail_path = tmp_path / "translations" / "de.json"
    with fail_path.open("w") as de_file:
        de_file.write("not json")

    translations = _read_app_translations(tmp_path)

    assert translations["en"]["configuration"]["test"]["name"] == "test"
    assert f"Can't read translations from {fail_path.as_posix()}" in caplog.text
