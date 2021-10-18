"""Test hostname dbus interface."""

from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.dbus.const import DBUS_NAME_SYSTEMD

from tests.common import load_json_fixture


async def test_dbus_systemd_info(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.systemd.boot_timestamp is None
    assert coresys.dbus.systemd.startup_time is None

    await coresys.dbus.systemd.connect()

    async def mock_get_properties(dbus_obj, interface):
        return load_json_fixture(
            f"{DBUS_NAME_SYSTEMD.replace('.', '_')}_properties.json"
        )

    with patch(
        "supervisor.utils.dbus_next.DBus.get_properties", new=mock_get_properties
    ):
        await coresys.dbus.systemd.update()

    assert coresys.dbus.systemd.boot_timestamp == 1632236713344227
    assert coresys.dbus.systemd.startup_time == 45.304696
