"""Test apps API network isolation options."""

from ipaddress import IPv4Address
from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.apps.app import App
from supervisor.const import ATTR_HOST_NETWORK
from supervisor.coresys import CoreSys
from supervisor.docker.const import ExternalNetworkDriver, NetworkIsolationConfig
from supervisor.docker.manager import DockerInfo

from ..const import TEST_ADDON_SLUG, TEST_INTERFACE_ETH_NAME


@pytest.fixture(name="docker_supports_isolation")
def fixture_docker_supports_isolation(coresys: CoreSys) -> None:
    """Set a Docker version that supports network isolation."""
    coresys.docker._info = DockerInfo(  # pylint: disable=protected-access
        AwesomeVersion("28.0.0"), "overlay2", "journald", "2", False
    )


async def test_options_requires_host_network(
    app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
):
    """Test isolation cannot be assigned to an app without host networking."""
    client, root = app_api_client_with_root

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={
            "network_isolation": {
                "interface": TEST_INTERFACE_ETH_NAME,
                "ipv4": "192.168.2.50",
            }
        },
    )

    assert resp.status == 400
    body = await resp.json()
    assert "host networking" in body["message"]
    assert install_app_ssh.network_isolation is None


async def test_options_requires_docker_version(
    app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
):
    """Test isolation requires a recent Docker engine."""
    client, root = app_api_client_with_root
    install_app_ssh.data[ATTR_HOST_NETWORK] = True

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={
            "network_isolation": {
                "interface": TEST_INTERFACE_ETH_NAME,
                "ipv4": "192.168.2.50",
            }
        },
    )

    assert resp.status == 400
    body = await resp.json()
    assert "requires Docker 28.0.0" in body["message"]


@pytest.mark.usefixtures("docker_supports_isolation")
async def test_options_set_and_clear(
    app_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
):
    """Test assigning and clearing network isolation."""
    client, root = app_api_client_with_root
    install_app_ssh.data[ATTR_HOST_NETWORK] = True

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={
            "network_isolation": {
                "interface": TEST_INTERFACE_ETH_NAME,
                "ipv4": "192.168.2.50",
            }
        },
    )

    assert resp.status == 200
    assert install_app_ssh.network_isolation == NetworkIsolationConfig(
        driver=ExternalNetworkDriver.MACVLAN,
        interface=TEST_INTERFACE_ETH_NAME,
        ipv4=IPv4Address("192.168.2.50"),
    )

    resp = await client.get(f"{root}/{TEST_ADDON_SLUG}/info")
    result = await resp.json()
    assert result["data"]["network_isolation"] == {
        "driver": "macvlan",
        "interface": TEST_INTERFACE_ETH_NAME,
        "ipv4": "192.168.2.50",
    }
    assert result["data"]["network_isolation_available"] is True
    # Container is not running with the endpoint attached
    assert result["data"]["network_isolation_mac"] is None

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options", json={"network_isolation": None}
    )
    assert resp.status == 200
    assert install_app_ssh.network_isolation is None


@pytest.mark.usefixtures("docker_supports_isolation")
@pytest.mark.parametrize(
    ("address", "reason"),
    [
        ("10.0.0.5", "not a usable address"),
        ("192.168.2.255", "not a usable address"),
        ("192.168.2.1", "already used by the host"),
        ("192.168.2.148", "already used by the host"),
    ],
)
async def test_options_invalid_address(
    app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
    address: str,
    reason: str,
):
    """Test invalid IP addresses are rejected."""
    client, root = app_api_client_with_root
    install_app_ssh.data[ATTR_HOST_NETWORK] = True

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={
            "network_isolation": {
                "interface": TEST_INTERFACE_ETH_NAME,
                "ipv4": address,
            }
        },
    )

    assert resp.status == 400
    body = await resp.json()
    assert reason in body["message"]
    assert install_app_ssh.network_isolation is None


@pytest.mark.usefixtures("docker_supports_isolation")
async def test_options_invalid_interface(
    app_api_client_with_root: tuple[TestClient, str],
    install_app_ssh: App,
):
    """Test unusable host interfaces are rejected."""
    client, root = app_api_client_with_root
    install_app_ssh.data[ATTR_HOST_NETWORK] = True

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={"network_isolation": {"interface": "eth42", "ipv4": "192.168.2.50"}},
    )

    assert resp.status == 400
    body = await resp.json()
    assert "interface not found" in body["message"]


@pytest.mark.usefixtures("docker_supports_isolation")
async def test_options_address_conflict(
    app_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
):
    """Test IP addresses already assigned to another app are rejected."""
    client, root = app_api_client_with_root
    install_app_ssh.data[ATTR_HOST_NETWORK] = True

    other = MagicMock(spec=App)
    other.slug = "other_addon"
    other.network_isolation = NetworkIsolationConfig(
        driver=ExternalNetworkDriver.MACVLAN,
        interface=TEST_INTERFACE_ETH_NAME,
        ipv4=IPv4Address("192.168.2.50"),
    )
    coresys.apps.local[other.slug] = other

    resp = await client.post(
        f"{root}/{TEST_ADDON_SLUG}/options",
        json={
            "network_isolation": {
                "interface": TEST_INTERFACE_ETH_NAME,
                "ipv4": "192.168.2.50",
            }
        },
    )

    assert resp.status == 400
    body = await resp.json()
    assert "already assigned to app other_addon" in body["message"]
