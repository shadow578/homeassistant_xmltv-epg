"""Sanity-checks for mock constants."""

from .const import MOCK_NOW, MOCK_TV_GUIDE

def test_coordinator_data_sanity():
    """Quick sanity-check for the mock data."""
    channel = MOCK_TV_GUIDE.get_channel("mock 1")
    assert channel

    program = channel.get_current_program(MOCK_NOW)
    assert program
    assert program.title == "CH 1 Current"

    program = channel.get_next_program(MOCK_NOW)
    assert program
    assert program.title == "CH 1 Upcoming"
