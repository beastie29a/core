"""Tests for home_connect binary_sensor entities."""

from collections.abc import Awaitable, Callable
from unittest.mock import MagicMock, Mock

from homeconnect.api import HomeConnectAppliance
import pytest

from homeassistant.components.home_connect.const import (
    BSH_DOOR_STATE,
    BSH_DOOR_STATE_CLOSED,
    BSH_DOOR_STATE_LOCKED,
    BSH_DOOR_STATE_OPEN,
    BSH_REMOTE_CONTROL_ACTIVATION_STATE,
    BSH_REMOTE_START_ALLOWANCE_STATE,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import async_update_entity

from tests.common import MockConfigEntry, load_json_object_fixture


@pytest.fixture
def platforms() -> list[str]:
    """Fixture to specify platforms to test."""
    return [Platform.BINARY_SENSOR]


@pytest.mark.usefixtures("bypass_throttle")
async def test_binary_sensors(
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: MagicMock,
    appliance: Mock,
) -> None:
    """Test binary sensor entities."""
    get_appliances.return_value = [appliance]
    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED


@pytest.mark.parametrize(
    ("entity_id", "state", "expected"),
    [
        (
            "binary_sensor.washer_door",
            {BSH_DOOR_STATE: {"value": BSH_DOOR_STATE_CLOSED}},
            "off",
        ),
        (
            "binary_sensor.washer_door",
            {BSH_DOOR_STATE: {"value": BSH_DOOR_STATE_LOCKED}},
            "off",
        ),
        (
            "binary_sensor.washer_door",
            {BSH_DOOR_STATE: {"value": BSH_DOOR_STATE_OPEN}},
            "on",
        ),
        (
            "binary_sensor.washer_door",
            {BSH_DOOR_STATE: {}},
            "unknown",
        ),
        (
            "binary_sensor.washer_remote_control",
            {BSH_REMOTE_CONTROL_ACTIVATION_STATE: {"value": False}},
            "off",
        ),
        (
            "binary_sensor.washer_remote_start",
            {BSH_REMOTE_START_ALLOWANCE_STATE: {"value": False}},
            "off",
        ),
        (
            "binary_sensor.washer_remote_control",
            {BSH_REMOTE_CONTROL_ACTIVATION_STATE: {}},
            "unknown",
        ),
    ],
)
@pytest.mark.usefixtures("bypass_throttle")
async def test_binary_sensors_door_states(
    entity_id: str,
    expected: str,
    state: str,
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: MagicMock,
    appliance: Mock,
) -> None:
    """Tests for Appliance door states."""
    appliance.status.update(
        HomeConnectAppliance.json2dict(
            load_json_object_fixture("home_connect/status.json")
            .get("data")
            .get("status")
        )
    )
    get_appliances.return_value = [appliance]
    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED

    appliance.status.update(state)
    await async_update_entity(hass, entity_id)
    await hass.async_block_till_done()
    assert hass.states.is_state(entity_id, expected)
