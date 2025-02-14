"""Test xmltv_epg setup process."""

from unittest.mock import PropertyMock, patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.helpers import device_registry, entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg import async_setup_entry
from custom_components.xmltv_epg.const import (
    DOMAIN,
    OPT_ENABLE_CHANNEL_ICONS,
    OPT_ENABLE_PROGRAM_IMAGES,
    OPT_ENABLE_UPCOMING_SENSOR,
    OPT_PROGRAM_LOOKAHEAD,
)
from custom_components.xmltv_epg.helper import program_get_normalized_identification
from custom_components.xmltv_epg.model import TVChannel

from .const import MOCK_NOW, MOCK_TV_GUIDE_URL


@pytest.fixture()
def mock_coordinator_current_time():
    """Fixture to replace 'XMLTVDataUpdateCoordinator.current_time' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.current_time",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = MOCK_NOW
        yield mock


@pytest.fixture()
def mock_coordinator_last_update_time():
    """Fixture to replace 'XMLTVDataUpdateCoordinator.last_update_time' property with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.last_update_time",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = MOCK_NOW
        yield mock


def has_image_entity_with_url(hass, entity_id: str, url: str) -> bool:
    """Test if the hass instance contains a image entity with the given url."""
    state = hass.states.get(entity_id)
    if not state:
        return False

    # TODO: actually check if the correct url is loaded
    # i didn't find any way to do this
    return state.attributes["entity_picture"].startswith("/api/image_proxy")


async def test_images_basic(
    anyio_backend,
    hass,
    mock_xmltv_client_get_data,
    mock_coordinator_current_time,
    mock_coordinator_last_update_time,
):
    """Test basic image entity setup and function."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: MOCK_TV_GUIDE_URL},
        options={
            OPT_PROGRAM_LOOKAHEAD: 0,  # 0 Minutes lookahead
            OPT_ENABLE_UPCOMING_SENSOR: True,  # Enable upcoming program sensor
            OPT_ENABLE_CHANNEL_ICONS: True,  # Enable channel icon entities
            OPT_ENABLE_PROGRAM_IMAGES: True,  # Enable program image entities
        },
        entry_id="MOCK",
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # last_update sensor should be created
    state = hass.states.get("sensor.mock_xmltv_last_update")
    assert state
    assert state.state == MOCK_NOW.astimezone().isoformat()

    # from the data in MOCK_TV_GUIDE, the following program image entities
    # with according urls values should be created:
    # - image.mock_1_program_image_current   : "http://example.com/pr/ch1_cur.jpg"
    # - image.mock_1_program_image_upcoming  : "http://example.com/pr/ch1_upc.jpg"
    # - image.mock_2_program_image_current   : "http://example.com/pr/ch2_cur.jpg"
    # - image.mock_2_program_image_upcoming  : "http://example.com/pr/ch2_upc.jpg"
    # - image.mock_3_program_image_current   : "http://example.com/pr/ch3_cur.jpg"
    # - image.mock_3_program_image_upcoming  : "http://example.com/pr/ch3_upc.jpg"
    assert has_image_entity_with_url(
        hass, "image.mock_1_program_image_current", "http://example.com/pr/ch1_cur.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_1_program_image_upcoming", "http://example.com/pr/ch1_upc.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_2_program_image_current", "http://example.com/pr/ch2_cur.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_2_program_image_upcoming", "http://example.com/pr/ch2_upc.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_3_program_image_current", "http://example.com/pr/ch3_cur.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_3_program_image_upcoming", "http://example.com/pr/ch3_upc.jpg"
    )

    # additionally, the following channel icon image entities are created
    # with according urls:
    # - image.mock_1_icon : "http://example.com/ch/mock1.jpg"
    # - image.mock_2_icon : "http://example.com/ch/mock2.jpg"
    # - image.mock_3_icon : "http://example.com/ch/mock3.jpg"
    assert has_image_entity_with_url(
        hass, "image.mock_1_icon", "http://example.com/ch/mock1.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_2_icon", "http://example.com/ch/mock2.jpg"
    )
    assert has_image_entity_with_url(
        hass, "image.mock_3_icon", "http://example.com/ch/mock3.jpg"
    )


async def test_program_sensor_device(
    anyio_backend,
    hass,
    mock_xmltv_client_get_data,
    mock_coordinator_current_time,
    mock_coordinator_last_update_time,
):
    """Test program sensor state and attributes."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: MOCK_TV_GUIDE_URL},
        options={
            OPT_PROGRAM_LOOKAHEAD: 0,  # 0 Minutes lookahead
            OPT_ENABLE_UPCOMING_SENSOR: True,  # Enable upcoming program sensor
            OPT_ENABLE_CHANNEL_ICONS: True,  # Enable channel icon entities
            OPT_ENABLE_PROGRAM_IMAGES: True,  # Enable program image entities
        },
        entry_id="MOCK",
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # get device entry for CH3 current image
    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    entity = er.async_get("image.mock_3_program_image_current")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None
    assert device.name == "Mock Channel 3"

    # same for CH3 icon
    entity = er.async_get("image.mock_3_icon")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None
    assert device.name == "Mock Channel 3"


def test_sensor_entity_ids():
    """Test sensor entity ids match the expected values."""

    # program image, current
    translation_key, entity_id = program_get_normalized_identification(
        TVChannel("CH 1", "Channel 1"), False, "program_image"
    )

    assert translation_key == "program_image_current"
    assert entity_id == "image.ch_1_program_image_current"

    # program image, upcoming
    translation_key, entity_id = program_get_normalized_identification(
        TVChannel("CH 1", "Channel 1"), True, "program_image"
    )

    assert translation_key == "program_image_upcoming"
    assert entity_id == "image.ch_1_program_image_upcoming"

    # channel icon
    translation_key, entity_id = program_get_normalized_identification(
        TVChannel("CH 1", "Channel 1"), False, "channel_icon"
    )

    assert translation_key == "channel_icon"
    assert entity_id == "image.ch_1_icon"
