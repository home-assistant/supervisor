"""Test panel API."""

from pathlib import Path

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys

PANEL_PATH = Path(__file__).parent.parent.parent.joinpath("supervisor/api/panel")


@pytest.mark.parametrize(
    "filename", ["entrypoint.js", "entrypoint.js.br", "entrypoint.js.gz"]
)
async def test_frontend_files(api_client: TestClient, coresys: CoreSys, filename: str):
    """Test frontend files served up correctly."""
    resp = await api_client.get(f"/app/{filename}")
    assert resp.status == 200

    body = await resp.read()
    file_bytes = await coresys.run_in_executor(PANEL_PATH.joinpath(filename).read_bytes)
    assert body == file_bytes
