"""Test cases for the helper module."""

from custom_components.xmltv_epg.helper import normalize_for_entity_id


def test_normalize_for_entity_id():
    """Test the normalize_for_entity_id function."""

    assert normalize_for_entity_id("WDR") == "wdr"
    assert normalize_for_entity_id("DE: My Channel 1") == "de_my_channel_1"
    assert normalize_for_entity_id("DE: WDR (Münster)") == "de_wdr_muenster"

    # test umlauts
    assert normalize_for_entity_id("ÄÖÜß") == "aeoeuess"

    # test special characters
    assert (
        normalize_for_entity_id('Special Characters: !"§$%&/()=?')
        == "special_characters"
    )

    # test leading and trailing spaces
    assert (
        normalize_for_entity_id("  Leading and Trailing Spaces  ")
        == "leading_and_trailing_spaces"
    )
