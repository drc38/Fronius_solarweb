"""Sensor platform for solarweb."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import CHANNEL_HA_MAP, CONF_PV_ID, DOMAIN
from .entity import SolarWebEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


@dataclass
class SolarWebSensorDescription(SensorEntityDescription):
    """Class to describe a Sensor entity."""


async def async_setup_entry(hass, entry, async_add_devices) -> None:
    """Do setup of the sensor."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    # _LOGGER.debug(coordinator.data)
    for coordinator in coordinators:
        if coordinator.data.get("data") is not None:
            for v in coordinator.data["data"]["sensors"].values():
                desc = SolarWebSensorDescription(
                    key=".".join([entry.title, v["channelName"]]),
                    name=v["channelName"],
                    native_unit_of_measurement=v["unit"],
                )
                async_add_devices([SolarWebSensor(coordinator, entry, desc)], False)


class SolarWebSensor(SolarWebEntity, SensorEntity):
    """SolarWeb Sensor class."""

    entity_description: SolarWebSensorDescription

    def __init__(
        self, coordinator, config_entry, description: SolarWebSensorDescription
    ) -> None:
        """Init sensor."""
        super().__init__(coordinator, config_entry, description)
        self._config = config_entry
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = ".".join(
            [self._config.data.get(CONF_PV_ID), description.key]
        )

    @property
    def available(self):
        """Return if online."""
        if self.coordinator.data.get("status"):
            online = self.coordinator.data["status"].get("isOnline", True)
        else:
            online = True
        not_none = self.native_value is not None
        return online and not_none

    @property
    def native_value(self):
        """Return the native measurement."""
        return self.coordinator.data["data"]["sensors"][self._attr_name]["value"]

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the native measurement precision."""
        value = self.coordinator.data["data"]["sensors"][self._attr_name]["channelType"]
        if value in CHANNEL_HA_MAP:
            return CHANNEL_HA_MAP.get(value).get("precision")
        return None

    @property
    def state_class(self):
        """Return the state class."""
        value = self.coordinator.data["data"]["sensors"][self._attr_name]["channelType"]
        if value in CHANNEL_HA_MAP:
            return CHANNEL_HA_MAP.get(value).get("state")
        return None

    @property
    def device_class(self):
        """Return the device class."""
        value = self.coordinator.data["data"]["sensors"][self._attr_name]["channelType"]
        if value in CHANNEL_HA_MAP:
            return CHANNEL_HA_MAP.get(value).get("device")
        return None

    @property
    def icon(self):
        """Return the state class."""
        value = self.coordinator.data["data"]["sensors"][self._attr_name]["channelType"]
        if value in CHANNEL_HA_MAP:
            return CHANNEL_HA_MAP.get(value).get("icon")
        return None
