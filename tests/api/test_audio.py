"""Test audio api."""


async def test_api_audio_logs(advanced_logs_tester) -> None:
    """Test audio logs."""
    await advanced_logs_tester("/audio", "hassio_audio")
