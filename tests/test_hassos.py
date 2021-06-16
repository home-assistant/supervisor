"""Test Home Assistant OS functionality."""

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_ota_url_generic_x86_64_rename(coresys: CoreSys) -> None:
    """Test download URL generated."""

    coresys.hassos._board = "intel-nuc"
    coresys.hassos._version = AwesomeVersion("5.13")
    await coresys.updater.fetch_data()

    version6 = AwesomeVersion("6.0")
    url = coresys.updater.ota_url.format(version=str(version6), board="generic-x86-64")

    assert coresys.hassos._get_download_url(version6) == url


def test_ota_url_generation(coresys: CoreSys) -> None:
    """Test OTA URL generation."""
    coresys.updater._data = {
        "ota": "https://github.com/home-assistant/operating-system/releases/download/{version}/haos_{board}-{version}.raucb"
    }

    url = coresys.hassos._get_download_url(AwesomeVersion("5.13"))
    assert "hassos" in url
    assert "haos" not in url

    url = coresys.hassos._get_download_url(AwesomeVersion("5"))
    assert "hassos" in url
    assert "haos" not in url

    url = coresys.hassos._get_download_url(AwesomeVersion("6.1"))
    assert "haos" in url
    assert "hassos" not in url

    url = coresys.hassos._get_download_url(AwesomeVersion("6"))
    assert "haos" in url
    assert "hassos" not in url
