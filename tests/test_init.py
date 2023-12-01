"""Test solarweb setup process."""
import logging

import pytest
from custom_components.solarweb import (
    async_reload_entry,
)
from custom_components.solarweb import (
    async_setup_entry,
)
from custom_components.solarweb import (
    async_unload_entry,
)
from custom_components.solarweb import (
    FlowDataUpdateCoordinator,
)
from custom_components.solarweb.const import (
    DOMAIN,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG_INIT


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
async def test_setup_unload_and_reload_entry(hass, bypass_get_data, caplog):
    """Test entry setup and unload."""
    caplog.set_level(logging.DEBUG)
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_INIT, entry_id="test_setup", title="test_setup"
    )
    # config_entry.add_to_hass(hass)
    hass.config_entries._entries[config_entry.entry_id] = config_entry

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the FlowDataUpdateCoordinator.async_get_data
    # call, no code from fronius_solarweb library.
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Note title is from Mock rather than PV_SYS_DATA as not using config flow
    stateFlow = hass.states.get("sensor.test_setup_energy")
    stateAggr = hass.states.get("sensor.test_setup_savings")

    assert stateFlow
    # Note precision included in state reported
    assert stateFlow.state == "1.0"

    assert stateAggr
    # Note precision included in state reported
    assert stateAggr.state == "0.5"

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id][0], FlowDataUpdateCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id][0], FlowDataUpdateCoordinator
    )

    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_INIT, entry_id="test", title="test"
    )
    config_entry.add_to_hass(hass)

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises((ConfigEntryNotReady, UpdateFailed)):
        assert await async_setup_entry(hass, config_entry)
