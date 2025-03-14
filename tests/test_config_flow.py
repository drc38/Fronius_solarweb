"""Test solarweb config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solarweb.const import DOMAIN

from .const import MOCK_CONFIG, PV_SYS_DATA
from .const import MOCK_CONFIG_INIT


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch(
            "custom_components.solarweb.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.solarweb.async_setup_entry",
            return_value=True,
        ),
    ):
        yield


# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
async def test_successful_config_flow(hass, bypass_get_data) -> None:
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to enter form it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == PV_SYS_DATA["name"]
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


async def test_reconfigure_entry(hass, bypass_get_data, caplog) -> None:
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_INIT,
        entry_id="test_reconfigure",
        title="test_reconfigure",
    )
    config_entry.add_to_hass(hass)
    # hass.config_entries._entries[config_entry.entry_id] = config_entry

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the FlowDataUpdateCoordinator.async_get_data
    # call, no code from fronius_solarweb library.
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry.entry_id,
        },
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # If a user were to enter form it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.FlowResultType.ABORT


# In this case, we want to simulate a failure during the config flow.
# We use the `error_on_get_data` mock instead of `bypass_get_data`
# (note the function parameters) to raise an Exception during
# validation of the input config.
async def test_failed_config_flow(hass, error_with_api) -> None:
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "auth"}
