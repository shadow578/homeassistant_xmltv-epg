"""Test xmltv_epg coordinator component."""

from datetime import timedelta
from unittest.mock import PropertyMock, patch

import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg.api import XMLTVClient
from custom_components.xmltv_epg.const import DOMAIN
from custom_components.xmltv_epg.coordinator import XMLTVDataUpdateCoordinator

from .const import MOCK_NOW, MOCK_TV_GUIDE, MOCK_TV_GUIDE_URL


@pytest.fixture()
def mock_actual_now():
    """Fixture to replace 'DataUpdateCoordinator.actual_now' with a mock."""
    with patch(
        "custom_components.xmltv_epg.coordinator.XMLTVDataUpdateCoordinator.actual_now",
        new_callable=PropertyMock,
    ) as mock:
        mock.return_value = MOCK_NOW
        yield mock


async def test_coordinator_basic(
    anyio_backend,
    hass,
    bypass_integration_setup,
    mock_xmltv_client_get_data,
    mock_actual_now,
):
    """Test the basic functionality of the coordinator."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test",
        data={},
    )

    # create the coordinator
    coordinator = XMLTVDataUpdateCoordinator(
        hass,
        config_entry=entry,
        client=XMLTVClient(
            session=async_get_clientsession(hass),
            url=MOCK_TV_GUIDE_URL,
        ),
        update_interval=1,  # every 1 hour
        lookahead=15,  # 15 minutes
        enable_upcoming_sensor=True,
    )

    # current_time is used by sensors etc. to determine the current program time to show.
    # this time should include the lookahead time.
    assert coordinator.current_time == MOCK_NOW + timedelta(minutes=15)

    # nothing was fetched yet, so the api client was not called yet
    assert mock_xmltv_client_get_data.call_count == 0

    # fetch the data for the first time
    data = await coordinator._async_update_data()
    assert data
    assert data == MOCK_TV_GUIDE

    # the api client was called once to fetch the data
    assert mock_xmltv_client_get_data.call_count == 1

    # last update time should be set
    assert coordinator._last_refetch_time == MOCK_NOW

    # fetch the data again, but this time the data should be returned from the cache
    data = await coordinator._async_update_data()
    assert data
    assert data == MOCK_TV_GUIDE

    # the api client was not called again, because the data is still fresh
    assert mock_xmltv_client_get_data.call_count == 1

    # last update time should still be the same
    assert coordinator._last_refetch_time == MOCK_NOW

    # time-travel 2 hours into the future
    # the data is now stale and should be refetched
    TWO_HOURS_FROM_NOW = MOCK_NOW + timedelta(hours=2)
    mock_actual_now.return_value = TWO_HOURS_FROM_NOW

    data = await coordinator._async_update_data()
    assert data
    assert data == MOCK_TV_GUIDE

    # the api client was called again, because the data was stale
    assert mock_xmltv_client_get_data.call_count == 2

    # last update time should be updated
    assert coordinator._last_refetch_time == TWO_HOURS_FROM_NOW
