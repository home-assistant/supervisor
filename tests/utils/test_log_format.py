"""Tests for message formater."""

from supervisor.utils.log_format import format_message


async def test_format_message_port():
    """Tests for message formater."""
    message = '500 Server Error: Internal Server Error:  Bind for 0.0.0.0:80 failed: port is already allocated")'
    assert (
        await format_message(message)
        == "Port '80' is already in use by something else on the host."
    )


async def test_format_message_port_alternative():
    """Tests for message formater."""
    message = 'Error starting userland proxy: listen tcp 0.0.0.0:80: bind: address already in use")'
    assert (
        await format_message(message)
        == "Port '80' is already in use by something else on the host."
    )


async def test_exeption():
    """Tests the exception handling."""
    message = b"byte"
    assert await format_message(message) == message
