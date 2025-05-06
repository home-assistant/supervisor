"""Testing handling with CoreState."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from aiohttp.hdrs import USER_AGENT
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.timedate import TimeDate
from supervisor.utils.dt import utcnow


async def test_timezone(coresys: CoreSys):
    """Test write corestate to /run/supervisor."""
    # pylint: disable=protected-access
    coresys.host.sys_dbus._timedate = TimeDate()
    # pylint: enable=protected-access

    assert coresys.timezone == "UTC"
    assert coresys.config.timezone is None

    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    assert coresys.timezone == "Etc/UTC"

    await coresys.config.set_timezone("Europe/Zurich")
    assert coresys.timezone == "Europe/Zurich"


async def test_now(coresys: CoreSys):
    """Test datetime now with local time."""
    await coresys.config.set_timezone("Europe/Zurich")

    zurich = coresys.now()
    utc = utcnow()

    assert zurich != utc
    assert zurich - utc <= timedelta(hours=2)


@pytest.mark.no_mock_init_websession
async def test_custom_user_agent(coresys: CoreSys):
    """Test custom useragent."""
    with patch(
        "supervisor.coresys.aiohttp.ClientSession", return_value=MagicMock()
    ) as mock_session:
        await coresys.init_websession()
        assert (
            "HomeAssistantSupervisor/9999.09.9.dev9999"
            in mock_session.call_args_list[0][1]["headers"][USER_AGENT]
        )


@pytest.mark.no_mock_init_websession
async def test_no_init_when_api_running(coresys: CoreSys):
    """Test ClientSession reinitialization is refused when API is running."""
    with patch("supervisor.coresys.aiohttp.ClientSession"):
        await coresys.init_websession()
        await coresys.core.set_state(CoreState.RUNNING)
        # Reinitialize websession should not be possible while running
        with pytest.raises(RuntimeError):
            await coresys.init_websession()
