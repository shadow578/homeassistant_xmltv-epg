"""Test cases for TVProgram class."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import pytest

from custom_components.xmltv_epg.model import TVChannel, TVProgram
from custom_components.xmltv_epg.model.program import parse_episode_number


def test_from_xml():
    """Test TVProgram.from_xml method with valid input."""
    xml = ET.fromstring(
        '<programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1"><title>Program 1</title><desc>Description 1</desc></programme>'
    )

    program = TVProgram.from_xml(xml)
    assert program is not None

    assert program._channel_id == "CH1"

    assert program.start == datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc)
    assert program.end == datetime(2020, 1, 1, 2, 0, tzinfo=timezone.utc)
    assert program.title == "Program 1"
    assert program.description == "Description 1"

    # all these should remain None as they are not set
    assert program.episode is None
    assert program.subtitle is None


def test_episode_num_system_season_episode():
    """Test TVProgram.from_xml parses episode_num in SxxExx format, 
    as seen in https://github.com/shadow578/homeassistant_xmltv-epg/issues/32."""
    xml = ET.fromstring(
        '<programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1"><title>Program 1</title><desc>Description 1</desc><episode-num system="SxxExx">S13E7</episode-num></programme>'
    )

    program = TVProgram.from_xml(xml)
    assert program is not None

    # episode number '12.6.' should be converted to 'S13E7'
    assert program.episode == "S13E7"

def test_episode_num_system_xmltv_ns():
    """Test TVProgram.from_xml parses episode_num in xmltv_ns format."""
    xml = ET.fromstring(
        '<programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1"><title>Program 1</title><desc>Description 1</desc><episode-num system="xmltv_ns">12.6.</episode-num></programme>'
    )

    program = TVProgram.from_xml(xml)
    assert program is not None

    # episode number 'S13E7' should remain as-is
    assert program.episode == "S13E7"


def test_from_xml_invalid_tag():
    """Test TVProgram.from_xml method with invalid input."""
    xml = ET.fromstring('<channel id="DE: WDR Essen"></channel>')

    program = TVProgram.from_xml(xml)
    assert program is None


def test_from_xml_invalid_datetime():
    """Test TVProgram.from_xml method with invalid datetime."""
    xml = ET.fromstring(
        '<programme start="20201314020000 +0000" stop="20200101020000 +0000"><title>Program 1</title><desc>Description 1</desc></programme>'
    )

    program = TVProgram.from_xml(xml)
    assert program is None


def test_from_xml_end_before_start():
    """Test TVProgram.from_xml method with end datetime before start datetime."""
    # Start 01.01.2020 02:00
    # End   01.01.2020 01:00 - 1 hour before start
    xml = ET.fromstring(
        '<programme start="20200101020000 +0000" stop="20200101010000 +0000" channel="CH1"><title>Program 1</title><desc>Description 1</desc></programme>'
    )

    program = TVProgram.from_xml(xml)
    assert program is None


def test_init_end_before_start():
    """Test TVProgram.__init__ method with end datetime before start datetime."""
    with pytest.raises(ValueError):
        TVProgram(
            "DE: WDR Essen",
            datetime(2020, 1, 1, 2, 0),  # Start 01.01.2020 02:00
            datetime(2020, 1, 1, 1, 0),  # End   01.01.2020 01:00 - 1 hour before start
            "Program 1",
            "Description 1",
        )


def test_cross_link_channel():
    """Test TVProgram.cross_link_channel method."""
    # prepare channels
    channel1 = TVChannel("CH1", "Channel 1")
    channel2 = TVChannel("CH2", "Channel 2")
    channels = [channel1, channel2]

    # prepare program
    program = TVProgram(
        channel1.id,
        datetime(2020, 1, 1, 1, 0),
        datetime(2020, 1, 1, 2, 0),
        "Program 1",
        "Description 1",
    )

    # cross-link channel
    program.cross_link_channel(channels)

    # channel should be set
    assert program.channel is not None
    assert program.channel.id == channel1.id

    # channel should know program
    assert program in channel1.programs


def test_duration():
    """Test TVProgram.duration property."""
    program = TVProgram(
        "CH1",
        datetime(2020, 1, 1, 1, 0),  # 1:00
        datetime(2020, 1, 1, 2, 15),  # 2:15 - 1h 15m
        "Program 1",
        "Description 1",
    )

    assert program.duration.total_seconds() == (60 + 15) * 60


def test_full_title():
    """Test TVProgram.full_title property."""
    program = TVProgram(
        "CH1",
        datetime(2020, 1, 1, 1, 0),
        datetime(2020, 1, 1, 2, 0),
        "Program 1",
        "Description 1",
    )

    # (1)
    assert program.full_title == "Program 1"

    # (2)
    program.episode = "S1 E1"
    assert program.full_title == "Program 1 (S1 E1)"

    # (3)
    program.subtitle = "Subtitle 1"
    assert program.full_title == "Program 1 - Subtitle 1 (S1 E1)"

    # (4)
    program.episode = None
    assert program.full_title == "Program 1 - Subtitle 1"


def test_parse_episode_number_season_episode():
    """Test the parse_episode_number function works for Season+Episode format."""
    xml = ET.fromstring(
        '<programme><episode-num system="SxxExx">S01E02</episode-num></programme>'
    )

    episode = parse_episode_number(xml)
    assert episode == "S01E02"


def test_parse_episode_number_xmltv_ns_full():
    """Test the parse_episode_number function works for tvxml_ns Season+Episode format."""
    xml = ET.fromstring(
        '<programme><episode-num system="xmltv_ns">0.1.</episode-num></programme>'
    )

    episode = parse_episode_number(xml)
    assert episode == "S01E02"


def test_parse_episode_number_xmltv_ns_season_only():
    """Test the parse_episode_number function works for tvxml_ns Season only format."""
    xml = ET.fromstring(
        '<programme><episode-num system="xmltv_ns">0..</episode-num></programme>'
    )

    episode = parse_episode_number(xml)
    assert episode == "S01"

def test_parse_episode_number_xmltv_ns_episode_only():
    """Test the parse_episode_number function works for tvxml_ns Episode only format."""
    xml = ET.fromstring(
        '<programme><episode-num system="xmltv_ns">.1.</episode-num></programme>'
    )

    episode = parse_episode_number(xml)
    assert episode == "E02"


def test_parse_episode_number_order():
    """Test the parse_episode_number function uses SxxExx format over tvxml_ns format."""
    # note: different data for xmltv_ns and SxxExx to distinguish them
    xml = ET.fromstring(
        '<programme><episode-num system="xmltv_ns">1.2.</episode-num><episode-num system="SxxExx">S01E02</episode-num></programme>'
    )

    episode = parse_episode_number(xml)
    assert episode == "S01E02"
