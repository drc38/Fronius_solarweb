"""Adds config flow for solarweb."""
from typing import Any
import logging
import voluptuous as vol


from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from fronius_solarweb import Fronius_Solarweb
from fronius_solarweb.errors import NotAuthorizedException

from .const import DOMAIN, CONF_PV_ID, CONF_ACCESSKEY_VALUE, CONF_ACCESSKEY_ID

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        client = Fronius_Solarweb(
            data[CONF_ACCESSKEY_ID], data[CONF_ACCESSKEY_VALUE], data[CONF_PV_ID]
        )

        system_data = await client.get_pvsystem_meta_data()
        _LOGGER.info("Retrieved PV system data from cloud API")

    except NotAuthorizedException:
        raise InvalidAuth

    # Return extra info that you want to store in the config entry.
    return {
        "title": system_data.peakPower,
    }


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
            try:
                info = await validate_input(user_input)
            except CannotConnect:
                self._errors["base"] = "cannot_connect"
            except InvalidAuth:
                self._errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                self._errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

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
