"""Custom integration to integrate solarweb with Home Assistant.

For more details about this integration, please refer to
https://github.com/drc38/Fronius_solarweb
"""

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from fronius_solarweb import Fronius_Solarweb
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ACCESSKEY_ID,
    CONF_ACCESSKEY_VALUE,
    CONF_PV_ID,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

if TYPE_CHECKING:
    from fronius_solarweb.schema.pvsystem import PvSystemAggrDataV2, PvSystemFlowData

SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER: logging.Logger = logging.getLogger(__package__)


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

    httpx_client = get_async_client(hass)
    client = Fronius_Solarweb(access_id, access_value, pv_id, httpx_client)

    coordinatorFlow = FlowDataUpdateCoordinator(hass, client=client)
    coordinatorAggr = AggrDataUpdateCoordinator(hass, client=client)

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
    """Process raw data to simply HA sensor processing."""
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


class FlowDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Fronius_Solarweb,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self.async_update_data,
        )

    async def async_update_data(self):
        """Update data via library."""
        try:
            data: PvSystemFlowData = await self.api.get_system_flow_data()
            _LOGGER.debug(f"Flow data polled: {data}")

            return await async_process_data(data)
        except Exception as exception:
            raise UpdateFailed from exception


class AggrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Fronius_Solarweb,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self.async_update_data,
        )

    async def async_update_data(self):
        """Update data via library."""
        try:
            data: PvSystemAggrDataV2 = await self.api.get_system_aggr_data_v2()
            _LOGGER.debug(f"Aggregated data polled: {data}")

            return await async_process_data(data)
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
