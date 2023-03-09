"""Shared fixtures for OS Agent tests."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture
async def os_agent_services(dbus_session_bus: MessageBus) -> dict[str, DBusServiceMock]:
    """Mock all services os agent connects to."""
    yield await mock_dbus_services(
        {
            "os_agent": None,
            "apparmor": None,
            "cgroup": None,
            "datadisk": None,
            "system": None,
            "boards": None,
            "boards_yellow": None,
        },
        dbus_session_bus,
    )
