"""Provides a binary sensor for Home Connect."""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HomeConnectDevice
from .const import (
    ATTR_VALUE,
    BSH_REMOTE_CONTROL_ACTIVATION_STATE,
    BSH_REMOTE_START_ALLOWANCE_STATE,
    DOMAIN,
)
from .entity import HomeConnectEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class HomeConnectBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Entity Description class for binary sensors."""

    state_key: str | None = None
    value_fn: Callable[[dict], bool] = lambda _: True
    exists_fn: Callable[[HomeConnectDevice], bool] = lambda _: True


BINARY_SENSORS: tuple[HomeConnectBinarySensorEntityDescription, ...] = (
    HomeConnectBinarySensorEntityDescription(
        state_key=BSH_REMOTE_CONTROL_ACTIVATION_STATE,
        key="Remote Control",
        device_class=None,
        value_fn=lambda status: status.get(BSH_REMOTE_CONTROL_ACTIVATION_STATE, {}).get(
            ATTR_VALUE, False
        ),
        exists_fn=lambda device: bool(
            device.appliance.status.get(BSH_REMOTE_CONTROL_ACTIVATION_STATE)
        ),
    ),
    HomeConnectBinarySensorEntityDescription(
        state_key=BSH_REMOTE_START_ALLOWANCE_STATE,
        key="Remote Start",
        device_class=None,
        value_fn=lambda status: status.get(BSH_REMOTE_START_ALLOWANCE_STATE, {}).get(
            ATTR_VALUE, False
        ),
        exists_fn=lambda device: bool(
            device.appliance.status.get(BSH_REMOTE_START_ALLOWANCE_STATE)
        ),
    ),
    HomeConnectBinarySensorEntityDescription(
        state_key="Refrigeration.FridgeFreezer.Event.DoorAlarmRefrigerator",
        key="Door Alarm Refrigerator",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda status: status.get(
            "Refrigeration.FridgeFreezer.Event.DoorAlarmRefrigerator", {}
        ).get(ATTR_VALUE, "")
        == "BSH.Common.EnumType.EventPresentState.Present"
        and status["BSH.Common.Status.DoorState"]
        != "BSH.Common.EnumType.DoorState.Closed",
        exists_fn=lambda device: bool(device.appliance.type == "FridgeFreezer"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Home Connect binary sensor."""

    def get_entities():
        entities = []
        hc_api = hass.data[DOMAIN][config_entry.entry_id]
        for device_dict in hc_api.devices:
            entities += [
                HomeConnectBinarySensor(
                    device_dict["device"], entity_description=description
                )
                for description in BINARY_SENSORS
                if description.exists_fn(device_dict["device"])
            ]
        return entities

    async_add_entities(await hass.async_add_executor_job(get_entities), True)


class HomeConnectBinarySensor(HomeConnectEntity, BinarySensorEntity):
    """Binary sensor for Home Connect."""

    def __init__(
        self,
        device,
        entity_description: HomeConnectBinarySensorEntityDescription,
    ) -> None:
        """Initialize the entity."""
        self.entity_description: HomeConnectBinarySensorEntityDescription = (
            entity_description
        )
        super().__init__(device, self.entity_description.key)
        self._state = None
        self._update_key = self.entity_description.state_key

    @property
    def available(self) -> bool:
        """Return true if the binary sensor is available."""
        return bool(self.device.appliance.status.get(self._update_key))

    async def async_update(self) -> None:
        """Update the binary sensor's status."""
        self._attr_is_on = self.entity_description.value_fn(
            self.device.appliance.status
        )
        _LOGGER.debug(
            "Updated: %s, new state: %s", self.device.appliance.haId, self._state
        )
