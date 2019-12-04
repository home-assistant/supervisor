"""Test validators."""

import hassio.validate
import voluptuous.error
import pytest

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
    """ tests the DNS validator with known-good ipv6 DNS URLs """
    for url in GOOD_V4:
        assert hassio.validate.dns_url(url)


async def test_dns_url_v6_good():
    """ tests the DNS validator with known-good ipv6 DNS URLs """
    for url in GOOD_V6:
        assert hassio.validate.dns_url(url)


async def test_dns_server_list_v4():
    """ test a list with v4 addresses """
    assert hassio.validate.DNS_SERVER_LIST(GOOD_V4)
    assert hassio.validate.DNS_SERVER_LIST(GOOD_V4)


async def test_dns_server_list_v6():
    """ test a list with v6 addresses """
    assert hassio.validate.DNS_SERVER_LIST(GOOD_V6)
    assert hassio.validate.DNS_SERVER_LIST(GOOD_V6, max_length=len(GOOD_V6))


async def test_dns_server_list_combined():
    """ test a list with both v4 and v6 addresses """
    combined = GOOD_V4 + GOOD_V6
    # test the matches
    assert hassio.validate.DNS_SERVER_LIST(combined)
    # test max_length is OK still
    assert hassio.validateDNS_SERVER_LIST(combined)
    # test that it fails when the list is too long
    with pytest.raises(voluptuous.error.Invalid):
        hassio.validate.dns_server_list(combined + combined + combined + combined)


async def test_dns_server_list_bad():
    """ test the bad list """
    # test the matches
    with pytest.raises(voluptuous.error.Invalid):
        assert hassio.validate.dns_server_list(BAD)


async def test_dns_server_list_bad_combined():
    """ test the bad list, combined with the good """
    combined = GOOD_V4 + GOOD_V6 + BAD

    with pytest.raises(voluptuous.error.Invalid):
        # bad list
        assert hassio.validate.dns_server_list(combined)
