"""Testing handling with CoreState."""

from supervisor.coresys import CoreSys


async def test_timezone(run_dir, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""

    assert coresys.timezone == "UTC"
    assert coresys.config.timezone is None

    await coresys.dbus.timedate.connect()
    await coresys.dbus.timedate.update()
    assert coresys.timezone == "Etc/UTC"

    coresys.config.timezone = "Europe/Zurich"
    assert coresys.timezone == "Europe/Zurich"
