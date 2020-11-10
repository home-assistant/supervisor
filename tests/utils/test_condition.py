"""Test the condition decorators."""
# pylint: disable=protected-access,import-error
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.utils.condition import Condition


async def test_healthy(coresys: CoreSys):
    """Test the healty decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Condition.healthy
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.core.healthy = False
    assert not await test.execute()


async def test_internet(coresys: CoreSys):
    """Test the internet decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Condition.internet
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.core.internet._connected = False
    assert not await test.execute()


async def test_free_space(coresys: CoreSys):
    """Test the free_space decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Condition.free_space
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    with patch("shutil.disk_usage", return_value=(42, 42, (1024.0 ** 3))):
        assert await test.execute()

    with patch("shutil.disk_usage", return_value=(42, 42, (512.0 ** 3))):
        assert not await test.execute()
