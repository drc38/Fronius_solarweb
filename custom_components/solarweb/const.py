"""Constants for solarweb."""
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorStateClass

# Base component constants
NAME = "Fronius Solar.Web"
DOMAIN = "solarweb"
DOMAIN_DATA = f"{DOMAIN}_data"

ATTRIBUTION = "https://www.solarweb.com/"
ISSUE_URL = "https://github.com/drc38/Fronius_solarweb/issues"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_ENABLED = "disabled"
CONF_ACCESSKEY_ID = "accesskeyid"
CONF_ACCESSKEY_VALUE = "accesskeyvalue"
CONF_PV_ID = "pvid"

# Channel types to HA details ie device class, state class, precision, icon)
CHANNEL_HA_MAP = {
    "Apparent Power": {
        "device": SensorDeviceClass.APPARENT_POWER,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 1,
        "icon": "mdi:solar-power",
    },
    "Power": {
        "device": SensorDeviceClass.POWER,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 1,
        "icon": "mdi:solar-power",
    },
    "Energy": {
        "device": SensorDeviceClass.ENERGY,
        "state": SensorStateClass.TOTAL_INCREASING,
        "precision": 1,
        "icon": "mdi:solar-power-variant",
    },
    "Voltage": {
        "device": SensorDeviceClass.VOLTAGE,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 0,
        "icon": "mdi:solar-power",
    },
    "Current": {
        "device": SensorDeviceClass.CURRENT,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 0,
        "icon": "mdi:solar-power",
    },
    "Temperature": {
        "device": SensorDeviceClass.TEMPERATURE,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 1,
        "icon": "mdi:sun-thermometer-outline",
    },
    "Currency": {
        "device": SensorDeviceClass.MONETARY,
        "state": SensorStateClass.TOTAL,
        "precision": 2,
        "icon": "mdi:cash-multiple",
    },
    "Percentage": {
        "device": SensorDeviceClass.BATTERY,
        "state": SensorStateClass.MEASUREMENT,
        "precision": 1,
        "icon": "mdi:battery-charging-medium",
    },
}

# Defaults
DEFAULT_NAME = DOMAIN

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
