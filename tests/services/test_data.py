"""Test services data."""


def test_data_initial(coresys):
    """Test initial data for services."""
    assert coresys.services.data.mqtt == {}
    assert coresys.services.data.mysql == {}
