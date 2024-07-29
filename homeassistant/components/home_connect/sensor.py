"""Provides a sensor for Home Connect."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from .api import HomeConnectDevice
from .const import (
    ATTR_DEVICE,
    ATTR_VALUE,
    BSH_DOOR_STATE,
    BSH_EVENT_PRESENT_STATE_ENUM,
    BSH_EVENT_PRESENT_STATE_OFF,
    BSH_OPERATION_STATE,
    BSH_OPERATION_STATE_DELAYED_START,
    BSH_OPERATION_STATE_ENUM,
    BSH_OPERATION_STATE_FINISHED,
    BSH_OPERATION_STATE_PAUSE,
    BSH_OPERATION_STATE_RUN,
    BSH_PROGRAM_PROGRESS,
    BSH_REMAINING_PROGRAM_TIME,
    COOKING_CURRENT_CAVITY_TEMP,
    DOMAIN,
    REFRIGERATION_EVENT_DOOR_ALARM_FREEZER,
    REFRIGERATION_EVENT_DOOR_ALARM_REFRIGERATOR,
    REFRIGERATION_EVENT_TEMP_ALARM_FREEZER,
    REFRIGERATION_STATUS_DOOR_CHILLER,
    REFRIGERATION_STATUS_DOOR_FREEZER,
    REFRIGERATION_STATUS_DOOR_REFRIGERATOR,
)
from .entity import HomeConnectEntity
from .models import StatusData

_LOGGER = logging.getLogger(__name__)


def program_running(status: dict) -> bool:
    """Return true if a program has started after initial delay."""

    return (
        (progress := status.get(BSH_PROGRAM_PROGRESS, {}).get(ATTR_VALUE, 0))
        and (remaining := status.get(BSH_REMAINING_PROGRAM_TIME, {}).get(ATTR_VALUE, 0))
    ) and (progress > 0 or remaining > 0)


def remove_from_status(status: dict, key: str) -> None:
    """Reset the state of event based sensors."""
    status.pop(key, None)


def update_event_state(status: dict) -> bool:
    """Return true if operation state is valid."""
    return status.get(BSH_OPERATION_STATE, {}).get(ATTR_VALUE, "") in (
        BSH_OPERATION_STATE_RUN,
        BSH_OPERATION_STATE_DELAYED_START,
        BSH_OPERATION_STATE_PAUSE,
        BSH_OPERATION_STATE_FINISHED,
    )


def format_state_attr(state: str) -> str:
    """Format state values to attribute values."""
    return state.rsplit(".", maxsplit=1)[-1].lower()


@dataclass(frozen=True)
class HomeConnectSensorEntityDescription(SensorEntityDescription):
    """Entity Description class for binary sensors."""

    device_class: SensorDeviceClass | None = SensorDeviceClass.ENUM
    state_key: str | None = None
    sign: int = 1
    value_fn: Callable[[dict], Any] = lambda _: None
    status_data_fn: Callable[[HomeConnectDevice], StatusData] = lambda _: StatusData(
        key="",
        value={},
    )
    options_fn: Callable[[StatusData], list[str] | None] = lambda _: None
    exists_fn: Callable[[HomeConnectDevice], bool] = lambda _: True


SENSORS: tuple[HomeConnectSensorEntityDescription, ...] = (
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_STATUS_DOOR_CHILLER,
        key="Chiller Door",
        translation_key="door_sensor",
        translation_placeholders={"name": "Chiller Door"},
        value_fn=lambda status: format_state_attr(
            status[REFRIGERATION_STATUS_DOOR_CHILLER].get(ATTR_VALUE)
        ),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{REFRIGERATION_STATUS_DOOR_CHILLER}")
        ),
        options_fn=lambda status_data: [
            format_state_attr(value) for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: bool(
            device.appliance.status.get(REFRIGERATION_STATUS_DOOR_CHILLER)
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_STATUS_DOOR_FREEZER,
        key="Freezer Door",
        translation_key="door_sensor",
        translation_placeholders={"name": "Freezer Door"},
        value_fn=lambda status: format_state_attr(
            status[REFRIGERATION_STATUS_DOOR_FREEZER].get(ATTR_VALUE)
        ),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{REFRIGERATION_STATUS_DOOR_FREEZER}")
        ),
        options_fn=lambda status_data: [
            format_state_attr(value) for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: device.appliance.status.get(
            REFRIGERATION_STATUS_DOOR_FREEZER, False
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_EVENT_DOOR_ALARM_FREEZER,
        key="Door Alarm Freezer",
        translation_key="alarm_sensor_freezer",
        translation_placeholders={
            "name": "Door Alarm Freezer",
        },
        value_fn=lambda status: format_state_attr(
            status.get(REFRIGERATION_EVENT_DOOR_ALARM_FREEZER, {}).get(
                ATTR_VALUE, BSH_EVENT_PRESENT_STATE_OFF
            )
        ),
        options_fn=lambda _: [
            format_state_attr(value) for value in BSH_EVENT_PRESENT_STATE_ENUM
        ],
        exists_fn=lambda device: device.appliance.status.get(
            REFRIGERATION_STATUS_DOOR_FREEZER, False
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_STATUS_DOOR_REFRIGERATOR,
        key="Refrigerator Door",
        translation_key="door_sensor",
        translation_placeholders={"name": "Refrigerator Door"},
        value_fn=lambda status: status[REFRIGERATION_STATUS_DOOR_REFRIGERATOR]
        .get(ATTR_VALUE)
        .rsplit(".", maxsplit=1)[-1]
        .lower(),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{REFRIGERATION_STATUS_DOOR_REFRIGERATOR}")
        ),
        options_fn=lambda status_data: [
            format_state_attr(value) for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: device.appliance.status.get(
            REFRIGERATION_STATUS_DOOR_REFRIGERATOR, False
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_EVENT_DOOR_ALARM_REFRIGERATOR,
        key="Door Alarm Refrigerator",
        translation_key="alarm_sensor_fridge",
        translation_placeholders={
            "name": "Door Alarm Refrigerator",
        },
        value_fn=lambda status: format_state_attr(
            status.get(REFRIGERATION_EVENT_DOOR_ALARM_REFRIGERATOR, {}).get(
                ATTR_VALUE, BSH_EVENT_PRESENT_STATE_OFF
            )
        ),
        options_fn=lambda _: [
            format_state_attr(value) for value in BSH_EVENT_PRESENT_STATE_ENUM
        ],
        exists_fn=lambda device: device.appliance.status.get(
            REFRIGERATION_STATUS_DOOR_REFRIGERATOR, False
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=REFRIGERATION_EVENT_TEMP_ALARM_FREEZER,
        key="Temperature Alarm Freezer",
        translation_key="alarm_sensor_temp",
        translation_placeholders={
            "name": "Temperature Alarm Freezer",
        },
        value_fn=lambda status: format_state_attr(
            status.get(REFRIGERATION_EVENT_TEMP_ALARM_FREEZER, {}).get(
                ATTR_VALUE, BSH_EVENT_PRESENT_STATE_OFF
            )
        ),
        options_fn=lambda _: [
            format_state_attr(value) for value in BSH_EVENT_PRESENT_STATE_ENUM
        ],
        exists_fn=lambda device: bool(
            device.appliance.type in ("FridgeFreezer", "Freezer")
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=BSH_DOOR_STATE,
        key="Door",
        translation_key="door_sensor",
        translation_placeholders={"name": "Door"},
        value_fn=lambda status: status[BSH_DOOR_STATE]
        .get(ATTR_VALUE)
        .rsplit(".", maxsplit=1)[-1]
        .lower(),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{BSH_DOOR_STATE}")
        ),
        options_fn=lambda status_data: [
            format_state_attr(value) for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: device.appliance.status.get(BSH_DOOR_STATE, False),
    ),
    HomeConnectSensorEntityDescription(
        state_key=BSH_REMAINING_PROGRAM_TIME,
        key="Remaining Program Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        translation_key="event_sensor",
        translation_placeholders={
            "name": "Remaining Program Time",
        },
        value_fn=lambda status: dt_util.utcnow()
        + timedelta(seconds=remaining_time.get(ATTR_VALUE))
        if (remaining_time := status.get(BSH_REMAINING_PROGRAM_TIME, False))
        and update_event_state(status)
        # Reset state: Remove entry from appliance.status
        else remove_from_status(status, BSH_REMAINING_PROGRAM_TIME)
        if remaining_time
        else None,
        exists_fn=lambda device: getattr(device, "programs", False),
    ),
    HomeConnectSensorEntityDescription(
        state_key=BSH_PROGRAM_PROGRESS,
        key="Program Progress",
        device_class=None,
        translation_key="event_sensor",
        translation_placeholders={
            "name": "Program Progress",
        },
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:progress-clock",
        value_fn=lambda status: progress.get(ATTR_VALUE)
        if (progress := status.get(BSH_PROGRAM_PROGRESS, False))
        and update_event_state(status)
        # Reset state: Remove entry from appliance.status
        else remove_from_status(status, BSH_PROGRAM_PROGRESS)
        if progress
        else None,
        exists_fn=lambda device: getattr(device, "programs", False),
    ),
    HomeConnectSensorEntityDescription(
        state_key=BSH_OPERATION_STATE,
        key="Operation State",
        icon="mdi:state-machine",
        translation_key="state_sensors",
        translation_placeholders={
            "name": "Operation State",
        },
        options_fn=lambda _: [
            format_state_attr(state) for state in BSH_OPERATION_STATE_ENUM
        ],
        value_fn=lambda status: format_state_attr(value)
        if (value := status[BSH_OPERATION_STATE][ATTR_VALUE])
        != BSH_OPERATION_STATE_DELAYED_START
        # Force state: An event STATUS with state 'Run' is not sent when there is a 'DelayedStart'
        else format_state_attr(BSH_OPERATION_STATE_RUN)
        if program_running(status)
        else format_state_attr(value),
        exists_fn=lambda device: device.appliance.status.get(
            BSH_OPERATION_STATE, False
        ),
    ),
    HomeConnectSensorEntityDescription(
        state_key=COOKING_CURRENT_CAVITY_TEMP,
        key="Current Cavity Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        translation_key="status_sensors",
        translation_placeholders={
            "name": "Current Cavity Temperature",
        },
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda status: status[COOKING_CURRENT_CAVITY_TEMP][ATTR_VALUE],
        exists_fn=lambda device: device.appliance.status.get(
            COOKING_CURRENT_CAVITY_TEMP, False
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Home Connect sensor."""

    def get_entities():
        """Get a list of entities."""
        entities = []
        hc_api = hass.data[DOMAIN][config_entry.entry_id]
        for device_dict in hc_api.devices:
            device: HomeConnectDevice = device_dict[ATTR_DEVICE]
            entities += [
                HomeConnectSensor(
                    device,
                    entity_description=description,
                    status_data=description.status_data_fn(device),
                )
                for description in SENSORS
                if description.exists_fn(device)
            ]
        return entities

    async_add_entities(await hass.async_add_executor_job(get_entities), True)


class HomeConnectSensor(HomeConnectEntity, SensorEntity):
    """Sensor class for Home Connect."""

    def __init__(
        self,
        device: HomeConnectDevice,
        entity_description: HomeConnectSensorEntityDescription,
        status_data: StatusData,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: HomeConnectSensorEntityDescription = entity_description
        super().__init__(device, self.entity_description.key)
        self._key = self.entity_description.state_key
        self._sign = self.entity_description.sign
        self._attr_icon = self.entity_description.icon
        _LOGGER.debug("Status Data: %s", status_data)
        self._status_data = status_data
        self._attr_options = self.entity_description.options_fn(self._status_data)

    @property
    def available(self) -> bool:
        """Return true if the sensor is available."""
        return self._attr_native_value is not None

    async def async_update(self) -> None:
        """Update the sensor's status."""
        self._attr_native_value = self.entity_description.value_fn(
            self.device.appliance.status
        )
        _LOGGER.debug(
            "Updated: %s, new state: %s",
            self._attr_unique_id,
            self._attr_native_value,
        )
