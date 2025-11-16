"""Test cases for TVChannel class."""

from datetime import datetime

import pytest
from pydantic_xml import ParsingError

from custom_components.xmltv_epg.model import TVChannel, TVProgram


def test_from_xml():
    """Test TVChannel.from_xml method with valid input."""
    xml = """
    <channel id="DE: WDR Essen">
        <display-name>DE: WDR Essen</display-name>
    </channel>
    """

    channel = TVChannel.from_xml(xml)
    assert channel is not None

    assert channel.id == "DE: WDR Essen"
    assert channel.name == "DE: WDR Essen"

    # 'XX: ' prefix should be removed from display name
    assert channel.display_name == "WDR Essen"

    # there should be no icon_url
    assert channel.icon is None


def test_from_xml_invalid_tag():
    """Test TVChannel.from_xml method with invalid input."""
    xml = """
    <programme id="DE: WDR Essen"></programme>
    """

    with pytest.raises(ParsingError):
        _ = TVChannel.from_xml(xml)


def test_parse_channel_icon_url():
    """Test TVChannel.from_xml method with valid input."""
    xml = """
    <channel id="DE: WDR Essen">
        <display-name>DE: WDR Essen</display-name>
        <icon src="http://example.com/channel.jpg"/>
    </channel>
    """

    channel = TVChannel.from_xml(xml)
    assert channel is not None

    assert channel.icon is not None
    assert channel.icon.url == "http://example.com/channel.jpg"


def test_get_current_or_next_program():
    """Test TVChannel.get_current_program and TVChannel.get_next_program methods."""

    # prepare channel with programs
    # prev @ 00:00 - 01:00
    # current @ 01:00 - 02:00
    # next @ 02:00 - 03:00
    program_prev = TVProgram(
        channel_id="DE: WDR Essen",
        start=datetime(2020, 1, 1, 0, 0),
        end=datetime(2020, 1, 1, 1, 0),
        title="Program 1",
        description="Description 1",
    )
    program_current = TVProgram(
        channel_id="DE: WDR Essen",
        start=datetime(2020, 1, 1, 1, 0),
        end=datetime(2020, 1, 1, 2, 0),
        title="Program 2",
        description="Description 2",
    )
    program_next = TVProgram(
        channel_id="DE: WDR Essen",
        start=datetime(2020, 1, 1, 2, 0),
        end=datetime(2020, 1, 1, 3, 0),
        title="Program 3",
        description="Description 3",
    )

    channel = TVChannel(id="DE: WDR Essen", name="WDR Essen")
    channel._link_program(program_prev)
    channel._link_program(program_current)
    channel._link_program(program_next)

    # get current program @ 01:15
    current = channel.get_current_program(datetime(2020, 1, 1, 1, 15))
    assert current is not None
    assert current.title == program_current.title

    # get next program @ 01:15
    next = channel.get_next_program(datetime(2020, 1, 1, 1, 15))
    assert next is not None
    assert next.title == program_next.title

    # last program entry is 'next'
    last = channel.last_program
    assert last is not None
    assert last.title == program_next.title
