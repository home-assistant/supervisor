"""Test Docker API."""

import asyncio
from unittest.mock import ANY

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys
from supervisor.jobs.const import ATTR_IGNORE_CONDITIONS, JobCondition
from supervisor.jobs.decorator import Job


async def test_api_jobs_info(api_client: TestClient):
    """Test jobs info api."""
    resp = await api_client.get("/jobs/info")
    result = await resp.json()

    assert result["data"][ATTR_IGNORE_CONDITIONS] == []
    assert result["data"]["jobs"] == []


async def test_api_jobs_options(api_client: TestClient, coresys: CoreSys):
    """Test jobs options api."""
    resp = await api_client.post(
        "/jobs/options", json={ATTR_IGNORE_CONDITIONS: [JobCondition.HEALTHY]}
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/jobs/info")
    result = await resp.json()
    assert result["data"][ATTR_IGNORE_CONDITIONS] == [JobCondition.HEALTHY]

    assert coresys.jobs.save_data.called


async def test_api_jobs_reset(api_client: TestClient, coresys: CoreSys):
    """Test jobs reset api."""
    resp = await api_client.post(
        "/jobs/options", json={ATTR_IGNORE_CONDITIONS: [JobCondition.HEALTHY]}
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/jobs/info")
    result = await resp.json()
    assert result["data"][ATTR_IGNORE_CONDITIONS] == [JobCondition.HEALTHY]

    assert coresys.jobs.save_data.called
    assert coresys.jobs.ignore_conditions == [JobCondition.HEALTHY]

    coresys.jobs.save_data.reset_mock()
    resp = await api_client.post("/jobs/reset")
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.jobs.ignore_conditions == []
    coresys.jobs.save_data.assert_called_once()


async def test_jobs_tree_representation(api_client: TestClient, coresys: CoreSys):
    """Test jobs are correctly represented in a tree."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.event = asyncio.Event()

        @Job(name="test_jobs_tree_outer")
        async def test_jobs_tree_outer(self):
            """Outer test method."""
            coresys.jobs.current.progress = 50
            await self.test_jobs_tree_inner()

        @Job(name="test_jobs_tree_inner")
        async def test_jobs_tree_inner(self):
            """Inner test method."""
            await self.event.wait()

        @Job(name="test_jobs_tree_alt", cleanup=False)
        async def test_jobs_tree_alt(self):
            """Alternate test method."""
            coresys.jobs.current.stage = "init"
            await self.test_jobs_tree_internal()
            coresys.jobs.current.stage = "end"

        @Job(name="test_jobs_tree_internal", internal=True)
        async def test_jobs_tree_internal(self):
            """Internal test method."""
            await self.event.wait()

    test = TestClass(coresys)
    asyncio.create_task(test.test_jobs_tree_outer())
    asyncio.create_task(test.test_jobs_tree_alt())
    await asyncio.sleep(0)

    resp = await api_client.get("/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "name": "test_jobs_tree_outer",
            "reference": None,
            "uuid": ANY,
            "progress": 50,
            "stage": None,
            "done": False,
            "errors": [],
            "child_jobs": [
                {
                    "name": "test_jobs_tree_inner",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 0,
                    "stage": None,
                    "done": False,
                    "child_jobs": [],
                    "errors": [],
                },
            ],
        },
        {
            "name": "test_jobs_tree_alt",
            "reference": None,
            "uuid": ANY,
            "progress": 0,
            "stage": "init",
            "done": False,
            "child_jobs": [],
            "errors": [],
        },
    ]

    test.event.set()
    await asyncio.sleep(0)

    resp = await api_client.get("/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "name": "test_jobs_tree_alt",
            "reference": None,
            "uuid": ANY,
            "progress": 0,
            "stage": "end",
            "done": True,
            "child_jobs": [],
            "errors": [],
        },
    ]
