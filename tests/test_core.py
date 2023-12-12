"""Testing handling with CoreState."""
# pylint: disable=W0212
import datetime
from unittest.mock import AsyncMock, PropertyMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import WhoamiSSLError
from supervisor.host.control import SystemControl
from supervisor.host.info import InfoCenter
from supervisor.utils.whoami import WhoamiData


def test_write_state(run_dir, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = CoreState.RUNNING

    assert run_dir.read_text() == CoreState.RUNNING

    coresys.core.state = CoreState.SHUTDOWN

    assert run_dir.read_text() == CoreState.SHUTDOWN


async def test_adjust_system_datetime(coresys: CoreSys):
    """Test _adjust_system_datetime method with successful retrieve_whoami."""
    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    with patch(
        "supervisor.core.retrieve_whoami",
        new_callable=AsyncMock,
        side_effect=[WhoamiData("Europe/Zurich", utc_ts)],
    ) as mock_retrieve_whoami:
        await coresys.core._adjust_system_datetime()
        mock_retrieve_whoami.assert_called_once()
        assert coresys.core.sys_config.timezone == "Europe/Zurich"

        # Validate we don't retrieve whoami once timezone has been set
        mock_retrieve_whoami.reset_mock()
        await coresys.core._adjust_system_datetime()
        mock_retrieve_whoami.assert_not_called()


async def test_adjust_system_datetime_without_ssl(run_dir, coresys: CoreSys):
    """Test _adjust_system_datetime method when retrieve_whoami raises WhoamiSSLError."""
    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    with patch(
        "supervisor.core.retrieve_whoami",
        new_callable=AsyncMock,
        side_effect=[WhoamiSSLError("SSL error"), WhoamiData("Europe/Zurich", utc_ts)],
    ) as mock_retrieve_whoami:
        await coresys.core._adjust_system_datetime()
        assert mock_retrieve_whoami.call_count == 2
        assert mock_retrieve_whoami.call_args_list[0].args[1]
        assert not mock_retrieve_whoami.call_args_list[1].args[1]
        assert coresys.core.sys_config.timezone == "Europe/Zurich"


async def test_adjust_system_datetime_if_time_behind(run_dir, coresys: CoreSys):
    """Test _adjust_system_datetime method when current time is ahead more than 3 days."""
    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC) + datetime.timedelta(
        days=4
    )
    with patch(
        "supervisor.core.retrieve_whoami",
        new_callable=AsyncMock,
        side_effect=[WhoamiData("Europe/Zurich", utc_ts)],
    ) as mock_retrieve_whoami, patch.object(
        SystemControl, "set_datetime"
    ) as mock_set_datetime, patch.object(
        InfoCenter, "dt_synchronized", new=PropertyMock(return_value=False)
    ):
        await coresys.core._adjust_system_datetime()
        mock_retrieve_whoami.assert_called_once()
        mock_set_datetime.assert_called_once()
