"""Adds config flow for TVXML."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    TVXMLClient,
    TVXMLClientError,
    TVXMLClientCommunicationError,
)
from .const import (
    DOMAIN,
    LOGGER,
    OPT_UPDATE_INTERVAL,
    OPT_PROGRAM_LOOKAHEAD,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_PROGRAM_LOOKAHEAD,
)

class TVXMLFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TVXML."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    url=user_input[CONF_HOST],
                )
            except TVXMLClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except TVXMLClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    )
                }
            ),
            errors=_errors,
        )

    async def _test_connection(self, url: str) -> None:
        """Validate connection."""
        client = TVXMLClient(
            session=async_create_clientsession(self.hass),
            url=url,
        )
        await client.async_get_data()

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get options flow handler."""
        return TVXMLOptionsFlowHandler(config_entry)


class TVXMLOptionsFlowHandler(config_entries.OptionsFlow):
    """TVXML options flow."""

    VERSION = 1

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize TVXML options flow."""
        self.config_entry = config_entry

        async def async_step_init(
                self,
                user_input: dict | None = None,
        ) -> config_entries.FlowResult:
            """TVXML Options Flow."""
            if user_input is not None:
                return self.async_create_entry(
                    data=user_input,
                )

            # show options form
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            OPT_UPDATE_INTERVAL,
                            default=self.config_entry.options.get(
                                OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                            ),
                        ): selector.NumberSelector(
                            selector.NumberSelectorConfig(
                                min=1,
                                step=1,
                                unit_of_measurement="h",
                                mode=selector.NumberSelectorMode.BOX,
                            )
                        ),
                        vol.Required(
                            OPT_PROGRAM_LOOKAHEAD,
                            default=self.config_entry.options.get(
                                OPT_PROGRAM_LOOKAHEAD, DEFAULT_PROGRAM_LOOKAHEAD
                            ),
                        ): selector.NumberSelector(
                            selector.NumberSelectorConfig(
                                min=0,
                                step=1,
                                unit_of_measurement="m",
                                mode=selector.NumberSelectorMode.BOX,
                            )
                        ),
                    }
                ),
            )
