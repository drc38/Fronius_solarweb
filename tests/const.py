"""Constants for solarweb_Powersensor tests."""
from custom_components.solarweb.const import CONF_ACCESSKEY_ID
from custom_components.solarweb.const import CONF_ACCESSKEY_VALUE
from custom_components.solarweb.const import CONF_PV_ID


MOCK_CONFIG = {
    CONF_ACCESSKEY_ID: "abcd",
    CONF_ACCESSKEY_VALUE: "efgh",
    CONF_PV_ID: "ijkl",
}

MOCK_CONFIG_INIT = {
    CONF_ACCESSKEY_ID: "abcd",
    CONF_ACCESSKEY_VALUE: "efgh",
    CONF_PV_ID: "xxxx",
}

PV_SYS_DATA = {
    "pvSystemId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Test",
    "address": {
        "country": "string",
        "zipCode": "string",
        "street": "string",
        "city": "string",
        "state": "string",
    },
    "pictureURL": "string",
    "peakPower": 0,
    "installationDate": None,
    "lastImport": None,
    "meteoData": "string",
    "timeZone": "string",
}

PV_FLOW_DATA = {
    "pvSystemId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "deviceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": {"isOnline": True, "battMode": 0},
    "data": {
        "logDateTime": None,
        "channels": [
            {"channelName": "Power", "channelType": "Power", "unit": "W", "value": 350},
            {
                "channelName": "Energy",
                "channelType": "Energy",
                "unit": "Wh",
                "value": 1,
            },
        ],
    },
}
