"""Sensor platform for solarweb."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorEntityDescription

from .const import CHANNEL_HA_MAP
from .const import DOMAIN
from .entity import SolarWebEntity


_LOGGER: logging.Logger = logging.getLogger(__package__)


@dataclass
class SolarWebSensorDescription(SensorEntityDescription):
    """Class to describe a Sensor entity."""


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug(coordinator.data)
    if coordinator.data.data is not None:
        for sens in coordinator.data.data.channels:
            desc = SolarWebSensorDescription(
                key=sens.channelName,
                name=sens.channelName,
                native_unit_of_measurement=sens.unit,
            )
            async_add_devices([SolarWebSensor(coordinator, entry, desc)], False)


class SolarWebSensor(SolarWebEntity, SensorEntity):
    """SolarWeb Sensor class."""

    entity_description: SolarWebSensorDescription

    def __init__(
        self, coordinator, config_entry, description: SolarWebSensorDescription
    ):
        super().__init__(coordinator, config_entry, description)
        self._config = config_entry
        self.entity_description = description
        self._extra_attr = {}
        self._attr_name = None

    @property
    def available(self):
        """Return if online."""
        return self.coordinator.data.status.isOnline
    
    @property
    def native_value(self):
        """Return the native measurement."""
        lst = self.coordinator.data.data.channels
        value = next(
            (item for item in lst if item.channelName == self._attr_name), None
        )
        if value:
            return value.value
        else:
            return None

    @property
    def native_precision(self):
        """Return the native measurement precision."""
        lst = self.coordinator.data.data.channels
        value = next(
            (item for item in lst if item.channelName == self._attr_name), None
        )
        if value:
            return CHANNEL_HA_MAP.get(value.channelType).get("precision")
        else:
            return None

    @property
    def state_class(self):
        """Return the state class."""
        lst = self.coordinator.data.data.channels
        value = next(
            (item for item in lst if item.channelName == self._attr_name), None
        )
        if value:
            return CHANNEL_HA_MAP.get(value.channelType).get("state")
        else:
            return None

    @property
    def device_class(self):
        """Return the device class."""
        lst = self.coordinator.data.data.channels
        value = next(
            (item for item in lst if item.channelName == self._attr_name), None
        )
        if value:
            return CHANNEL_HA_MAP.get(value.channelType).get("device")
        else:
            return None

    @property
    def icon(self):
        """Return the state class."""
        lst = self.coordinator.data.data.channels
        value = next(
            (item for item in lst if item.channelName == self._attr_name), None
        )
        if value:
            return CHANNEL_HA_MAP.get(value.channelType).get("icon")
        else:
            return None

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.
        False if entity pushes its state to HA.
        """
        return True
