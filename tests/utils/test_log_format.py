"""Tests for message formater."""

from supervisor.utils.log_format import format_message


def test_format_message_port():
    """Tests for message formater."""
    message = '500 Server Error: Internal Server Error:  Bind for 0.0.0.0:80 failed: port is already allocated")'
    assert (
        format_message(message)
        == "Port '80' is already in use by something else on the host."
    )


def test_format_message_port_alternative():
    """Tests for message formater."""
    message = 'Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use")'
    assert (
        format_message(message)
        == "Port '80' is already in use by something else on the host."
    )
