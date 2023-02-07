"""SolarWebEntity class"""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_PV_ID
from .const import DOMAIN


class SolarWebEntity(CoordinatorEntity):
    """Overall device class for PV System."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry, description):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = description

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            configuration_url=ATTRIBUTION,
            identifiers={(DOMAIN, self.config_entry.data[CONF_PV_ID])},
            name=self.config_entry.title,
            manufacturer="Fronius",
        )
