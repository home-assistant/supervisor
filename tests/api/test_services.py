"""Test services API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import App
from supervisor.const import ATTR_SERVICES
from supervisor.coresys import CoreSys

from tests.const import TEST_ADDON_SLUG


@pytest.mark.parametrize(
    ("method", "url"),
    [("get", "/services/bad"), ("post", "/services/bad"), ("delete", "/services/bad")],
)
async def test_service_not_found(api_client: TestClient, method: str, url: str):
    """Test service not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Service does not exist"


@pytest.mark.parametrize("service", ["mqtt", "mysql"])
@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_set_service_already_provided(
    api_client: TestClient,
    coresys: CoreSys,
    install_app_ssh: App,
    service: str,
):
    """Test setting service data when another app already provides it returns 409."""
    install_app_ssh.data[ATTR_SERVICES] = [f"{service}:provide"]
    await coresys.services.load()

    coresys.services.data._data[service].update(  # pylint: disable=protected-access
        {"host": "existing", "port": 1883, "addon": "core_mosquitto"}
    )

    resp = await api_client.post(
        f"/services/{service}",
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
@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_del_service_not_provided(
    api_client: TestClient,
    coresys: CoreSys,
    install_app_ssh: App,
    service: str,
):
    """Test deleting service data when no app provides it returns 404."""
    install_app_ssh.data[ATTR_SERVICES] = [f"{service}:provide"]
    await coresys.services.load()

    coresys.services.data._data[service].clear()  # pylint: disable=protected-access

    resp = await api_client.delete(f"/services/{service}")
    assert resp.status == 404
    body = await resp.json()
    assert body["result"] == "error"
    assert body["error_key"] == "service_not_provided_error"
    assert body["extra_fields"] == {"service": service}
    assert (
        body["message"] == f"The {service} service is not currently provided by any app"
    )
