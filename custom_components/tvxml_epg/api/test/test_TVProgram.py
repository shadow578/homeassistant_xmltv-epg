import pytest
from datetime import datetime
import xml.etree.ElementTree as ET

from ..model import TVProgram, TVChannel

def test_from_xml():
    """Test TVProgram.from_xml method with valid input."""
    xml = ET.fromstring('<programme start="20200101010000 +0000" stop="20200101020000 +0000"><title>Program 1</title><desc>Description 1</desc></programme>')

    program = TVProgram.from_xml(xml)
    assert program is not None

    assert program.start == datetime(2020, 1, 1, 1, 0)
    assert program.end == datetime(2020, 1, 1, 2, 0)
    assert program.title == 'Program 1'
    assert program.description == 'Description 1'

def test_from_xml_invalid_tag():
    """Test TVProgram.from_xml method with invalid input."""
    xml = ET.fromstring('<channel id="DE: WDR Essen"></channel>')

    program = TVProgram.from_xml(xml)
    assert program is None

def test_from_xml_invalid_datetime():
    """Test TVProgram.from_xml method with invalid datetime."""
    xml = ET.fromstring('<programme start="20201314020000 +0000" stop=20200101020000 +0000"><title>Program 1</title><desc>Description 1</desc></programme>')

    program = TVProgram.from_xml(xml)
    assert program is None

def test_from_xml_end_before_start():
    """Test TVProgram.from_xml method with end datetime before start datetime."""
    # Start 01.01.2020 02:00
    # End   01.01.2020 01:00 - 1 hour before start
    xml = ET.fromstring('<programme start="20200101020000 +0000" stop="20200101010000 +0000"><title>Program 1</title><desc>Description 1</desc></programme>')

    program = TVProgram.from_xml(xml)
    assert program is None

def test_init_end_before_start():
    """Test TVProgram.__init__ method with end datetime before start datetime."""
    with pytest.raises(ValueError):
        TVProgram('DE: WDR Essen',
                  datetime(2020, 1, 1, 2, 0), # Start 01.01.2020 02:00
                  datetime(2020, 1, 1, 1, 0), # End   01.01.2020 01:00 - 1 hour before start
                  'Program 1',
                  'Description 1')

def test_cross_link_channel():
    """Test TVProgram.cross_link_channel method."""
    # prepare channels
    channel1 = TVChannel('CH1', 'Channel 1')
    channel2 = TVChannel('CH2', 'Channel 2')
    channels = [channel1, channel2]

    # prepare program
    program = TVProgram(channel1.id, datetime(2020, 1, 1, 1, 0), datetime(2020, 1, 1, 2, 0), 'Program 1', 'Description 1')

    # cross-link channel
    program.cross_link_channel(channels)

    # channel should be set
    assert program.channel is not None
    assert program.channel.id == channel1.id

    # channel should know program
    assert program in channel1.programs
