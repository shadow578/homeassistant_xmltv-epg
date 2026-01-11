"""Test cases for TVGuide class."""

from custom_components.xmltv_epg.model import TVChannel, TVGuide


def test_from_xml():
    """Test TVGuide.from_xml method with valid input."""
    xml = """
<tv generator-info-name="xmltv_epg" generator-info-url="http://example.com">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
"""

    guide = TVGuide.from_xml(xml)

    assert guide is not None
    assert guide.generator_name == "xmltv_epg"
    assert guide.generator_url == "http://example.com"

    assert len(guide.channels) == 1
    assert len(guide.programs) == 1

    # cross-linked ?
    assert guide.programs[0].channel is not None
    assert guide.programs[0].channel.id == "CH1"

    assert guide.channels[0].last_program is not None
    assert guide.channels[0].last_program.title == "Program 1"


def test_get_channel():
    """Test TVGuide.get_channel method."""
    guide = TVGuide()

    # empty guide, cannot find channels
    assert guide.get_channel("CH1") is None

    # add channel(s)
    guide.channels.append(TVChannel(id="CH1", name="Channel 1"))
    guide.channels.append(TVChannel(id="CH2", name="Channel 2"))
    assert guide.get_channel("CH1") is not None

    # non-existing channel
    assert guide.get_channel("CH3") is None


def test_name_url_properties():
    """Test TVGuide.name and TVGuide.url properties."""
    # no names or urls
    guide = TVGuide()
    assert guide.name is None
    assert guide.url is None

    # generator name/url takes precedence
    guide = TVGuide(
        source_name="Source Name",
        source_url="http://source.url",
        generator_name="Generator Name",
        generator_url="http://generator.url",
    )
    assert guide.name == "Generator Name"
    assert guide.url == "http://generator.url"

    # fallback to source name/url if no generator name/url
    guide = TVGuide(
        source_name="Source Name",
        source_url="http://source.url",
    )
    assert guide.name == "Source Name"
    assert guide.url == "http://source.url"


def test_from_xml_partially_invalid():
    """Test TVGuide.from_xml method with partially invalid input.

    Invalid program and channel entries should be omitted, instead of failing to parse.
    """
    # scenario:
    # - CH1 and Program1 are valid
    # - CH2 and Program2 missing mandatory elements
    # - CH3 and Program3 missing mandatory attributes
    xml = """
<tv generator-info-name="xmltv_epg" generator-info-url="http://example.com">
    <channel id="CH1">
        <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
    <channel id="CH2">
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH2">
    </programme>
    <channel>
        <display-name>Channel 3</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000">
        <title>Program 3</title>
        <desc>Description 3</desc>
    </programme>
</tv>
"""

    guide = TVGuide.from_xml(xml)

    assert guide is not None
    assert len(guide.channels) == 1
    assert len(guide.programs) == 1


def test_from_xml_program_invalid_start_after_end():
    """Test TVGuide.from_xml method with a program entry where start time is after end time.

    Invalid program and channel entries should be omitted, instead of failing to parse.
    """
    xml = """
<tv generator-info-name="xmltv_epg" generator-info-url="http://example.com">
    <channel id="CH1">
        <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
    <programme start="20200101030000 +0000" stop="20200101020000 +0000" channel="CH1">
        <title>Program 2</title>
        <desc>Description 2</desc>
    </programme>
</tv>
"""

    guide = TVGuide.from_xml(xml)

    assert guide is not None
    assert len(guide.channels) == 1
    assert len(guide.programs) == 1
