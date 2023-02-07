"""Adds config flow for solarweb."""
import logging
from typing import Any

import voluptuous as vol
from fronius_solarweb import Fronius_Solarweb
from fronius_solarweb.errors import NotAuthorizedException
from fronius_solarweb.errors import NotFoundException
from homeassistant import config_entries

from .const import CONF_ACCESSKEY_ID
from .const import CONF_ACCESSKEY_VALUE
from .const import CONF_PV_ID
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SolarWebFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for solarweb."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            info = await self._validate_input(user_input)
            if info:
                return self.async_create_entry(title=info["title"], data=user_input)
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)
        else:
            return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PV_ID): str,
                    vol.Required(CONF_ACCESSKEY_ID): str,
                    vol.Required(CONF_ACCESSKEY_VALUE): str,
                }
            ),
            errors=self._errors,
        )

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the user input allows us to connect.
        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        try:
            client = Fronius_Solarweb(
                data[CONF_ACCESSKEY_ID], data[CONF_ACCESSKEY_VALUE], data[CONF_PV_ID]
            )

            system_data = await client.get_pvsystem_meta_data()
            _LOGGER.info("Retrieved PV system data from cloud API")

            # Return extra info that you want to store in the config entry.
            return {
                "title": system_data.name,
            }
        except (NotFoundException, NotAuthorizedException):
            return None
