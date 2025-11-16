"""Test cases for TVImage class."""

from custom_components.xmltv_epg.model import (
    TVImage,
)


def test_parse_tv_image():
    """Test TVImage class parses image XML correctly."""
    xml = """<icon src="http://example.com/image.png" width="640" height="480"/>"""

    image = TVImage.from_xml(xml)
    assert image.url == "http://example.com/image.png"
    assert image.width == 640
    assert image.height == 480


def test_parse_tv_image_missing_dimensions():
    """Test TVImage class handles missing width/height attributes."""
    xml = """<icon src="http://example.com/image.png"/>"""

    image = TVImage.from_xml(xml)
    assert image.url == "http://example.com/image.png"
    assert image.width is None
    assert image.height is None
