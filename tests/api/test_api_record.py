"""Test API response recorder used for client compatibility checks."""

import json
from pathlib import Path
from unittest.mock import patch

from aiohttp.test_utils import TestClient
import pytest

from ..common import API_RECORD_DIR_ENV


async def test_api_record_writes_record(
    app_api_client_with_root: tuple[TestClient, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
):
    """Test JSON responses are recorded with route template and params."""
    api_client, root = app_api_client_with_root
    monkeypatch.setenv(API_RECORD_DIR_ENV, str(tmp_path))
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw7")

    resp = await api_client.get(
        f"{root}/does_not_exist/info", params=[("a", "1"), ("b", ""), ("a", "2")]
    )
    body = await resp.json()

    assert [path.name for path in tmp_path.iterdir()] == ["gw7.jsonl"]
    assert [
        json.loads(line)
        for line in (tmp_path / "gw7.jsonl").read_text("utf-8").splitlines()
    ] == [
        {
            "method": "GET",
            "template": f"{root}/{{app}}/info",
            "params": ["does_not_exist"],
            "query": [["a", "1"], ["b", ""], ["a", "2"]],
            "status": resp.status,
            "body": body,
            "test": request.node.nodeid,
        }
    ]


async def test_api_record_disabled(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    """Test nothing is recorded when the record directory is not set."""
    monkeypatch.delenv(API_RECORD_DIR_ENV, raising=False)

    with patch("tests.common._write_api_record") as write_record:
        resp = await api_client.get("/addons/does_not_exist/info")

    assert resp.status == 404
    write_record.assert_not_called()
