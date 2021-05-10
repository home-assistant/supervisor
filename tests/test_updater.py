"""Test updater files."""

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

    assert coresys.updater.image_homeassistant == data["image"]["core"].format(
        machine=coresys.machine
    )

    assert coresys.updater.image_supervisor == data["image"]["supervisor"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_cli == data["image"]["cli"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_audio == data["image"]["audio"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_dns == data["image"]["dns"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_observer == data["image"]["observer"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_multicast == data["image"]["multicast"].format(
        arch=coresys.arch.supervisor
    )
