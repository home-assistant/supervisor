"""Test Home Assistant core."""
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantJobError


async def test_update_fails_if_out_of_date(coresys: CoreSys):
    """Test update of Home Assistant fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ), pytest.raises(HomeAssistantJobError):
        await coresys.homeassistant.core.update()

    with patch.object(
        type(coresys.plugins.audio), "need_update", new=PropertyMock(return_value=True)
    ), pytest.raises(HomeAssistantJobError):
        await coresys.homeassistant.core.update()
