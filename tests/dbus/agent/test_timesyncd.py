"""Test Timesyncd configuration interface."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent

from tests.dbus_service_mocks.agent_timesyncd import Timesyncd as TimesyncdService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(name="timesyncd_service", autouse=True)
async def fixture_timesyncd_service(
    os_agent_services: dict[str, DBusServiceMock],
) -> TimesyncdService:
    """Mock Timesyncd dbus service."""
    return os_agent_services["agent_timesyncd"]


async def test_dbus_osagent_timesyncd_ntp_servers(
    timesyncd_service: TimesyncdService, dbus_session_bus: MessageBus
):
    """Test DBus API for NTP servers."""
    os_agent = OSAgent()

    assert os_agent.timesyncd.ntp_servers is None
    await os_agent.timesyncd.connect(dbus_session_bus)

    assert os_agent.timesyncd.ntp_servers == ["time.cloudflare.com"]

    await os_agent.timesyncd.set_ntp_servers(["pool.ntp.org"])
    await timesyncd_service.ping()
    assert os_agent.timesyncd.ntp_servers == ["pool.ntp.org"]


async def test_dbus_osagent_timesyncd_fallback_ntp_servers(
    timesyncd_service: TimesyncdService, dbus_session_bus: MessageBus
):
    """Test DBus API for fallback NTP servers."""
    os_agent = OSAgent()

    assert os_agent.timesyncd.fallback_ntp_servers is None
    await os_agent.timesyncd.connect(dbus_session_bus)

    assert os_agent.timesyncd.fallback_ntp_servers == ["time.google.com"]

    await os_agent.timesyncd.set_fallback_ntp_servers(["time.nist.gov"])
    await timesyncd_service.ping()
    assert os_agent.timesyncd.fallback_ntp_servers == ["time.nist.gov"]
