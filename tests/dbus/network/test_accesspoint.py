"""Test NetworkWireless AP object."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network.accesspoint import NetworkWirelessAP

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.network_access_point import (
    AccessPoint as AccessPointService,
)


@pytest.fixture(name="access_point_service", autouse=True)
async def fixture_access_point_service(
    dbus_session_bus: MessageBus,
) -> AccessPointService:
    """Mock Access Point service."""
    yield (
        await mock_dbus_services(
            {
                "network_access_point": "/org/freedesktop/NetworkManager/AccessPoint/43099"
            },
            dbus_session_bus,
        )
    )["network_access_point"]


async def test_accesspoint(
    access_point_service: AccessPointService, dbus_session_bus: MessageBus
):
    """Test accesspoint."""
    wireless_ap = NetworkWirelessAP("/org/freedesktop/NetworkManager/AccessPoint/43099")

    assert wireless_ap.mac is None
    assert wireless_ap.mode is None

    await wireless_ap.connect(dbus_session_bus)

    assert wireless_ap.mac == "E4:57:40:A9:D7:DE"
    assert wireless_ap.mode == 2
    assert wireless_ap.strength == 47

    # We don't listen for property changes on access points, too noisy
    access_point_service.emit_properties_changed({"Strength": 74})
    await access_point_service.ping()
    assert wireless_ap.strength == 47
