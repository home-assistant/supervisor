"""Test supervisor.utils.sanitize_url."""

from supervisor.misc.filter import sanitize_host, sanitize_url, sanitize_url_credentials


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


def test_sanitize_url_credentials():
    """Test supervisor.misc.filter.sanitize_url_credentials."""
    assert sanitize_url_credentials("test") == "test"
    assert (
        sanitize_url_credentials(
            "https://x-access-token:github_pat_secret@github.com/example/repo"
        )
        == "https://github.com/example/repo"
    )
    assert (
        sanitize_url_credentials("https://user@github.com/example/repo")
        == "https://github.com/example/repo"
    )
    assert (
        sanitize_url_credentials("https://github.com/example/repo")
        == "https://github.com/example/repo"
    )
    assert (
        sanitize_url_credentials(
            "Can't clone https://user:pass@example.com/repo repository"
        )
        == "Can't clone https://example.com/repo repository"
    )
