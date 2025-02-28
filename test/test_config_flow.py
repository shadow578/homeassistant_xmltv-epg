"""Test xmltv_epg config and options flow."""

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xmltv_epg.api import (
    XMLTVClientCommunicationError,
    XMLTVClientError,
)
from custom_components.xmltv_epg.const import (
    DOMAIN,
    OPT_ENABLE_CHANNEL_ICONS,
    OPT_ENABLE_PROGRAM_IMAGES,
    OPT_ENABLE_UPCOMING_SENSOR,
    OPT_PROGRAM_LOOKAHEAD,
    OPT_UPDATE_INTERVAL,
)

from .const import MOCK_TV_GUIDE_NAME, MOCK_TV_GUIDE_URL


# note: need to bypass integration setup to avoid hass actually trying to setup the entry, which would
# interfere with counters on xmltv_client_get_data
async def test_config_flow_user_step_ok(
    anyio_backend, hass, bypass_integration_setup, mock_xmltv_client_get_data
):
    """Test that the 'user' config step correctly creates a config entry."""

    # initialize the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # check that the first step is a 'form'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # if a user were to enter 'http://example.com/epg.xml' and submit the form
    # it would result in this call.
    # behind the scenes, the connection should be tested and the config entry
    # is created with title = generator_name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: MOCK_TV_GUIDE_URL},
    )

    # to test the connection, a XMLTVClient should be created and
    # the async_get_data method should be called
    mock_xmltv_client_get_data.assert_called_once()

    # a new config entry should be created
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_TV_GUIDE_NAME
    assert result["data"] == {CONF_HOST: MOCK_TV_GUIDE_URL}
    assert result["options"] == {}  # no options set yet
    assert result["result"]


async def test_config_flow_user_step_handles_error(
    anyio_backend, hass, bypass_integration_setup, mock_xmltv_client_get_data
):
    """Test that the 'user' config step correctly handles errors in _test_connection."""

    # initialize the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # check that the first step is a 'form'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # raise an communication exception when doing the connection test
    mock_xmltv_client_get_data.side_effect = XMLTVClientCommunicationError(
        "MOCK client communication error"
    )

    # input a "invalid" url.
    # Since the client is mocked to raise an exception, the actual
    # url entered does not matter.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: MOCK_TV_GUIDE_URL},
    )

    # still on the 'user' step, but now with a 'connection' error
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "connection"}

    # raise a generic exception when doing the connection test
    mock_xmltv_client_get_data.side_effect = XMLTVClientError(
        "MOCK client communication error"
    )

    # input a "invalid" url.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: MOCK_TV_GUIDE_URL},
    )

    # still on the 'user' step, but now with a 'unknown' error
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}


async def test_option_flow_init_step_ok(anyio_backend, hass, bypass_integration_setup):
    """Test that the 'init' options step correctly creates a config entry."""

    # create a new MockConfigEntry and add to HASS, bypassing the config flow
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: MOCK_TV_GUIDE_URL}, entry_id="MOCK"
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
            OPT_PROGRAM_LOOKAHEAD: 10,
            OPT_ENABLE_UPCOMING_SENSOR: True,
            OPT_ENABLE_CHANNEL_ICONS: True,
            OPT_ENABLE_PROGRAM_IMAGES: True,
        },
    )

    # the flow should now finish and create an entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        OPT_UPDATE_INTERVAL: 24,
        OPT_PROGRAM_LOOKAHEAD: 10,
        OPT_ENABLE_UPCOMING_SENSOR: True,
        OPT_ENABLE_CHANNEL_ICONS: True,
        OPT_ENABLE_PROGRAM_IMAGES: True,
    }
