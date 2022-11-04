"""Test Yellow board."""

import asyncio

from dbus_fast.aio.message_bus import MessageBus

from supervisor.dbus.agent.boards.yellow import Yellow


async def test_dbus_yellow(dbus: list[str], dbus_bus: MessageBus):
    """Test Yellow board load."""
    yellow = Yellow()
    await yellow.connect(dbus_bus)

    assert yellow.name == "Yellow"
    assert yellow.disk_led is True
    assert yellow.heartbeat_led is True
    assert yellow.power_led is True


async def test_dbus_yellow_set_disk_led(dbus: list[str], dbus_bus: MessageBus):
    """Test setting disk led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_bus)

    dbus.clear()
    yellow.disk_led = False
    await asyncio.sleep(0)

    assert dbus == ["/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.DiskLED"]


async def test_dbus_yellow_set_heartbeat_led(dbus: list[str], dbus_bus: MessageBus):
    """Test setting heartbeat led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_bus)

    dbus.clear()
    yellow.heartbeat_led = False
    await asyncio.sleep(0)

    assert dbus == ["/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.HeartbeatLED"]


async def test_dbus_yellow_set_power_led(dbus: list[str], dbus_bus: MessageBus):
    """Test setting power led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_bus)

    dbus.clear()
    yellow.power_led = False
    await asyncio.sleep(0)

    assert dbus == ["/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.PowerLED"]
