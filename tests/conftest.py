"""Global fixtures for solarweb integration."""

from unittest.mock import patch

import pytest
import pytest_asyncio
from fronius_solarweb.errors import NotAuthorizedException
from fronius_solarweb.schema.pvsystem import (
    PvSystemAggrDataV2,
    PvSystemFlowData,
    PvSystemMetaData,
)

from .const import PV_AGGR_DATA, PV_FLOW_DATA, PV_SYS_DATA

pytest_plugins = "pytest_homeassistant_custom_component"

sys_data = PvSystemMetaData(**PV_SYS_DATA)
raw_flow_data = PvSystemFlowData(**PV_FLOW_DATA)
raw_aggr_data = PvSystemAggrDataV2(**PV_AGGR_DATA)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations) -> None:
    """Enable custom integrations defined in the test dir."""
    return


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


# This fixture, when used, will result in calls to async_update_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest_asyncio.fixture(name="bypass_get_data")
async def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    with (
        patch(
            "fronius_solarweb.Fronius_Solarweb.get_system_flow_data",
            return_value=raw_flow_data,
        ),
        patch(
            "fronius_solarweb.Fronius_Solarweb.get_system_aggr_data_v2",
            return_value=raw_aggr_data,
        ),
        patch(
            "fronius_solarweb.Fronius_Solarweb.get_pvsystem_meta_data",
            return_value=sys_data,
        ),
    ):
        yield


# In this fixture, we are forcing calls to api to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with (
        patch(
            "fronius_solarweb.Fronius_Solarweb.get_system_flow_data",
            side_effect=Exception,
        ),
        patch(
            "fronius_solarweb.Fronius_Solarweb.get_system_aggr_data_v2",
            side_effect=Exception,
        ),
    ):
        yield


# In this fixture, we are forcing calls to api to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_with_api")
def error_with_api_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "fronius_solarweb.Fronius_Solarweb.get_pvsystem_meta_data",
        side_effect=NotAuthorizedException,
    ):
        yield
