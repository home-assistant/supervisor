"""Test services API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.apps.app import App
from supervisor.const import ATTR_SERVICES
from supervisor.coresys import CoreSys


@pytest.mark.parametrize(
    ("method", "url"),
    [("get", "/services/bad"), ("post", "/services/bad"), ("delete", "/services/bad")],
)
async def test_service_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test service not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Service does not exist"


@pytest.mark.parametrize("service", ["mqtt", "mysql"])
async def test_set_service_already_provided(
    app_api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
    service: str,
):
    """Test setting service data when another app already provides it returns 409."""
    api_client, prefix = app_api_client_with_prefix
    install_app_ssh.data[ATTR_SERVICES] = [f"{service}:provide"]
    await coresys.services.load()

    coresys.services.data._data[service].update(  # pylint: disable=protected-access
        {"host": "existing", "port": 1883, "app": "core_mosquitto"}
    )

    resp = await api_client.post(
        f"{prefix}/services/{service}",
        json={"host": "new.example.com", "port": 1883},
    )
    assert resp.status == 409
    body = await resp.json()
    assert body["result"] == "error"
    assert body["error_key"] == "service_already_provided_error"
    assert body["extra_fields"] == {"service": service, "app": "core_mosquitto"}
    assert (
        body["message"]
        == f"The {service} service is already provided by core_mosquitto"
    )


@pytest.mark.parametrize("service", ["mqtt", "mysql"])
async def test_del_service_not_provided(
    app_api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
    service: str,
):
    """Test deleting service data when no app provides it returns 404."""
    api_client, prefix = app_api_client_with_prefix
    install_app_ssh.data[ATTR_SERVICES] = [f"{service}:provide"]
    await coresys.services.load()

    coresys.services.data._data[service].clear()  # pylint: disable=protected-access

    resp = await api_client.delete(f"{prefix}/services/{service}")
    assert resp.status == 404
    body = await resp.json()
    assert body["result"] == "error"
    assert body["error_key"] == "service_not_provided_error"
    assert body["extra_fields"] == {"service": service}
    assert (
        body["message"] == f"The {service} service is not currently provided by any app"
    )


@pytest.mark.parametrize("service", ["mqtt", "mysql"])
async def test_get_service_v1_v2_keys(
    app_api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
    service: str,
):
    """Test GET /services/{service} returns 'addon' key on V1 and 'app' key on V2."""
    api_client, prefix = app_api_client_with_prefix

    install_app_ssh.data[ATTR_SERVICES] = [f"{service}:provide"]
    await coresys.services.load()

    coresys.services.data._data[service].update(  # pylint: disable=protected-access
        {"host": "existing.local", "port": 1883, "app": "core_mosquitto"}
    )

    resp = await api_client.get(f"{prefix}/services/{service}")
    assert resp.status == 200
    body = await resp.json()

    app_key = "app" if prefix == "/v2" else "addon"
    absent_key = "addon" if prefix == "/v2" else "app"
    assert body["data"][app_key] == "core_mosquitto"
    assert absent_key not in body["data"]
