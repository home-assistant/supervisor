"""Test Home Assistant OS functionality."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HassOSJobError

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_ota_url_generic_x86_64_rename(coresys: CoreSys) -> None:
    """Test download URL generated."""
    coresys.os._board = "intel-nuc"
    coresys.os._version = AwesomeVersion("5.13")
    await coresys.updater.fetch_data()

    version6 = AwesomeVersion("6.0")
    url = coresys.updater.ota_url.format(
        version=str(version6), board="generic-x86-64", os_name="haos"
    )

    assert coresys.os._get_download_url(version6) == url


def test_ota_url_os_name(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""
    board = "generic-x86-64"
    os_name = "haos"
    versionstr = "6.0"

    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name=os_name)

    coresys.os._board = board
    coresys.os._os_name = os_name
    coresys.updater._data = {"ota": url}

    url = coresys.os._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted


def test_ota_url_os_name_rel_5_downgrade(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""
    board = "generic-x86-64"
    versionstr = "5.9"

    # On downgrade below 6.0 we need to use hassos as os_name.
    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name="hassos")

    coresys.os._board = board
    coresys.os._os_name = "haos"
    coresys.updater._data = {"ota": url}

    url = coresys.os._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted


async def test_update_fails_if_out_of_date(coresys: CoreSys) -> None:
    """Test update of OS fails if Supervisor is out of date."""
    coresys.core.state = CoreState.RUNNING
    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ), patch.object(
        type(coresys.os), "available", new=PropertyMock(return_value=True)
    ), pytest.raises(
        HassOSJobError
    ):
        await coresys.os.update()


async def test_board_name_supervised(coresys: CoreSys) -> None:
    """Test board name is supervised when not on haos."""
    with patch("supervisor.os.manager.CPE.get_product", return_value=["not-hassos"]):
        # Board should be none if hostname gave us no info
        await coresys.os.load()
        assert coresys.os.board is None

        # If hostname gave us CPE and we're not on HAOS then its supervised
        await coresys.dbus.hostname.connect(coresys.dbus.bus)
        await coresys.os.load()
        assert coresys.os.board == "supervised"
