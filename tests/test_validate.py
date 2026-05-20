"""Test validators."""

import pytest
import voluptuous as vol

from supervisor import validate
from supervisor.validate import SCHEMA_SUPERVISOR_CONFIG

DNS_GOOD_V4 = [
    "dns://10.0.0.1",  # random local
    "dns://254.254.254.254",  # random high numbers
    "DNS://1.1.1.1",  # cloudflare
    "dns://9.9.9.9",  # quad-9
]
DNS_V6_UNSUPPORTED = [
    "dns://2606:4700:4700::1111",  # cloudflare
    "DNS://2606:4700:4700::1001",  # cloudflare
]
DNS_BAD = ["hello world", "https://foo.bar", "", "dns://example.com"]
IMAGE_NAME_GOOD = [
    "ghcr.io/home-assistant/{machine}-homeassistant",
    "ghcr.io/home-assistant/{arch}-homeassistant",
    "homeassistant/{arch}-homeassistant",
    "doocker.io/homeassistant/{arch}-homeassistant",
    "ghcr.io/home-assistant/amd64-homeassistant",
    "homeassistant/amd64-homeassistant",
    "ttl.sh/homeassistant",
    "myreg.local:8080/homeassistant",
    "localhost/myimage",
    "localhost:5000/myimage",
    "127.0.0.1/myimage",
    "127.0.0.1:5000/org/myimage",
    "[::1]:5000/myimage",
    "dockeruser/nice-app-1.2",
    "ghcr.io/blakeblackshear/frigate",
]
IMAGE_NAME_BAD = [
    "ghcr.io/home-assistant/homeassistant:123",
    "ghcr.io/blakeblackshear/frigate:stable-rocm",
    ".ghcr.io/home-assistant/homeassistant",
    "HOMEASSISTANT/homeassistant",
    "homeassistant/HOMEASSISTANT",
    "homeassistant/_homeassistant",
    "homeassistant/-homeassistant",
    "GHCR.IO/home-assistant/homeassistant",
]


def test_dns_url_v4_good():
    """Test the DNS validator with known-good IPv4 DNS URLs."""
    for url in DNS_GOOD_V4:
        assert validate.dns_url(url)


@pytest.mark.parametrize("url", DNS_V6_UNSUPPORTED)
def test_dns_url_v6_rejected(url: str):
    """Test the DNS validator rejects well-formed IPv6 DNS URLs.

    IPv6 is currently not supported for DNS because it doesn't work with
    the Docker network.
    """
    with pytest.raises(vol.error.Invalid):
        validate.dns_url(url)


def test_dns_server_list_v4():
    """Test a list with v4 addresses."""
    assert validate.dns_server_list(DNS_GOOD_V4)


def test_dns_server_list_v6_rejected():
    """Test that lists of IPv6 DNS URLs are rejected."""
    with pytest.raises(vol.error.Invalid):
        assert validate.dns_server_list(DNS_V6_UNSUPPORTED)


def test_dns_server_list_combined():
    """Test a list with both v4 and v6 addresses."""
    combined = DNS_GOOD_V4 + DNS_V6_UNSUPPORTED
    # test the matches
    with pytest.raises(vol.error.Invalid):
        validate.dns_server_list(combined)
    # test max_length is OK still
    with pytest.raises(vol.error.Invalid):
        validate.dns_server_list(combined)
    # test that it fails when the list is too long
    with pytest.raises(vol.error.Invalid):
        validate.dns_server_list(combined + combined + combined + combined)


def test_dns_server_list_bad():
    """Test the bad list."""
    # test the matches
    with pytest.raises(vol.error.Invalid):
        assert validate.dns_server_list(DNS_BAD)


def test_dns_server_list_bad_combined():
    """Test the bad list, combined with the good."""
    combined = DNS_GOOD_V4 + DNS_V6_UNSUPPORTED + DNS_BAD

    with pytest.raises(vol.error.Invalid):
        # bad list
        assert validate.dns_server_list(combined)


def test_image_name_good():
    """Test container image names validator with known-good image names."""
    for image_name in IMAGE_NAME_GOOD:
        assert validate.docker_image(image_name)


def test_image_name_bad():
    """Test container image names validator with known-bad image names."""
    for image_name in IMAGE_NAME_BAD:
        with pytest.raises(vol.error.Invalid):
            assert validate.docker_image(image_name)


def test_version_complex():
    """Test version simple with good version."""
    for version in (
        "landingpage",
        "dev",
        "1c002dd",
        "1.1.1",
        "1.0",
        "0.150.1",
        "0.150.1b1",
        "0.150.1.dev20200715",
        "1",
        "alpine-5.4",
        1,
        1.1,
    ):
        assert validate.version_tag(version) == str(version)

    assert validate.version_tag(None) is None


def test_supervisor_config_migration_addons_custom_list():
    """Test that old 'addons_custom_list' key is migrated to 'apps_custom_list'."""
    result = SCHEMA_SUPERVISOR_CONFIG(
        {"addons_custom_list": ["https://example.com/repo"]}
    )
    assert result["apps_custom_list"] == ["https://example.com/repo"]
    assert "addons_custom_list" not in result


def test_supervisor_config_apps_custom_list_unchanged():
    """Test that new 'apps_custom_list' key passes through unchanged."""
    result = SCHEMA_SUPERVISOR_CONFIG(
        {"apps_custom_list": ["https://example.com/repo"]}
    )
    assert result["apps_custom_list"] == ["https://example.com/repo"]
