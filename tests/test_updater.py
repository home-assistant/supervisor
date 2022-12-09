"""Test updater files."""
from unittest.mock import patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys

URL_TEST = "https://version.home-assistant.io/stable.json"


@pytest.mark.asyncio
async def test_fetch_versions(coresys: CoreSys) -> None:
    """Test download and sync version."""

    coresys.security.force = True
    await coresys.updater.fetch_data()

    async with coresys.websession.get(URL_TEST) as request:
        data = await request.json()

    assert coresys.updater.version_supervisor == data["supervisor"]
    assert coresys.updater.version_homeassistant == data["homeassistant"]["default"]

    assert coresys.updater.version_audio == data["audio"]
    assert coresys.updater.version_cli == data["cli"]
    assert coresys.updater.version_dns == data["dns"]
    assert coresys.updater.version_multicast == data["multicast"]
    assert coresys.updater.version_observer == data["observer"]

    assert coresys.updater.image_homeassistant == data["images"]["core"].format(
        machine=coresys.machine
    )

    assert coresys.updater.image_supervisor == data["images"]["supervisor"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_cli == data["images"]["cli"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_audio == data["images"]["audio"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_dns == data["images"]["dns"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_observer == data["images"]["observer"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_multicast == data["images"]["multicast"].format(
        arch=coresys.arch.supervisor
    )


@pytest.mark.parametrize(
    "version, expected",
    [
        ("3.1", "3.13"),
        ("4.5", "4.20"),
        ("5.0", "5.13"),
        ("6.4", "6.6"),
        ("4.20", "5.13"),
    ],
)
async def test_os_update_path(coresys: CoreSys, version: str, expected: str):
    """Test OS upgrade path across major versions."""
    coresys.os._board = "rpi4"  # pylint: disable=protected-access
    coresys.os._version = AwesomeVersion(version)  # pylint: disable=protected-access
    with patch.object(type(coresys.security), "verify_own_content"):
        await coresys.updater.fetch_data()

        assert coresys.updater.version_hassos == AwesomeVersion(expected)
