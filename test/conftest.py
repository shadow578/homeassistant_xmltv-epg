"""Configure pytest for all tests."""

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

@pytest.fixture()
def hass(hass, enable_custom_integrations):
    """Return a Home Assistant instance that can load custom integrations."""
    yield hass

@pytest.fixture
def anyio_backend():
    """Define the 'anyio_backend' fixture for asyncio.

    see https://anyio.readthedocs.io/en/stable/testing.html
    """
    return 'asyncio'
