"""Test xmltv_epg setup process."""
from datetime import datetime
import pytest

from homeassistant.const import CONF_HOST

from unittest.mock import patch, PropertyMock
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg import (
    async_setup_entry,
    async_unload_entry,
    async_reload_entry
)
from custom_components.xmltv_epg.const import DOMAIN
from custom_components.xmltv_epg.coordinator import XMLTVDataUpdateCoordinator

from custom_components.xmltv_epg.xmltv.model import TVGuide

UPDATE_COORDINATOR_DATA = TVGuide("MOCK", "http://example.com/epg.xml")

@pytest.fixture()
def mock_xmltv_client_get():
    """Fixture to replace 'XMLTVClient.async_get_data' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.api.XMLTVClient.async_get_data",
        return_value=UPDATE_COORDINATOR_DATA
    ) as mock:
        yield mock

async def test_setup_unload_and_reload_entry(anyio_backend,
                                             hass,
                                             mock_xmltv_client_get):
    """Test entry setup, unload and reload."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={ CONF_HOST: "http://example.com/epg.xml" },
        entry_id="MOCK",
    )

    # helper to assert entry
    def assert_entry():
        assert DOMAIN in hass.data
        assert config_entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][config_entry.entry_id],
            XMLTVDataUpdateCoordinator
        )

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    assert_entry()

    # should have called coordinator update
    assert mock_xmltv_client_get.call_count == 1

    # reload the entry and check the data is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert_entry()

    # assert the coordinator was updated again.
    # since the coordinator is re-created on reload, the data will be re-fetched too
    assert mock_xmltv_client_get.call_count == 2

    # unload the entry and check the data is gone
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]

    # coordinator was NOT updated again, re-fetch count did not change
    assert mock_xmltv_client_get.call_count == 2
