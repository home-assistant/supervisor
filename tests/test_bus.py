"""Test bus backend."""

import asyncio

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys


async def test_bus_event(coresys: CoreSys) -> None:
    """Test bus events over the backend."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None))
    assert results[-1] is None

    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, "test"))
    assert results[-1] == "test"


async def test_bus_event_not_called(coresys: CoreSys) -> None:
    """Test bus events over the backend."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_REMOVE_DEVICE, None))
    assert len(results) == 0


async def test_bus_event_removed(coresys: CoreSys) -> None:
    """Test bus events over the backend and remove."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    listener = coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None))
    assert results[-1] is None

    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, "test"))
    assert results[-1] == "test"

    coresys.bus.remove_listener(listener)

    # No listeners remain, so no tasks are returned to gather.
    await asyncio.gather(*coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None))
    assert results[-1] == "test"
