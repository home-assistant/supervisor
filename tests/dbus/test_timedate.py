"""Test TimeDate dbus interface."""

# pylint: disable=import-error
from datetime import UTC, datetime

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.timedate import TimeDate
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.timedate import TimeDate as TimeDateService


@pytest.fixture(name="timedate_service")
async def fixture_timedate_service(dbus_session_bus: MessageBus) -> TimeDateService:
    """Mock timedate dbus service."""
    yield (await mock_dbus_services({"timedate": None}, dbus_session_bus))["timedate"]


async def test_timedate_info(
    timedate_service: TimeDateService, dbus_session_bus: MessageBus
):
    """Test timedate properties."""
    timedate = TimeDate()

    assert timedate.dt_utc is None
    assert timedate.ntp is None

    await timedate.connect(dbus_session_bus)

    assert timedate.dt_utc == datetime(2021, 5, 19, 8, 36, 54, 405718, tzinfo=UTC)
    assert timedate.ntp is True

    assert timedate.dt_utc.isoformat() == "2021-05-19T08:36:54.405718+00:00"

    timedate_service.emit_properties_changed({"NTP": False})
    await timedate_service.ping()
    assert timedate.ntp is False

    timedate_service.emit_properties_changed({}, ["NTP"])
    await timedate_service.ping()
    await timedate_service.ping()  # To process the follow-up get all properties call
    assert timedate.ntp is True


async def test_dbus_settime(
    timedate_service: TimeDateService, dbus_session_bus: MessageBus
):
    """Set timestamp on backend."""
    timedate_service.SetTime.calls.clear()
    timedate = TimeDate()

    test_dt = datetime(2021, 5, 19, 8, 36, 54, 405718, tzinfo=UTC)

    with pytest.raises(DBusNotConnectedError):
        await timedate.set_time(test_dt)

    await timedate.connect(dbus_session_bus)

    assert await timedate.set_time(test_dt) is None
    assert timedate_service.SetTime.calls == [(1621413414405718, False, False)]


async def test_dbus_setntp(
    timedate_service: TimeDateService, dbus_session_bus: MessageBus
):
    """Disable NTP on backend."""
    timedate_service.SetNTP.calls.clear()
    timedate = TimeDate()

    with pytest.raises(DBusNotConnectedError):
        await timedate.set_ntp(False)

    await timedate.connect(dbus_session_bus)

    assert timedate.ntp is True
    assert await timedate.set_ntp(False) is None
    assert timedate_service.SetNTP.calls == [(False, False)]
    await timedate_service.ping()
    assert timedate.ntp is False


async def test_dbus_timedate_connect_error(
    dbus_session_bus: MessageBus, caplog: pytest.LogCaptureFixture
):
    """Test connecting to timedate error."""
    timedate = TimeDate()
    await timedate.connect(dbus_session_bus)
    assert "No timedate support on the host" in caplog.text
