"""Test supervisor.utils.sanitize_url."""

from supervisor.misc.filter import sanitize_host, sanitize_url


def test_sanitize_host():
    """Test supervisor.utils.sanitize_host."""
    assert sanitize_host("my.duckdns.org") == "sanitized-host.invalid"


def test_sanitize_url():
    """Test supervisor.utils.sanitize_url."""
    assert sanitize_url("test") == "test"
    assert sanitize_url("http://my.duckdns.org") == "http://sanitized-host.invalid"
    assert (
        sanitize_url("http://my.duckdns.org/test")
        == "http://sanitized-host.invalid/test"
    )
    assert (
        sanitize_url("http://my.duckdns.org/test?test=123")
        == "http://sanitized-host.invalid/test?test=123"
    )
