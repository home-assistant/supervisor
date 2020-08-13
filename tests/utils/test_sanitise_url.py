"""Test supervisor.utils.sanitise_url."""
from supervisor.utils import sanitise_url


def test_sanitise_url():
    """Test supervisor.utils.sanitise_url."""
    assert sanitise_url("test") == "test"
    assert sanitise_url("http://my.duckdns.org") == "http://example.com"
    assert sanitise_url("http://my.duckdns.org/test") == "http://example.com/test"
