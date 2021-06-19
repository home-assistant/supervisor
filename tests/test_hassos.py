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


def test_ota_url_os_name(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""

    board = "generic-x86-64"
    os_name = "haos"
    versionstr = "6.0"

    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name=os_name)

    coresys.hassos._board = board
    coresys.hassos._os_name = os_name
    coresys.updater._data = {"ota": url}

    url = coresys.hassos._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted


def test_ota_url_os_name_rel_5_downgrade(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""

    board = "generic-x86-64"
    versionstr = "5.9"

    # On downgrade below 6.0 we need to use hassos as os_name.
    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name="hassos")

    coresys.hassos._board = board
    coresys.hassos._os_name = "haos"
    coresys.updater._data = {"ota": url}

    url = coresys.hassos._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted
