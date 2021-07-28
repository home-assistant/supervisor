"""Testing handling with CoreState."""

from datetime import timedelta

from aiohttp.hdrs import USER_AGENT

from supervisor.coresys import CoreSys
from supervisor.utils.dt import utcnow


async def test_timezone(run_dir, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""

    assert coresys.timezone == "UTC"
    assert coresys.config.timezone is None

    await coresys.dbus.timedate.connect()
    await coresys.dbus.timedate.update()
    assert coresys.timezone == "Etc/UTC"

    coresys.config.timezone = "Europe/Zurich"
    assert coresys.timezone == "Europe/Zurich"


def test_now(coresys: CoreSys):
    """Test datetime now with local time."""
    coresys.config.timezone = "Europe/Zurich"

    zurich = coresys.now()
    utc = utcnow()

    assert zurich != utc
    assert zurich - utc <= timedelta(hours=2)


def test_custom_user_agent(coresys: CoreSys):
    """Test custom useragent."""
    assert (
        "HomeAssistantSupervisor/DEV"
        in coresys.websession._default_headers[  # pylint: disable=protected-access
            USER_AGENT
        ]
    )
