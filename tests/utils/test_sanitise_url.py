"""Test supervisor.utils.sanitize_url."""
from supervisor.utils.filter import sanitize_url


def test_sanitize_url():
    """Test supervisor.utils.sanitize_url."""
    assert sanitize_url("test") == "test"
    assert sanitize_url("http://my.duckdns.org") == "http://example.com"
    assert sanitize_url("http://my.duckdns.org/test") == "http://example.com/test"
