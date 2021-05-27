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
