"""Adds config flow for solarweb."""

import logging
from typing import Any

import voluptuous as vol
from fronius_solarweb import Fronius_Solarweb
from fronius_solarweb.errors import NotAuthorizedException, NotFoundException
from homeassistant import config_entries

from . import save_token

from .const import (
    CONF_ACCESSKEY_ID,
    CONF_ACCESSKEY_VALUE,
    CONF_LOGIN_NAME,
    CONF_LOGIN_PASSWORD,
    CONF_PV_ID,
    DEFAULT_ACCESSKEY_ID,
    DEFAULT_ACCESSKEY_VALUE,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SolarWebFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for solarweb."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
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
            self._errors["base"] = "auth"

            return await self._show_config_form()
        return await self._show_config_form()

    async def _show_config_form(self, id="user"):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id=id,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PV_ID): str,
                    vol.Required(CONF_ACCESSKEY_ID, default=DEFAULT_ACCESSKEY_ID): str,
                    vol.Required(
                        CONF_ACCESSKEY_VALUE, default=DEFAULT_ACCESSKEY_VALUE
                    ): str,
                    vol.Optional(CONF_LOGIN_NAME, None): str,
                    vol.Optional(CONF_LOGIN_PASSWORD, None): str,
                }
            ),
            errors=self._errors,
        )

    async def _show_reconfig_form(self, entry, id="reconfigure"):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id=id,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PV_ID, default=entry.data.get(CONF_PV_ID)): str,
                    vol.Required(
                        CONF_ACCESSKEY_ID, default=entry.data.get(CONF_ACCESSKEY_ID)
                    ): str,
                    vol.Required(
                        CONF_ACCESSKEY_VALUE,
                        default=entry.data.get(CONF_ACCESSKEY_VALUE),
                    ): str,
                    vol.Optional(CONF_LOGIN_NAME, entry.data.get(CONF_LOGIN_NAME)): str,
                    vol.Optional(
                        CONF_LOGIN_PASSWORD, entry.data.get(CONF_LOGIN_PASSWORD)
                    ): str,
                }
            ),
            errors=self._errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Add reconfigure step to allow to reconfigure a config entry."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry

        if user_input is not None:
            info = await self._validate_input(user_input)
            if info:
                return self.async_update_reload_and_abort(
                    entry, data=user_input, reason="reconfigure_successful"
                )
            self._errors["base"] = "auth"
            return await self._show_reconfig_form(entry)

        return await self._show_reconfig_form(entry)

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """

        try:
            client = Fronius_Solarweb(
                access_key_id=data[CONF_ACCESSKEY_ID],
                access_key_value=data[CONF_ACCESSKEY_VALUE],
                pv_system_id=data[CONF_PV_ID],
                login_name=data.get(CONF_LOGIN_NAME),
                login_password=data.get(CONF_LOGIN_PASSWORD),
            )

            if data.get(CONF_LOGIN_PASSWORD):
                await client.login()

            system_data = await client.get_pvsystem_meta_data()
            _LOGGER.info("Retrieved PV system data from cloud API")

            if data.get(CONF_LOGIN_PASSWORD):
                await self.hass.async_add_executor_job(
                    save_token, self.hass, system_data.name, client.jwt_data
                )

            # Return extra info that you want to store in the config entry.
            return {
                "title": system_data.name,
            }
        except (NotFoundException, NotAuthorizedException):
            return None
