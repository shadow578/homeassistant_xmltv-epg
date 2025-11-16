"""Test cases for TVProgram class."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from pydantic_xml import ParsingError

from custom_components.xmltv_epg.model import (
    TVProgram,
    TVProgramEpisodeNumber,
)


def test_from_xml():
    """Test TVProgram.from_xml method with valid input."""
    xml = """
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
    """

    program = TVProgram.from_xml(xml)
    assert program is not None

    assert program.channel_id == "CH1"

    assert program.start == datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc)
    assert program.end == datetime(2020, 1, 1, 2, 0, tzinfo=timezone.utc)
    assert program.title == "Program 1"
    assert program.description == "Description 1"

    # all these should remain None as they are not set
    assert program.episode is None
    assert program.subtitle is None
    assert program.image is None


def test_episode_num_system_season_episode():
    """Test TVProgram.from_xml parses episode_num in SxxExx format.

    as seen in https://github.com/shadow578/homeassistant_xmltv-epg/issues/32
    """
    xml = """
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
        <episode-num system="SxxExx">S13E7</episode-num>
    </programme>
    """

    program = TVProgram.from_xml(xml)
    assert program is not None

    # episode number 'S13E7' should remain as 'S13E7'
    assert program.episode == "S13E7"


def test_episode_num_system_xmltv_ns():
    """Test TVProgram.from_xml parses episode_num in xmltv_ns format."""
    xml = """
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
        <episode-num system="xmltv_ns">12.6.</episode-num>
    </programme>
    """

    program = TVProgram.from_xml(xml)
    assert program is not None

    # episode number '12.6.' should be converted to 'S13E7'
    assert program.episode == "S13E7"


def test_parse_program_image_url():
    """Test TVProgram.from_xml method parses image url correctly."""
    xml = """
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
        <icon src="http://example.com/program.jpg"/>
    </programme>
    """

    program = TVProgram.from_xml(xml)
    assert program is not None

    # there should be a image_url set
    assert program.image is not None
    assert program.image.url == "http://example.com/program.jpg"


def test_from_xml_invalid_tag():
    """Test TVProgram.from_xml method with invalid input."""
    xml = """<channel id="DE: WDR Essen"></channel>"""

    with pytest.raises(ParsingError):
        _ = TVProgram.from_xml(xml)


def test_from_xml_invalid_datetime():
    """Test TVProgram.from_xml method with invalid datetime."""
    xml = """
    <programme start="20201314020000 +0000" stop="20200101020000 +0000">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
    """

    with pytest.raises(ValidationError):
        _ = TVProgram.from_xml(xml)


def test_from_xml_end_before_start():
    """Test TVProgram.from_xml method with end datetime before start datetime."""
    # Start 01.01.2020 02:00
    # End   01.01.2020 01:00 - 1 hour before start
    xml = """
    <programme start="20200101020000 +0000" stop="20200101010000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
    """

    with pytest.raises(ValidationError):
        _ = TVProgram.from_xml(xml)


def test_init_end_before_start():
    """Test TVProgram.__init__ method with end datetime before start datetime."""
    with pytest.raises(ValueError):
        TVProgram(
            channel_id="DE: WDR Essen",
            start=datetime(2020, 1, 1, 2, 0),  # Start 01.01.2020 02:00
            end=datetime(
                2020, 1, 1, 1, 0
            ),  # End   01.01.2020 01:00 - 1 hour before start
            title="Program 1",
            description="Description 1",
        )


def test_duration():
    """Test TVProgram.duration property."""
    program = TVProgram(
        channel_id="CH1",
        start=datetime(2020, 1, 1, 1, 0),  # 1:00
        end=datetime(2020, 1, 1, 2, 15),  # 2:15 - 1h 15m
        title="Program 1",
    )

    assert program.duration.total_seconds() == (60 + 15) * 60


def test_full_title():
    """Test TVProgram.full_title property."""
    # (1)
    program = TVProgram(
        channel_id="CH1",
        start=datetime(2020, 1, 1, 1, 0),
        end=datetime(2020, 1, 1, 2, 0),
        title="Program 1",
    )
    assert program.full_title == "Program 1"

    # (2)
    program = TVProgram(
        channel_id="CH1",
        start=datetime(2020, 1, 1, 1, 0),
        end=datetime(2020, 1, 1, 2, 0),
        title="Program 1",
        episode_raw=[TVProgramEpisodeNumber(system="onscreen", raw_value="S1E1")],
    )
    assert program.full_title == "Program 1 (S1E1)"

    # (3)
    program = TVProgram(
        channel_id="CH1",
        start=datetime(2020, 1, 1, 1, 0),
        end=datetime(2020, 1, 1, 2, 0),
        title="Program 1",
        subtitle="Subtitle 1",
        episode_raw=[TVProgramEpisodeNumber(system="onscreen", raw_value="S1E1")],
    )
    assert program.full_title == "Program 1 - Subtitle 1 (S1E1)"

    # (4)
    program = TVProgram(
        channel_id="CH1",
        start=datetime(2020, 1, 1, 1, 0),
        end=datetime(2020, 1, 1, 2, 0),
        title="Program 1",
        subtitle="Subtitle 1",
    )
    assert program.full_title == "Program 1 - Subtitle 1"
