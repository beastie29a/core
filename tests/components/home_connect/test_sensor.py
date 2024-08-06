"""Tests for home_connect sensor entities."""

from collections.abc import Awaitable, Callable
from unittest.mock import MagicMock, Mock

from freezegun.api import FrozenDateTimeFactory
from homeconnect.api import HomeConnectAppliance
import pytest

from homeassistant.components.home_connect.const import (
    ATTR_VALUE,
    BSH_OPERATION_STATE,
    BSH_OPERATION_STATE_DELAYED_START,
    BSH_OPERATION_STATE_READY,
    BSH_OPERATION_STATE_RUN,
    BSH_PROGRAM_PROGRESS,
    BSH_REMAINING_PROGRAM_TIME,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import async_update_entity

from tests.common import MockConfigEntry, load_json_object_fixture

TEST_HC_APP = "Dishwasher"


EVENT_PROG_DELAYED_START = {
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_DELAYED_START},
}

EVENT_PROG_REMAIN_NO_VALUE = {
    BSH_REMAINING_PROGRAM_TIME: {},
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_DELAYED_START},
}


EVENT_PROG_RUN = {
    BSH_REMAINING_PROGRAM_TIME: {ATTR_VALUE: 0},
    BSH_PROGRAM_PROGRESS: {ATTR_VALUE: 60},
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_RUN},
}


EVENT_PROG_UPDATE_1 = {
    BSH_REMAINING_PROGRAM_TIME: {ATTR_VALUE: 0},
    BSH_PROGRAM_PROGRESS: {ATTR_VALUE: 80},
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_RUN},
}

EVENT_PROG_UPDATE_2 = {
    BSH_REMAINING_PROGRAM_TIME: {ATTR_VALUE: 20},
    BSH_PROGRAM_PROGRESS: {ATTR_VALUE: 99},
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_RUN},
}

EVENT_PROG_END = {
    BSH_OPERATION_STATE: {ATTR_VALUE: BSH_OPERATION_STATE_READY},
}


@pytest.fixture
def platforms() -> list[str]:
    """Fixture to specify platforms to test."""
    return [Platform.SENSOR]


@pytest.mark.usefixtures("bypass_throttle")
async def test_sensors(
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: MagicMock,
    appliance: Mock,
) -> None:
    """Test sensor entities."""
    get_appliances.return_value = [appliance]
    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED


# Appliance program sequence with a delayed start.
PROGRAM_SEQUENCE_EVENTS = (
    EVENT_PROG_DELAYED_START,
    EVENT_PROG_RUN,
    EVENT_PROG_UPDATE_1,
    EVENT_PROG_UPDATE_2,
    EVENT_PROG_END,
)

# Entity mapping to expected state at each program sequence.
ENTITY_ID_STATES = {
    "sensor.dishwasher_operation_state": (
        "DelayedStart",
        "Run",
        "Run",
        "Run",
        "Ready",
    ),
    "sensor.dishwasher_remaining_program_time": (
        "unavailable",
        "2021-01-09T12:00:00+00:00",
        "2021-01-09T12:00:00+00:00",
        "2021-01-09T12:00:20+00:00",
        "unavailable",
    ),
    "sensor.dishwasher_program_progress": (
        "unavailable",
        "60",
        "80",
        "99",
        "unavailable",
    ),
}


@pytest.mark.parametrize("appliance", [TEST_HC_APP], indirect=True)
@pytest.mark.parametrize(
    ("states", "event_run"),
    list(
        zip(
            list(zip(*ENTITY_ID_STATES.values(), strict=False)),
            PROGRAM_SEQUENCE_EVENTS,
            strict=False,
        )
    ),
)
@pytest.mark.usefixtures("bypass_throttle")
async def test_event_sensors(
    appliance: Mock,
    states: tuple[str, str],
    event_run: dict[str, dict[str, str]],
    freezer: FrozenDateTimeFactory,
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: MagicMock,
) -> None:
    """Test sequence for sensors that are only available after an event happens."""
    entity_ids = ENTITY_ID_STATES.keys()

    time_to_freeze = "2021-01-09 12:00:00+00:00"
    freezer.move_to(time_to_freeze)
    appliance.get.side_effect = (
        lambda x: load_json_object_fixture("home_connect/status-data.json")
        .get(x, {})
        .get("data", {})
    )
    appliance.get_programs_available.return_value = [
        p["key"]
        for p in load_json_object_fixture("home_connect/programs-available.json")
        .get(appliance.name, {})
        .get("data", {})
        .get("programs", [])
    ]
    appliance.status.update(
        HomeConnectAppliance.json2dict(
            load_json_object_fixture("home_connect/status.json")
            .get("data", {})
            .get("status", {})
        )
    )
    get_appliances.return_value = [appliance]

    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED

    appliance.status.update(event_run)
    for entity_id, state in zip(entity_ids, states, strict=False):
        await async_update_entity(hass, entity_id)
        await hass.async_block_till_done()
        assert hass.states.is_state(entity_id, state)


# Program sequence for SensorDeviceClass.TIMESTAMP edge cases.
PROGRAM_SEQUENCE_EDGE_CASE = [
    EVENT_PROG_REMAIN_NO_VALUE,
    EVENT_PROG_RUN,
    EVENT_PROG_END,
    EVENT_PROG_END,
]

# Expected state at each sequence.
ENTITY_ID_EDGE_CASE_STATES = [
    "unavailable",
    "2021-01-09T12:00:01+00:00",
    "unavailable",
    "unavailable",
]


@pytest.mark.parametrize("appliance", [TEST_HC_APP], indirect=True)
@pytest.mark.usefixtures("bypass_throttle")
async def test_remaining_prog_time_edge_cases(
    appliance: Mock,
    freezer: FrozenDateTimeFactory,
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    integration_setup: Callable[[], Awaitable[bool]],
    setup_credentials: None,
    get_appliances: MagicMock,
) -> None:
    """Run program sequence to test edge cases for the remaining_prog_time entity."""
    appliance.get.side_effect = (
        lambda x: load_json_object_fixture("home_connect/status-data.json")
        .get(x, {})
        .get("data", {})
    )
    appliance.get_programs_available.return_value = [
        p["key"]
        for p in load_json_object_fixture("home_connect/programs-available.json")
        .get(appliance.name)
        .get("data")
        .get("programs")
    ]
    appliance.status.update(
        HomeConnectAppliance.json2dict(
            load_json_object_fixture("home_connect/status.json")
            .get("data")
            .get("status")
        )
    )
    get_appliances.return_value = [appliance]
    entity_id = "sensor.dishwasher_remaining_program_time"
    time_to_freeze = "2021-01-09 12:00:00+00:00"
    freezer.move_to(time_to_freeze)

    assert config_entry.state == ConfigEntryState.NOT_LOADED
    assert await integration_setup()
    assert config_entry.state == ConfigEntryState.LOADED

    for (
        event,
        expected_state,
    ) in zip(PROGRAM_SEQUENCE_EDGE_CASE, ENTITY_ID_EDGE_CASE_STATES, strict=False):
        appliance.status.update(event)
        await async_update_entity(hass, entity_id)
        await hass.async_block_till_done()
        freezer.tick()
        assert hass.states.is_state(entity_id, expected_state)
