"""Test xmltv_epg config and options flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg.const import (
    DOMAIN,
    OPT_UPDATE_INTERVAL,
    OPT_PROGRAM_LOOKAHEAD
)
from custom_components.xmltv_epg.api import XMLTVClientCommunicationError, XMLTVClientError

TEST_CONNECTION_MOCK_RESPONSE = "MOCK"

@pytest.fixture()
def mock_test_connection_fixture():
    """Fixture to replace 'XMLTVFlowHandler._test_connection' method with a mock."""
    with patch(
        "custom_components.xmltv_epg.config_flow.XMLTVFlowHandler._test_connection",
        return_value=TEST_CONNECTION_MOCK_RESPONSE
    ) as mock_test_connection:
        yield mock_test_connection

async def test_config_flow_user_step_ok(anyio_backend, hass, mock_test_connection_fixture):
    """Test that the 'user' config step correctly creates a config entry."""

    # initialize the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={ "source": config_entries.SOURCE_USER },
    )

    # check that the first step is a 'form'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # if a user were to enter 'http://example.com/epg.xml' and submit the form
    # it would result in this call.
    # behind the scenes, the _test_connection method is called and will
    # return TEST_CONNECTION_MOCK_RESPONSE as generator_name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "http://example.com/epg.xml"
        },
    )

    # _test_connection should have been called with CONF_HOST as url
    mock_test_connection_fixture.assert_called_once_with(url="http://example.com/epg.xml")

    # a new config entry should be created
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == TEST_CONNECTION_MOCK_RESPONSE # == generator_name
    assert result["data"] == {
        CONF_HOST: "http://example.com/epg.xml"
    }
    assert result["options"] == {} # no options set yet
    assert result["result"]

async def test_config_flow_user_step_handles_error(anyio_backend, hass, mock_test_connection_fixture):
    """Test that the 'user' config step correctly handles errors in _test_connection."""

    # initialize the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={ "source": config_entries.SOURCE_USER },
    )

    # check that the first step is a 'form'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # raise an exception when _test_connection is called
    mock_test_connection_fixture.side_effect = XMLTVClientCommunicationError("MOCK client communication error")

    # input a "invalid" url.
    # Since the _test_connection method is mocked to raise an exception, the actual
    # url entered does not matter.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "http://example.com/epg.xml"
        },
    )

    # still on the 'user' step, but now with a 'connection' error
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == { "base": "connection" }

    # raise a generic exception when _test_connection is called
    mock_test_connection_fixture.side_effect = XMLTVClientError("MOCK client communication error")

    # input a "invalid" url.
    # Since the _test_connection method is mocked to raise an exception, the actual
    # url entered does not matter.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "http://example.com/epg.xml"
        },
    )

    # still on the 'user' step, but now with a 'unknown' error
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == { "base": "unknown" }

async def test_option_flow_init_step_ok(anyio_backend, hass):
    """Test that the 'init' options step correctly creates a config entry."""

    # create a new MockConfigEntry and add to HASS, bypassing the config flow
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={ CONF_HOST: "http://example.com/epg.xml" },
        entry_id="MOCK"
    )
    entry.add_to_hass(hass)

    # initialize the options flow
    await hass.config_entries.async_setup(entry.entry_id)
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # the first step should be a 'form' with id 'init'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # select update interval of 24 hours
    # and lookahead of 10 minutes
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            OPT_UPDATE_INTERVAL: 24,
            OPT_PROGRAM_LOOKAHEAD: 10
        },
    )

    # the flow should now finish and create an entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        OPT_UPDATE_INTERVAL: 24,
        OPT_PROGRAM_LOOKAHEAD: 10
    }
