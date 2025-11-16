"""Test cases for TVProgramEpisodeNumber class."""

from custom_components.xmltv_epg.model import (
    TVProgramEpisodeNumber,
)


def test_parse_episode_number_season_episode_full():
    """Test TVProgramEpisodeNumber class parses SxxExx Season+Episode format."""
    xml = """<episode-num system="SxxExx">S1E2</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "SxxExx"
    assert episode.raw_value == "S1E2"
    assert episode.value == (1, 2)
    assert episode.value_onscreen == "S1E2"


def test_parse_episode_number_season_episode_season_only():
    """Test TVProgramEpisodeNumber class parses SxxExx Season only format."""
    xml = """<episode-num system="SxxExx">S1</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "SxxExx"
    assert episode.raw_value == "S1"
    assert episode.value == (1, None)
    assert episode.value_onscreen == "S1"


def test_parse_episode_number_season_episode_episode_only():
    """Test TVProgramEpisodeNumber class parses SxxExx Episode only format."""
    xml = """<episode-num system="SxxExx">E2</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "SxxExx"
    assert episode.raw_value == "E2"
    assert episode.value == (None, 2)
    assert episode.value_onscreen == "E2"


def test_parse_episode_number_xmltv_ns_full():
    """Test TVProgramEpisodeNumber class parses tvxml_ns Season+Episode format."""
    xml = """<episode-num system="xmltv_ns">0.1.</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "xmltv_ns"
    assert episode.raw_value == "0.1."
    assert episode.value == (1, 2)
    assert episode.value_onscreen == "S1E2"


def test_parse_episode_number_xmltv_ns_season_only():
    """Test TVProgramEpisodeNumber class parses tvxml_ns Season only format."""
    xml = """<episode-num system="xmltv_ns">0..</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "xmltv_ns"
    assert episode.raw_value == "0.."
    assert episode.value == (1, None)
    assert episode.value_onscreen == "S1"


def test_parse_episode_number_xmltv_ns_episode_only():
    """Test TVProgramEpisodeNumber class parses tvxml_ns Episode only format."""
    xml = """<episode-num system="xmltv_ns">.1.</episode-num>"""

    episode = TVProgramEpisodeNumber.from_xml(xml)
    assert episode.system == "xmltv_ns"
    assert episode.raw_value == ".1."
    assert episode.value == (None, 2)
    assert episode.value_onscreen == "E2"
