"""Test cases for TVGuide class."""

import xml.etree.ElementTree as ET

from ..model import TVGuide, TVChannel


def test_from_xml():
    """Test TVGuide.from_xml method with valid input."""
    xml = ET.fromstring("""
<tv generator-info-name="tvxml_epg" generator-info-url="http://example.com">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
""")

    guide = TVGuide.from_xml(xml)

    assert guide is not None
    assert guide.generator_name == 'tvxml_epg'
    assert guide.generator_url == 'http://example.com'

    assert len(guide.channels) == 1
    assert len(guide.programs) == 1

    # cross-linked ?
    assert guide.programs[0].channel is not None
    assert guide.programs[0].channel.id == 'CH1'


def test_get_channel():
    """Test TVGuide.get_channel method."""
    guide = TVGuide()

    # empty guide, cannot find channels
    assert guide.get_channel('CH1') is None

    # add channel(s)
    guide.channels.append(TVChannel('CH1', 'Channel 1'))
    guide.channels.append(TVChannel('CH2', 'Channel 2'))
    assert guide.get_channel('CH1') is not None

    # non-existing channel
    assert guide.get_channel('CH3') is None
