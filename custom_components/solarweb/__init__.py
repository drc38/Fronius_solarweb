"""
Custom integration to integrate solarweb with Home Assistant.

For more details about this integration, please refer to
https://github.com/drc38/Fronius_solarweb
"""
import asyncio
import logging
from datetime import timedelta

from fronius_solarweb import Fronius_Solarweb
from fronius_solarweb.schema.pvsystem import PvSystemFlowData
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import CONF_ACCESSKEY_ID
from .const import CONF_ACCESSKEY_VALUE
from .const import CONF_PV_ID
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(
    hass: HomeAssistant, config: Config
):  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    access_id = entry.data.get(CONF_ACCESSKEY_ID)
    access_value = entry.data.get(CONF_ACCESSKEY_VALUE)
    pv_id = entry.data.get(CONF_PV_ID)

    client = Fronius_Solarweb(access_id, access_value, pv_id)
    # wait for data to be received
    # await asyncio.sleep(2)

    coordinator = SolarWebDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        coordinator.platforms.append(platform)
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.add_update_listener(async_reload_entry)

    return True


class SolarWebDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: Fronius_Solarweb,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data: PvSystemFlowData = await self.api.get_system_flow_data()
            _LOGGER.debug(f"Flow data polled: {data}")
            # Alter Data structure to simplify sensor usage
            # from [{data}, {data}...]
            # {channel1: {data}, channel2: {data}..}
            sens = data.dict()
            if sens.get("data") or sens["data"].get("channels") is None:
                return sens
            for item in sens["data"]["channels"]:
                sens["data"]["sensors"][item.channelName] = item
            del sens["data"]["channels"]
            _LOGGER.debug(f"New flow data structure: {sens}")
            return sens
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
