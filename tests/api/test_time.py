"""Test time API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys

from tests.dbus_service_mocks.agent_timesyncd import Timesyncd as TimesyncdService
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService

# Oldest OS Agent that can write the timesyncd drop-in
NTP_OS_AGENT_VERSION = "1.13.0"


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_time_info(api_client_with_prefix: tuple[TestClient, str]):
    """Test time info API."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/time/info")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"] == {
        "config": {
            "servers": ["time.cloudflare.com"],
            "fallback_servers": ["time.google.com"],
        }
    }


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_time_options(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys: CoreSys,
):
    """Test time options API."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    timesyncd_service: TimesyncdService = all_dbus_services["agent_timesyncd"]
    systemd_service.RestartUnit.calls.clear()

    # Post new set of servers and verify timesyncd is updated and restarted
    resp = await api_client.post(
        f"{prefix}/time/options",
        json={
            "servers": ["pool.ntp.org", "time.cloudflare.com"],
            "fallback_servers": [],
        },
    )

    assert resp.status == 200
    await timesyncd_service.ping()
    assert coresys.dbus.agent.timesyncd.ntp_servers == [
        "pool.ntp.org",
        "time.cloudflare.com",
    ]
    assert coresys.dbus.agent.timesyncd.fallback_ntp_servers == []
    assert systemd_service.RestartUnit.calls == [
        ("systemd-timesyncd.service", "replace")
    ]

    # Posting the same set of servers again still restarts timesyncd
    systemd_service.RestartUnit.calls.clear()
    resp = await api_client.post(
        f"{prefix}/time/options",
        json={
            "servers": ["pool.ntp.org", "time.cloudflare.com"],
            "fallback_servers": [],
        },
    )

    assert resp.status == 200
    assert systemd_service.RestartUnit.calls == [
        ("systemd-timesyncd.service", "replace")
    ]

    # Empty post leaves config untouched and does not restart
    systemd_service.RestartUnit.calls.clear()
    resp = await api_client.post(f"{prefix}/time/options", json={})

    assert resp.status == 200
    assert systemd_service.RestartUnit.calls == []


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_time_options_partial(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys: CoreSys,
):
    """Test time options API leaves omitted fields untouched."""
    api_client, prefix = api_client_with_prefix
    timesyncd_service: TimesyncdService = all_dbus_services["agent_timesyncd"]

    resp = await api_client.post(
        f"{prefix}/time/options", json={"servers": ["pool.ntp.org"]}
    )

    assert resp.status == 200
    await timesyncd_service.ping()
    assert coresys.dbus.agent.timesyncd.ntp_servers == ["pool.ntp.org"]
    assert coresys.dbus.agent.timesyncd.fallback_ntp_servers == ["time.google.com"]


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
@pytest.mark.parametrize(
    "payload",
    [
        {"servers": [""]},
        {"servers": ["pool ntp.org"]},
        {"fallback_servers": ["time.google.com # comment"]},
        {"servers": ["pool.ntp.org\n"]},
        {"servers": ["pool.ntp.org\x00"]},
        {"fallback_servers": ["[::1]"]},
    ],
)
async def test_api_time_options_invalid(
    api_client_with_prefix: tuple[TestClient, str], payload: dict[str, list[str]]
):
    """Test time options API validation."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.post(f"{prefix}/time/options", json=payload)

    assert resp.status == 400


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_time_not_available(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test time API when OS Agent Timesyncd is not available."""
    api_client, prefix = api_client_with_prefix
    coresys.dbus.agent.timesyncd.disconnect()

    resp = await api_client.get(f"{prefix}/time/info")
    assert resp.status == 404

    resp = await api_client.post(
        f"{prefix}/time/options", json={"servers": ["pool.ntp.org"]}
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_agent_version", ["1.12.0"], indirect=True)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_time_old_os_agent(api_client_with_prefix: tuple[TestClient, str]):
    """Test time API when OS Agent is too old to write the drop-in."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/time/info")
    assert resp.status == 404

    resp = await api_client.post(
        f"{prefix}/time/options", json={"servers": ["pool.ntp.org"]}
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_agent_version", [NTP_OS_AGENT_VERSION], indirect=True)
@pytest.mark.usefixtures("os_agent_version")
async def test_api_time_supervised(api_client_with_prefix: tuple[TestClient, str]):
    """Test time API is unavailable without Home Assistant OS."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/time/info")
    assert resp.status == 404

    resp = await api_client.post(
        f"{prefix}/time/options", json={"servers": ["pool.ntp.org"]}
    )
    assert resp.status == 404
