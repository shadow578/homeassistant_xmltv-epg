"""Test xmltv_epg setup process."""
from datetime import datetime, timedelta

import pytest

from homeassistant.const import CONF_HOST

from unittest.mock import patch, PropertyMock
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg import async_setup_entry
from custom_components.xmltv_epg.const import DOMAIN, OPT_PROGRAM_LOOKAHEAD

from custom_components.xmltv_epg.xmltv.model import TVGuide, TVChannel, TVProgram

TEST_NOW = datetime(2024, 5, 17, 12, 45, 0)

def get_mock_tv_guide() -> TVGuide:
    """Build a mock TV Guide object."""
    guide = TVGuide("MOCK", "http://example.com/epg.xml")

    channels = [
        TVChannel(id="mock 1", name="Mock Channel 1"),
        TVChannel(id="mock 2", name="Mock Channel 2"),
        TVChannel(id="mock 3", name="Mock Channel 3"),
    ]

    current_start = TEST_NOW - timedelta(minutes=15)
    current_end = TEST_NOW + timedelta(minutes=15)

    upcoming_start = TEST_NOW + timedelta(minutes=15)
    upcoming_end = TEST_NOW + timedelta(minutes=45)

    programs = [
        TVProgram(
            channel_id="mock 1",
            start=current_start,
            end=current_end,
            title="CH 1 Current",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 2",
            start=current_start,
            end=current_end,
            title="CH 2 Current",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 3",
            start=current_start,
            end=current_end,
            title="CH 3 Current",
            description="Description",
            episode="S1E1",
            subtitle="Subtitle",
        ),
        TVProgram(
            channel_id="mock 1",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 1 Upcoming",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 2",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 2 Upcoming",
            description="Description",
        ),
        TVProgram(
            channel_id="mock 3",
            start=upcoming_start,
            end=upcoming_end,
            title="CH 3 Upcoming",
            description="Description",
            episode="S1E2",
            subtitle="Subtitle",
        ),
    ]

    # cross-link programs with channels
    for program in programs:
        program.cross_link_channel(channels)

    guide.channels = channels
    guide.programs = programs
    return guide

UPDATE_COORDINATOR_DATA = get_mock_tv_guide()

def test_coordinator_data_sanity():
    """Quick sanity-check for the mock data."""
    channel = UPDATE_COORDINATOR_DATA.get_channel("mock 1")
    assert channel

    program = channel.get_current_program(TEST_NOW)
    assert program
    assert program.title == "CH 1 Current"

    program = channel.get_next_program(TEST_NOW)
    assert program
    assert program.title == "CH 1 Upcoming"

@pytest.fixture()
def mock_coordinator_data():
    """Fixture to replace 'XMLTVDataUpdateCoordinator._async_update_data' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator._async_update_data",
        return_value=UPDATE_COORDINATOR_DATA
    ) as mock:
        yield mock

@pytest.fixture()
def mock_coordinator_current_time():
    """Fixture to replace 'XMLTVDataUpdateCoordinator.current_time' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.current_time",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value=TEST_NOW
        yield mock

@pytest.fixture()
def mock_coordinator_last_update_time():
    """Fixture to replace 'XMLTVDataUpdateCoordinator.last_update_time' property with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.last_update_time",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = TEST_NOW
        yield mock

async def test_sensors_basic(
        anyio_backend,
        hass,
        mock_coordinator_data,
        mock_coordinator_current_time,
        mock_coordinator_last_update_time
    ):
    """Test basic sensor setup and function."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "http://example.com/epg.xml"
        },
        options={
            OPT_PROGRAM_LOOKAHEAD: 0 # 0 Minutes lookahead
        },
        entry_id="MOCK",
    )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # last_update sensor should be created
    state = hass.states.get("sensor.mock_last_update")
    assert state
    assert state.state == TEST_NOW.astimezone().isoformat()

    # from the data in UPDATE_COORDINATOR_DATA, the following sensors
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
        mock_coordinator_data,
        mock_coordinator_current_time,
        mock_coordinator_last_update_time
    ):
    """Test program sensor state and attributes."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "http://example.com/epg.xml"
        },
        options={
            OPT_PROGRAM_LOOKAHEAD: 0 # 0 Minutes lookahead
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

    assert state.attributes["start"] == (TEST_NOW - timedelta(minutes=15))
    assert state.attributes["end"] == (TEST_NOW + timedelta(minutes=15))
    assert state.attributes["duration"] == "00:30"
    assert state.attributes["title"] == "CH 3 Current"
    assert state.attributes["description"] == "Description"
    assert state.attributes["episode"] == "S1E1"
    assert state.attributes["subtitle"] == "Subtitle"

async def test_last_update_sensor_attributes(
        anyio_backend,
        hass,
        mock_coordinator_data,
        mock_coordinator_current_time,
        mock_coordinator_last_update_time
    ):
    """Test last_update sensor state and attributes."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "http://example.com/epg.xml"
        },
        options={
            OPT_PROGRAM_LOOKAHEAD: 0 # 0 Minutes lookahead
        },
        entry_id="MOCK",
    )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # check sensor attributes
    state = hass.states.get("sensor.mock_last_update")
    assert state
    assert state.state == TEST_NOW.astimezone().isoformat()

    assert state.attributes["generator_name"] == "MOCK"
    assert state.attributes["generator_url"] == "http://example.com/epg.xml"
