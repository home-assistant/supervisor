"""Test validators."""

import pytest
import voluptuous.error

import supervisor.validate

GOOD_V4 = [
    "dns://10.0.0.1",  # random local
    "dns://254.254.254.254",  # random high numbers
    "DNS://1.1.1.1",  # cloudflare
    "dns://9.9.9.9",  # quad-9
]
GOOD_V6 = [
    "dns://2606:4700:4700::1111",  # cloudflare
    "DNS://2606:4700:4700::1001",  # cloudflare
]
BAD = ["hello world", "https://foo.bar", "", "dns://example.com"]


async def test_dns_url_v4_good():
    """Test the DNS validator with known-good ipv6 DNS URLs."""
    for url in GOOD_V4:
        assert supervisor.validate.dns_url(url)


async def test_dns_url_v6_good():
    """Test the DNS validator with known-good ipv6 DNS URLs."""
    for url in GOOD_V6:
        assert supervisor.validate.dns_url(url)


async def test_dns_server_list_v4():
    """Test a list with v4 addresses."""
    assert supervisor.validate.dns_server_list(GOOD_V4)


async def test_dns_server_list_v6():
    """Test a list with v6 addresses."""
    assert supervisor.validate.dns_server_list(GOOD_V6)


async def test_dns_server_list_combined():
    """Test a list with both v4 and v6 addresses."""
    combined = GOOD_V4 + GOOD_V6
    # test the matches
    assert supervisor.validate.dns_server_list(combined)
    # test max_length is OK still
    assert supervisor.validate.dns_server_list(combined)
    # test that it fails when the list is too long
    with pytest.raises(voluptuous.error.Invalid):
        supervisor.validate.dns_server_list(combined + combined + combined + combined)


async def test_dns_server_list_bad():
    """Test the bad list."""
    # test the matches
    with pytest.raises(voluptuous.error.Invalid):
        assert supervisor.validate.dns_server_list(BAD)


async def test_dns_server_list_bad_combined():
    """Test the bad list, combined with the good."""
    combined = GOOD_V4 + GOOD_V6 + BAD

    with pytest.raises(voluptuous.error.Invalid):
        # bad list
        assert supervisor.validate.dns_server_list(combined)
