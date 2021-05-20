"""Test Home Assistant OS functionality."""

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys

URL_TEST = "https://version.home-assistant.io/stable.json"

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_ota_url_generic_x86_64_rename(coresys: CoreSys) -> None:
    """Test download URL generated."""

    coresys.hassos._board = "intel-nuc"
    coresys.hassos._version = AwesomeVersion("5.13")
    await coresys.updater.fetch_data()

    version6str = "6.0"
    version6 = AwesomeVersion(version6str)
    url = coresys.updater.ota_url.format(
        version=str(version6str), board="generic-x86-64"
    )

    assert coresys.hassos._get_download_url(version6) == url
