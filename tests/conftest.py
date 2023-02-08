"""Global fixtures for solarweb integration."""
from unittest.mock import patch

import pytest
import pytest_asyncio
from fronius_solarweb.errors import NotAuthorizedException
from fronius_solarweb.schema.pvsystem import PvSystemFlowData
from fronius_solarweb.schema.pvsystem import PvSystemMetaData
from custom_components.solarweb import (
    async_process_data,
)

from .const import PV_FLOW_DATA
from .const import PV_SYS_DATA


pytest_plugins = "pytest_homeassistant_custom_component"

sys_data = PvSystemMetaData(**PV_SYS_DATA)
raw_flow_data = PvSystemFlowData(**PV_FLOW_DATA)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will result in calls to async_update_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest_asyncio.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    # Data manipulation to match that in SolarWebDataUpdateCoordinator_async_update_data()
    flow_data = await async_process_data(raw_flow_data)
    with patch(
        "custom_components.solarweb.SolarWebDataUpdateCoordinator._async_update_data",
        return_value=flow_data,
    ), patch(
        "fronius_solarweb.Fronius_Solarweb.get_pvsystem_meta_data",
        return_value=sys_data,
    ):
        yield


# In this fixture, we are forcing calls to api to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "fronius_solarweb.Fronius_Solarweb.get_pvsystem_meta_data",
        side_effect=NotAuthorizedException,
    ), patch(
        "custom_components.solarweb.SolarWebDataUpdateCoordinator._async_update_data",
        side_effect=Exception,
    ):
        yield
