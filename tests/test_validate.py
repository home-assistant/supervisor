"""Test validators."""

import pytest
import voluptuous as vol

from supervisor import validate

DNS_GOOD_V4 = [
    "dns://10.0.0.1",  # random local
    "dns://254.254.254.254",  # random high numbers
    "DNS://1.1.1.1",  # cloudflare
    "dns://9.9.9.9",  # quad-9
]
DNS_GOOD_V6 = [
    "dns://2606:4700:4700::1111",  # cloudflare
    "DNS://2606:4700:4700::1001",  # cloudflare
]
DNS_BAD = ["hello world", "https://foo.bar", "", "dns://example.com"]


async def test_dns_url_v4_good():
    """Test the DNS validator with known-good ipv6 DNS URLs."""
    for url in DNS_GOOD_V4:
        assert validate.dns_url(url)


def test_dns_url_v6_good():
    """Test the DNS validator with known-good ipv6 DNS URLs."""
    for url in DNS_GOOD_V6:
        assert validate.dns_url(url)


def test_dns_server_list_v4():
    """Test a list with v4 addresses."""
    assert validate.dns_server_list(DNS_GOOD_V4)


def test_dns_server_list_v6():
    """Test a list with v6 addresses."""
    assert validate.dns_server_list(DNS_GOOD_V6)


def test_dns_server_list_combined():
    """Test a list with both v4 and v6 addresses."""
    combined = DNS_GOOD_V4 + DNS_GOOD_V6
    # test the matches
    assert validate.dns_server_list(combined)
    # test max_length is OK still
    assert validate.dns_server_list(combined)
    # test that it failed when the list is too long
    with pytest.raises(vol.error.Invalid):
        validate.dns_server_list(combined + combined + combined + combined)


def test_dns_server_list_bad():
    """Test the bad list."""
    # test the matches
    with pytest.raises(vol.error.Invalid):
        assert validate.dns_server_list(DNS_BAD)


def test_dns_server_list_bad_combined():
    """Test the bad list, combined with the good."""
    combined = DNS_GOOD_V4 + DNS_GOOD_V6 + DNS_BAD

    with pytest.raises(vol.error.Invalid):
        # bad list
        assert validate.dns_server_list(combined)


def test_version_complex():
    """Test version simple with good version."""
    for version in (
        "landingpage",
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
