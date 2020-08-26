"""Test Supervisor scheduler backend."""
import asyncio

from supervisor.const import CoreStates


async def test_simple_task(coresys):
    """Schedule a simple task."""
    coresys.core.state = CoreStates.RUNNING
    trigger = []

    async def test_task():
        """Test task for schedule."""
        trigger.append(True)

    coresys.scheduler.register_task(test_task, 0.1, False)
    await asyncio.sleep(0.3)

    assert len(trigger) == 1


async def test_simple_task_repeat(coresys):
    """Schedule a simple task and repeat."""
    coresys.core.state = CoreStates.RUNNING
    trigger = []

    async def test_task():
        """Test task for schedule."""
        trigger.append(True)

    coresys.scheduler.register_task(test_task, 0.1, True)
    await asyncio.sleep(0.3)

    assert len(trigger) > 1


async def test_simple_task_shutdown(coresys):
    """Schedule a simple task with shudown."""
    coresys.core.state = CoreStates.RUNNING
    trigger = []

    async def test_task():
        """Test task for schedule."""
        trigger.append(True)

    coresys.scheduler.register_task(test_task, 0.1, True)
    await asyncio.sleep(0.3)
    await coresys.scheduler.shutdown()

    assert len(trigger) > 1

    old = len(trigger)
    await asyncio.sleep(0.2)

    assert len(trigger) == old


async def test_simple_task_repeat_block(coresys):
    """Schedule a simple task with repeat and block."""
    coresys.core.state = CoreStates.RUNNING
    trigger = []

    async def test_task():
        """Test task for schedule."""
        trigger.append(True)
        await asyncio.sleep(2)

    coresys.scheduler.register_task(test_task, 0.1, True)
    await asyncio.sleep(0.3)

    assert len(trigger) == 1
    await coresys.scheduler.shutdown()
