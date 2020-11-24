"""Test Docker API."""
import pytest

from supervisor.jobs.const import ATTR_IGNORE_CONDITIONS, JobCondition


@pytest.mark.asyncio
async def test_api_jobs_info(api_client):
    """Test jobs info api."""
    resp = await api_client.get("/jobs/info")
    result = await resp.json()

    assert result["data"][ATTR_IGNORE_CONDITIONS] == []


@pytest.mark.asyncio
async def test_api_jobs_options(api_client, coresys):
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


@pytest.mark.asyncio
async def test_api_jobs_reset(api_client, coresys):
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

    resp = await api_client.post("/jobs/reset")
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.jobs.ignore_conditions == []
