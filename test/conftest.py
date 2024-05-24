"""Configure pytest for all tests."""

import pytest

from unittest.mock import patch

from .const import MOCK_TV_GUIDE

pytest_plugins = "pytest_homeassistant_custom_component"

@pytest.fixture()
def hass(hass, enable_custom_integrations):
    """Return a Home Assistant instance that can load custom integrations."""
    yield hass

@pytest.fixture()
def anyio_backend():
    """Define the 'anyio_backend' fixture for asyncio.

    see https://anyio.readthedocs.io/en/stable/testing.html
    """
    return 'asyncio'

@pytest.fixture()
def bypass_integration_setup():
    """Fixture to replace 'async_setup_entry' with a mock."""
    with patch(
        "custom_components.xmltv_epg.async_setup_entry",
        return_value=True
    ), patch(
        "custom_components.xmltv_epg.async_unload_entry",
        return_value=True
    ) as mock:
        yield mock

@pytest.fixture()
def mock_xmltv_client_get_data():
    """Fixture to replace 'XMLTVClient.async_get_data' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.api.XMLTVClient.async_get_data",
        return_value=MOCK_TV_GUIDE
    ) as mock:
        yield mock
