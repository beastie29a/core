"""Provides a sensor for Home Connect."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property
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
    REFRIGERATION_STATUS_DOOR_CHILLER,
    REFRIGERATION_STATUS_DOOR_FREEZER,
    REFRIGERATION_STATUS_DOOR_REFRIGERATOR,
)
from .entity import HomeConnectEntity
from .models import StatusData

_LOGGER = logging.getLogger(__name__)


def update_event_state(status: dict) -> bool:
    """Return value for event drviven sensors."""
    return status.get(BSH_OPERATION_STATE, {}).get(ATTR_VALUE, "") in [
        BSH_OPERATION_STATE_RUN,
        BSH_OPERATION_STATE_DELAYED_START,
        BSH_OPERATION_STATE_PAUSE,
        BSH_OPERATION_STATE_FINISHED,
    ]


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
        value_fn=lambda status: status[REFRIGERATION_STATUS_DOOR_CHILLER]
        .get(ATTR_VALUE)
        .rsplit(".", maxsplit=1)[-1]
        .lower(),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{REFRIGERATION_STATUS_DOOR_CHILLER}")
        ),
        options_fn=lambda status_data: [
            value.rsplit(".", maxsplit=1)[-1].lower()
            for value in status_data.constraints.allowedvalues
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
        value_fn=lambda status: status[REFRIGERATION_STATUS_DOOR_FREEZER]
        .get(ATTR_VALUE)
        .rsplit(".", maxsplit=1)[-1]
        .lower(),
        status_data_fn=lambda device: StatusData(
            **device.appliance.get(f"/status/{REFRIGERATION_STATUS_DOOR_FREEZER}")
        ),
        options_fn=lambda status_data: [
            value.rsplit(".", maxsplit=1)[-1].lower()
            for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: bool(
            device.appliance.status.get(REFRIGERATION_STATUS_DOOR_FREEZER)
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
            value.rsplit(".", maxsplit=1)[-1].lower()
            for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: bool(
            device.appliance.status.get(REFRIGERATION_STATUS_DOOR_REFRIGERATOR)
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
            value.rsplit(".", maxsplit=1)[-1].lower()
            for value in status_data.constraints.allowedvalues
        ],
        exists_fn=lambda device: bool(device.appliance.status.get(BSH_DOOR_STATE)),
    ),
    HomeConnectSensorEntityDescription(
        state_key=BSH_REMAINING_PROGRAM_TIME,
        key="Remaining Program Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        translation_key="event_sensor",
        translation_placeholders={
            "name": "Remaining Program Time",
            "remaining_program_time": "Remaining Program Time",
            "completed_program_time": "Completed Program Time",
        },
        value_fn=lambda status: dt_util.utcnow()
        + timedelta(seconds=status.get(BSH_REMAINING_PROGRAM_TIME, {}).get(ATTR_VALUE))
        if update_event_state(status) and status.get(BSH_REMAINING_PROGRAM_TIME)
        else None,
        exists_fn=lambda device: bool(bool(device.programs)),
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
        value_fn=lambda status: status.get(BSH_PROGRAM_PROGRESS, {}).get(ATTR_VALUE)
        if update_event_state(status)
        else None,
        exists_fn=lambda device: bool(device.programs),
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
            state.rsplit(".", maxsplit=1)[-1].lower()
            for state in BSH_OPERATION_STATE_ENUM
        ],
        value_fn=lambda status: status[BSH_OPERATION_STATE]
        .get(ATTR_VALUE)
        .rsplit(".", maxsplit=1)[-1]
        .lower(),
        exists_fn=lambda device: bool(device.appliance.status.get(BSH_OPERATION_STATE)),
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
        value_fn=lambda status: status[COOKING_CURRENT_CAVITY_TEMP].get(ATTR_VALUE),
        exists_fn=lambda device: bool(
            device.appliance.status.get("Cooking.Oven.Status.CurrentCavityTemperature")
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

    @property
    def available(self) -> bool:
        """Return true if the sensor is available."""
        return self._attr_native_value is not None

    @cached_property
    def options(self) -> list | None:
        """Return a list valid states for ENUM device_class or None otherwise."""
        return self.entity_description.options_fn(self._status_data)

    async def async_update(self) -> None:
        """Update the sensor's status."""
        self._attr_native_value = self.entity_description.value_fn(
            self.device.appliance.status
        )
        _LOGGER.debug("Updated, new state: %s", self._attr_native_value)
