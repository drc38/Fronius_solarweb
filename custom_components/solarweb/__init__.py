"""Custom integration to integrate solarweb with Home Assistant.

For more details about this integration, please refer to
https://github.com/drc38/Fronius_solarweb
"""

import logging
import os
import json
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from fronius_solarweb import Fronius_Solarweb
from fronius_solarweb.errors import NotAuthorizedException
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.sun import is_up
from homeassistant.util import dt as dt_util
from httpx import HTTPStatusError

from .const import (
    CONF_ACCESSKEY_ID,
    CONF_ACCESSKEY_VALUE,
    CONF_LOGIN_NAME,
    CONF_LOGIN_PASSWORD,
    CONF_PV_ID,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    TOKEN_EXPIRATION,
    TOKEN_FILE_NAME,
    TOKEN,
)

if TYPE_CHECKING:
    from fronius_solarweb.schema.pvsystem import PvSystemAggrDataV2, PvSystemFlowData

SCAN_INTERVAL_FLOW = timedelta(minutes=5)
SCAN_INTERVAL_AGG = timedelta(minutes=15)

_LOGGER: logging.Logger = logging.getLogger(__package__)


def save_token(
    hass: HomeAssistant,
    name: str,
    token: dict = None,
) -> None:
    """Save the jwt Token data to file."""
    config_dir = hass.config.config_dir
    filename = name.replace(" ", "_") + "_" + TOKEN_FILE_NAME
    file = os.path.join(config_dir, filename)
    flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
    _LOGGER.debug(f"Persisting session token to: {file}")

    with open(os.open(file, flags, 0o600), "w") as spf:
        json.dump(token, spf)


def load_token(
    hass: HomeAssistant,
    name: str,
) -> dict[str, str] | None:
    """Load the jwt Token data from file."""
    config_dir = hass.config.config_dir
    filename = name.replace(" ", "_") + "_" + TOKEN_FILE_NAME
    file = os.path.join(config_dir, filename)
    _LOGGER.debug(f"Reading session token from: {file}")

    if os.path.isfile(file):
        with open(file) as spf:
            try:
                token = json.loads(spf.read())
            except json.decoder.JSONDecodeError:
                _LOGGER.error(f"Unable to read/decode token from: {file}")
                token = None
    else:
        token = None
    return token


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    access_id = entry.data.get(CONF_ACCESSKEY_ID)
    access_value = entry.data.get(CONF_ACCESSKEY_VALUE)
    pv_id = entry.data.get(CONF_PV_ID)
    login_name = entry.data.get(CONF_LOGIN_NAME)
    login_password = entry.data.get(CONF_LOGIN_PASSWORD)

    httpx_client = get_async_client(hass)
    client = Fronius_Solarweb(
        access_key_id=access_id,
        access_key_value=access_value,
        pv_system_id=pv_id,
        httpx_client=httpx_client,
        login_name=login_name,
        login_password=login_password,
    )

    if login_password:
        token = await hass.async_add_executor_job(load_token, hass, entry.title)
        if token:
            client.jwt_data = token
            client._jwt_headers = {
                "Authorization": "Bearer " + client.jwt_data.get(TOKEN)
            }
        else:
            await client.login()
        try:
            await aysnc_check_expiry(hass, client, entry.title)
        except HTTPStatusError:
            await client.login()
        await hass.async_add_executor_job(
            save_token, hass, entry.title, client.jwt_data
        )

    coordinatorFlow = FlowDataUpdateCoordinator(hass, client=client, name=entry.title)
    coordinatorAggr = AggrDataUpdateCoordinator(hass, client=client, name=entry.title)

    coordinators = [coordinatorFlow, coordinatorAggr]

    for coord in coordinators:
        await coord.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinators

    for platform in PLATFORMS:
        for coord in coordinators:
            coord.platforms.append(platform)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_process_data(data) -> dict[str, Any]:
    """Process raw data to simplify HA sensor processing."""
    # Alter Data Channels structure to simplify sensor usage
    # from "channels": [{data}, {data}...] to
    # "sensors":{channel1: {data}, channel2: {data}..}
    sens = data.model_dump()
    _LOGGER.debug(f"Data converted to dict: {sens}")
    if isinstance(sens["data"], list):
        sens["data"] = sens["data"][0]

    sens["data"]["sensors"] = {}
    if sens["data"].get("channels") is None:
        return sens
    for item in sens["data"]["channels"]:
        sens["data"]["sensors"][item["channelName"]] = item
    del sens["data"]["channels"]
    _LOGGER.debug(f"New data structure: {sens}")
    return sens


async def aysnc_check_expiry(
    hass: HomeAssistant, client: Fronius_Solarweb, name: str
) -> None:
    """Check token expiry and refresh if required."""
    expires = client.jwt_data.get(TOKEN_EXPIRATION)
    if expires:
        if dt_util.parse_datetime(expires) < dt_util.as_utc(dt_util.now()):
            _LOGGER.debug(f"Token expired on: {expires}, refreshing")
            await client.refresh_token()
            await hass.async_add_executor_job(save_token, hass, name, client.jwt_data)
            _LOGGER.debug(f"Token new expiry: {client.jwt_data.get(TOKEN_EXPIRATION)}")


class FlowDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Fronius_Solarweb,
        name: str,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL_FLOW,
            update_method=self.async_update_data,
        )

    async def async_update_data(self):
        """Update data via library."""
        # Pause updates after sunset and before sunrise
        # Check for no data in case the integration is being setup
        if not is_up(self.hass) and self.data is not None:
            return self.data
        try:
            await aysnc_check_expiry(self.hass, self.api, self.name)
            data: PvSystemFlowData = await self.api.get_system_flow_data()
            _LOGGER.debug(f"Flow data polled: {data}")

            return await async_process_data(data)
        except NotAuthorizedException:
            raise
        except Exception as exception:
            raise UpdateFailed from exception


class AggrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Fronius_Solarweb,
        name: str,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL_AGG,
            update_method=self.async_update_data,
        )

    async def async_update_data(self):
        """Update data via library."""
        # Pause updates after sunset and before sunrise
        # Check for no data in case the integration is being setup
        if not is_up(self.hass) and self.data is not None:
            return self.data
        try:
            await aysnc_check_expiry(self.hass, self.api, self.name)
            data: PvSystemAggrDataV2 = await self.api.get_system_aggr_data_v2()
            _LOGGER.debug(f"Aggregated data polled: {data}")

            return await async_process_data(data)
        except NotAuthorizedException:
            raise
        except Exception as exception:
            raise UpdateFailed from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Not sure why needed but prevents lingering timers from DataUpdateCoordinator
    for coord in hass.data[DOMAIN][entry.entry_id]:
        await coord.async_shutdown()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
