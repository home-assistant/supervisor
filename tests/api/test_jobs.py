"""Test Docker API."""

import asyncio
from unittest.mock import ANY, AsyncMock

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import SupervisorError
from supervisor.jobs.const import ATTR_IGNORE_CONDITIONS, JobCondition
from supervisor.jobs.decorator import Job


class _JobsTreeTestHelper:
    """Helper class for test_jobs_tree_representation."""

    def __init__(self, coresys: CoreSys):
        """Initialize the test class."""
        self.coresys = coresys
        self.event = asyncio.Event()

    @Job(name="test_jobs_tree_outer")
    async def test_jobs_tree_outer(self):
        """Outer test method."""
        self.coresys.jobs.current.progress = 50
        await self.test_jobs_tree_inner()

    @Job(name="test_jobs_tree_inner")
    async def test_jobs_tree_inner(self):
        """Inner test method."""
        await self.event.wait()

    @Job(name="test_jobs_tree_alt", cleanup=False)
    async def test_jobs_tree_alt(self):
        """Alternate test method."""
        self.coresys.jobs.current.stage = "init"
        await self.test_jobs_tree_internal()
        self.coresys.jobs.current.stage = "end"

    @Job(name="test_jobs_tree_internal", internal=True)
    async def test_jobs_tree_internal(self):
        """Internal test method."""
        await self.event.wait()


class _JobManualCleanupTestHelper:
    """Helper class for test_job_manual_cleanup."""

    def __init__(self, coresys: CoreSys):
        """Initialize the test class."""
        self.coresys = coresys
        self.event = asyncio.Event()
        self.job_id: str | None = None

    @Job(name="test_job_manual_cleanup", cleanup=False)
    async def test_job_manual_cleanup(self) -> None:
        """Job that requires manual cleanup."""
        self.job_id = self.coresys.jobs.current.uuid
        await self.event.wait()


class _JobsSortedTestHelper:
    """Helper class for test_jobs_sorted."""

    def __init__(self, coresys: CoreSys):
        """Initialize the test class."""
        self.coresys = coresys

    @Job(name="test_jobs_sorted_1", cleanup=False)
    async def test_jobs_sorted_1(self):
        """Sorted test method 1."""
        await self.test_jobs_sorted_inner_1()
        await self.test_jobs_sorted_inner_2()

    @Job(name="test_jobs_sorted_inner_1", cleanup=False)
    async def test_jobs_sorted_inner_1(self):
        """Sorted test inner method 1."""

    @Job(name="test_jobs_sorted_inner_2", cleanup=False)
    async def test_jobs_sorted_inner_2(self):
        """Sorted test inner method 2."""

    @Job(name="test_jobs_sorted_2", cleanup=False)
    async def test_jobs_sorted_2(self):
        """Sorted test method 2."""


class _JobWithErrorTestHelper:
    """Helper class for test_job_with_error."""

    def __init__(self, coresys: CoreSys):
        """Initialize the test class."""
        self.coresys = coresys

    @Job(name="test_jobs_api_error_outer", cleanup=False)
    async def test_jobs_api_error_outer(self):
        """Error test outer method."""
        self.coresys.jobs.current.stage = "test"
        await self.test_jobs_api_error_inner()

    @Job(name="test_jobs_api_error_inner", cleanup=False)
    async def test_jobs_api_error_inner(self):
        """Error test inner method."""
        raise SupervisorError("bad")


async def test_api_jobs_info(api_client_with_prefix: tuple[TestClient, str]):
    """Test jobs info api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()

    assert result["data"][ATTR_IGNORE_CONDITIONS] == []
    assert result["data"]["jobs"] == []


async def test_api_jobs_options(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test jobs options api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/jobs/options", json={ATTR_IGNORE_CONDITIONS: [JobCondition.HEALTHY]}
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"][ATTR_IGNORE_CONDITIONS] == [JobCondition.HEALTHY]

    assert coresys.jobs.save_data.called


async def test_api_jobs_reset(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test jobs reset api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/jobs/options", json={ATTR_IGNORE_CONDITIONS: [JobCondition.HEALTHY]}
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"][ATTR_IGNORE_CONDITIONS] == [JobCondition.HEALTHY]

    assert coresys.jobs.save_data.called
    assert coresys.jobs.ignore_conditions == [JobCondition.HEALTHY]

    coresys.jobs.save_data.reset_mock()
    resp = await api_client.post(f"{prefix}/jobs/reset")
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.jobs.ignore_conditions == []
    coresys.jobs.save_data.assert_called_once()


async def test_jobs_tree_representation(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test jobs are correctly represented in a tree."""
    api_client, prefix = api_client_with_prefix
    test = _JobsTreeTestHelper(coresys)
    outer_task = asyncio.create_task(test.test_jobs_tree_outer())
    alt_task = asyncio.create_task(test.test_jobs_tree_alt())
    await asyncio.sleep(0)

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "created": ANY,
            "name": "test_jobs_tree_alt",
            "reference": None,
            "uuid": ANY,
            "progress": 0,
            "stage": "init",
            "done": False,
            "child_jobs": [],
            "errors": [],
            "extra": None,
        },
        {
            "created": ANY,
            "name": "test_jobs_tree_outer",
            "reference": None,
            "uuid": ANY,
            "progress": 50,
            "stage": None,
            "done": False,
            "errors": [],
            "extra": None,
            "child_jobs": [
                {
                    "created": ANY,
                    "name": "test_jobs_tree_inner",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 0,
                    "stage": None,
                    "done": False,
                    "child_jobs": [],
                    "errors": [],
                    "extra": None,
                },
            ],
        },
    ]

    test.event.set()
    await asyncio.sleep(0)

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "created": ANY,
            "name": "test_jobs_tree_alt",
            "reference": None,
            "uuid": ANY,
            "progress": 100,
            "stage": "end",
            "done": True,
            "child_jobs": [],
            "errors": [],
            "extra": None,
        },
    ]
    await outer_task
    await alt_task


async def test_job_manual_cleanup(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test manually cleaning up a job via API."""
    api_client, prefix = api_client_with_prefix
    test = _JobManualCleanupTestHelper(coresys)
    task = asyncio.create_task(test.test_job_manual_cleanup())
    await asyncio.sleep(0)

    # Check the job details
    resp = await api_client.get(f"{prefix}/jobs/{test.job_id}")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"] == {
        "created": ANY,
        "name": "test_job_manual_cleanup",
        "reference": None,
        "uuid": test.job_id,
        "progress": 0,
        "stage": None,
        "done": False,
        "child_jobs": [],
        "errors": [],
        "extra": None,
    }

    # Only done jobs can be deleted via API
    resp = await api_client.delete(f"{prefix}/jobs/{test.job_id}")
    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == f"Job {test.job_id} is not done!"

    # Let the job finish
    test.event.set()
    await task

    # Check that it is now done
    resp = await api_client.get(f"{prefix}/jobs/{test.job_id}")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["done"] is True

    # Delete it
    resp = await api_client.delete(f"{prefix}/jobs/{test.job_id}")
    assert resp.status == 200

    # Confirm it no longer exists
    resp = await api_client.get(f"{prefix}/jobs/{test.job_id}")
    assert resp.status == 404
    result = await resp.json()
    assert result["message"] == "Job does not exist"


@pytest.mark.parametrize(
    ("method", "url"),
    [("get", "/jobs/bad"), ("delete", "/jobs/bad")],
)
async def test_job_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test job not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Job does not exist"


async def test_jobs_sorted(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test jobs are sorted by datetime in results."""
    api_client, prefix = api_client_with_prefix
    test = _JobsSortedTestHelper(coresys)
    await test.test_jobs_sorted_1()
    await test.test_jobs_sorted_2()

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "created": ANY,
            "name": "test_jobs_sorted_2",
            "reference": None,
            "uuid": ANY,
            "progress": 100,
            "stage": None,
            "done": True,
            "errors": [],
            "child_jobs": [],
            "extra": None,
        },
        {
            "created": ANY,
            "name": "test_jobs_sorted_1",
            "reference": None,
            "uuid": ANY,
            "progress": 100,
            "stage": None,
            "done": True,
            "errors": [],
            "extra": None,
            "child_jobs": [
                {
                    "created": ANY,
                    "name": "test_jobs_sorted_inner_1",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 100,
                    "stage": None,
                    "done": True,
                    "errors": [],
                    "child_jobs": [],
                    "extra": None,
                },
                {
                    "created": ANY,
                    "name": "test_jobs_sorted_inner_2",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 100,
                    "stage": None,
                    "done": True,
                    "errors": [],
                    "child_jobs": [],
                    "extra": None,
                },
            ],
        },
    ]


async def test_job_with_error(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
):
    """Test job output with an error."""
    api_client, prefix = api_client_with_prefix
    test = _JobWithErrorTestHelper(coresys)
    with pytest.raises(SupervisorError):
        await test.test_jobs_api_error_outer()

    resp = await api_client.get(f"{prefix}/jobs/info")
    result = await resp.json()
    assert result["data"]["jobs"] == [
        {
            "created": ANY,
            "name": "test_jobs_api_error_outer",
            "reference": None,
            "uuid": ANY,
            "progress": 0,
            "stage": "test",
            "done": True,
            "extra": None,
            "errors": [
                {
                    "type": "SupervisorError",
                    "message": "bad",
                    "stage": "test",
                    "error_key": None,
                    "extra_fields": None,
                }
            ],
            "child_jobs": [
                {
                    "created": ANY,
                    "name": "test_jobs_api_error_inner",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 0,
                    "stage": None,
                    "done": True,
                    "extra": None,
                    "errors": [
                        {
                            "type": "SupervisorError",
                            "message": "bad",
                            "stage": None,
                            "error_key": None,
                            "extra_fields": None,
                        }
                    ],
                    "child_jobs": [],
                },
            ],
        },
    ]


async def test_api_jobs_legacy_name_compatibility(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
):
    """Test V1 API maps renamed jobs to legacy names while V2 uses new names."""
    api_client, prefix = api_client_with_prefix
    expected_name = "app_manager_update" if prefix else "addon_manager_update"
    job = coresys.jobs.new_job("app_manager_update", reference="local_example")
    job.stage = "update"
    job.progress = 50
    with job.start():
        pass

    resp = await api_client.get(f"{prefix}/jobs/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["jobs"][0]["name"] == expected_name

    resp = await api_client.get(f"{prefix}/jobs/{job.uuid}")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["name"] == expected_name

    # Websocket events always use the legacy names Core and frontend expect
    job_events = [
        evt.args[0]["data"]["data"]
        for evt in ha_ws_client.async_send_command.call_args_list
        if "data" in evt.args[0] and evt.args[0]["data"]["event"] == "job"
    ]
    assert any(job_event["name"] == "addon_manager_update" for job_event in job_events)
    assert not any(
        job_event["name"] == "app_manager_update" for job_event in job_events
    )
