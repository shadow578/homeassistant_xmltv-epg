"""Test xmltv_epg coordinator component."""
from datetime import datetime, timedelta

import pytest

from unittest.mock import patch, PropertyMock

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.xmltv_epg.coordinator import XMLTVDataUpdateCoordinator
from custom_components.xmltv_epg.api import XMLTVClient

from custom_components.xmltv_epg.model import TVGuide

TEST_NOW = datetime(2024, 5, 17, 12, 45, 0)
XMLTV_CLIENT_DATA = TVGuide("MOCK", "http://example.com/epg.xml")

@pytest.fixture
def mock_xmltv_client_get():
    """Fixture to replace 'XMLTVClient.async_get_data' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.api.XMLTVClient.async_get_data",
        return_value=XMLTV_CLIENT_DATA
    ) as mock:
        yield mock

@pytest.fixture
def mock_actual_now():
    """Fixture to replace 'DataUpdateCoordinator.actual_now' with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.actual_now",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = TEST_NOW
        yield mock

@pytest.fixture()
def mock_async_setup_entry():
    """Fixture to replace 'async_setup_entry' with a mock."""
    with patch(
        "custom_components.xmltv_epg.async_setup_entry",
        return_value=True
    ) as mock:
        yield mock


async def test_coordinator_basic(
        anyio_backend,
        hass,
        mock_xmltv_client_get,
        mock_actual_now,
        mock_async_setup_entry):
    """Test the basic functionality of the coordinator."""

    # create the coordinator
    coordinator = XMLTVDataUpdateCoordinator(
        hass,
        client=XMLTVClient(
            session=async_get_clientsession(hass),
            url="http://example.com/epg.xml"
        ),
        update_interval=1, # every 1 hour
        lookahead=15, # 15 minutes
    )

    # current_time is used by sensors etc. to determine the current program time to show.
    # this time should include the lookahead time.
    assert coordinator.current_time == TEST_NOW + timedelta(minutes=15)

    # nothing was fetched yet, so the api client was not called yet
    assert mock_xmltv_client_get.call_count == 0

    # fetch the data for the first time
    data = await coordinator._async_update_data()
    assert data
    assert data == XMLTV_CLIENT_DATA

    # the api client was called once to fetch the data
    assert mock_xmltv_client_get.call_count == 1

    # last update time should be set
    assert coordinator._last_refetch_time == TEST_NOW


    # fetch the data again, but this time the data should be returned from the cache
    data = await coordinator._async_update_data()
    assert data
    assert data == XMLTV_CLIENT_DATA

    # the api client was not called again, because the data is still fresh
    assert mock_xmltv_client_get.call_count == 1

    # last update time should still be the same
    assert coordinator._last_refetch_time == TEST_NOW


    # time-travel 2 hours into the future
    # the data is now stale and should be refetched
    TWO_HOURS_FROM_NOW = TEST_NOW + timedelta(hours=2)
    mock_actual_now.return_value = TWO_HOURS_FROM_NOW

    data = await coordinator._async_update_data()
    assert data
    assert data == XMLTV_CLIENT_DATA

    # the api client was called again, because the data was stale
    assert mock_xmltv_client_get.call_count == 2

    # last update time should be updated
    assert coordinator._last_refetch_time == TWO_HOURS_FROM_NOW
