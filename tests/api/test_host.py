"""Test Host API."""

import pytest

from supervisor.coresys import CoreSys

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_api_host_info(api_client, tmp_path, coresys: CoreSys):
    """Test host info api."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    coresys.hardware.disk.get_disk_life_time = lambda x: 0
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.hardware.disk.get_disk_total_space = lambda x: 50000
    coresys.hardware.disk.get_disk_used_space = lambda x: 45000

    resp = await api_client.get("/host/info")
    result = await resp.json()

    assert result["data"]["apparmor"] == "2.13.2"
