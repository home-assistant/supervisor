"""Test Addons API."""
import pytest

from supervisor.addons.addon import Addon
from supervisor.const import AddonState
from supervisor.exceptions import AddonsError


async def test_addon_state_on_update(addon: Addon):
    """Test blocking add-on states."""
    with pytest.raises(
        AddonsError, match="Add-on is starting, this is not a valid state for update"
    ):
        addon.state = AddonState.STARTING
        await addon.update()

    with pytest.raises(
        AddonsError, match="Add-on is stopping, this is not a valid state for update"
    ):
        addon.state = AddonState.STOPPING
        await addon.update()

    addon.state = AddonState.STARTED
    await addon.update()
    assert addon.state == AddonState.STARTED
