"""Tests for home_connect sensor entities."""

from collections.abc import Awaitable, Callable, Generator
from unittest.mock import Mock

from homeconnect.api import HomeConnectAppliance
import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .conftest import get_all_appliances

from tests.common import MockConfigEntry, load_json_object_fixture

MOCK_GET_SETTINGS_RESPONSES = {
    setting["key"]: setting
    for setting in load_json_object_fixture("home_connect/settings.json")
    .get("FridgeFreezer")
    .get("data")
    .get("settings")
}


@pytest.fixture
def platforms() -> list[str]:
    """Fixture to specify platforms to test."""
    return [Platform.NUMBER]


async def test_number(
    bypass_throttle: Generator[None],
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: Mock,
) -> None:
    """Test number platform."""
    get_appliances.side_effect = get_all_appliances
    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED


@pytest.mark.parametrize("appliance", ["FridgeFreezer"], indirect=True)
async def test_number_functionality(
    appliance: Mock,
    bypass_throttle: Generator[None],
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: Mock,
) -> None:
    """Test number platform."""
    appliance.get.side_effect = lambda key: MOCK_GET_SETTINGS_RESPONSES[
        key.split("/")[-1]
    ]
    appliance.status.update(
        HomeConnectAppliance.json2dict(
            load_json_object_fixture("home_connect/settings.json")
            .get(appliance.name)
            .get("data")
            .get("settings")
        )
    )
    get_appliances.return_value = [appliance]

    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED
