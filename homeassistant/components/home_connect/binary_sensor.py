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
    BSH_DOOR_STATE,
    BSH_DOOR_STATE_CLOSED,
    BSH_DOOR_STATE_LOCKED,
    BSH_DOOR_STATE_OPEN,
    BSH_REMOTE_CONTROL_ACTIVATION_STATE,
    BSH_REMOTE_START_ALLOWANCE_STATE,
    DOMAIN,
)
from .entity import HomeConnectEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HomeConnectBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Entity Description class for binary sensors."""

    state_key: str
    value_fn: Callable[[dict[str, dict[str, bool]], str], bool | None] = (
        lambda status, state_key: status.get(state_key, {}).get(ATTR_VALUE)
    )


BINARY_SENSORS: tuple[HomeConnectBinarySensorEntityDescription, ...] = (
    HomeConnectBinarySensorEntityDescription(
        key="Door",
        device_class=BinarySensorDeviceClass.DOOR,
        state_key=BSH_DOOR_STATE,
        value_fn=lambda status, state_key: True
        if (door_state := status.get(state_key, {}).get(ATTR_VALUE, ""))
        == BSH_DOOR_STATE_OPEN
        else False
        if door_state
        in (
            BSH_DOOR_STATE_CLOSED,
            BSH_DOOR_STATE_LOCKED,
        )
        else None,
    ),
    HomeConnectBinarySensorEntityDescription(
        key="Remote Control",
        state_key=BSH_REMOTE_CONTROL_ACTIVATION_STATE,
    ),
    HomeConnectBinarySensorEntityDescription(
        key="Remote Start",
        state_key=BSH_REMOTE_START_ALLOWANCE_STATE,
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
            device: HomeConnectDevice = device_dict["device"]
            entities.extend(
                HomeConnectBinarySensor(device=device, entity_description=description)
                for description in BINARY_SENSORS
                if description.state_key in device.appliance.status
            )
        return entities

    async_add_entities(await hass.async_add_executor_job(get_entities), True)


class HomeConnectBinarySensor(HomeConnectEntity, BinarySensorEntity):
    """Binary sensor for Home Connect."""

    entity_description: HomeConnectBinarySensorEntityDescription

    def __init__(
        self,
        device,
        entity_description: HomeConnectBinarySensorEntityDescription,
    ) -> None:
        """Initialize the entity."""
        self.entity_description = entity_description
        super().__init__(device=device, desc=self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return true if the binary sensor is available."""
        return self.entity_description.state_key in self.device.appliance.status

    async def async_update(self) -> None:
        """Update the binary sensor's status."""
        _LOGGER.debug(
            "Updating: %s, cur state: %s",
            self._attr_unique_id,
            self._attr_state,
        )
        self._attr_is_on = self.entity_description.value_fn(
            self.device.appliance.status, self.entity_description.state_key
        )
        _LOGGER.debug(
            "Updated: %s, new state: %s",
            self._attr_unique_id,
            self._attr_state,
        )
