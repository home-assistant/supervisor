"""Test API response recorder used for client compatibility checks."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.apps.app import App
from supervisor.const import ATTR_ACCESS_TOKEN
from supervisor.homeassistant.api import HomeAssistantAPI

from ..common import API_RECORD_DIR_ENV, API_RECORD_PASSTHROUGH


async def test_api_record_writes_record(
    app_api_client_with_root: tuple[TestClient, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
):
    """Test JSON responses are recorded with route template and params."""
    api_client, root = app_api_client_with_root
    record_dir = tmp_path / "records"
    monkeypatch.setenv(API_RECORD_DIR_ENV, str(record_dir))
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw7")

    resp = await api_client.get(
        f"{root}/does_not_exist/info", params=[("a", "1"), ("b", ""), ("a", "2")]
    )
    body = await resp.json()

    assert [path.name for path in record_dir.iterdir()] == ["gw7.jsonl"]
    assert [
        json.loads(line)
        for line in (record_dir / "gw7.jsonl").read_text("utf-8").splitlines()
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


async def test_api_record_skips_core_proxy(
    api_client: TestClient,
    install_app_example: App,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test Core API proxy responses are not recorded, even if envelope shaped."""
    monkeypatch.setenv(API_RECORD_DIR_ENV, str(tmp_path))
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw7")
    install_app_example.persist[ATTR_ACCESS_TOKEN] = "abc123"
    install_app_example.data["homeassistant_api"] = True

    with patch.object(HomeAssistantAPI, "make_request") as make_request:
        core_response = AsyncMock()
        core_response.status = 200
        core_response.content_type = "application/json"
        core_response.read.return_value = b'{"result": "ok"}'
        make_request.return_value.__aenter__.return_value = core_response

        resp = await api_client.post(
            "/core/api/services/light/turn_on",
            headers={"Authorization": "Bearer abc123"},
            json={},
        )
    assert resp.status == 200
    assert await resp.json() == {"result": "ok"}

    resp = await api_client.get("/core/info")
    assert resp.status == 200

    assert [
        json.loads(line)["template"]
        for line in (tmp_path / "gw7.jsonl").read_text("utf-8").splitlines()
    ] == ["/core/info"]


@pytest.mark.parametrize(
    ("template", "passthrough"),
    [
        *(
            pytest.param(template, True, id=template)
            for template in (
                "/core/api/",
                "/core/api/{path}",
                "/core/api/stream",
                "/core/api/websocket",
                "/core/websocket",
                "/homeassistant/api/",
                "/homeassistant/api/{path}",
                "/homeassistant/websocket",
                "/ingress/{token}/{path}",
                "/v2/core/api/{path}",
                "/v2/core/websocket",
                "/v2/ingress/{token}/{path}",
            )
        ),
        *(
            pytest.param(template, False, id=template)
            for template in (
                "/core/info",
                "/homeassistant/info",
                "/ingress/panels",
                "/ingress/session",
                "/v2/core/stats",
                "/v2/ingress/validate_session",
            )
        ),
    ],
)
def test_api_record_passthrough(template: str, passthrough: bool):
    """Test Core API proxy and ingress routes are the passthrough routes."""
    assert bool(API_RECORD_PASSTHROUGH.match(template)) is passthrough
