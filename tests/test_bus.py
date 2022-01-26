"""Test bus backend."""

import asyncio

import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys


@pytest.mark.asyncio
async def test_bus_event(coresys: CoreSys) -> None:
    """Test bus events over the backend."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None)
    await asyncio.sleep(0)
    assert results[-1] is None

    coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, "test")
    await asyncio.sleep(0)
    assert results[-1] == "test"


@pytest.mark.asyncio
async def test_bus_event_not_called(coresys: CoreSys) -> None:
    """Test bus events over the backend."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    coresys.bus.fire_event(BusEvent.HARDWARE_REMOVE_DEVICE, None)
    await asyncio.sleep(0)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_bus_event_removed(coresys: CoreSys) -> None:
    """Test bus events over the backend and remove."""
    results = []

    async def callback(data) -> None:
        """Test callback."""
        results.append(data)

    listener = coresys.bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, callback)

    coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None)
    await asyncio.sleep(0)
    assert results[-1] is None

    coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, "test")
    await asyncio.sleep(0)
    assert results[-1] == "test"

    coresys.bus.remove_listener(listener)

    coresys.bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, None)
    await asyncio.sleep(0)
    assert results[-1] == "test"
