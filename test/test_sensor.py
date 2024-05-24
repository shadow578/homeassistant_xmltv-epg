"""Test xmltv_epg setup process."""

from datetime import timedelta
from unittest.mock import PropertyMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg import async_setup_entry
from custom_components.xmltv_epg.const import DOMAIN, OPT_PROGRAM_LOOKAHEAD

from .const import MOCK_NOW, MOCK_TV_GUIDE_NAME, MOCK_TV_GUIDE_URL


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


async def test_sensors_basic(
    anyio_backend,
    hass,
    mock_xmltv_client_get_data,
    mock_coordinator_current_time,
    mock_coordinator_last_update_time,
):
    """Test basic sensor setup and function."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: MOCK_TV_GUIDE_URL},
        options={
            OPT_PROGRAM_LOOKAHEAD: 0  # 0 Minutes lookahead
        },
        entry_id="MOCK",
    )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # last_update sensor should be created
    state = hass.states.get("sensor.mock_xmltv_last_update")
    assert state
    assert state.state == MOCK_NOW.astimezone().isoformat()

    # from the data in MOCK_TV_GUIDE, the following sensors
    # with according native values should be created:
    # - sensor.mock_1_program_current   : "CH 1 Current"
    # - sensor.mock_1_program_upcoming  : "CH 1 Upcoming"
    # - sensor.mock_2_program_current   : "CH 2 Current"
    # - sensor.mock_2_program_upcoming  : "CH 2 Upcoming"
    # - sensor.mock_3_program_current   : "CH 3 Current"
    # - sensor.mock_3_program_upcoming  : "CH 3 Upcoming"

    state = hass.states.get("sensor.mock_1_program_current")
    assert state
    assert state.state == "CH 1 Current"

    state = hass.states.get("sensor.mock_1_program_upcoming")
    assert state
    assert state.state == "CH 1 Upcoming"

    state = hass.states.get("sensor.mock_2_program_current")
    assert state
    assert state.state == "CH 2 Current"

    state = hass.states.get("sensor.mock_2_program_upcoming")
    assert state
    assert state.state == "CH 2 Upcoming"

    state = hass.states.get("sensor.mock_3_program_current")
    assert state
    assert state.state == "CH 3 Current - Subtitle (S1E1)"

    state = hass.states.get("sensor.mock_3_program_upcoming")
    assert state
    assert state.state == "CH 3 Upcoming - Subtitle (S1E2)"


async def test_program_sensor_attributes(
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
            OPT_PROGRAM_LOOKAHEAD: 0  # 0 Minutes lookahead
        },
        entry_id="MOCK",
    )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # check CH 3 Current sensor attributes match the program
    state = hass.states.get("sensor.mock_3_program_current")
    assert state
    assert state.state == "CH 3 Current - Subtitle (S1E1)"

    assert state.attributes["start"] == (MOCK_NOW - timedelta(minutes=15))
    assert state.attributes["end"] == (MOCK_NOW + timedelta(minutes=15))
    assert state.attributes["duration"] == "00:30"
    assert state.attributes["title"] == "CH 3 Current"
    assert state.attributes["description"] == "Description"
    assert state.attributes["episode"] == "S1E1"
    assert state.attributes["subtitle"] == "Subtitle"


async def test_last_update_sensor_attributes(
    anyio_backend,
    hass,
    mock_xmltv_client_get_data,
    mock_coordinator_current_time,
    mock_coordinator_last_update_time,
):
    """Test last_update sensor state and attributes."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: MOCK_TV_GUIDE_URL},
        options={
            OPT_PROGRAM_LOOKAHEAD: 0  # 0 Minutes lookahead
        },
        entry_id="MOCK",
    )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # check sensor attributes
    state = hass.states.get("sensor.mock_xmltv_last_update")
    assert state
    assert state.state == MOCK_NOW.astimezone().isoformat()

    assert state.attributes["generator_name"] == MOCK_TV_GUIDE_NAME
    assert state.attributes["generator_url"] == MOCK_TV_GUIDE_URL
