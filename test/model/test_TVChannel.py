"""Test cases for TVChannel class."""

from datetime import datetime
import xml.etree.ElementTree as ET

from custom_components.xmltv_epg.model import TVChannel, TVProgram

def test_from_xml():
    """Test TVChannel.from_xml method with valid input."""
    xml = ET.fromstring('<channel id="DE: WDR Essen"><display-name>DE: WDR Essen</display-name></channel>')

    channel = TVChannel.from_xml(xml)
    assert channel is not None

    assert channel.id == 'DE: WDR Essen'

    # 'XX: ' prefix should be removed
    assert channel.name == 'WDR Essen'

def test_from_xml_invalid_tag():
    """Test TVChannel.from_xml method with invalid input."""
    xml = ET.fromstring('<programme id="DE: WDR Essen"></programme>')

    channel = TVChannel.from_xml(xml)
    assert channel is None

def test_get_current_or_next_program():
    """Test TVChannel.get_current_program and TVChannel.get_next_program methods."""

    # prepare channel with programs
    # prev @ 00:00 - 01:00
    # current @ 01:00 - 02:00
    # next @ 02:00 - 03:00
    program_prev = TVProgram('DE: WDR Essen', datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 1, 1, 0), 'Program 1', 'Description 1')
    program_current = TVProgram('DE: WDR Essen', datetime(2020, 1, 1, 1, 0), datetime(2020, 1, 1, 2, 0), 'Program 2', 'Description 2')
    program_next = TVProgram('DE: WDR Essen', datetime(2020, 1, 1, 2, 0), datetime(2020, 1, 1, 3, 0), 'Program 3', 'Description 3')

    channel = TVChannel('DE: WDR Essen', 'WDR Essen')
    channel.add_program(program_prev)
    channel.add_program(program_current)
    channel.add_program(program_next)

    # get current program @ 01:15
    current = channel.get_current_program(datetime(2020, 1, 1, 1, 15))
    assert current is not None
    assert current.title == program_current.title

    # get next program @ 01:15
    next = channel.get_next_program(datetime(2020, 1, 1, 1, 15))
    assert next is not None
    assert next.title == program_next.title
